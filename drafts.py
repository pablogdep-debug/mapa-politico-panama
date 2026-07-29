"""Contrato puro y validado para borradores temporales del cuestionario."""

from __future__ import annotations

import json
import math
import time

from demographics import ALL_RESIDENCE_OPTIONS, AGE_RANGES
from instrument_version import INSTRUMENT_VERSION
from questions import QUESTIONS
from submission import is_valid_response_uuid


DRAFT_SCHEMA_VERSION = 1
DRAFT_TTL_SECONDS = 30 * 60
DRAFT_STORAGE_KEY = "brujula_democratica_draft"
QUESTION_IDS = tuple(question["id"] for question in QUESTIONS)
_QUESTION_ID_SET = frozenset(QUESTION_IDS)
_DISTRICT_BY_LABEL = {
    option.label: option
    for option in ALL_RESIDENCE_OPTIONS
}
_DRAFT_KEYS = frozenset(
    {
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
)


def current_step(state):
    """Representa q01–q24 como 1–24 y los dos datos finales como 25–26."""
    demographic_step = state.get("demographic_step", 0)
    if demographic_step == 1:
        return 25
    if demographic_step == 2:
        return 26
    index = state.get("current_question", 0)
    return min(max(int(index), 0), len(QUESTION_IDS) - 1) + 1


def build_draft(
    state,
    *,
    elapsed_active_seconds,
    now_ms=None,
):
    """Crea únicamente el conjunto de datos local permitido."""
    timestamp_ms = int(time.time() * 1000) if now_ms is None else int(now_ms)
    district_option = state.get("dem_district")
    district_label = (
        district_option.label
        if district_option in ALL_RESIDENCE_OPTIONS
        else None
    )
    return {
        "schema_version": DRAFT_SCHEMA_VERSION,
        "instrument_version": INSTRUMENT_VERSION,
        "response_uuid": state.get("response_uuid"),
        "current_question": current_step(state),
        "responses": dict(state.get("answers", {})),
        "age": state.get("age_range"),
        "district": district_label,
        "elapsed_active_seconds": round(float(elapsed_active_seconds), 3),
        "saved_at_ms": timestamp_ms,
        "expires_at_ms": timestamp_ms + DRAFT_TTL_SECONDS * 1000,
    }


def serialize_draft(draft):
    """Produce una representación estable para evitar escrituras repetidas."""
    return json.dumps(
        draft,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def parse_and_validate_draft(serialized_draft, *, now_ms=None):
    """Devuelve un borrador completo o None; nunca restaura parcialmente."""
    if not isinstance(serialized_draft, str) or not serialized_draft:
        return None
    try:
        draft = json.loads(serialized_draft)
    except (TypeError, ValueError, json.JSONDecodeError):
        return None
    return validate_draft(draft, now_ms=now_ms)


def validate_draft(draft, *, now_ms=None):
    """Trata localStorage como entrada no confiable y valida todo en Python."""
    if not isinstance(draft, dict) or frozenset(draft) != _DRAFT_KEYS:
        return None
    if draft["schema_version"] != DRAFT_SCHEMA_VERSION:
        return None
    if draft["instrument_version"] != INSTRUMENT_VERSION:
        return None
    if not is_valid_response_uuid(draft["response_uuid"]):
        return None

    step = draft["current_question"]
    if isinstance(step, bool) or not isinstance(step, int) or not 1 <= step <= 26:
        return None

    responses = draft["responses"]
    if not isinstance(responses, dict) or len(responses) > len(QUESTION_IDS):
        return None
    if not set(responses).issubset(_QUESTION_ID_SET):
        return None
    if any(
        isinstance(value, bool)
        or not isinstance(value, int)
        or value not in range(1, 6)
        for value in responses.values()
    ):
        return None

    age = draft["age"]
    if age is not None and age not in AGE_RANGES:
        return None
    district = draft["district"]
    if district is not None and district not in _DISTRICT_BY_LABEL:
        return None

    elapsed = draft["elapsed_active_seconds"]
    if (
        isinstance(elapsed, bool)
        or not isinstance(elapsed, (int, float))
        or not math.isfinite(elapsed)
        or not 0 <= elapsed <= DRAFT_TTL_SECONDS
    ):
        return None

    saved_at = draft["saved_at_ms"]
    expires_at = draft["expires_at_ms"]
    if (
        isinstance(saved_at, bool)
        or isinstance(expires_at, bool)
        or not isinstance(saved_at, (int, float))
        or not isinstance(expires_at, (int, float))
        or not math.isfinite(saved_at)
        or not math.isfinite(expires_at)
        or saved_at < 0
        or expires_at - saved_at != DRAFT_TTL_SECONDS * 1000
    ):
        return None
    current_ms = int(time.time() * 1000) if now_ms is None else int(now_ms)
    if expires_at <= current_ms:
        return None

    if step >= 25 and set(responses) != _QUESTION_ID_SET:
        return None
    if step == 26 and age not in AGE_RANGES:
        return None

    return {
        **draft,
        "responses": dict(responses),
        "elapsed_active_seconds": float(elapsed),
    }


def district_option_for_draft(draft):
    """Reconstruye exclusivamente una opción territorial oficial existente."""
    return _DISTRICT_BY_LABEL.get(draft.get("district"))
