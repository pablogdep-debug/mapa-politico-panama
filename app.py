"""Aplicación de Brújula Política de Panamá."""

import base64
import html
import json
import re
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import streamlit as st
import streamlit.components.v1 as components

from config import PATREON_URL
from demographics import (
    AGE_FIELD_ID,
    AGE_RANGES,
    DISTRICT_FIELD_ID,
    build_demographic_record,
    filter_residence_options,
    is_valid_age_range,
    is_valid_residence_option,
)
from interpretations import classify_position, describe
from nuances import build_nuance_bar
from plotting import create_map, create_social_map
from questions import QUESTIONS
from scoring import calculate_scores
from shared_results import (
    build_share_url,
    build_social_message,
    decode_result,
    facebook_share_url,
    whatsapp_share_url,
)
from social import classify_social_position, describe_social
from storage.google_sheets import (
    apply_response_save_result,
    save_anonymous_response,
    save_subscriber_email,
)


st.set_page_config(
    page_title="Brújula Democrática",
    page_icon="assets/brujula.png",
    layout="wide",
)

PUBLIC_APP_URL = "https://brujula-politica-panama.streamlit.app"
APP_VERSION = "1.0"
LOGO_PATH = Path("assets/brujula.png")
LOGO_ALT = (
    "Brújula Democrática — Movimiento de inteligencia participativa "
    "informada por la ciencia en Panamá"
)
SOCIAL_LINKS = {
    "pablo_instagram": "https://www.instagram.com/pablo.garciadeparedes/",
    "mark_instagram": "https://www.instagram.com/markharricka/",
    "brujula_instagram": "",
    "brujula_facebook": "",
}


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
        --compass-bg: #e9edf2;
        --compass-panel: #ffffff;
        --compass-panel-soft: #f2f4f7;
        --compass-text: #102a50;
        --compass-muted: #526174;
        --compass-blue: #0a438f;
        --compass-red: #c43d4d;
        --compass-cyan: #087f8c;
        --compass-violet: #8b5cf6;
        --compass-magenta: #b936c5;
        --compass-border: #d8dee8;
        --compass-shadow: 0 8px 28px rgba(16, 42, 80, 0.08);
    }

    .stApp {
        background:
            radial-gradient(circle at 8% 0%, rgba(10, 67, 143, 0.07), transparent 35rem),
            radial-gradient(circle at 96% 94%, rgba(139, 92, 246, 0.06), transparent 34rem),
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
        border: 1px solid var(--compass-border);
        border-radius: 24px;
        background: var(--compass-panel);
        box-shadow: var(--compass-shadow);
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

    [class*="st-key-cover_logo"] {
        position: relative;
        width: min(100%, 780px);
        aspect-ratio: 2.05 / 1;
        overflow: hidden;
        margin: 0 auto 1.25rem;
    }

    [class*="st-key-cover_logo"] img {
        position: absolute;
        top: 50%;
        left: 0;
        width: 100%;
        height: auto;
        object-fit: contain;
        transform: translateY(-50%);
    }

    .cover-copy {
        max-width: 660px;
        margin: 0 auto;
        color: var(--compass-muted);
        font-size: clamp(0.98rem, 2vw, 1.12rem);
        line-height: 1.62;
    }

    .cover-introduction {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.85rem;
        max-width: 760px;
        margin: 1.85rem auto 0;
        text-align: left;
    }

    .intro-card {
        min-height: 100%;
        padding: 1.2rem 1.15rem 1.25rem;
        border: 1px solid var(--compass-border);
        border-radius: 17px;
        background: var(--compass-panel-soft);
        box-shadow: 0 10px 28px rgba(16, 42, 80, 0.06);
    }

    .intro-icon {
        width: 34px;
        height: 34px;
        display: grid;
        place-items: center;
        margin-bottom: 1rem;
        border: 1px solid rgba(72, 207, 255, 0.16);
        border-radius: 10px;
        background: rgba(59, 130, 246, 0.08);
        color: var(--compass-blue);
    }

    .intro-icon svg {
        width: 18px;
        height: 18px;
        fill: none;
        stroke: currentColor;
        stroke-linecap: round;
        stroke-linejoin: round;
        stroke-width: 1.8;
    }

    .intro-card h2 {
        min-height: 2.45em;
        margin: 0 0 0.8rem;
        color: var(--compass-text);
        font-size: 1.02rem;
        line-height: 1.22;
        letter-spacing: -0.01em;
    }

    .intro-card p {
        margin: 0 0 0.8rem;
        color: var(--compass-muted);
        font-size: 0.84rem;
        line-height: 1.55;
    }

    .intro-card p:last-child {
        margin-bottom: 0;
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
        border: 1px solid var(--compass-border);
        border-radius: 13px;
        background: var(--compass-panel-soft);
        color: var(--compass-text);
        font-size: 0.94rem;
    }

    .cover-detail-icon {
        width: 1.6rem;
        font-size: 1.1rem;
        text-align: center;
    }

    .privacy-note {
        margin: 0.9rem auto 0;
        color: var(--compass-muted);
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
        border: 1px solid var(--compass-border);
        border-radius: 24px;
        background:
            radial-gradient(circle at 100% 0%, rgba(139, 92, 246, 0.07), transparent 22rem),
            var(--compass-panel);
        box-shadow: var(--compass-shadow);
    }

    [class*="st-key-patreon_support_card"] {
        width: min(100%, 920px);
        margin: 2.2rem auto 1.4rem;
        padding: clamp(1.4rem, 3vw, 2rem);
        overflow: hidden;
        border: 1px solid var(--compass-border);
        border-left: 4px solid var(--compass-blue);
        border-right: 4px solid var(--compass-red);
        border-radius: 22px;
        background: var(--compass-panel);
        box-shadow: 0 14px 34px rgba(21, 50, 88, 0.1);
    }

    .patreon-heading {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        margin: 0 0 0.7rem;
        color: var(--compass-text);
        font-size: clamp(1.4rem, 2.8vw, 1.9rem);
        line-height: 1.2;
        letter-spacing: -0.025em;
    }

    .patreon-icon {
        font-size: 1.25rem;
    }

    .patreon-copy,
    .patreon-note {
        max-width: 800px;
        color: var(--compass-muted);
        line-height: 1.58;
    }

    .patreon-copy {
        margin: 0 0 0.7rem;
    }

    .patreon-note {
        margin: 0 0 1.1rem;
        font-size: 0.9rem;
    }

    [class*="st-key-patreon_support_card"] a {
        min-height: 52px;
        border: 0 !important;
        border-radius: 14px;
        background: var(--compass-blue) !important;
        box-shadow: 0 10px 22px rgba(21, 50, 88, 0.18);
        color: white !important;
        font-weight: 740;
    }

    [class*="st-key-patreon_support_card"] a:hover {
        background: #102f59 !important;
        color: white !important;
    }

    .subscription-intro {
        max-width: 680px;
        margin-bottom: 1.45rem;
    }

    .subscription-title {
        margin: 0 0 1rem;
        color: var(--compass-text);
        font-size: clamp(1.55rem, 3.2vw, 2.15rem);
        line-height: 1.18;
        letter-spacing: -0.025em;
    }

    .subscription-copy {
        margin: 0 0 0.8rem;
        color: var(--compass-muted);
        line-height: 1.6;
    }

    [class*="st-key-subscription_card"] [data-testid="stTextInput"] label {
        color: var(--compass-text);
        font-weight: 650;
    }

    [class*="st-key-subscription_card"] [data-testid="stTextInput"] input {
        min-height: 52px;
        border-color: var(--compass-border);
        border-radius: 13px;
        background: #fff;
        color: var(--compass-text);
    }

    [class*="st-key-subscription_card"] form button {
        min-height: 52px;
        border: 0 !important;
        border-radius: 14px;
        background: linear-gradient(105deg, var(--compass-blue), var(--compass-violet)) !important;
        color: white !important;
        font-weight: 720;
    }

    .subscription-note {
        margin: 0.85rem 0 0;
        color: var(--compass-muted);
        font-size: 0.79rem;
        line-height: 1.5;
    }

    .question-meta {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 0.7rem;
        color: var(--compass-text);
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
        background: #dbe2ea;
        box-shadow: inset 0 1px 2px rgba(16, 42, 80, 0.12);
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
        font-size: clamp(27px, 2.7vw, 32px) !important;
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
        border: 1px solid var(--compass-border);
        border-left: 4px solid var(--answer-accent);
        border-radius: 16px;
        background: #fff;
        box-shadow: inset 14px 0 32px -30px var(--answer-accent);
        color: var(--compass-text);
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
        background: color-mix(in srgb, var(--answer-accent) 8%, white);
        box-shadow: 0 8px 24px color-mix(in srgb, var(--answer-accent) 12%, transparent);
        color: var(--compass-text);
    }

    [class*="st-key-answer_"] .stButton > button[kind="primary"],
    [class*="st-key-answer_"] .stButton > button[data-testid="stBaseButton-primary"] {
        border-color: var(--answer-accent) !important;
        background: color-mix(in srgb, var(--answer-accent) 13%, white) !important;
        box-shadow: 0 0 0 1px var(--answer-accent), 0 10px 26px color-mix(in srgb, var(--answer-accent) 17%, transparent);
        color: var(--compass-text) !important;
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

    .demographic-intro {
        margin: 1.5rem 0 1.25rem;
        padding: 1rem 1.1rem;
        border: 1px solid var(--compass-border);
        border-radius: 15px;
        background: var(--compass-panel-soft);
    }

    .demographic-intro h1 {
        margin: 0 0 0.45rem;
        color: var(--compass-text);
        font-size: clamp(1.35rem, 2.5vw, 1.7rem);
        letter-spacing: -0.02em;
    }

    .demographic-intro p,
    .demographic-help {
        margin: 0;
        color: var(--compass-muted);
        line-height: 1.55;
    }

    [class*="st-key-dem_age_range_"] button {
        min-height: 58px;
        justify-content: flex-start;
        margin-bottom: 0.25rem;
        padding-inline: 1rem;
        border: 1px solid var(--compass-border);
        border-left: 4px solid var(--compass-blue);
        border-radius: 14px;
        background: #fff;
        color: var(--compass-text);
        font-weight: 620;
        text-align: left;
    }

    [class*="st-key-dem_age_range_"] button[kind="primary"],
    [class*="st-key-dem_age_range_"] button[data-testid="stBaseButton-primary"] {
        border-color: var(--compass-blue);
        background: #eaf1fa;
        box-shadow: 0 0 0 1px var(--compass-blue);
        color: var(--compass-text);
    }

    [class*="st-key-dem_age_range_"] button:focus-visible,
    [class*="dem_district"] [data-baseweb="select"] > div:focus-within {
        outline: 3px solid rgba(10, 67, 143, 0.24);
        outline-offset: 2px;
    }

    [class*="dem_district"] [data-baseweb="select"] > div,
    [class*="dem_district"] .react-aria-ComboBox [role="group"],
    [class*="district_search"] [data-testid="stTextInput"] input {
        min-height: 52px;
        border-color: var(--compass-border) !important;
        border-radius: 13px;
        background: #fff !important;
        color: var(--compass-text) !important;
    }

    [class*="dem_district"] label,
    [class*="district_search"] label {
        color: var(--compass-text) !important;
        font-weight: 620;
    }

    [class*="dem_district"] svg {
        fill: var(--compass-text) !important;
    }

    [class*="dem_district"] .react-aria-ComboBox input,
    [class*="dem_district"] .react-aria-ComboBox button {
        background: #fff !important;
        color: var(--compass-text) !important;
    }

    [class*="dem_district"] input::placeholder,
    [class*="district_search"] input::placeholder {
        color: var(--compass-muted) !important;
        opacity: 1 !important;
    }

    [class*="st-key-next_demographic_age"] button,
    [class*="st-key-finish_demographics"] button {
        border: 0 !important;
        background: linear-gradient(105deg, var(--compass-blue), var(--compass-violet)) !important;
        color: white !important;
    }

    [class*="st-key-next_demographic_age"] button:disabled,
    [class*="st-key-finish_demographics"] button:disabled {
        border: 1px solid var(--compass-border) !important;
        background: #dbe2ea !important;
        color: #69798c !important;
    }

    [class*="st-key-back_"] button {
        border: 1px solid var(--compass-border) !important;
        background: #fff !important;
        color: var(--compass-text) !important;
    }

    [class*="st-key-next_"] button {
        border: 0 !important;
        background: linear-gradient(105deg, var(--compass-blue), var(--compass-violet)) !important;
        box-shadow: 0 10px 24px rgba(76, 92, 230, 0.23);
        color: white !important;
    }

    [class*="st-key-next_"] button:disabled {
        background: #dbe2ea !important;
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
        background: var(--compass-panel);
        border: 1px solid var(--compass-border);
        border-radius: 20px;
        padding: clamp(1.15rem, 2.4vw, 1.55rem);
        box-shadow: var(--compass-shadow);
    }

    .result-plane-title {
        margin: 0 0 0.65rem;
        color: var(--compass-text);
        font-size: clamp(1.2rem, 2.1vw, 1.45rem) !important;
        line-height: 1.28;
        letter-spacing: -0.02em;
    }

    .result-plane-summary {
        margin: 0 0 1.6rem;
        color: var(--compass-muted);
        font-size: 0.9rem;
        line-height: 1.55;
    }

    .result-label {
        margin: 0 0 0.4rem;
        color: var(--compass-cyan);
        font-size: 0.72rem;
        font-weight: 760;
        letter-spacing: 0.11em;
        text-transform: uppercase;
    }

    .result-profile {
        margin: 0 0 0.75rem;
        color: var(--compass-text);
        font-size: clamp(1.8rem, 3.3vw, 2.25rem) !important;
        line-height: 1.12;
        letter-spacing: -0.035em;
    }

    .result-interpretation {
        margin: 0 0 1rem;
        color: var(--compass-muted);
        font-size: 0.96rem;
        line-height: 1.62;
    }

    .result-intensity {
        display: inline-flex;
        flex-wrap: wrap;
        gap: 0.35rem;
        margin: 0 0 1.8rem;
        padding: 0.5rem 0.72rem;
        border: 1px solid var(--compass-border);
        border-radius: 10px;
        background: var(--compass-panel-soft);
        color: var(--compass-muted);
        font-size: 0.82rem;
        line-height: 1.35;
    }

    .result-explainer {
        margin: 0 0 1.25rem;
        padding-top: 1.25rem;
        border-top: 1px solid var(--compass-border);
    }

    .result-explainer h4 {
        margin: 0 0 0.55rem;
        color: var(--compass-text);
        font-size: 0.96rem;
    }

    .result-explainer p {
        margin: 0;
        color: var(--compass-muted);
        font-size: 0.85rem;
        line-height: 1.58;
    }

    .result-technical {
        margin: 0.65rem 0 0.2rem;
        color: var(--compass-muted);
        font-size: 0.72rem;
        line-height: 1.45;
        text-align: center;
    }

    .nuance-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 1rem;
        margin: 0.5rem 0 2rem;
    }

    .nuance-card {
        border: 1px solid var(--compass-border);
        border-radius: 18px;
        padding: 1rem 1.1rem;
        background: var(--compass-panel);
        box-shadow: var(--compass-shadow);
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
        color: var(--compass-muted);
    }

    .nuance-labels span:last-child { text-align: right; }

    .nuance-track {
        position: relative;
        height: 10px;
        margin: 0.55rem 0 0.7rem;
        border-radius: 999px;
        background: #dbe2ea;
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
        color: var(--compass-muted);
        font-size: 0.9rem;
    }

    .shared-banner,
    .share-card,
    .social-outro {
        width: min(100%, 920px);
        margin: 1.5rem auto;
        padding: clamp(1.25rem, 3vw, 1.8rem);
        border: 1px solid var(--compass-border);
        border-radius: 20px;
        background: var(--compass-panel);
        box-shadow: var(--compass-shadow);
    }

    .shared-badge {
        display: inline-block;
        margin-bottom: 0.75rem;
        padding: 0.35rem 0.65rem;
        border-radius: 999px;
        background: #e7effa;
        color: var(--compass-blue);
        font-size: 0.76rem;
        font-weight: 760;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    .shared-banner h1,
    .share-card h2,
    .social-outro h2 {
        margin: 0 0 0.55rem;
        color: var(--compass-text);
        letter-spacing: -0.025em;
    }

    .shared-banner p,
    .share-card p,
    .social-outro p {
        margin: 0.35rem 0;
        color: var(--compass-muted);
        line-height: 1.55;
    }

    .creator-links {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.75rem;
        margin: 1rem 0 1.35rem;
    }

    .creator-link {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        min-height: 58px;
        padding: 0.7rem 0.9rem;
        border: 1px solid var(--compass-border);
        border-radius: 13px;
        background: var(--compass-panel-soft);
        color: var(--compass-text) !important;
        text-decoration: none !important;
        transition: transform 140ms ease, border-color 140ms ease;
    }

    .creator-link:hover {
        transform: translateY(-1px);
        border-color: #9db2cf;
    }

    .creator-link:focus-visible {
        outline: 3px solid rgba(10, 67, 143, 0.24);
        outline-offset: 2px;
    }

    .creator-link strong,
    .creator-link small { display: block; }
    .creator-link small { color: var(--compass-muted); }
    .coming-soon { font-size: 0.86rem; }

    [class*="st-key-shared_cta_"] button {
        min-height: 58px;
        border: 0 !important;
        border-radius: 15px;
        background: linear-gradient(105deg, var(--compass-blue), var(--compass-violet)) !important;
        color: white !important;
        font-weight: 740;
        white-space: normal;
    }

    [class*="st-key-share_actions"] iframe {
        height: 150px !important;
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
        .cover-introduction {
            grid-template-columns: 1fr;
            gap: 0.75rem;
            margin-top: 1.4rem;
        }
        .intro-card {
            padding: 1.1rem;
        }
        .intro-card h2 {
            min-height: 0;
        }

        [class*="st-key-cover_logo"] {
            width: 95%;
        }

        .creator-links {
            grid-template-columns: 1fr;
        }

        [class*="st-key-share_actions"] iframe {
            height: 285px !important;
        }

        .question-title {
            margin: 1.35rem 0 1.25rem;
            font-size: clamp(22px, 6.2vw, 25px) !important;
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
        "demographic_step": 0,
        "age_range": None,
        "residence_region": None,
        "residence_district": None,
        "dem_district": None,
        "district_search": "",
        "demographic_record": {},
        "show_results": False,
        "analysis_complete": False,
        "email_submitted": False,
        "email_save_message": "",
        "response_uuid": None,
        "response_saved": False,
        "response_save_attempted": False,
        "response_save_message": "",
        "submitted_at_utc": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    if not st.session_state.response_uuid:
        st.session_state.response_uuid = str(uuid.uuid4())


def reset_questionnaire():
    """Regresa a la portada y elimina todas las respuestas del recorrido."""
    st.session_state.started = False
    st.session_state.current_question = 0
    st.session_state.answers = {}
    st.session_state.demographic_step = 0
    st.session_state.age_range = None
    st.session_state.residence_region = None
    st.session_state.residence_district = None
    st.session_state.dem_district = None
    st.session_state.district_search = ""
    st.session_state.pop("_dem_district", None)
    st.session_state.pop("_district_search", None)
    st.session_state.demographic_record = {}
    st.session_state.show_results = False
    st.session_state.analysis_complete = False
    st.session_state.email_submitted = False
    st.session_state.email_save_message = ""
    st.session_state.response_uuid = str(uuid.uuid4())
    st.session_state.response_saved = False
    st.session_state.response_save_attempted = False
    st.session_state.response_save_message = ""
    st.session_state.submitted_at_utc = None


def start_own_questionnaire():
    """Sale de una vista compartida y prepara un recorrido completamente nuevo."""
    reset_questionnaire()
    st.query_params.clear()


def is_valid_email(email):
    """Comprueba solamente que el correo tenga una estructura razonable."""
    return bool(
        len(email) <= 254
        and re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)
    )


def format_decimal_es(value):
    """Muestra un número con un decimal y coma, sin cambiar su valor."""
    return f"{value:.1f}".replace(".", ",")


def describe_intensity(intensity):
    """Añade una etiqueta visual al porcentaje calculado previamente."""
    if intensity < 25:
        return "Muy cercana al centro"
    if intensity < 50:
        return "Moderada"
    if intensity < 75:
        return "Definida"
    return "Muy definida"


def result_summary_html(title, summary, profile, interpretation, intensity, explanation):
    """Ordena el texto visible de un plano sin intervenir en sus cálculos."""
    return (
        f'<h2 class="result-plane-title">{html.escape(title)}</h2>'
        f'<p class="result-plane-summary">{html.escape(summary)}</p>'
        '<p class="result-label">Tu resultado</p>'
        f'<h3 class="result-profile">{html.escape(profile)}</h3>'
        f'<p class="result-interpretation">{html.escape(interpretation)}</p>'
        '<p class="result-intensity">'
        "Intensidad de tu orientación: "
        f"{format_decimal_es(intensity)} % · {describe_intensity(intensity)}"
        "</p>"
        '<div class="result-explainer">'
        "<h4>¿Qué mide este plano?</h4>"
        f"<p>{html.escape(explanation)}</p>"
        "</div>"
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


def logo_data_uri():
    """Lee el logo local sin cambiar sus píxeles ni depender de una URL externa."""
    encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def render_cover():
    """Muestra la portada antes de revelar el cuestionario."""
    with st.container(key="cover_card"):
        st.markdown(
            f"""
            <div class="cover-shell">
                <div class="st-key-cover_logo">
                    <img src="{logo_data_uri()}" alt="{html.escape(LOGO_ALT)}">
                </div>
                <div class="cover-introduction">
                    <div class="intro-card">
                        <span class="intro-icon" aria-hidden="true">
                            <svg viewBox="0 0 24 24">
                                <circle cx="12" cy="12" r="8"></circle>
                                <path d="m14.8 9.2-1.7 3.9-3.9 1.7 1.7-3.9 3.9-1.7Z"></path>
                            </svg>
                        </span>
                        <h2>¿Qué es la Brújula Política Panameña?</h2>
                        <p>
                            La Brújula Política Panameña es un modelo de
                            orientación política que identifica el perfil con el
                            que más se alinean tus ideas sobre el Estado, la
                            sociedad y la organización del país.
                        </p>
                        <p>
                            Responderás únicamente 24 preguntas y al finalizar
                            recibirás un resultado inmediato acompañado de una
                            breve interpretación.
                        </p>
                    </div>
                    <div class="intro-card">
                        <span class="intro-icon" aria-hidden="true">
                            <svg viewBox="0 0 24 24">
                                <rect x="5" y="10" width="14" height="10" rx="2"></rect>
                                <path d="M8 10V7a4 4 0 0 1 8 0v3"></path>
                            </svg>
                        </span>
                        <h2>¿Es privado?</h2>
                        <p>
                            Tus respuestas son anónimas. No solicitamos tu
                            nombre, cédula ni dirección. Tu rango de edad y
                            distrito se utilizarán únicamente para análisis
                            estadísticos agrupados.
                        </p>
                        <p>
                            En caso decidas dejar un correo para recibir
                            noticias del movimiento, el correo que dejes
                            voluntariamente no se vincula con tu resultado.
                        </p>
                    </div>
                    <div class="intro-card">
                        <span class="intro-icon" aria-hidden="true">
                            <svg viewBox="0 0 24 24">
                                <circle cx="9" cy="8" r="3"></circle>
                                <circle cx="17" cy="9" r="2"></circle>
                                <path d="M3.5 19a5.5 5.5 0 0 1 11 0"></path>
                                <path d="M14 15.5a4 4 0 0 1 6.5 3.5"></path>
                            </svg>
                        </span>
                        <h2>¿Quiénes somos?</h2>
                        <p>
                            Este proyecto fue creado por Pablo García de Paredes
                            y Mark Harrick con el propósito de contribuir a una
                            conversación pública más reflexiva, respetuosa e
                            informada entre los panameños.
                        </p>
                        <p>
                            Creemos que una mejor democracia comienza cuando
                            entendemos primero nuestras propias ideas.
                        </p>
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
                next_label = "Continuar →" if final_question else "Siguiente →"

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
                            st.session_state.demographic_step = 1
                            st.rerun()
                    else:
                        st.session_state.current_question += 1
                        st.rerun()


def demographic_progress(step):
    """Muestra un contador propio sin convertir los datos en q25 o q26."""
    percentage = step * 50
    st.markdown(
        '<div class="question-shell">'
        '<div class="question-meta">'
        f"<span>Datos finales · {step} de 2</span>"
        f'<span class="question-percent">{percentage}%</span>'
        "</div>"
        '<div class="progress-track" role="progressbar" '
        'aria-label="Progreso de los datos finales" aria-valuemin="0" '
        f'aria-valuemax="2" aria-valuenow="{step}">'
        f'<div class="progress-fill" style="width:{percentage}%"></div>'
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )


def render_age_range():
    """Solicita un rango general de edad, separado de las respuestas políticas."""
    selected_age = st.session_state.age_range

    with st.container(key="question_card_demographic_age"):
        demographic_progress(1)
        st.markdown(
            """
            <section class="demographic-intro">
                <h1>Dos datos para entender mejor el mapa</h1>
                <p>
                    Antes de mostrarte tu resultado, necesitamos dos datos
                    generales. Nos ayudarán a analizar cómo cambian las ideas
                    políticas entre generaciones y territorios. No solicitamos
                    tu nombre, cédula ni dirección.
                </p>
            </section>
            <h1 class="question-title">
                ¿En qué rango de edad te encuentras?
            </h1>
            """,
            unsafe_allow_html=True,
        )

        for index, age_range in enumerate(AGE_RANGES):
            is_selected = selected_age == age_range
            visible_label = age_range + ("  ✓ Seleccionada" if is_selected else "")
            if st.button(
                visible_label,
                key=f"{AGE_FIELD_ID}_{index}",
                type="primary" if is_selected else "secondary",
                use_container_width=True,
            ):
                st.session_state.age_range = age_range
                st.rerun()

        if selected_age is None:
            st.caption("Selecciona tu rango de edad para continuar.")

        with st.container(key="navigation"):
            back_column, next_column = st.columns(2, gap="small")
            with back_column:
                if st.button(
                    "← Atrás",
                    use_container_width=True,
                    key="back_demographic_age",
                ):
                    st.session_state.demographic_step = 0
                    st.session_state.current_question = len(QUESTIONS) - 1
                    st.rerun()
            with next_column:
                if st.button(
                    "Siguiente →",
                    type="primary",
                    disabled=not is_valid_age_range(selected_age),
                    use_container_width=True,
                    key="next_demographic_age",
                ):
                    st.session_state.demographic_step = 2
                    st.rerun()


def persist_district_search():
    """Copia la búsqueda fuera de la clave temporal del widget."""
    st.session_state.district_search = st.session_state._district_search


def persist_district_selection():
    """Conserva la opción territorial aunque el usuario vuelva a otra pantalla."""
    selected_option = st.session_state._dem_district
    st.session_state.dem_district = selected_option
    if selected_option is not None:
        st.session_state.residence_region = selected_option.region
        st.session_state.residence_district = selected_option.district


def render_district():
    """Solicita un distrito oficial mediante búsqueda tolerante a tildes."""
    if "_district_search" not in st.session_state:
        st.session_state._district_search = st.session_state.district_search
    if "_dem_district" not in st.session_state:
        st.session_state._dem_district = st.session_state.dem_district

    with st.container(key="question_card_demographic_district"):
        demographic_progress(2)
        st.markdown(
            """
            <h1 class="question-title">
                ¿En qué distrito resides actualmente?
            </h1>
            <p class="demographic-help">
                Escribe el nombre o búscalo en la lista. La provincia o comarca
                aparece junto al distrito para evitar confusiones.
            </p>
            """,
            unsafe_allow_html=True,
        )

        query = st.text_input(
            "Buscar distrito",
            placeholder="Puedes escribir el nombre sin tildes",
            key="_district_search",
            on_change=persist_district_search,
        )
        filtered_options = filter_residence_options(query)
        current_option = st.session_state.get(DISTRICT_FIELD_ID)
        if current_option is not None and current_option not in filtered_options:
            filtered_options = (current_option,) + filtered_options

        st.selectbox(
            "Distrito de residencia",
            options=filtered_options,
            index=None,
            placeholder="Escribe o selecciona tu distrito",
            format_func=lambda option: option.label,
            key=f"_{DISTRICT_FIELD_ID}",
            on_change=persist_district_selection,
        )
        selected_option = st.session_state.dem_district

        valid_selection = (
            is_valid_residence_option(selected_option)
            and st.session_state.residence_region is not None
            and st.session_state.residence_district is not None
        )
        if not filtered_options:
            st.info("No encontramos coincidencias. Prueba con otra palabra.")
        if not valid_selection:
            st.caption("Selecciona tu distrito de residencia para continuar.")

        with st.container(key="navigation"):
            back_column, next_column = st.columns(2, gap="small")
            with back_column:
                if st.button(
                    "← Atrás",
                    use_container_width=True,
                    key="back_demographic_district",
                ):
                    st.session_state.demographic_step = 1
                    st.rerun()
            with next_column:
                if st.button(
                    "Ver mis resultados",
                    type="primary",
                    disabled=not valid_selection,
                    use_container_width=True,
                    key="finish_demographics",
                ):
                    st.session_state.demographic_record = build_demographic_record(
                        st.session_state.age_range,
                        st.session_state.residence_region,
                        st.session_state.residence_district,
                    )
                    st.session_state.show_results = True
                    st.session_state.analysis_complete = False
                    st.rerun()


def render_demographics():
    """Enruta las dos pantallas finales manteniendo una pregunta por pantalla."""
    if st.session_state.demographic_step == 1:
        render_age_range()
    else:
        render_district()


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
                    Gracias por participar
                </h2>
                <p class="subscription-copy">
                    Esperamos que este resultado te haya ayudado a comprender
                    mejor tu manera de pensar sobre la política.
                </p>
                <p class="subscription-copy">
                    La Brújula Política Panameña es un proyecto en desarrollo.
                    Si deseas recibir futuras encuestas y nuevos contenidos,
                    puedes dejarnos voluntariamente tu correo.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.session_state.email_submitted:
            st.success(st.session_state.email_save_message)
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
                else:
                    save_result = save_subscriber_email(normalized_email)
                    if save_result.success:
                        st.session_state.email_submitted = True
                        st.session_state.email_save_message = save_result.message
                        st.rerun()
                    else:
                        st.error(save_result.message)

            st.markdown(
                """
                <p class="subscription-note">
                    No compartiremos tu correo con terceros.
                </p>
                """,
                unsafe_allow_html=True,
            )


def render_patreon_support():
    """Invita a apoyar el proyecto mediante un enlace externo y estático."""
    with st.container(key="patreon_support_card"):
        st.markdown(
            """
            <section class="patreon-content">
                <h2 class="patreon-heading">
                    <span class="patreon-icon" aria-hidden="true">🧭</span>
                    Haz que Brújula siga creciendo
                </h2>
                <p class="patreon-copy">
                    Brújula Democrática es una iniciativa independiente. Tu apoyo
                    nos ayuda a mantener la plataforma, desarrollar nuevos
                    cuestionarios y convertir las respuestas anónimas en análisis
                    abiertos sobre cómo pensamos en Panamá.
                </p>
                <p class="patreon-note">
                    El apoyo es completamente voluntario y no cambia tu resultado
                    ni el acceso a la herramienta.
                </p>
            </section>
            """,
            unsafe_allow_html=True,
        )
        st.link_button(
            "Hazte miembro en Patreon",
            PATREON_URL,
            width="stretch",
        )


def render_shared_cta(key):
    """Invita a iniciar un cuestionario propio desde un resultado de solo lectura."""
    st.button(
        (
            "Completa tu cuestionario para ver dónde te ubicas tú "
            "en la Brújula Democrática"
        ),
        on_click=start_own_questionnaire,
        type="primary",
        use_container_width=True,
        key=f"shared_cta_{key}",
    )


def render_share_section(scores, political_name, social_name):
    """Muestra exclusivamente WhatsApp, Facebook e Instagram para compartir."""
    share_url = build_share_url(PUBLIC_APP_URL, scores)
    message = build_social_message(political_name, social_name, share_url)
    whatsapp_url = whatsapp_share_url(message)
    facebook_url = facebook_share_url(share_url)

    st.markdown(
        """
        <section class="share-card">
            <h2>Comparte tu resultado</h2>
            <p>
                Comparte tu perfil con tus amigos y descubre si terminan cerca
                de ti o en otro rincón de la Brújula Democrática.
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    escaped_message = json.dumps(message, ensure_ascii=False)
    escaped_url = json.dumps(share_url)
    escaped_whatsapp = html.escape(whatsapp_url, quote=True)
    escaped_facebook = html.escape(facebook_url, quote=True)
    with st.container(key="share_actions"):
        components.html(
            f"""
        <style>
            * {{ box-sizing: border-box; }}
            body {{
                margin: 0;
                color: #102a50;
                font-family: Inter, ui-sans-serif, system-ui, -apple-system,
                    BlinkMacSystemFont, "Segoe UI", sans-serif;
            }}
            .share-actions {{
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 12px;
            }}
            .share-button {{
                min-height: 54px;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 12px 14px;
                border: 1px solid #d8dee8;
                border-radius: 13px;
                color: #102a50;
                background: #fff;
                font-size: 15px;
                font-weight: 720;
                line-height: 1.2;
                text-align: center;
                text-decoration: none;
                cursor: pointer;
            }}
            .whatsapp {{ border-color: #8bd9aa; background: #effbf4; }}
            .facebook {{ border-color: #a9bee5; background: #f1f5fc; }}
            .instagram {{ border-color: #d8b0d8; background: #fbf2fb; }}
            .share-button:hover {{ filter: brightness(0.98); transform: translateY(-1px); }}
            .share-button:focus-visible {{
                outline: 3px solid rgba(10, 67, 143, 0.25);
                outline-offset: 2px;
            }}
            .copy-button {{
                display: block;
                margin: 13px auto 0;
                border: 0;
                background: transparent;
                color: #526174;
                font: inherit;
                font-size: 13px;
                text-decoration: underline;
                cursor: pointer;
            }}
            #share-status {{
                min-height: 22px;
                margin: 8px 0 0;
                color: #526174;
                font-size: 13px;
                text-align: center;
            }}
            @media (max-width: 640px) {{
                .share-actions {{ grid-template-columns: 1fr; }}
                .share-button {{ min-height: 58px; }}
            }}
        </style>
        <div class="share-actions">
            <a class="share-button whatsapp" href="{escaped_whatsapp}"
               target="_blank" rel="noopener noreferrer">
                Compartir por WhatsApp
            </a>
            <a class="share-button facebook" href="{escaped_facebook}"
               target="_blank" rel="noopener noreferrer">
                Compartir en Facebook
            </a>
            <button class="share-button instagram" type="button"
                    onclick="shareInstagram()">
                Compartir en Instagram
            </button>
        </div>
        <button class="copy-button" type="button" onclick="copyLink()">
            Copiar enlace del resultado
        </button>
        <p id="share-status" role="status" aria-live="polite"></p>
        <script>
            const message = {escaped_message};
            const shareUrl = {escaped_url};
            const status = document.getElementById("share-status");

            async function copyText(text) {{
                try {{
                    await navigator.clipboard.writeText(text);
                }} catch (_) {{
                    const area = document.createElement("textarea");
                    area.value = text;
                    area.style.position = "fixed";
                    area.style.opacity = "0";
                    document.body.appendChild(area);
                    area.select();
                    document.execCommand("copy");
                    area.remove();
                }}
            }}

            async function shareInstagram() {{
                if (navigator.share) {{
                    try {{
                        await navigator.share({{
                            title: "Mi resultado en Brújula Democrática",
                            text: message,
                            url: shareUrl
                        }});
                        status.textContent = "Elige Instagram para compartir tu resultado.";
                        resizeFrame();
                        return;
                    }} catch (error) {{
                        if (error && error.name === "AbortError") return;
                    }}
                }}
                await copyText(message);
                status.textContent =
                    "Tu resultado fue copiado. Abre Instagram y pégalo en tu historia, publicación o mensaje.";
                resizeFrame();
            }}

            async function copyLink() {{
                await copyText(shareUrl);
                status.textContent = "Enlace copiado.";
                resizeFrame();
            }}

            function resizeFrame() {{
                window.parent.postMessage({{
                    isStreamlitMessage: true,
                    type: "streamlit:setFrameHeight",
                    height: document.documentElement.scrollHeight
                }}, "*");
            }}

            new ResizeObserver(resizeFrame).observe(document.body);
            resizeFrame();
        </script>
            """,
            height=150,
            scrolling=False,
        )


def render_social_outro():
    """Muestra redes reales y oculta correctamente las cuentas aún inexistentes."""
    official_links = []
    if SOCIAL_LINKS["brujula_instagram"]:
        official_links.append(
            ("Instagram", SOCIAL_LINKS["brujula_instagram"])
        )
    if SOCIAL_LINKS["brujula_facebook"]:
        official_links.append(
            ("Facebook", SOCIAL_LINKS["brujula_facebook"])
        )

    official_html = "".join(
        (
            f'<a class="creator-link" href="{html.escape(url, quote=True)}" '
            'target="_blank" rel="noopener noreferrer">'
            f"<span><strong>{html.escape(name)}</strong>"
            "<small>Brújula Democrática</small></span></a>"
        )
        for name, url in official_links
    )
    if not official_html:
        official_html = (
            '<p class="coming-soon">'
            "Redes oficiales de Brújula Democrática — próximamente"
            "</p>"
        )

    st.markdown(
        f"""
        <section class="social-outro">
            <h2>Sigue el proyecto y a sus creadores</h2>
            <p><strong>Creadores de Brújula Democrática</strong></p>
            <div class="creator-links">
                <a class="creator-link"
                   href="{SOCIAL_LINKS["pablo_instagram"]}"
                   target="_blank" rel="noopener noreferrer">
                    <span aria-hidden="true">◎</span>
                    <span><strong>Pablo García de Paredes</strong>
                    <small>@pablo.garciadeparedes</small></span>
                </a>
                <a class="creator-link"
                   href="{SOCIAL_LINKS["mark_instagram"]}"
                   target="_blank" rel="noopener noreferrer">
                    <span aria-hidden="true">◎</span>
                    <span><strong>Mark Harricka</strong>
                    <small>@markharricka</small></span>
                </a>
            </div>
            <p><strong>Redes de Brújula Democrática</strong></p>
            {official_html}
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_result_report(scores, shared=False):
    """Dibuja el mismo informe para el participante o para un enlace compartido."""

    x = scores["x"]
    y = scores["y"]
    classification = classify_position(x, y)

    social_x = scores["familia"]
    social_y = scores["modernidad"]
    social_classification = classify_social_position(social_x, social_y)

    if shared:
        st.markdown(
            """
            <section class="shared-banner">
                <span class="shared-badge">Resultado compartido</span>
                <h1>Un amigo compartió contigo su resultado</h1>
                <p>
                    Explora su ubicación en la Brújula Democrática y luego
                    descubre dónde te ubicas tú.
                </p>
            </section>
            """,
            unsafe_allow_html=True,
        )
        render_shared_cta("top")
    else:
        st.title("Tu perfil político panameño")
        st.write(
            "Dos planos para entender cómo ves al Estado, la política y la sociedad."
        )

    with st.container(key="results_grid"):
        political_column, social_column = st.columns(2, gap="large")

        with political_column:
            st.markdown(
                result_summary_html(
                    title="1. ¿Cómo prefieres que se gobierne el país?",
                    summary=(
                        "Este plano muestra qué valoras más al ejercer el "
                        "gobierno: la capacidad técnica, las reglas y la gestión "
                        "pública, o la cercanía política, la representación y la "
                        "resolución directa de problemas."
                    ),
                    profile=classification["name"],
                    interpretation=describe(classification),
                    intensity=classification["intensity"],
                    explanation=(
                        "Este plano representa dos aspectos de tu manera de "
                        "entender el gobierno. En la dirección horizontal compara "
                        "los favores y contactos con el mérito y la capacidad. En "
                        "la dirección vertical compara la preferencia por un "
                        "gobierno pequeño con un gobierno activo."
                    ),
                ),
                unsafe_allow_html=True,
            )

            figure = create_map(x, y)
            st.pyplot(figure, use_container_width=True)
            plt.close(figure)
            st.markdown(
                '<p class="result-technical">'
                f"Datos técnicos: X = {format_decimal_es(x)} · "
                f"Y = {format_decimal_es(y)}"
                "</p>",
                unsafe_allow_html=True,
            )

        with social_column:
            st.markdown(
                result_summary_html(
                    title="2. ¿Cómo entiendes la familia y el cambio social?",
                    summary=(
                        "Este plano muestra cómo combinas la tradición familiar "
                        "y moral con la autonomía personal, y la costumbre y la "
                        "autoridad religiosa con la ciencia y la modernización."
                    ),
                    profile=social_classification["name"],
                    interpretation=describe_social(social_classification),
                    intensity=social_classification["intensity"],
                    explanation=(
                        "En la dirección horizontal, este plano compara la "
                        "tradición moral y la familia tradicional con la autonomía "
                        "personal y la diversidad. En la dirección vertical "
                        "compara la costumbre, la religión y la autoridad moral "
                        "con la ciencia, la secularidad y la modernización."
                    ),
                ),
                unsafe_allow_html=True,
            )

            social_figure = create_social_map(social_x, social_y)
            st.pyplot(social_figure, use_container_width=True)
            plt.close(social_figure)
            st.markdown(
                '<p class="result-technical">'
                f"Datos técnicos: X = {format_decimal_es(social_x)} · "
                f"Y = {format_decimal_es(social_y)}"
                "</p>",
                unsafe_allow_html=True,
            )

    st.subheader("Tus matices")
    st.markdown(
        '<div class="nuance-grid">'
        + nuance_card_html("seguridad", scores["seguridad"])
        + nuance_card_html("partidismo", scores["partidismo"])
        + "</div>",
        unsafe_allow_html=True,
    )

    if shared:
        render_shared_cta("bottom")
        render_social_outro()
    else:
        render_patreon_support()
        render_subscription()
        render_share_section(
            scores,
            classification["name"],
            social_classification["name"],
        )
        render_social_outro()
        st.button(
            "Volver a realizar el cuestionario",
            on_click=reset_questionnaire,
            type="primary",
            use_container_width=True,
            key="restart_button",
        )


def build_anonymous_response_record(scores):
    """Ordena los datos ya calculados sin añadir información identificable."""
    political = classify_position(scores["x"], scores["y"])
    social = classify_social_position(scores["familia"], scores["modernidad"])
    demographics = st.session_state.demographic_record
    if not st.session_state.submitted_at_utc:
        st.session_state.submitted_at_utc = datetime.now(timezone.utc).isoformat()

    return {
        "response_uuid": st.session_state.response_uuid,
        "submitted_at_utc": st.session_state.submitted_at_utc,
        "app_version": APP_VERSION,
        "age_range": demographics.get("age_range", ""),
        "residence_region": demographics.get("residence_region", ""),
        "residence_district": demographics.get("residence_district", ""),
        **dict(st.session_state.answers),
        "political_x": scores["x"],
        "political_y": scores["y"],
        "political_classification": political["name"],
        "political_profile": political["profile"] or "",
        "political_position_type": political["position_type"],
        "political_intensity": political["intensity"],
        "social_x": scores["familia"],
        "social_y": scores["modernidad"],
        "social_classification": social["name"],
        "social_profile": social["profile"] or "",
        "social_position_type": social["position_type"],
        "social_intensity": social["intensity"],
        "security_score": scores["seguridad"],
        "partisanship_score": scores["partidismo"],
    }


def save_current_response(scores):
    """Intenta guardar una sola vez; un fallo queda disponible para reintento."""
    if st.session_state.response_saved or st.session_state.response_save_attempted:
        return
    result = save_anonymous_response(build_anonymous_response_record(scores))
    apply_response_save_result(st.session_state, result)


def render_response_save_status(scores):
    """Informa del registro sin ocultar ni condicionar el resultado político."""
    if st.session_state.response_saved:
        st.success(st.session_state.response_save_message)
        return

    st.warning(st.session_state.response_save_message)
    if st.button("Intentar registrar nuevamente", key="retry_response_save"):
        st.session_state.response_save_attempted = False
        save_current_response(scores)
        st.rerun()


def render_results():
    """Calcula la sesión actual y delega su presentación sin alterar la fórmula."""
    numeric_answers = dict(st.session_state.answers)
    scores = calculate_scores(numeric_answers)
    save_current_response(scores)
    render_response_save_status(scores)
    render_result_report(scores)


def shared_result_from_query():
    """Obtiene un resultado compartido válido o limpia silenciosamente la URL."""
    encoded = st.query_params.get("r")
    if not encoded:
        return None
    result = decode_result(encoded)
    if result is None:
        st.query_params.clear()
    return result


initialize_state()

shared_result = shared_result_from_query()

if shared_result is not None:
    render_result_report(shared_result, shared=True)
elif not st.session_state.started:
    render_cover()
elif not st.session_state.show_results:
    if st.session_state.demographic_step:
        render_demographics()
    else:
        render_question()
elif not st.session_state.analysis_complete:
    render_analysis()
else:
    render_results()
