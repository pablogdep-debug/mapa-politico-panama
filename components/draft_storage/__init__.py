"""Puente mínimo entre Streamlit y el borrador local del navegador."""

from pathlib import Path

import streamlit as st


STORAGE_KEY = "brujula_democratica_draft"
PENDING_DRAFT = "__brujula_draft_pending__"
_JS = Path(__file__).with_name("index.js").read_text(encoding="utf-8")
_COMPONENT = st.components.v2.component(
    "brujula_draft_storage",
    js=_JS,
)


def _noop():
    """Callback requerido para declarar el estado devuelto por Components v2."""


def read_draft():
    """Lee la única clave autorizada; el valor permanece como texto JSON."""
    result = _COMPONENT(
        key="draft_storage_reader",
        data={"operation": "read"},
        default={"draft": PENDING_DRAFT},
        height=0,
        width="content",
        on_draft_change=_noop,
    )
    return result.draft


def save_draft(serialized_draft):
    """Escribe silenciosamente solo cuando el contenido realmente cambió."""
    _COMPONENT(
        key="draft_storage_writer",
        data={"operation": "save", "payload": serialized_draft},
        height=0,
        width="content",
    )


def idle_draft_storage():
    """Mantiene estable la posición del componente entre todos los reruns."""
    _COMPONENT(
        key="draft_storage_writer",
        data={"operation": "idle"},
        height=0,
        width="content",
    )


def clear_draft():
    """Elimina el borrador sin devolver estado ni provocar un nuevo rerun."""
    _COMPONENT(
        key="draft_storage_writer",
        data={"operation": "clear"},
        height=0,
        width="content",
    )
