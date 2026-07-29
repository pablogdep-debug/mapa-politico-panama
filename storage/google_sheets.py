"""Almacenamiento centralizado y seguro en Google Sheets.

Este módulo nunca calcula resultados políticos. Solo valida y guarda datos
que la aplicación ya produjo.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import logging
import re
import threading
import time
import uuid
import weakref

import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

from demographics import ALL_RESIDENCE_OPTIONS, is_valid_age_range
import instrument_version


LOGGER = logging.getLogger(__name__)
SCOPES = ("https://www.googleapis.com/auth/spreadsheets",)
QUESTION_IDS = tuple(f"q{number:02d}" for number in range(1, 25))

RESPONSE_HEADERS = (
    "response_uuid",
    "submitted_at_utc",
    "app_version",
    "age_range",
    "residence_region",
    "residence_district",
    *QUESTION_IDS,
    "political_x",
    "political_y",
    "political_classification",
    "political_profile",
    "political_position_type",
    "political_intensity",
    "social_x",
    "social_y",
    "social_classification",
    "social_profile",
    "social_position_type",
    "social_intensity",
    "security_score",
    "partisanship_score",
    "instrument_version",
)
SUBSCRIBER_HEADERS = ("email", "consent_date", "source", "status")

_CONFIG_KEYS = (
    "responses_spreadsheet_id",
    "responses_worksheet",
    "subscribers_spreadsheet_id",
    "subscribers_worksheet",
)
_EMAIL_PATTERN = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
_RESPONSE_APPEND_LOCK = threading.Lock()
_SUBSCRIBER_APPEND_LOCK = threading.Lock()
_RETRIABLE_API_CODES = frozenset({408, 429, 500, 502, 503, 504})
_RETRY_DELAYS = (1.0, 2.0, 4.0, 8.0)
_RESPONSE_UUID_CACHE = weakref.WeakKeyDictionary()
_SUBSCRIBER_EMAIL_CACHE = weakref.WeakKeyDictionary()


@dataclass(frozen=True)
class SaveResult:
    """Resultado estable que la interfaz puede mostrar sin conocer gspread."""

    success: bool
    already_exists: bool = False
    message: str = ""

    @property
    def status(self):
        if not self.success:
            return "failed"
        return "already_exists" if self.already_exists else "saved"


class StorageConfigurationError(RuntimeError):
    """La configuración privada está ausente o incompleta."""


class HeaderMismatchError(RuntimeError):
    """La pestaña existe, pero sus columnas no coinciden con el contrato."""


class InvalidRecordError(ValueError):
    """Los datos no cumplen el contrato de almacenamiento anónimo."""


def sanitize_cell(value):
    """Evita que una cadena sea interpretada como fórmula por Google Sheets."""
    if isinstance(value, str) and value.startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def normalize_email(email):
    """Normaliza el correo sin añadir información sobre la participación."""
    return email.strip().lower() if isinstance(email, str) else ""


def _secrets_section(name):
    try:
        section = st.secrets[name]
        return dict(section)
    except (KeyError, FileNotFoundError):
        return None


def is_google_sheets_configured():
    """Indica si están presentes todos los secretos, sin exponerlos."""
    account = _secrets_section("google_service_account")
    sheets = _secrets_section("brujula_sheets")
    required_account = {
        "type",
        "project_id",
        "private_key_id",
        "private_key",
        "client_email",
        "client_id",
        "auth_uri",
        "token_uri",
    }
    return bool(
        account
        and required_account.issubset(account)
        and sheets
        and all(sheets.get(key) for key in _CONFIG_KEYS)
    )


@st.cache_resource(show_spinner=False)
def _google_client():
    """Crea una sola conexión autenticada por proceso de Streamlit."""
    account = _secrets_section("google_service_account")
    if not account:
        raise StorageConfigurationError("Falta google_service_account.")
    credentials = Credentials.from_service_account_info(
        account,
        scopes=SCOPES,
    )
    return gspread.authorize(credentials)


@st.cache_resource(show_spinner=False)
def _worksheet(kind):
    config = _secrets_section("brujula_sheets")
    if not config or not all(config.get(key) for key in _CONFIG_KEYS):
        raise StorageConfigurationError("Falta la configuración de hojas.")

    if kind == "responses":
        spreadsheet_id = config["responses_spreadsheet_id"]
        worksheet_name = config["responses_worksheet"]
    else:
        spreadsheet_id = config["subscribers_spreadsheet_id"]
        worksheet_name = config["subscribers_worksheet"]

    return _google_client().open_by_key(spreadsheet_id).worksheet(worksheet_name)


def _read_headers_and_first_column(worksheet):
    """Lee una vez el contrato y los identificadores ya registrados."""
    headers = tuple(
        _api_call("read_headers", lambda: worksheet.row_values(1))
    )
    first_column = tuple(
        str(value)
        for value in _api_call(
            "read_first_column",
            lambda: worksheet.col_values(1),
        )
        if value not in (None, "")
    )
    return headers, first_column


def _response_uuid_set(worksheet, *, refresh=False):
    """Carga una vez los UUID; las escrituras normales no releen la hoja."""
    if not refresh and worksheet in _RESPONSE_UUID_CACHE:
        return _RESPONSE_UUID_CACHE[worksheet]

    headers, first_column = _read_headers_and_first_column(worksheet)
    if not headers:
        _api_call(
            "append_response_headers",
            lambda: worksheet.append_row(
                list(RESPONSE_HEADERS),
                value_input_option="RAW",
            ),
        )
    elif headers == RESPONSE_HEADERS:
        pass
    elif headers == RESPONSE_HEADERS[:-1]:
        missing_columns = len(RESPONSE_HEADERS) - worksheet.col_count
        if missing_columns > 0:
            _api_call(
                "expand_response_columns",
                lambda: worksheet.add_cols(missing_columns),
            )
        _api_call(
            "extend_response_headers",
            lambda: worksheet.update_cell(
                1,
                len(RESPONSE_HEADERS),
                "instrument_version",
            ),
        )
    else:
        raise HeaderMismatchError("Los encabezados no coinciden.")

    known_uuids = {
        value
        for value in first_column
        if value and value != "response_uuid"
    }
    _RESPONSE_UUID_CACHE[worksheet] = known_uuids
    return known_uuids


def _subscriber_email_set(worksheet, *, refresh=False):
    """Carga una vez los correos, separados de las respuestas políticas."""
    if not refresh and worksheet in _SUBSCRIBER_EMAIL_CACHE:
        return _SUBSCRIBER_EMAIL_CACHE[worksheet]

    headers, first_column = _read_headers_and_first_column(worksheet)
    if not headers:
        _api_call(
            "append_subscriber_headers",
            lambda: worksheet.append_row(
                list(SUBSCRIBER_HEADERS),
                value_input_option="RAW",
            ),
        )
    elif headers != SUBSCRIBER_HEADERS:
        raise HeaderMismatchError("Los encabezados no coinciden.")

    known_emails = {
        normalize_email(value)
        for value in first_column
        if value and value != "email"
    }
    _SUBSCRIBER_EMAIL_CACHE[worksheet] = known_emails
    return known_emails


def response_uuid_exists(worksheet, response_uuid):
    """Busca el identificador únicamente en su columna contractual."""
    existing_values = worksheet.col_values(1)
    return str(response_uuid) in {
        str(value) for value in existing_values[1:] if value
    }


def _is_temporary_error(error):
    if isinstance(error, gspread.exceptions.APIError):
        return error.code in _RETRIABLE_API_CODES
    return isinstance(error, (ConnectionError, TimeoutError))


def _safe_error_label(error):
    """Resume un error de Google sin registrar datos, IDs ni credenciales."""
    if isinstance(error, gspread.exceptions.APIError):
        status = str(error.error.get("status", "UNKNOWN"))
        return f"APIError code={error.code} status={status}"
    return type(error).__name__


def _api_call(stage, operation):
    """Etiqueta la operación fallida sin registrar contenido ni IDs privados."""
    try:
        return operation()
    except Exception as error:
        LOGGER.error(
            "Google Sheets operation=%s failed (%s).",
            stage,
            _safe_error_label(error),
        )
        raise


def _run_with_retry(operation, kind):
    for attempt in range(len(_RETRY_DELAYS) + 1):
        try:
            return operation()
        except Exception as error:
            if not _is_temporary_error(error) or attempt == len(_RETRY_DELAYS):
                raise
            LOGGER.warning(
                "Fallo temporal en %s/%s (%s).",
                kind,
                operation.__name__,
                _safe_error_label(error),
            )
            time.sleep(_RETRY_DELAYS[attempt])


def _validate_response(record):
    if not isinstance(record, dict):
        raise InvalidRecordError("La respuesta debe ser un diccionario.")
    if set(record) != set(RESPONSE_HEADERS):
        raise InvalidRecordError("La respuesta está incompleta o tiene campos extra.")
    try:
        parsed_uuid = uuid.UUID(str(record["response_uuid"]))
    except (ValueError, TypeError, AttributeError) as error:
        raise InvalidRecordError("El identificador de respuesta no es válido.") from error
    if parsed_uuid.version != 4:
        raise InvalidRecordError("El identificador de respuesta debe ser UUID versión 4.")
    for question_id in QUESTION_IDS:
        value = record[question_id]
        if isinstance(value, bool) or not isinstance(value, int) or value not in range(1, 6):
            raise InvalidRecordError(f"{question_id} debe estar entre 1 y 5.")
    for field in (
        "submitted_at_utc",
        "app_version",
        "instrument_version",
        "age_range",
        "residence_region",
        "residence_district",
        "political_classification",
        "political_position_type",
        "social_classification",
        "social_position_type",
    ):
        if not isinstance(record[field], str) or not record[field].strip():
            raise InvalidRecordError(f"{field} es obligatorio.")
    if record["instrument_version"] != instrument_version.INSTRUMENT_VERSION:
        raise InvalidRecordError("La versión del instrumento no es válida.")
    if not is_valid_age_range(record["age_range"]):
        raise InvalidRecordError("El rango de edad no es válido.")
    valid_residence = any(
        option.region == record["residence_region"]
        and option.district == record["residence_district"]
        for option in ALL_RESIDENCE_OPTIONS
    )
    if not valid_residence:
        raise InvalidRecordError("La residencia no es válida.")
    if record["political_position_type"] not in {"center", "axis", "quadrant"}:
        raise InvalidRecordError("El tipo de posición política no es válido.")
    if record["social_position_type"] not in {"center", "axis", "quadrant"}:
        raise InvalidRecordError("El tipo de posición social no es válido.")
    for field in (
        "political_x",
        "political_y",
        "political_intensity",
        "social_x",
        "social_y",
        "social_intensity",
        "security_score",
        "partisanship_score",
    ):
        value = record[field]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InvalidRecordError(f"{field} debe ser numérico.")
        minimum = 0 if field.endswith("intensity") else -100
        if not minimum <= value <= 100:
            raise InvalidRecordError(f"{field} está fuera de rango.")


def save_anonymous_response(record: dict) -> SaveResult:
    """Guarda una participación anónima, sin correo y sin recalcularla."""
    try:
        _validate_response(record)
        if not is_google_sheets_configured():
            raise StorageConfigurationError("Google Sheets no está configurado.")

        def append_response():
            with _RESPONSE_APPEND_LOCK:
                worksheet = _worksheet("responses")
                response_uuid = str(record["response_uuid"])
                known_uuids = _response_uuid_set(worksheet)
                if response_uuid in known_uuids:
                    return SaveResult(
                        success=True,
                        already_exists=True,
                        message="Tu participación ya había sido registrada.",
                    )
                row = [sanitize_cell(record[header]) for header in RESPONSE_HEADERS]
                try:
                    _api_call(
                        "append_response_row",
                        lambda: worksheet.append_row(
                            row,
                            value_input_option="RAW",
                        ),
                    )
                except Exception as error:
                    if _is_temporary_error(error):
                        refreshed_uuids = _response_uuid_set(
                            worksheet,
                            refresh=True,
                        )
                        if response_uuid in refreshed_uuids:
                            return SaveResult(
                                success=True,
                                already_exists=True,
                                message="Tu participación ya había sido registrada.",
                            )
                    raise
                known_uuids.add(response_uuid)
                return SaveResult(
                    success=True,
                    message="Tu participación fue registrada correctamente.",
                )

        return _run_with_retry(append_response, "responses")
    except (InvalidRecordError, StorageConfigurationError, HeaderMismatchError):
        return SaveResult(
            success=False,
            message=(
                "No pudimos registrar tu participación en este momento. "
                "Puedes intentar nuevamente."
            ),
        )
    except Exception as error:
        LOGGER.error(
            "No se pudo guardar responses (%s).",
            _safe_error_label(error),
        )
        return SaveResult(
            success=False,
            message=(
                "No pudimos registrar tu participación en este momento. "
                "Puedes intentar nuevamente."
            ),
        )


def save_subscriber_email(email: str) -> SaveResult:
    """Guarda únicamente un correo voluntario, separado de las respuestas."""
    normalized = normalize_email(email)
    if len(normalized) > 254 or not _EMAIL_PATTERN.fullmatch(normalized):
        return SaveResult(
            success=False,
            message="No pudimos registrar tu correo en este momento. Intenta nuevamente.",
        )

    try:
        if not is_google_sheets_configured():
            raise StorageConfigurationError("Google Sheets no está configurado.")

        def append_subscriber():
            with _SUBSCRIBER_APPEND_LOCK:
                worksheet = _worksheet("subscribers")
                known_emails = _subscriber_email_set(worksheet)
                if normalized in known_emails:
                    return SaveResult(
                        success=True,
                        already_exists=True,
                        message="Este correo ya estaba registrado para recibir noticias.",
                    )
                record = {
                    "email": normalized,
                    "consent_date": datetime.now(timezone.utc).isoformat(),
                    "source": "brujula_streamlit",
                    "status": "active",
                }
                row = [sanitize_cell(record[header]) for header in SUBSCRIBER_HEADERS]
                try:
                    _api_call(
                        "append_subscriber_row",
                        lambda: worksheet.append_row(
                            row,
                            value_input_option="RAW",
                        ),
                    )
                except Exception as error:
                    if _is_temporary_error(error):
                        refreshed_emails = _subscriber_email_set(
                            worksheet,
                            refresh=True,
                        )
                        if normalized in refreshed_emails:
                            return SaveResult(
                                success=True,
                                already_exists=True,
                                message=(
                                    "Este correo ya estaba registrado para recibir noticias."
                                ),
                            )
                    raise
                known_emails.add(normalized)
                return SaveResult(
                    success=True,
                    message="Tu correo fue registrado correctamente.",
                )

        return _run_with_retry(append_subscriber, "subscribers")
    except (StorageConfigurationError, HeaderMismatchError):
        return SaveResult(
            success=False,
            message="No pudimos registrar tu correo en este momento. Intenta nuevamente.",
        )
    except Exception as error:
        LOGGER.error(
            "No se pudo guardar subscribers (%s).",
            _safe_error_label(error),
        )
        return SaveResult(
            success=False,
            message="No pudimos registrar tu correo en este momento. Intenta nuevamente.",
        )
