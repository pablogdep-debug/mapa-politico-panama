"""Control metodológico del tiempo mínimo de una participación."""

from __future__ import annotations

from collections.abc import MutableMapping
import time


MINIMUM_COMPLETION_SECONDS = 30
INVALID_COMPLETION_MESSAGE = (
    "No fue posible completar el cuestionario.\n\n"
    "Este instrumento requiere un tiempo mínimo de respuesta para garantizar "
    "la calidad de los resultados. Si deseas participar, vuelve a completar "
    "el cuestionario leyendo cada pregunta con atención."
)


def start_questionnaire_timer(state: MutableMapping):
    """Inicia el reloj una sola vez, cuando se muestra q01."""
    if state.get("questionnaire_started_at") is None:
        state["questionnaire_started_at"] = time.monotonic()
    return state["questionnaire_started_at"]


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

    elapsed_seconds = time.monotonic() - started_at
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
    state["completion_time_validated"] = False
    state["invalid_completion"] = False
