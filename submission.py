"""Identidad y estados de guardado de una participación anónima."""

from __future__ import annotations

from collections.abc import MutableMapping
import uuid


SUBMISSION_IDLE = "idle"
SUBMISSION_SUBMITTING = "submitting"
SUBMISSION_SUCCESS = "success"
SUBMISSION_ERROR = "error"
SUBMISSION_STATUSES = frozenset(
    {
        SUBMISSION_IDLE,
        SUBMISSION_SUBMITTING,
        SUBMISSION_SUCCESS,
        SUBMISSION_ERROR,
    }
)


def generate_response_uuid():
    """Genera un identificador aleatorio sin incorporar datos personales."""
    return str(uuid.uuid4())


def is_valid_response_uuid(value):
    """Comprueba que el identificador sea un UUID versión 4."""
    try:
        parsed = uuid.UUID(str(value))
    except (ValueError, TypeError, AttributeError):
        return False
    return parsed.version == 4 and str(parsed) == str(value).lower()


def ensure_response_uuid(state: MutableMapping):
    """Conserva el UUID existente durante todos los reruns de la participación."""
    current = state.get("response_uuid")
    if not is_valid_response_uuid(current):
        current = generate_response_uuid()
        state["response_uuid"] = current
    return current


def reset_submission(state: MutableMapping):
    """Prepara una identidad nueva únicamente para una nueva participación."""
    state["response_uuid"] = generate_response_uuid()
    state["submission_status"] = SUBMISSION_IDLE
    state["submission_message"] = ""
    state["submitted_at_utc"] = None
    return state["response_uuid"]


def apply_submission_result(state: MutableMapping, result):
    """Traduce el resultado del almacenamiento a un estado estable de interfaz."""
    state["submission_message"] = result.message
    state["submission_status"] = (
        SUBMISSION_SUCCESS if result.success else SUBMISSION_ERROR
    )


def submission_button_disabled(status):
    """Desactiva cualquier control de envío durante o después del éxito."""
    return status in {SUBMISSION_SUBMITTING, SUBMISSION_SUCCESS}


def can_start_submission(status, *, allow_retry=False):
    """Impide escrituras repetidas y permite reintentar solo después de un error."""
    return status == SUBMISSION_IDLE or (
        allow_retry and status == SUBMISSION_ERROR
    )
