"""Pruebas sin esperas reales para el criterio mínimo de calidad."""

from pathlib import Path
from unittest.mock import Mock, patch

from response_quality import (
    INVALID_COMPLETION_MESSAGE,
    MINIMUM_COMPLETION_SECONDS,
    can_persist_response,
    reset_response_quality,
    start_questionnaire_timer,
    validate_completion_time,
)


APP_SOURCE = Path("app.py").read_text(encoding="utf-8")


def fresh_state():
    return {
        "questionnaire_started_at": None,
        "completion_time_validated": False,
        "invalid_completion": False,
    }


def test_cover_does_not_start_timer_and_q01_starts_it_once():
    state = fresh_state()
    assert state["questionnaire_started_at"] is None
    with patch("response_quality.time.monotonic", side_effect=(100.0, 200.0)) as clock:
        assert start_questionnaire_timer(state) == 100.0
        assert start_questionnaire_timer(state) == 100.0
    clock.assert_called_once()


def test_reruns_forward_and_back_preserve_start_time():
    state = fresh_state()
    with patch("response_quality.time.monotonic", return_value=100.0):
        started_at = start_questionnaire_timer(state)
    for question_index in (0, 1, 10, 23, 22, 4, 0):
        state["current_question"] = question_index
        with patch("response_quality.time.monotonic") as clock:
            assert start_questionnaire_timer(state) == started_at
        clock.assert_not_called()


def test_29_point_9_seconds_is_permanently_invalid():
    state = fresh_state()
    state["questionnaire_started_at"] = 100.0
    with patch("response_quality.time.monotonic", return_value=129.9):
        assert not validate_completion_time(state)
    assert state["completion_time_validated"]
    assert state["invalid_completion"]
    assert not can_persist_response(state)

    with patch("response_quality.time.monotonic", return_value=1000.0) as clock:
        assert not validate_completion_time(state)
    clock.assert_not_called()
    assert state["invalid_completion"]


def test_exactly_30_seconds_is_valid():
    state = fresh_state()
    state["questionnaire_started_at"] = 100.0
    with patch(
        "response_quality.time.monotonic",
        return_value=100.0 + MINIMUM_COMPLETION_SECONDS,
    ):
        assert validate_completion_time(state)
    assert can_persist_response(state)
    assert not state["invalid_completion"]


def test_more_than_30_seconds_is_valid():
    state = fresh_state()
    state["questionnaire_started_at"] = 100.0
    with patch("response_quality.time.monotonic", return_value=145.0):
        assert validate_completion_time(state)
    assert can_persist_response(state)


def test_invalid_flow_executes_no_scoring_payload_or_storage_callback():
    state = fresh_state()
    state["questionnaire_started_at"] = 100.0
    scoring = Mock()
    payload = Mock()
    google_sheets = Mock()
    with patch("response_quality.time.monotonic", return_value=129.9):
        if validate_completion_time(state):
            scoring()
            payload()
            google_sheets()
    scoring.assert_not_called()
    payload.assert_not_called()
    google_sheets.assert_not_called()


def test_reset_clears_rejection_and_new_q01_gets_new_start():
    state = {
        "questionnaire_started_at": 100.0,
        "completion_time_validated": True,
        "invalid_completion": True,
    }
    reset_response_quality(state)
    assert state == fresh_state()
    with patch("response_quality.time.monotonic", return_value=500.0):
        assert start_questionnaire_timer(state) == 500.0
    assert state["questionnaire_started_at"] != 100.0


def test_app_guards_before_scoring_payload_and_storage():
    validation_position = APP_SOURCE.index(
        "elif not validate_completion_time(st.session_state):"
    )
    analysis_position = APP_SOURCE.index(
        "elif not st.session_state.analysis_complete:"
    )
    assert validation_position < analysis_position

    render_results_start = APP_SOURCE.index("def render_results():")
    calculate_position = APP_SOURCE.index(
        "scores = calculate_scores(numeric_answers)",
        render_results_start,
    )
    render_results_guard = APP_SOURCE.index(
        "if not can_persist_response(st.session_state):",
        render_results_start,
    )
    assert render_results_guard < calculate_position

    save_start = APP_SOURCE.index("def save_current_response(")
    build_payload_position = APP_SOURCE.index(
        "save_anonymous_response(build_anonymous_response_record(scores))",
        save_start,
    )
    save_guard = APP_SOURCE.index(
        "if not can_persist_response(st.session_state):",
        save_start,
    )
    assert save_guard < build_payload_position


def test_rejection_message_is_exact_and_hides_threshold():
    expected = (
        "No fue posible completar el cuestionario.\n\n"
        "Este instrumento requiere un tiempo mínimo de respuesta para garantizar "
        "la calidad de los resultados. Si deseas participar, vuelve a completar "
        "el cuestionario leyendo cada pregunta con atención."
    )
    assert INVALID_COMPLETION_MESSAGE == expected
    render_start = APP_SOURCE.index("def render_invalid_completion():")
    render_end = APP_SOURCE.index("def shared_result_from_query():", render_start)
    visible_rejection_source = APP_SOURCE[render_start:render_end]
    assert "30 segundos" not in visible_rejection_source
    assert "Patreon" not in visible_rejection_source
    assert "render_subscription" not in visible_rejection_source
    assert "render_share_section" not in visible_rejection_source
