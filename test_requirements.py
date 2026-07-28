"""Valida que las dependencias directas estén fijadas y sean reproducibles."""

from pathlib import Path
import re


EXACT_REQUIREMENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*==[A-Za-z0-9][A-Za-z0-9._+-]*$")
EXPECTED_DIRECT_DEPENDENCIES = {
    "google-auth",
    "gspread",
    "matplotlib",
    "numpy",
    "pytest",
    "streamlit",
}
STANDARD_LIBRARY_NAMES = {
    "base64",
    "dataclasses",
    "datetime",
    "html",
    "json",
    "logging",
    "math",
    "os",
    "pathlib",
    "re",
    "textwrap",
    "threading",
    "time",
    "typing",
    "unicodedata",
    "urllib",
    "uuid",
}


def active_requirements():
    path = Path("requirements.txt")
    assert path.exists()
    return tuple(
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    )


def test_every_active_requirement_uses_an_exact_version():
    requirements = active_requirements()
    assert requirements
    assert all(EXACT_REQUIREMENT.fullmatch(line) for line in requirements)


def test_direct_dependencies_are_present_once():
    names = [line.split("==", 1)[0].lower() for line in active_requirements()]
    assert len(names) == len(set(names))
    assert set(names) == EXPECTED_DIRECT_DEPENDENCIES


def test_standard_library_modules_are_not_requirements():
    names = {line.split("==", 1)[0].lower() for line in active_requirements()}
    assert names.isdisjoint(STANDARD_LIBRARY_NAMES)
