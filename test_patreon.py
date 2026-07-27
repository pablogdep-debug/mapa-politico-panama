"""Pruebas de integración estática de la tarjeta de Patreon."""

import ast
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from config import PATREON_URL
from questions import QUESTIONS
from scoring import QUESTION_IDS, calculate_scores


APP_PATH = Path(__file__).with_name("app.py")
APP_SOURCE = APP_PATH.read_text(encoding="utf-8")


def _render_result_report_node():
    tree = ast.parse(APP_SOURCE)
    return next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "render_result_report"
    )


def _called_function_names(nodes):
    names = []
    for node in nodes:
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                names.append(child.func.id)
    return names


def test_patreon_url_is_exact_and_static():
    assert PATREON_URL == "https://www.patreon.com/BrujulaDemocratica"
    parsed = urlparse(PATREON_URL)
    assert parsed.query == ""
    assert parsed.fragment == ""
    assert parse_qs(parsed.query) == {}


def test_patreon_url_contains_no_participant_data():
    forbidden = (
        "email",
        "correo",
        "uuid",
        "edad",
        "age",
        "distrito",
        "district",
        "q01",
        "respuesta",
        "answer",
        "coordinate",
        "coordenada",
        "profile",
        "perfil",
    )
    lowered = PATREON_URL.lower()
    assert all(term not in lowered for term in forbidden)


def test_patreon_card_is_only_in_normal_result_branch():
    function = _render_result_report_node()
    shared_branches = [
        node
        for node in function.body
        if isinstance(node, ast.If)
        and isinstance(node.test, ast.Name)
        and node.test.id == "shared"
    ]
    result_branch = next(
        node
        for node in shared_branches
        if "render_patreon_support" in _called_function_names(node.orelse)
    )
    assert "render_patreon_support" not in _called_function_names(result_branch.body)
    assert _called_function_names(result_branch.orelse).count(
        "render_patreon_support"
    ) == 1
    normal_calls = _called_function_names(result_branch.orelse)
    assert normal_calls.index("render_patreon_support") < normal_calls.index(
        "render_subscription"
    )
    assert normal_calls.index("render_subscription") < normal_calls.index(
        "render_share_section"
    )
    assert normal_calls.index("render_share_section") < normal_calls.index(
        "render_social_outro"
    )


def test_patreon_card_is_not_rendered_in_question_or_demographic_functions():
    tree = ast.parse(APP_SOURCE)
    prohibited = {"render_question", "render_demographics", "render_cover"}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in prohibited:
            assert "render_patreon_support" not in _called_function_names(node.body)


def test_email_form_and_google_sheets_are_not_mixed_with_patreon():
    assert "subscription_form" in APP_SOURCE
    assert "Quiero recibir futuras encuestas" in APP_SOURCE
    storage_source = Path("storage/google_sheets.py").read_text(encoding="utf-8")
    assert "patreon" not in storage_source.lower()
    assert "PATREON_URL" not in storage_source


def test_scoring_and_question_count_remain_stable():
    assert len(QUESTIONS) == 24
    assert tuple(question["id"] for question in QUESTIONS) == QUESTION_IDS
    neutral = {question_id: 3 for question_id in QUESTION_IDS}
    assert calculate_scores(neutral) == {
        "x": 0.0,
        "y": 0.0,
        "seguridad": 0.0,
        "familia": 0.0,
        "modernidad": 0.0,
        "partidismo": 0.0,
    }


def test_no_el_resuelve_visual_test_code_remains():
    assert "dev_test_mode" not in APP_SOURCE
    assert "BRUJULA_DEV_TEST_PROFILE" not in APP_SOURCE
    assert "build_el_resuelve_answers" not in APP_SOURCE
    assert not Path("dev_visual_test.py").exists()
