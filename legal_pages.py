"""Presentación compartida para documentos legales estáticos."""

from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent


def render_legal_page(*, page_title, markdown_filename):
    """Muestra un documento legal sin iniciar ni modificar el cuestionario."""
    st.set_page_config(
        page_title=f"{page_title} · Brújula Democrática",
        page_icon="assets/brujula.png",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    st.markdown(
        """
        <style>
        :root {
            --legal-bg: #e9edf2;
            --legal-panel: #ffffff;
            --legal-text: #102a50;
            --legal-muted: #526174;
            --legal-blue: #0a438f;
            --legal-border: #d8dee8;
        }

        .stApp {
            background:
                radial-gradient(
                    circle at 8% 0%,
                    rgba(10, 67, 143, 0.07),
                    transparent 35rem
                ),
                var(--legal-bg);
            color: var(--legal-text);
        }

        .block-container {
            width: min(100%, 900px);
            padding-top: clamp(1.5rem, 5vw, 3.5rem);
            padding-bottom: 4rem;
        }

        [data-testid="stSidebar"],
        [data-testid="stExpandSidebarButton"] {
            display: none !important;
        }

        [class*="st-key-legal_document"] {
            padding: clamp(1.35rem, 4vw, 2.5rem);
            border: 1px solid var(--legal-border);
            border-radius: 22px;
            background: var(--legal-panel);
            box-shadow: 0 8px 28px rgba(16, 42, 80, 0.08);
        }

        [class*="st-key-legal_document"] h1 {
            margin-top: 1.25rem;
            color: var(--legal-text);
            font-size: clamp(1.65rem, 4vw, 2.35rem);
            line-height: 1.15;
            letter-spacing: -0.025em;
        }

        [class*="st-key-legal_document"] h2 {
            margin-top: 2rem;
            color: var(--legal-text);
            font-size: clamp(1.1rem, 2.5vw, 1.35rem);
            line-height: 1.3;
        }

        [class*="st-key-legal_document"] p,
        [class*="st-key-legal_document"] li {
            color: var(--legal-muted);
            font-size: clamp(0.94rem, 1.8vw, 1.02rem);
            line-height: 1.7;
        }

        [class*="st-key-legal_document"] li {
            margin-bottom: 0.45rem;
        }

        [class*="st-key-legal_document"] [data-testid="stPageLink"] a {
            min-height: auto;
            padding: 0.3rem 0;
            border: 0;
            background: transparent;
            box-shadow: none;
            color: var(--legal-blue);
            font-size: 0.88rem;
            font-weight: 650;
            text-decoration: underline;
            text-underline-offset: 0.18em;
        }

        [class*="st-key-legal_document"] [data-testid="stPageLink"] a:hover {
            background: transparent;
            color: var(--legal-text);
        }

        @media (max-width: 600px) {
            .block-container {
                padding-inline: 0.8rem;
            }

            [class*="st-key-legal_document"] {
                border-radius: 18px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.container(key="legal_document"):
        st.page_link(
            "app.py",
            label="← Volver a la página principal",
            width="content",
        )
        markdown_path = PROJECT_ROOT / "legal" / markdown_filename
        try:
            content = markdown_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            st.error(
                "No pudimos cargar este documento en este momento. "
                "Vuelve a la página principal e inténtalo nuevamente."
            )
        else:
            st.markdown(content)
