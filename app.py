"""Aplicación de Brújula Política de Panamá."""

import matplotlib.pyplot as plt
import streamlit as st

from interpretations import classify_position, describe
from nuances import build_nuance_bar
from plotting import create_map, create_social_map
from questions import LIKERT_OPTIONS, QUESTIONS
from scoring import calculate_scores
from social import classify_social_position, describe_social


st.set_page_config(
    page_title="Brújula Política de Panamá",
    page_icon="🧭",
    layout="wide",
)

st.markdown(
    """
    <style>
    div[data-testid="stColumn"] {
        background: var(--secondary-background-color);
        border: 1px solid color-mix(in srgb, var(--text-color) 14%, transparent);
        border-radius: 16px;
        padding: 1.15rem;
    }
    .nuance-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 1rem;
        margin: 0.5rem 0 2rem;
    }
    .nuance-card {
        border: 1px solid color-mix(in srgb, var(--text-color) 16%, transparent);
        border-radius: 14px;
        padding: 1rem 1.1rem;
        background: var(--secondary-background-color);
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
        color: var(--text-color);
        opacity: 0.78;
    }
    .nuance-labels span:last-child { text-align: right; }
    .nuance-track {
        position: relative;
        height: 10px;
        margin: 0.55rem 0 0.7rem;
        border-radius: 999px;
        background: #e7ecef;
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
        color: var(--text-color);
        opacity: 0.86;
        font-size: 0.9rem;
    }
    @media (max-width: 900px) {
        div[data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
        }
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
            width: 100% !important;
            flex: 1 1 100% !important;
        }
        .nuance-grid { grid-template-columns: 1fr; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


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

st.title("Brújula Política de Panamá")
st.write(
    "Responde según lo que realmente piensas. "
    "No hay respuestas buenas o malas."
)

# Un formulario permite enviar todas las respuestas juntas al final.
with st.form("political_questionnaire"):
    text_answers = {}

    for number, question in enumerate(QUESTIONS, start=1):
        text_answers[question["id"]] = st.radio(
            f"{number}. {question['text']}",
            options=list(LIKERT_OPTIONS.keys()),
            index=None,
            key=question["id"],
        )

    submitted = st.form_submit_button("Ver resultado", type="primary")


if submitted:
    # Primero comprobamos que todas las preguntas tengan respuesta.
    missing = [
        question_id
        for question_id, answer in text_answers.items()
        if answer is None
    ]

    if missing:
        st.error("Faltan respuestas en: " + ", ".join(missing))
    else:
        # Aquí convertimos las palabras elegidas en valores del 1 al 5.
        numeric_answers = {
            question_id: LIKERT_OPTIONS[answer]
            for question_id, answer in text_answers.items()
        }

        scores = calculate_scores(numeric_answers)
        x = scores["x"]
        y = scores["y"]
        classification = classify_position(x, y)

        social_x = scores["familia"]
        social_y = scores["modernidad"]
        social_classification = classify_social_position(social_x, social_y)

        st.divider()
        st.title("Tu perfil político panameño")
        st.write(
            "Dos planos para entender cómo ves al Estado, la política y la sociedad."
        )

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
            st.write(
                f"**Coordenadas:** X = {social_x:.1f}, Y = {social_y:.1f}"
            )
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
