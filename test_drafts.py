"""Pruebas puras del borrador local, sin navegador ni Google Sheets."""

from pathlib import Path
import json
import uuid

import pytest

from demographics import ALL_RESIDENCE_OPTIONS, AGE_RANGES
from drafts import (
    DRAFT_SCHEMA_VERSION,
    DRAFT_STORAGE_KEY,
    DRAFT_TTL_SECONDS,
    QUESTION_IDS,
    build_draft,
    district_option_for_draft,
    parse_and_validate_draft,
    serialize_draft,
    validate_draft,
)
from instrument_version import INSTRUMENT_VERSION
from questions import QUESTIONS
from scoring import calculate_scores
from submission import reset_submission


NOW_MS = 2_000_000_000_000
COMPONENT_JS = Path("components/draft_storage/index.js").read_text(
    encoding="utf-8"
)


def draft_state(*, response_count=12, step=12):
    answers = {
        question_id: (index % 5) + 1
        for index, question_id in enumerate(QUESTION_IDS[:response_count])
    }
    state = {
        "response_uuid": str(uuid.uuid4()),
        "current_question": min(step, 24) - 1,
        "demographic_step": 0,
        "answers": answers,
        "age_range": None,
        "dem_district": None,
    }
    return state


def valid_draft(*, response_count=12, step=12):
    state = draft_state(response_count=response_count, step=step)
    return build_draft(
        state,
        elapsed_active_seconds=74.2,
        now_ms=NOW_MS,
    )


def test_draft_serializes_only_the_allowed_schema_and_q01_to_q24():
    draft = valid_draft(response_count=24, step=24)
    restored = parse_and_validate_draft(
        serialize_draft(draft),
        now_ms=NOW_MS + 1,
    )
    assert restored is not None
    assert set(restored["responses"]) == set(QUESTION_IDS)
    assert len(restored["responses"]) == 24
    assert set(restored) == {
        "schema_version",
        "instrument_version",
        "response_uuid",
        "current_question",
        "responses",
        "age",
        "district",
        "elapsed_active_seconds",
        "saved_at_ms",
        "expires_at_ms",
    }


@pytest.mark.parametrize("value", [0, 6, True, "3", None])
def test_draft_rejects_answers_outside_integer_likert_range(value):
    draft = valid_draft()
    draft["responses"]["q01"] = value
    assert validate_draft(draft, now_ms=NOW_MS + 1) is None


def test_draft_rejects_unknown_question_ids():
    draft = valid_draft()
    draft["responses"]["q99"] = 3
    assert validate_draft(draft, now_ms=NOW_MS + 1) is None


def test_draft_rejects_previous_instrument_version():
    draft = valid_draft()
    draft["instrument_version"] = "beta-anterior"
    assert validate_draft(draft, now_ms=NOW_MS + 1) is None


def test_draft_rejects_expired_value_without_waiting():
    draft = valid_draft()
    assert validate_draft(draft, now_ms=draft["expires_at_ms"]) is None


@pytest.mark.parametrize("invalid_uuid", ["", "no-es-uuid", str(uuid.uuid1())])
def test_draft_rejects_invalid_or_non_v4_uuid(invalid_uuid):
    draft = valid_draft()
    draft["response_uuid"] = invalid_uuid
    assert validate_draft(draft, now_ms=NOW_MS + 1) is None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("age", "edad inventada"),
        ("district", "distrito inventado"),
    ],
)
def test_draft_rejects_unknown_demographic_values(field, value):
    draft = valid_draft()
    draft[field] = value
    assert validate_draft(draft, now_ms=NOW_MS + 1) is None


def test_valid_draft_preserves_position_uuid_answers_and_elapsed_time():
    draft = valid_draft()
    restored = validate_draft(draft, now_ms=NOW_MS + 1)
    assert restored["current_question"] == 12
    assert restored["response_uuid"] == draft["response_uuid"]
    assert restored["responses"] == draft["responses"]
    assert restored["elapsed_active_seconds"] == 74.2


def test_demographic_draft_restores_official_district_object():
    state = draft_state(response_count=24, step=24)
    state["demographic_step"] = 2
    state["age_range"] = AGE_RANGES[1]
    state["dem_district"] = ALL_RESIDENCE_OPTIONS[0]
    draft = build_draft(
        state,
        elapsed_active_seconds=120,
        now_ms=NOW_MS,
    )
    restored = validate_draft(draft, now_ms=NOW_MS + 1)
    assert restored["current_question"] == 26
    assert district_option_for_draft(restored) == ALL_RESIDENCE_OPTIONS[0]


@pytest.mark.parametrize(
    "elapsed",
    [-1, DRAFT_TTL_SECONDS + 0.1, float("inf"), "74.2", True],
)
def test_draft_rejects_invalid_active_time(elapsed):
    draft = valid_draft()
    draft["elapsed_active_seconds"] = elapsed
    assert validate_draft(draft, now_ms=NOW_MS + 1) is None


def test_draft_ttl_is_exactly_30_minutes_from_valid_activity():
    draft = valid_draft()
    assert DRAFT_TTL_SECONDS == 30 * 60
    assert draft["expires_at_ms"] - draft["saved_at_ms"] == 30 * 60 * 1000


def test_draft_contains_no_email_result_profile_or_coordinates():
    serialized = serialize_draft(valid_draft())
    forbidden = (
        "email",
        "profile",
        "political_x",
        "political_y",
        "coordinates",
        "interpretation",
        "patreon",
    )
    assert all(term not in serialized.casefold() for term in forbidden)


def test_component_uses_one_fixed_key_and_no_network_or_console():
    assert DRAFT_STORAGE_KEY == "brujula_democratica_draft"
    assert COMPONENT_JS.count('"brujula_democratica_draft"') == 1
    assert "localStorage.getItem(STORAGE_KEY)" in COMPONENT_JS
    assert "localStorage.setItem(STORAGE_KEY" in COMPONENT_JS
    assert "localStorage.removeItem(STORAGE_KEY)" in COMPONENT_JS
    assert "fetch(" not in COMPONENT_JS
    assert "XMLHttpRequest" not in COMPONENT_JS
    assert "console." not in COMPONENT_JS


def test_component_does_not_emit_state_after_save_or_clear():
    save_block = COMPONENT_JS.split('operation === "save"', 1)[1].split(
        'operation === "clear"',
        1,
    )[0]
    clear_block = COMPONENT_JS.split('operation === "clear"', 1)[1]
    assert "setStateValue" not in save_block
    assert "setStateValue" not in clear_block


def test_draft_modules_make_no_google_sheets_calls_or_imports():
    source = Path("drafts.py").read_text(encoding="utf-8")
    component_source = Path("components/draft_storage/__init__.py").read_text(
        encoding="utf-8"
    )
    for forbidden in ("google_sheets", "gspread", "save_anonymous_response"):
        assert forbidden not in source
        assert forbidden not in component_source


def test_questions_and_scoring_are_unchanged():
    assert len(QUESTIONS) == 24
    assert tuple(question["id"] for question in QUESTIONS) == QUESTION_IDS
    assert calculate_scores({question_id: 3 for question_id in QUESTION_IDS}) == {
        "x": 0.0,
        "y": 0.0,
        "seguridad": 0.0,
        "familia": 0.0,
        "modernidad": 0.0,
        "partidismo": 0.0,
    }


def test_invalid_json_or_unexpected_keys_are_rejected_completely():
    assert parse_and_validate_draft("{", now_ms=NOW_MS) is None
    draft = valid_draft()
    draft["unexpected"] = "no permitido"
    assert (
        parse_and_validate_draft(
            json.dumps(draft),
            now_ms=NOW_MS + 1,
        )
        is None
    )


def test_starting_again_generates_a_different_uuid():
    old_uuid = valid_draft()["response_uuid"]
    state = {
        "response_uuid": old_uuid,
        "submission_status": "idle",
        "submission_message": "",
        "submitted_at_utc": None,
    }
    new_uuid = reset_submission(state)
    assert new_uuid != old_uuid


def test_autosave_and_recovery_code_do_not_call_google_sheets():
    source = Path("app.py").read_text(encoding="utf-8")
    autosave = source[
        source.index("def mark_draft_activity():"):
        source.index("def check_for_browser_draft():")
    ]
    recovery = source[
        source.index("def restore_browser_draft():"):
        source.index("def clear_draft_for_outcome():")
    ]
    forbidden = ("save_anonymous_response", "save_subscriber_email", "_worksheet")
    assert all(name not in autosave for name in forbidden)
    assert all(name not in recovery for name in forbidden)


def test_app_clears_draft_on_restart_rejection_and_results():
    source = Path("app.py").read_text(encoding="utf-8")
    reset_source = source[
        source.index("def reset_questionnaire():"):
        source.index("def start_own_questionnaire():")
    ]
    invalid_source = source[
        source.index("def render_invalid_completion():"):
        source.index("def shared_result_from_query():")
    ]
    result_source = source[
        source.index("def render_results():"):
        source.index("def render_invalid_completion():")
    ]
    assert "queue_draft_clear()" in reset_source
    assert "clear_draft_for_outcome()" in invalid_source
    assert "clear_draft_for_outcome()" in result_source
