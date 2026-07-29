"""Regresiones para entregar el resultado antes del almacenamiento externo."""

import ast
from pathlib import Path


APP_SOURCE = Path("app.py").read_text(encoding="utf-8")


def function_source(name):
    tree = ast.parse(APP_SOURCE)
    lines = APP_SOURCE.splitlines()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return "\n".join(lines[node.lineno - 1 : node.end_lineno])
    raise AssertionError(f"No se encontró la función {name}.")


def test_result_is_rendered_before_storage_and_status():
    source = function_source("render_results")
    report_position = source.index("render_result_report(scores)")
    save_position = source.index("save_current_response(scores)")
    status_position = source.index("render_response_save_status(scores)")
    assert report_position < save_position < status_position


def test_storage_error_explicitly_says_result_is_available():
    source = function_source("render_response_save_status")
    assert "Tu resultado ya está disponible." in source
    assert "Intentar registrar nuevamente" in source


def test_heavy_plotting_imports_are_not_module_level():
    tree = ast.parse(APP_SOURCE)
    top_level_imports = [
        node
        for node in tree.body
        if isinstance(node, (ast.Import, ast.ImportFrom))
    ]
    assert all(
        not (
            isinstance(node, ast.Import)
            and any(alias.name == "matplotlib.pyplot" for alias in node.names)
        )
        for node in top_level_imports
    )
    assert all(
        not (
            isinstance(node, ast.ImportFrom)
            and node.module == "plotting"
        )
        for node in top_level_imports
    )

    planes = function_source("render_result_planes")
    assert "import matplotlib.pyplot as plt" in planes
    assert "from plotting import create_map, create_social_map" in planes


def test_result_plots_use_current_streamlit_width_api():
    source = function_source("render_result_planes")
    assert 'st.pyplot(figure, width="stretch")' in source
    assert 'st.pyplot(social_figure, width="stretch")' in source
    assert "use_container_width" not in source
