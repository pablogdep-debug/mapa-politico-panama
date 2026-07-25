"""Aplicación de Brújula Política de Panamá."""

import html
import re
import time

import matplotlib.pyplot as plt
import streamlit as st

from interpretations import classify_position, describe
from nuances import build_nuance_bar
from plotting import create_map, create_social_map
from questions import QUESTIONS
from scoring import calculate_scores
from social import classify_social_position, describe_social


st.set_page_config(
    page_title="Brújula Política de Panamá",
    page_icon="🧭",
    layout="wide",
)


LIKERT_CHOICES = (
    (1, "😠", "Totalmente en desacuerdo"),
    (2, "🙁", "En desacuerdo"),
    (3, "😐", "Ni de acuerdo ni en desacuerdo"),
    (4, "🙂", "De acuerdo"),
    (5, "😄", "Totalmente de acuerdo"),
)


st.markdown(
    """
    <style>
    :root {
        --compass-bg: #07111d;
        --compass-panel: rgba(10, 20, 34, 0.94);
        --compass-panel-soft: rgba(255, 255, 255, 0.035);
        --compass-text: #f3f7fb;
        --compass-muted: #94a4b8;
        --compass-blue: #3b82f6;
        --compass-cyan: #28d7c0;
        --compass-violet: #8b5cf6;
        --compass-magenta: #d946ef;
    }

    .stApp {
        background:
            radial-gradient(circle at 8% 0%, rgba(20, 120, 180, 0.12), transparent 35rem),
            radial-gradient(circle at 96% 94%, rgba(150, 60, 220, 0.09), transparent 34rem),
            var(--compass-bg);
        color: var(--compass-text);
    }

    .block-container {
        max-width: 1240px;
        padding-top: 4rem;
        padding-bottom: 4rem;
    }

    [class*="st-key-cover_card"],
    [class*="st-key-question_card_"],
    [class*="st-key-analysis_card"] {
        width: min(100%, 820px);
        margin-inline: auto;
        padding: clamp(1.5rem, 4vw, 2.25rem);
        border: 1px solid rgba(255, 255, 255, 0.10);
        border-radius: 24px;
        background: var(--compass-panel);
        box-shadow: 0 24px 60px rgba(0, 0, 0, 0.35);
        backdrop-filter: blur(10px);
    }

    .cover-shell,
    .question-shell,
    .analysis-shell {
        animation: gentle-enter 280ms ease-out both;
    }

    @keyframes gentle-enter {
        from { opacity: 0; transform: translateY(7px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .cover-shell {
        text-align: center;
        padding: clamp(0.5rem, 3vw, 2rem) 0 1.4rem;
    }

    .cover-mark {
        width: 64px;
        height: 64px;
        display: grid;
        place-items: center;
        margin: 0 auto 1.5rem;
        border: 1px solid rgba(72, 207, 255, 0.22);
        border-radius: 20px;
        background: linear-gradient(145deg, rgba(59, 130, 246, 0.16), rgba(139, 92, 246, 0.12));
        box-shadow: 0 14px 34px rgba(24, 102, 174, 0.15);
        font-size: 1.9rem;
    }

    .cover-title {
        max-width: 720px;
        margin: 0 auto 1rem;
        color: var(--compass-text);
        font-size: clamp(2.15rem, 5vw, 3.5rem);
        line-height: 1.08;
        letter-spacing: -0.04em;
        font-weight: 760;
    }

    .cover-gradient {
        display: inline-block;
        background: linear-gradient(100deg, #59a8ff 0%, #38dfcf 34%, #9b72ff 68%, #ef6adf 100%);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }

    .cover-copy {
        max-width: 660px;
        margin: 0 auto;
        color: #b7c3d3;
        font-size: clamp(0.98rem, 2vw, 1.12rem);
        line-height: 1.62;
    }

    .cover-introduction {
        max-width: 680px;
        margin: 1.65rem auto 0;
        color: #b7c3d3;
        font-size: clamp(0.94rem, 1.8vw, 1.04rem);
        line-height: 1.68;
        text-align: left;
    }

    .cover-introduction p {
        margin: 0 0 1rem;
    }

    .cover-introduction .intro-lead {
        padding-left: 1rem;
        border-left: 3px solid rgba(40, 215, 192, 0.72);
        color: #e9f1f8;
        font-size: 1.04em;
        font-weight: 620;
    }

    .cover-introduction .intro-authors {
        margin: 1.25rem 0 0;
        color: #7f90a5;
        font-size: 0.82rem;
    }

    .cover-details {
        display: grid;
        gap: 0.75rem;
        max-width: 540px;
        margin: 2rem auto 0.6rem;
        text-align: left;
    }

    .cover-detail {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        padding: 0.7rem 0.9rem;
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 13px;
        background: rgba(255, 255, 255, 0.025);
        color: #dbe5ef;
        font-size: 0.94rem;
    }

    .cover-detail-icon {
        width: 1.6rem;
        font-size: 1.1rem;
        text-align: center;
    }

    .privacy-note {
        margin: 0.9rem auto 0;
        color: #7f90a5;
        font-size: 0.76rem;
        line-height: 1.45;
        text-align: center;
    }

    [class*="st-key-start_button"] button,
    [class*="st-key-restart_button"] button {
        min-height: 58px;
        border: 0 !important;
        border-radius: 16px;
        background: linear-gradient(105deg, var(--compass-blue), var(--compass-violet)) !important;
        box-shadow: 0 12px 28px rgba(79, 92, 246, 0.26);
        color: white !important;
        font-size: 1.05rem;
        font-weight: 750;
        transition: transform 150ms ease, box-shadow 150ms ease;
    }

    [class*="st-key-start_button"] button:hover,
    [class*="st-key-restart_button"] button:hover {
        transform: translateY(-1px);
        box-shadow: 0 15px 34px rgba(79, 92, 246, 0.34);
    }

    [class*="st-key-subscription_card"] {
        width: min(100%, 820px);
        margin: 2.2rem auto 1.4rem;
        padding: clamp(1.5rem, 4vw, 2.25rem);
        border: 1px solid rgba(72, 207, 255, 0.14);
        border-radius: 24px;
        background:
            radial-gradient(circle at 100% 0%, rgba(139, 92, 246, 0.10), transparent 22rem),
            rgba(10, 20, 34, 0.94);
        box-shadow: 0 24px 60px rgba(0, 0, 0, 0.28);
    }

    .subscription-intro {
        max-width: 700px;
        margin-bottom: 1.35rem;
    }

    .subscription-title {
        margin: 0 0 1rem;
        color: var(--compass-text);
        font-size: clamp(1.55rem, 3.2vw, 2.15rem);
        line-height: 1.18;
        letter-spacing: -0.025em;
    }

    .subscription-copy {
        margin: 0 0 0.9rem;
        color: #b7c3d3;
        line-height: 1.65;
    }

    [class*="st-key-subscription_card"] [data-testid="stTextInput"] label {
        color: #e9f1f8;
        font-weight: 650;
    }

    [class*="st-key-subscription_card"] [data-testid="stTextInput"] input {
        min-height: 52px;
        border-color: rgba(255, 255, 255, 0.14);
        border-radius: 13px;
        background: rgba(255, 255, 255, 0.045);
        color: white;
    }

    [class*="st-key-subscription_card"] form button {
        min-height: 52px;
        border: 0 !important;
        border-radius: 14px;
        background: linear-gradient(105deg, var(--compass-blue), var(--compass-violet)) !important;
        color: white !important;
        font-weight: 720;
    }

    .subscription-note,
    .subscription-privacy {
        color: #8495aa;
        line-height: 1.5;
    }

    .subscription-note {
        margin: 0.9rem 0 0.45rem;
        font-size: 0.79rem;
    }

    .subscription-privacy {
        margin: 0;
        font-size: 0.75rem;
    }

    .question-meta {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 0.7rem;
        color: #e8eef6;
        font-size: 0.9rem;
        font-weight: 580;
    }

    .question-current {
        color: var(--compass-cyan);
        font-weight: 720;
    }

    .question-total,
    .question-percent {
        color: var(--compass-muted);
    }

    .question-percent {
        font-variant-numeric: tabular-nums;
    }

    .progress-track {
        width: 100%;
        height: 9px;
        overflow: hidden;
        border-radius: 999px;
        background: #1b2939;
        box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.32);
    }

    .progress-fill {
        height: 100%;
        border-radius: inherit;
        background: linear-gradient(90deg, var(--compass-blue), var(--compass-cyan));
        box-shadow: 0 0 18px rgba(40, 215, 192, 0.24);
        transition: width 240ms ease;
    }

    .question-title {
        max-width: 720px;
        margin: 2rem 0 1.75rem;
        color: var(--compass-text);
        font-size: clamp(30px, 3vw, 36px) !important;
        line-height: 1.34;
        letter-spacing: -0.025em;
        font-weight: 600 !important;
    }

    .question-title * {
        font-weight: 600 !important;
    }

    [class*="st-key-answer_"] .stButton > button {
        min-height: 68px;
        justify-content: flex-start !important;
        margin-bottom: 0.32rem;
        padding: 0.85rem 1.1rem;
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-left: 4px solid var(--answer-accent);
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.025);
        box-shadow: inset 14px 0 32px -30px var(--answer-accent);
        color: #eaf1f8;
        font-size: 1rem;
        font-weight: 560;
        text-align: left;
        white-space: normal;
        line-height: 1.3;
        transition: transform 140ms ease, border-color 140ms ease, background 140ms ease, box-shadow 140ms ease;
    }

    [class*="st-key-answer_"] .stButton > button > div,
    [class*="st-key-answer_"] .stButton > button > div > span,
    [class*="st-key-answer_"] .stButton > button [data-testid="stMarkdownContainer"] {
        width: 100%;
    }

    [class*="st-key-answer_"] .stButton > button p {
        width: 100% !important;
        flex: 1 1 100% !important;
        align-self: stretch;
        color: inherit;
        text-align: left !important;
        display: grid;
        grid-template-columns: minmax(64px, 24%) minmax(0, 1fr);
        align-items: center;
        padding: 0;
    }

    [class*="st-key-answer_"] .stButton > button p::before {
        grid-column: 1;
        grid-row: 1;
        justify-self: center;
        width: 44px;
        text-align: center;
        font-size: 2.15rem;
        line-height: 1;
    }

    [class*="st-key-answer_"] .stButton > button:hover {
        transform: translateY(-1px);
        border-color: color-mix(in srgb, var(--answer-accent) 58%, white 8%);
        background: color-mix(in srgb, var(--answer-accent) 8%, rgba(255, 255, 255, 0.025));
        box-shadow: 0 8px 24px color-mix(in srgb, var(--answer-accent) 12%, transparent);
        color: white;
    }

    [class*="st-key-answer_"] .stButton > button[kind="primary"],
    [class*="st-key-answer_"] .stButton > button[data-testid="stBaseButton-primary"] {
        border-color: var(--answer-accent) !important;
        background: color-mix(in srgb, var(--answer-accent) 13%, #0d1a29) !important;
        box-shadow: 0 0 0 1px var(--answer-accent), 0 10px 26px color-mix(in srgb, var(--answer-accent) 17%, transparent);
        color: white !important;
    }

    [class*="st-key-answer_"] .stButton > button:focus-visible {
        outline: 3px solid color-mix(in srgb, var(--answer-accent) 48%, transparent);
        outline-offset: 2px;
    }

    [class*="st-key-answer_value_1_"] { --answer-accent: #ff6b72; }
    [class*="st-key-answer_value_2_"] { --answer-accent: #ff9f43; }
    [class*="st-key-answer_value_3_"] { --answer-accent: #e7c84b; }
    [class*="st-key-answer_value_4_"] { --answer-accent: #75d78f; }
    [class*="st-key-answer_value_5_"] { --answer-accent: #31d4c3; }
    [class*="st-key-answer_value_1_"] button p::before { content: "😠"; }
    [class*="st-key-answer_value_2_"] button p::before { content: "🙁"; }
    [class*="st-key-answer_value_3_"] button p::before { content: "😐"; }
    [class*="st-key-answer_value_4_"] button p::before { content: "🙂"; }
    [class*="st-key-answer_value_5_"] button p::before { content: "😄"; }

    [class*="st-key-navigation"] {
        margin-top: 1.45rem;
    }

    [class*="st-key-navigation"] button {
        min-height: 52px;
        border-radius: 14px;
        font-weight: 650;
    }

    [class*="st-key-back_"] button {
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        background: #142131 !important;
        color: #c9d4df !important;
    }

    [class*="st-key-next_"] button {
        border: 0 !important;
        background: linear-gradient(105deg, var(--compass-blue), var(--compass-violet)) !important;
        box-shadow: 0 10px 24px rgba(76, 92, 230, 0.23);
        color: white !important;
    }

    [class*="st-key-next_"] button:disabled {
        background: #1b2939 !important;
        box-shadow: none;
        color: #69798c !important;
    }

    .analysis-shell {
        padding: min(10vh, 5rem) 0 1.5rem;
        text-align: center;
    }

    .analysis-icon {
        width: 72px;
        height: 72px;
        display: grid;
        place-items: center;
        margin: 0 auto 1.2rem;
        border: 1px solid rgba(59, 130, 246, 0.25);
        border-radius: 50%;
        background: linear-gradient(145deg, rgba(59, 130, 246, 0.16), rgba(139, 92, 246, 0.14));
        box-shadow: 0 0 34px rgba(89, 110, 246, 0.14);
        font-size: 2rem;
    }

    .analysis-title {
        margin: 0 0 0.65rem;
        color: var(--compass-text);
        font-size: clamp(1.8rem, 4vw, 2.65rem);
        font-weight: 700;
        letter-spacing: -0.035em;
    }

    .analysis-copy {
        color: var(--compass-muted);
        margin-bottom: 1.5rem;
    }

    [class*="st-key-analysis_card"] .stProgress > div > div {
        background: linear-gradient(90deg, var(--compass-blue), var(--compass-cyan)) !important;
    }

    [class*="st-key-results_grid"] div[data-testid="stColumn"] {
        background: rgba(10, 20, 34, 0.92);
        border: 1px solid rgba(255, 255, 255, 0.10);
        border-radius: 20px;
        padding: 1.15rem;
        box-shadow: 0 18px 44px rgba(0, 0, 0, 0.22);
    }

    .nuance-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 1rem;
        margin: 0.5rem 0 2rem;
    }

    .nuance-card {
        border: 1px solid rgba(255, 255, 255, 0.10);
        border-radius: 18px;
        padding: 1rem 1.1rem;
        background: rgba(10, 20, 34, 0.92);
    }

    .nuance-heading {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        font-weight: 700;
        margin-bottom: 0.75rem;
    }

    .nuance-value { font-variant-numeric: tabular-nums; }

    .nuance-labels {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        font-size: 0.78rem;
        color: #9eacbd;
    }

    .nuance-labels span:last-child { text-align: right; }

    .nuance-track {
        position: relative;
        height: 10px;
        margin: 0.55rem 0 0.7rem;
        border-radius: 999px;
        background: #1b2939;
    }

    .nuance-zero {
        position: absolute;
        left: 50%;
        top: -4px;
        width: 2px;
        height: 18px;
        background: #64727a;
    }

    .nuance-fill {
        position: absolute;
        top: 0;
        height: 10px;
        border-radius: 999px;
        background: #567c8d;
    }

    .nuance-marker {
        position: absolute;
        top: 50%;
        width: 16px;
        height: 16px;
        border: 2px solid #17242b;
        border-radius: 50%;
        background: #f04f5f;
        transform: translate(-50%, -50%);
    }

    .nuance-description {
        margin: 0;
        color: #b7c3d2;
        font-size: 0.9rem;
    }

    @media (max-width: 900px) {
        [class*="st-key-results_grid"] div[data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
        }

        [class*="st-key-results_grid"] div[data-testid="stColumn"] {
            width: 100% !important;
            flex: 1 1 100% !important;
        }

        .nuance-grid { grid-template-columns: 1fr; }
    }

    @media (max-width: 640px) {
        .block-container {
            padding: 3.75rem 0.7rem 2.5rem;
        }

        [class*="st-key-cover_card"],
        [class*="st-key-question_card_"],
        [class*="st-key-analysis_card"] {
            padding: 1.2rem;
            border-radius: 20px;
        }

        .cover-shell { padding-top: 0.4rem; }
        .cover-title {
            font-size: clamp(2rem, 11vw, 2.65rem);
            line-height: 1.08;
        }
        .cover-copy { line-height: 1.55; }
        .cover-details { margin-top: 1.5rem; }

        .question-title {
            margin: 1.35rem 0 1.25rem;
            font-size: clamp(24px, 7vw, 28px) !important;
            line-height: 1.36;
            font-weight: 600 !important;
        }

        [class*="st-key-answer_"] .stButton > button {
            min-height: 64px;
            padding: 0.72rem 0.85rem;
            font-size: 0.9rem;
        }

        [class*="st-key-answer_"] .stButton > button p {
            grid-template-columns: 68px minmax(0, 1fr);
        }

        [class*="st-key-answer_"] .stButton > button p::before {
            font-size: 1.95rem;
        }

        [class*="st-key-navigation"] div[data-testid="stHorizontalBlock"] {
            gap: 0.55rem;
        }

        [class*="st-key-navigation"] button {
            min-height: 50px;
            font-size: 0.9rem;
        }
    }

    @media (prefers-reduced-motion: reduce) {
        .cover-shell,
        .question-shell,
        .analysis-shell {
            animation: none;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def initialize_state():
    """Crea el estado mínimo del recorrido sin borrar respuestas existentes."""
    defaults = {
        "started": False,
        "current_question": 0,
        "answers": {},
        "show_results": False,
        "analysis_complete": False,
        "email_submitted": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_questionnaire():
    """Regresa a la portada y elimina todas las respuestas del recorrido."""
    st.session_state.started = False
    st.session_state.current_question = 0
    st.session_state.answers = {}
    st.session_state.show_results = False
    st.session_state.analysis_complete = False


def is_valid_email(email):
    """Comprueba solamente que el correo tenga una estructura razonable."""
    return bool(
        len(email) <= 254
        and re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)
    )


def save_subscription_email(email):
    """Punto de conexión para un futuro servicio de suscripciones.

    La interfaz no guarda el correo ni lo relaciona con las respuestas.
    Cuando se elija un proveedor, esta función podrá enviar únicamente
    ``email`` a Google Sheets, Brevo, Mailchimp u otro servicio.
    """
    del email
    return True


def nuance_card_html(kind, value):
    """Construye una tarjeta visual para uno de los dos matices."""
    model = build_nuance_bar(kind, value)
    return (
        '<div class="nuance-card">'
        '<div class="nuance-heading">'
        f'<span>{model["name"]}</span>'
        f'<span class="nuance-value">{model["value"]:+.1f}</span>'
        "</div>"
        '<div class="nuance-labels">'
        f'<span>{model["negative"]}</span>'
        f'<span>{model["positive"]}</span>'
        "</div>"
        '<div class="nuance-track">'
        '<div class="nuance-zero"></div>'
        f'<div class="nuance-fill" style="left:{model["fill_left_percent"]}%; '
        f'width:{model["fill_width_percent"]}%;"></div>'
        f'<div class="nuance-marker" style="left:{model["marker_percent"]}%;"></div>'
        "</div>"
        f'<p class="nuance-description">{model["description"]}</p>'
        "</div>"
    )


def render_cover():
    """Muestra la portada antes de revelar el cuestionario."""
    with st.container(key="cover_card"):
        st.markdown(
            """
            <div class="cover-shell">
                <div class="cover-mark" aria-hidden="true">🧭</div>
                <h1 class="cover-title">
                    Descubre tu <span class="cover-gradient">brújula política</span>
                </h1>
                <p class="cover-copy">
                    Comprende cómo piensas sobre el Estado, la sociedad y los
                    grandes temas que marcan el futuro de Panamá.
                </p>
                <div class="cover-introduction">
                    <p class="intro-lead">
                        Crear conciencia política comienza por reflexionar sobre
                        nuestras propias ideas acerca del orden político y la
                        organización de la sociedad.
                    </p>
                    <p>
                        Este cuestionario fue creado para facilitar esa reflexión
                        y estimular el pensamiento crítico, no para decirte qué
                        debes pensar.
                    </p>
                    <p>
                        Responderás únicamente 24 preguntas y no necesitas
                        proporcionar tu nombre ni ningún dato personal para
                        conocer tu resultado. Al finalizar, descubrirás con qué
                        perfil político se alinea más tu manera de pensar y
                        recibirás una breve interpretación de tus respuestas.
                    </p>
                    <p>
                        Somos panameños que amamos nuestro país y creemos que una
                        mejor democracia comienza con una conversación pública
                        más respetuosa, informada y reflexiva. Si al finalizar
                        deseas seguir participando, podrás dejar voluntariamente
                        tu correo para recibir futuras encuestas y contenidos
                        relacionados con este proyecto.
                    </p>
                    <p class="intro-authors">
                        Autores: Pablo García de Paredes y Mark Harrick.
                    </p>
                </div>
                <div class="cover-details">
                    <div class="cover-detail">
                        <span class="cover-detail-icon" aria-hidden="true">🕒</span>
                        <span>Aproximadamente 4 minutos</span>
                    </div>
                    <div class="cover-detail">
                        <span class="cover-detail-icon" aria-hidden="true">⚖️</span>
                        <span>No existen respuestas correctas o incorrectas</span>
                    </div>
                    <div class="cover-detail">
                        <span class="cover-detail-icon" aria-hidden="true">📊</span>
                        <span>Resultado inmediato y personalizado</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(
            "Comenzar",
            type="primary",
            use_container_width=True,
            key="start_button",
        ):
            st.session_state.started = True
            st.session_state.current_question = 0
            st.rerun()
        st.markdown(
            '<p class="privacy-note">'
            "Tus respuestas se utilizan únicamente durante esta sesión para "
            "calcular tu perfil."
            "</p>",
            unsafe_allow_html=True,
        )


def render_question():
    """Muestra una sola pregunta y conserva su respuesta por ID."""
    total = len(QUESTIONS)
    index = st.session_state.current_question
    question = QUESTIONS[index]
    question_id = question["id"]
    selected_value = st.session_state.answers.get(question_id)
    progress_value = (index + 1) / total
    progress_percentage = round(progress_value * 100)

    with st.container(key=f"question_card_{index}"):
        st.markdown(
            '<div class="question-shell">'
            '<div class="question-meta">'
            "<span>Pregunta "
            f'<strong class="question-current">{index + 1}</strong> '
            f'<span class="question-total">de {total}</span></span>'
            f'<span class="question-percent">{progress_percentage}%</span>'
            "</div>"
            '<div class="progress-track" role="progressbar" '
            'aria-label="Progreso del cuestionario" aria-valuemin="0" '
            f'aria-valuemax="{total}" aria-valuenow="{index + 1}">'
            f'<div class="progress-fill" style="width:{progress_percentage}%"></div>'
            "</div>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<h1 class="question-title">{html.escape(question["text"])}</h1>',
            unsafe_allow_html=True,
        )

        for value, face, label in LIKERT_CHOICES:
            is_selected = selected_value == value
            visible_label = label
            if is_selected:
                visible_label += "  ✓ Seleccionada"

            if st.button(
                visible_label,
                key=f"answer_value_{value}_{question_id}",
                type="primary" if is_selected else "secondary",
                use_container_width=True,
            ):
                st.session_state.answers[question_id] = value
                st.rerun()

        with st.container(key="navigation"):
            back_column, next_column = st.columns(2, gap="small")

            with back_column:
                if index > 0 and st.button(
                    "← Atrás",
                    use_container_width=True,
                    key=f"back_{index}",
                ):
                    st.session_state.current_question -= 1
                    st.rerun()

            with next_column:
                final_question = index == total - 1
                next_label = "Ver mis resultados" if final_question else "Siguiente →"

                if st.button(
                    next_label,
                    type="primary",
                    disabled=selected_value is None,
                    use_container_width=True,
                    key=f"next_{index}",
                ):
                    if final_question:
                        expected_ids = {item["id"] for item in QUESTIONS}
                        if set(st.session_state.answers) != expected_ids:
                            st.error(
                                "Antes de ver tus resultados, responde las 24 preguntas."
                            )
                        else:
                            st.session_state.show_results = True
                            st.session_state.analysis_complete = False
                            st.rerun()
                    else:
                        st.session_state.current_question += 1
                        st.rerun()


def render_analysis():
    """Presenta una transición breve antes de mostrar los resultados."""
    with st.container(key="analysis_card"):
        st.markdown(
            """
            <div class="analysis-shell">
                <div class="analysis-icon" aria-hidden="true">🧭</div>
                <h1 class="analysis-title">Analizando tus respuestas…</h1>
                <p class="analysis-copy">
                    Estamos organizando tus dos planos y tus matices.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        progress = st.progress(0)
        message = st.empty()
        steps = (
            (34, "✓ Calculando tu orientación política"),
            (67, "✓ Identificando tus matices"),
            (100, "✓ Preparando tus perfiles"),
        )
        for percentage, text in steps:
            message.write(text)
            progress.progress(percentage)
            time.sleep(0.55)

    st.session_state.analysis_complete = True
    st.rerun()


def render_subscription():
    """Muestra una invitación opcional, separada del resultado político."""
    with st.container(key="subscription_card"):
        st.markdown(
            """
            <div class="subscription-intro">
                <h2 class="subscription-title">
                    Sigamos construyendo una ciudadanía más consciente
                </h2>
                <p class="subscription-copy">
                    Gracias por completar la Brújula Política Panameña.
                </p>
                <p class="subscription-copy">
                    Esperamos que este ejercicio haya servido para reflexionar
                    sobre algunas de las ideas que orientan tu manera de entender
                    la política y la sociedad. Nuestro objetivo no es decirle a
                    nadie qué pensar, sino promover una conversación pública más
                    crítica, respetuosa e informada.
                </p>
                <p class="subscription-copy">
                    Si te interesa seguir participando, puedes dejarnos
                    voluntariamente tu correo. Te enviaremos futuras encuestas,
                    nuevos análisis y otros contenidos relacionados con este
                    proyecto.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.session_state.email_submitted:
            st.success(
                "¡Muchas gracias! Será un gusto seguir reflexionando contigo."
            )
        else:
            with st.form("subscription_form", clear_on_submit=False):
                email = st.text_input(
                    "Tu correo electrónico",
                    placeholder="nombre@correo.com",
                )
                submitted = st.form_submit_button(
                    "Quiero recibir futuras encuestas",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:
                normalized_email = email.strip().lower()
                if not is_valid_email(normalized_email):
                    st.error(
                        "Parece que el correo no está completo. "
                        "Revísalo e inténtalo nuevamente."
                    )
                elif save_subscription_email(normalized_email):
                    st.session_state.email_submitted = True
                    st.rerun()

            st.markdown(
                """
                <p class="subscription-note">
                    Solo utilizaremos tu correo para compartir nuevos contenidos
                    y futuras encuestas. Podrás darte de baja cuando quieras.
                </p>
                <p class="subscription-privacy">
                    🔒 Tu correo no será compartido con terceros ni utilizado
                    para fines distintos a este proyecto.
                </p>
                """,
                unsafe_allow_html=True,
            )


def render_results():
    """Reutiliza sin cambios la lógica existente de puntuación y resultados."""
    numeric_answers = dict(st.session_state.answers)
    scores = calculate_scores(numeric_answers)

    x = scores["x"]
    y = scores["y"]
    classification = classify_position(x, y)

    social_x = scores["familia"]
    social_y = scores["modernidad"]
    social_classification = classify_social_position(social_x, social_y)

    st.title("Tu perfil político panameño")
    st.write("Dos planos para entender cómo ves al Estado, la política y la sociedad.")

    with st.container(key="results_grid"):
        political_column, social_column = st.columns(2, gap="large")

        with political_column:
            st.subheader("1. Estado y forma de hacer política")
            st.caption(
                "Cómo combinas el papel del Estado con la forma de resolver "
                "problemas y ejercer la política."
            )
            st.markdown(f"### {classification['name']}")
            st.write(f"**Coordenadas:** X = {x:.1f}, Y = {y:.1f}")
            st.write(f"**Intensidad:** {classification['intensity']:.1f}%")

            figure = create_map(x, y)
            st.pyplot(figure, use_container_width=True)
            plt.close(figure)
            st.write(describe(classification))

        with social_column:
            st.subheader("2. Valores sociales, familia y modernidad")
            st.caption(
                "Cómo relacionas la familia y la autonomía personal con la "
                "tradición, la ciencia y la modernización."
            )
            st.markdown(f"### {social_classification['name']}")
            st.write(f"**Coordenadas:** X = {social_x:.1f}, Y = {social_y:.1f}")
            st.write(
                f"**Intensidad:** {social_classification['intensity']:.1f}%"
            )

            social_figure = create_social_map(social_x, social_y)
            st.pyplot(social_figure, use_container_width=True)
            plt.close(social_figure)
            st.write(describe_social(social_classification))

    st.subheader("Tus matices")
    st.markdown(
        '<div class="nuance-grid">'
        + nuance_card_html("seguridad", scores["seguridad"])
        + nuance_card_html("partidismo", scores["partidismo"])
        + "</div>",
        unsafe_allow_html=True,
    )

    render_subscription()

    st.button(
        "Volver a realizar el cuestionario",
        on_click=reset_questionnaire,
        type="primary",
        use_container_width=True,
        key="restart_button",
    )


initialize_state()

if not st.session_state.started:
    render_cover()
elif not st.session_state.show_results:
    render_question()
elif not st.session_state.analysis_complete:
    render_analysis()
else:
    render_results()
