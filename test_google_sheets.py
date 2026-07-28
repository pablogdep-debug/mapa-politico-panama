"""Pruebas sin red para el contrato privado de Google Sheets."""

from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
import uuid

import pytest

import instrument_version
from questions import QUESTIONS
from scoring import QUESTION_IDS, calculate_scores
from storage.google_sheets import (
    RESPONSE_HEADERS,
    SUBSCRIBER_HEADERS,
    response_uuid_exists,
    sanitize_cell,
    save_anonymous_response,
    save_subscriber_email,
)


class FakeWorksheet:
    def __init__(self, headers=(), first_column=(), fail_after_append_once=False):
        self.headers = list(headers)
        self.first_column = (
            list(first_column)
            if first_column
            else ([self.headers[0]] if self.headers else [])
        )
        self.appended = []
        self.updated_cells = []
        self.fail_after_append_once = fail_after_append_once

    def row_values(self, row):
        assert row == 1
        return list(self.headers)

    def col_values(self, column):
        assert column == 1
        if self.first_column:
            return list(self.first_column)
        return [self.headers[0]] if self.headers else []

    def append_row(self, row, value_input_option):
        assert value_input_option == "RAW"
        self.appended.append(list(row))
        if not self.headers:
            self.headers = list(row)
        elif row:
            self.first_column.append(row[0])
        if self.fail_after_append_once:
            self.fail_after_append_once = False
            raise TimeoutError("confirmación ambigua")

    def update_cell(self, row, column, value):
        self.updated_cells.append((row, column, value))
        if row == 1 and column == len(self.headers) + 1:
            self.headers.append(value)


def response_record():
    answers = {question_id: 3 for question_id in QUESTION_IDS}
    scores = calculate_scores(answers)
    return {
        "response_uuid": str(uuid.uuid4()),
        "submitted_at_utc": "2026-07-27T12:00:00+00:00",
        "app_version": "1.0",
        **instrument_version.instrument_metadata(),
        "age_range": "25 a 34 años",
        "residence_region": "Panamá",
        "residence_district": "Panamá",
        **answers,
        "political_x": scores["x"],
        "political_y": scores["y"],
        "political_classification": "Centro pragmático",
        "political_profile": "",
        "political_position_type": "center",
        "political_intensity": 0.0,
        "social_x": scores["familia"],
        "social_y": scores["modernidad"],
        "social_classification": "Posición social pragmática",
        "social_profile": "",
        "social_position_type": "center",
        "social_intensity": 0.0,
        "security_score": scores["seguridad"],
        "partisanship_score": scores["partidismo"],
    }


def configured_patches(worksheet):
    return (
        patch("storage.google_sheets.is_google_sheets_configured", return_value=True),
        patch("storage.google_sheets._worksheet", return_value=worksheet),
    )


def test_questions_and_known_scoring_remain_unchanged():
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


def test_response_headers_contain_each_question_once_and_no_email():
    assert [header for header in RESPONSE_HEADERS if header.startswith("q")] == list(
        QUESTION_IDS
    )
    assert "email" not in RESPONSE_HEADERS
    assert RESPONSE_HEADERS[-1] == "instrument_version"
    assert RESPONSE_HEADERS.count("instrument_version") == 1


def test_subscriber_headers_contain_no_political_or_demographic_data():
    assert SUBSCRIBER_HEADERS == ("email", "consent_date", "source", "status")
    forbidden = {
        "response_uuid",
        "instrument_version",
        "age_range",
        "residence_district",
        *QUESTION_IDS,
    }
    assert forbidden.isdisjoint(SUBSCRIBER_HEADERS)


def test_response_row_uses_exact_header_order():
    worksheet = FakeWorksheet(RESPONSE_HEADERS)
    record = response_record()
    configured, selected = configured_patches(worksheet)
    with configured, selected:
        result = save_anonymous_response(record)
    assert result.success
    assert worksheet.appended == [[record[header] for header in RESPONSE_HEADERS]]


def test_empty_response_sheet_receives_headers_then_row():
    worksheet = FakeWorksheet()
    configured, selected = configured_patches(worksheet)
    with configured, selected:
        result = save_anonymous_response(response_record())
    assert result.success
    assert worksheet.appended[0] == list(RESPONSE_HEADERS)
    assert len(worksheet.appended) == 2


def test_legacy_response_sheet_only_receives_new_header_at_the_end():
    legacy_headers = RESPONSE_HEADERS[:-1]
    worksheet = FakeWorksheet(legacy_headers)
    record = response_record()
    configured, selected = configured_patches(worksheet)
    with configured, selected:
        result = save_anonymous_response(record)
    assert result.success
    assert worksheet.updated_cells == [
        (1, len(RESPONSE_HEADERS), "instrument_version")
    ]
    assert worksheet.headers == list(RESPONSE_HEADERS)
    assert worksheet.appended == [[record[header] for header in RESPONSE_HEADERS]]


@pytest.mark.parametrize(
    "mutation",
    [
        lambda record: record.pop("q24"),
        lambda record: record.update(q01=0),
        lambda record: record.update(q01=6),
        lambda record: record.update(age_range="desconocido"),
        lambda record: record.update(residence_district="inventado"),
        lambda record: record.update(political_x=101),
        lambda record: record.update(instrument_version="beta-otra"),
        lambda record: record.update(extra_field="no permitido"),
    ],
)
def test_incomplete_or_invalid_response_is_rejected(mutation):
    record = response_record()
    mutation(record)
    worksheet = FakeWorksheet(RESPONSE_HEADERS)
    configured, selected = configured_patches(worksheet)
    with configured, selected:
        result = save_anonymous_response(record)
    assert not result.success
    assert worksheet.appended == []


def test_duplicate_response_uuid_does_not_append():
    record = response_record()
    worksheet = FakeWorksheet(
        RESPONSE_HEADERS,
        ("response_uuid", record["response_uuid"]),
    )
    configured, selected = configured_patches(worksheet)
    with configured, selected:
        result = save_anonymous_response(record)
    assert result.success and result.already_exists
    assert worksheet.appended == []


def test_uuid_lookup_uses_the_contract_column_only():
    response_uuid = str(uuid.uuid4())
    worksheet = FakeWorksheet(
        RESPONSE_HEADERS,
        ("response_uuid", response_uuid),
    )
    assert response_uuid_exists(worksheet, response_uuid)


def test_repeated_save_with_same_uuid_produces_exactly_one_row():
    worksheet = FakeWorksheet(RESPONSE_HEADERS)
    record = response_record()
    configured, selected = configured_patches(worksheet)
    with configured, selected:
        first = save_anonymous_response(record)
        second = save_anonymous_response(record)
    assert first.status == "saved"
    assert second.status == "already_exists"
    assert len(worksheet.appended) == 1


def test_concurrent_calls_with_same_uuid_produce_exactly_one_row():
    worksheet = FakeWorksheet(RESPONSE_HEADERS)
    record = response_record()
    configured, selected = configured_patches(worksheet)
    with configured, selected:
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(
                executor.map(
                    lambda _: save_anonymous_response(record),
                    range(2),
                )
            )
    assert sorted(result.status for result in results) == [
        "already_exists",
        "saved",
    ]
    assert len(worksheet.appended) == 1


def test_retry_after_ambiguous_timeout_detects_existing_uuid():
    worksheet = FakeWorksheet(
        RESPONSE_HEADERS,
        fail_after_append_once=True,
    )
    configured, selected = configured_patches(worksheet)
    with configured, selected, patch("storage.google_sheets.time.sleep"):
        result = save_anonymous_response(response_record())
    assert result.status == "already_exists"
    assert len(worksheet.appended) == 1


def test_email_is_normalized_and_saved_without_other_data():
    worksheet = FakeWorksheet(SUBSCRIBER_HEADERS)
    configured, selected = configured_patches(worksheet)
    with configured, selected:
        result = save_subscriber_email("  Persona@Ejemplo.COM ")
    assert result.success
    assert worksheet.appended[0][0] == "persona@ejemplo.com"
    assert len(worksheet.appended[0]) == len(SUBSCRIBER_HEADERS)


def test_duplicate_normalized_email_does_not_append():
    worksheet = FakeWorksheet(
        SUBSCRIBER_HEADERS,
        ("email", "persona@ejemplo.com"),
    )
    configured, selected = configured_patches(worksheet)
    with configured, selected:
        result = save_subscriber_email(" Persona@Ejemplo.com ")
    assert result.success and result.already_exists
    assert worksheet.appended == []


def test_missing_configuration_fails_safely():
    with patch(
        "storage.google_sheets.is_google_sheets_configured",
        return_value=False,
    ):
        response_result = save_anonymous_response(response_record())
        email_result = save_subscriber_email("persona@ejemplo.com")
    assert not response_result.success
    assert not email_result.success


@pytest.mark.parametrize("prefix", ["=", "+", "-", "@"])
def test_formula_like_strings_are_sanitized(prefix):
    value = prefix + "SUM(A1:A2)"
    assert sanitize_cell(value) == "'" + value


def test_header_mismatch_is_a_controlled_failure():
    worksheet = FakeWorksheet(("wrong", "headers"))
    configured, selected = configured_patches(worksheet)
    with configured, selected:
        result = save_anonymous_response(response_record())
    assert not result.success
    assert worksheet.appended == []


def test_temporary_connection_error_is_retried_then_succeeds():
    worksheet = FakeWorksheet(RESPONSE_HEADERS)
    with (
        patch(
            "storage.google_sheets.is_google_sheets_configured",
            return_value=True,
        ),
        patch(
            "storage.google_sheets._worksheet",
            side_effect=(ConnectionError("temporal"), worksheet),
        ) as selected,
        patch("storage.google_sheets.time.sleep") as pause,
    ):
        result = save_anonymous_response(response_record())
    assert result.success
    assert selected.call_count == 2
    pause.assert_called_once_with(0.5)
