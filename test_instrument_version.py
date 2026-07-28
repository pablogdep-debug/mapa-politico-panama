"""Pruebas de la fuente única de versión del instrumento."""

from pathlib import Path
from unittest.mock import patch

import instrument_version


APP_SOURCE = Path("app.py").read_text(encoding="utf-8")
STORAGE_SOURCE = Path("storage/google_sheets.py").read_text(encoding="utf-8")


def test_instrument_version_has_one_source_of_truth():
    assert instrument_version.INSTRUMENT_VERSION == "beta-1.0.5"
    assert "INSTRUMENT_VERSION =" not in APP_SOURCE
    assert "INSTRUMENT_VERSION =" not in STORAGE_SOURCE


def test_display_text_is_exact_and_comes_from_the_constant():
    assert (
        instrument_version.instrument_version_display_text()
        == "Brújula Democrática · Versión beta 1.0.5"
    )
    assert "instrument_version.instrument_version_display_text()" in APP_SOURCE
    assert "beta-1.0.5" not in APP_SOURCE


def test_payload_metadata_uses_the_same_constant():
    assert instrument_version.instrument_metadata() == {
        "instrument_version": "beta-1.0.5"
    }
    assert "**instrument_version.instrument_metadata()" in APP_SOURCE


def test_changing_one_constant_updates_display_and_payload_together():
    with patch.object(instrument_version, "INSTRUMENT_VERSION", "beta-1.0.6"):
        assert (
            instrument_version.instrument_version_display_text()
            == "Brújula Democrática · Versión beta 1.0.6"
        )
        assert instrument_version.instrument_metadata() == {
            "instrument_version": "beta-1.0.6"
        }


def test_storage_contract_uses_the_constant_without_linking_subscribers():
    assert (
        'record["instrument_version"] != instrument_version.INSTRUMENT_VERSION'
        in STORAGE_SOURCE
    )
    assert "instrument_version" not in (
        "email",
        "consent_date",
        "source",
        "status",
    )
