"""Pruebas del UUID y los estados idempotentes de una participación."""

import uuid

import pytest

from storage.google_sheets import SaveResult
from submission import (
    SUBMISSION_ERROR,
    SUBMISSION_IDLE,
    SUBMISSION_SUBMITTING,
    SUBMISSION_SUCCESS,
    SUBMISSION_STATUSES,
    apply_submission_result,
    can_start_submission,
    ensure_response_uuid,
    generate_response_uuid,
    reset_submission,
    submission_button_disabled,
)


def test_generated_ids_are_distinct_uuid_version_four():
    first = generate_response_uuid()
    second = generate_response_uuid()
    assert first != second
    assert uuid.UUID(first).version == 4
    assert uuid.UUID(second).version == 4


def test_submission_status_contract_is_exact():
    assert SUBMISSION_STATUSES == {
        SUBMISSION_IDLE,
        SUBMISSION_SUBMITTING,
        SUBMISSION_SUCCESS,
        SUBMISSION_ERROR,
    }


def test_reruns_and_questionnaire_steps_preserve_the_same_uuid():
    state = {}
    response_uuid = ensure_response_uuid(state)
    for step in range(1, 25):
        state["current_question"] = step - 1
        assert ensure_response_uuid(state) == response_uuid
    state["age_range"] = "25 a 34 años"
    assert ensure_response_uuid(state) == response_uuid
    state["residence_district"] = "Panamá"
    assert ensure_response_uuid(state) == response_uuid
    state["show_results"] = True
    assert ensure_response_uuid(state) == response_uuid


def test_failed_attempt_and_retry_keep_the_same_uuid():
    state = {
        "response_uuid": generate_response_uuid(),
        "submission_status": SUBMISSION_SUBMITTING,
    }
    response_uuid = state["response_uuid"]
    apply_submission_result(state, SaveResult(False, message="falló"))
    assert state["submission_status"] == SUBMISSION_ERROR
    assert state["response_uuid"] == response_uuid
    assert can_start_submission(state["submission_status"], allow_retry=True)
    state["submission_status"] = SUBMISSION_SUBMITTING
    assert state["response_uuid"] == response_uuid


@pytest.mark.parametrize("already_exists", [False, True])
def test_saved_and_existing_results_finish_in_success(already_exists):
    state = {"submission_status": SUBMISSION_SUBMITTING}
    apply_submission_result(
        state,
        SaveResult(True, already_exists=already_exists, message="listo"),
    )
    assert state == {
        "submission_status": SUBMISSION_SUCCESS,
        "submission_message": "listo",
    }


def test_new_participation_replaces_uuid_and_resets_submission():
    state = {
        "response_uuid": generate_response_uuid(),
        "submission_status": SUBMISSION_SUCCESS,
        "submission_message": "guardada",
        "submitted_at_utc": "2026-07-27T12:00:00+00:00",
    }
    previous = state["response_uuid"]
    current = reset_submission(state)
    assert current != previous
    assert uuid.UUID(current).version == 4
    assert state["submission_status"] == SUBMISSION_IDLE
    assert state["submission_message"] == ""
    assert state["submitted_at_utc"] is None


@pytest.mark.parametrize(
    ("status", "disabled"),
    [
        (SUBMISSION_IDLE, False),
        (SUBMISSION_SUBMITTING, True),
        (SUBMISSION_SUCCESS, True),
        (SUBMISSION_ERROR, False),
    ],
)
def test_submission_button_state(status, disabled):
    assert submission_button_disabled(status) is disabled


def test_only_idle_or_explicit_error_retry_can_start_submission():
    assert can_start_submission(SUBMISSION_IDLE)
    assert not can_start_submission(SUBMISSION_SUBMITTING)
    assert not can_start_submission(SUBMISSION_SUCCESS)
    assert not can_start_submission(SUBMISSION_ERROR)
    assert can_start_submission(SUBMISSION_ERROR, allow_retry=True)


def test_uuid_contains_no_user_data():
    response_uuid = generate_response_uuid()
    for personal_value in (
        "persona@ejemplo.com",
        "25 a 34 años",
        "Panamá",
        "Centro pragmático",
    ):
        assert personal_value not in response_uuid
