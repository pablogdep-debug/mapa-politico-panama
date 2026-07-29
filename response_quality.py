"""Control metodológico del tiempo mínimo de una participación."""

from __future__ import annotations

from collections.abc import MutableMapping
import time


MINIMUM_COMPLETION_SECONDS = 30
MAXIMUM_RESTORED_ACTIVE_SECONDS = 30 * 60
INVALID_COMPLETION_MESSAGE = (
    "No fue posible completar el cuestionario.\n\n"
    "Este instrumento requiere un tiempo mínimo de respuesta para garantizar "
    "la calidad de los resultados. Si deseas participar, vuelve a completar "
    "el cuestionario leyendo cada pregunta con atención."
)


def start_questionnaire_timer(state: MutableMapping):
    """Inicia el reloj una sola vez, cuando se muestra q01."""
    state.setdefault("questionnaire_elapsed_active_seconds", 0.0)
    if state.get("questionnaire_started_at") is None:
        state["questionnaire_started_at"] = time.monotonic()
    return state["questionnaire_started_at"]


def active_elapsed_seconds(state: MutableMapping):
    """Suma el tramo activo actual al tiempo recuperado de forma defensiva."""
    accumulated = state.get("questionnaire_elapsed_active_seconds", 0.0)
    if (
        isinstance(accumulated, bool)
        or not isinstance(accumulated, (int, float))
        or accumulated < 0
    ):
        accumulated = 0.0
    accumulated = min(float(accumulated), MAXIMUM_RESTORED_ACTIVE_SECONDS)
    started_at = state.get("questionnaire_started_at")
    if started_at is None:
        return accumulated
    current_segment = max(0.0, time.monotonic() - started_at)
    return min(
        accumulated + current_segment,
        MAXIMUM_RESTORED_ACTIVE_SECONDS,
    )


def restore_questionnaire_timer(state: MutableMapping, elapsed_active_seconds):
    """Inicia un tramo nuevo sin contar el tiempo que la app estuvo suspendida."""
    if (
        isinstance(elapsed_active_seconds, bool)
        or not isinstance(elapsed_active_seconds, (int, float))
        or elapsed_active_seconds < 0
    ):
        elapsed_active_seconds = 0.0
    state["questionnaire_elapsed_active_seconds"] = min(
        float(elapsed_active_seconds),
        MAXIMUM_RESTORED_ACTIVE_SECONDS,
    )
    state["questionnaire_started_at"] = time.monotonic()


def validate_completion_time(state: MutableMapping):
    """Congela la decisión de calidad antes de calcular o guardar resultados."""
    if state.get("invalid_completion"):
        return False
    if state.get("completion_time_validated"):
        return True

    started_at = state.get("questionnaire_started_at")
    state["completion_time_validated"] = True
    if started_at is None:
        state["invalid_completion"] = True
        return False

    elapsed_seconds = active_elapsed_seconds(state)
    if elapsed_seconds < MINIMUM_COMPLETION_SECONDS:
        state["invalid_completion"] = True
        return False
    return True


def can_persist_response(state: MutableMapping):
    """Impide guardar si la validación no ocurrió o quedó rechazada."""
    return bool(
        state.get("completion_time_validated")
        and not state.get("invalid_completion")
    )


def reset_response_quality(state: MutableMapping):
    """Limpia el reloj y el rechazo para una participación completamente nueva."""
    state["questionnaire_started_at"] = None
    state["questionnaire_elapsed_active_seconds"] = 0.0
    state["completion_time_validated"] = False
    state["invalid_completion"] = False
