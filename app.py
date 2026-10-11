"""
Controle de Indicações - Aplicativo Principal

Sistema para controle de cursos militares, indicações e seus prazos (SIAT, SIGAD, OM).
Interface redesenhada no conceito 'fichas de progresso' (flight progress strips),
sem emojis decorativos, com linguagem direta e padrão visual austero.
"""

import html
import re
from pathlib import Path
from typing import Dict, List, Optional
import streamlit as st
import pandas as pd
from datetime import date

# =============================================================================
# CONFIGURAÇÕES E CONSTANTES
# =============================================================================

from config import Settings, Messages

# =============================================================================
# LOGGER
# =============================================================================

from utils.logger import get_logger

logger = get_logger(__name__)

# =============================================================================
# COMPONENTES UI
# =============================================================================

from components import (
    page_header,
    page_title,
    show_success,
    show_error,
    show_warning,
    show_info,
    render_faixa_curso,
    render_cabecalho_cursos,
    render_form_novo_curso,
    render_form_editar_curso,
    render_topbar,
    render_sidebar,
    CalendarView,
    plural,
    limpar_confirmacoes_exclusao,
)

# =============================================================================
# MANAGERS E VALIDADORES
# =============================================================================

from data_manager import DataManager
from dashboard import Dashboard
from backup_manager import BackupManager
from json_import import JSONImporter
from managers.auth_manager import AuthManager
from utils.validators import parse_data, limpar_valor, curso_concluido


# =============================================================================
# CARREGAMENTO DE RECURSOS E SESSÃO
# =============================================================================

def init_theme() -> str:
    """Inicializa e sincroniza a escolha do tema com query params e session_state."""
    if "tema" not in st.session_state:
        qp_tema = st.query_params.get("tema")
        if qp_tema and str(qp_tema).lower() in ["escuro", "dark"]:
            st.session_state["tema"] = "Escuro"
        else:
            st.session_state["tema"] = "Claro"
        st.query_params["tema"] = st.session_state["tema"]
    else:
        qp_tema = st.query_params.get("tema")
        if qp_tema and str(qp_tema).capitalize() in ["Claro", "Escuro"] and st.session_state["tema"] != str(qp_tema).capitalize():
            st.session_state["tema"] = str(qp_tema).capitalize()
    tema_atual = st.session_state.get("tema", "Claro")
    if st.session_state.get("tema_switch") != tema_atual:
        st.session_state["tema_switch"] = tema_atual
    return tema_atual


def get_theme_css(tema: str = "Claro") -> str:
    """Gera bloco CSS com os tokens e sobreposições para o tema ativo."""
    eh_escuro = (tema == "Escuro")

    if eh_escuro:
        tokens = """
  --paper: #121A23;
  --surface: #1A2430;
  --ink: #E6ECF2;
  --ink-soft: #9AA8B6;
  --line: #2C3946;
  --blue: #5B95E0;
  --blue-tint: #15253C;
  --late: #F0705F;
  --late-tint: #3A1F1E;
  --soon: #F2B33D;
  --soon-tint: #3A2E14;
  --ok: #4FBF8B;
  --ok-tint: #173326;
  --none: #6B7A89;
"""
        btn_primary_bg = "#2F6BB8"
        btn_primary_hover = "#3A7AC9"
        scrollbar_thumb = "#3A4856"
        scrollbar_thumb_hover = "#4D5E6F"
    else:
        tokens = """
  --paper: #EDF1F5;
  --surface: #FFFFFF;
  --ink: #1A2633;
  --ink-soft: #5A6878;
  --line: #D5DCE4;
  --blue: #1F4E8C;
  --blue-tint: #E3ECF7;
  --late: #C0392B;
  --late-tint: #FBE9E7;
  --soon: #945B00;
  --soon-tint: #FDF3DC;
  --ok: #246B4C;
  --ok-tint: #E4F2EB;
  --none: #9AA6B2;
"""
        btn_primary_bg = "#1F4E8C"
        btn_primary_hover = "#183F72"
        scrollbar_thumb = "#B8C3CF"
        scrollbar_thumb_hover = "#8C99A8"

    return f"""
:root {{
{tokens}
}}

/* Transição do corpo: 120ms para cores, desativada sob prefers-reduced-motion */
body, .stApp {{
  background-color: var(--paper) !important;
  color: var(--ink) !important;
  transition: background-color 120ms ease, color 120ms ease;
}}

@media (prefers-reduced-motion: reduce) {{
  body, .stApp {{
    transition: none !important;
  }}
}}

/* Superfícies e blocos principais */
.main,
.main .block-container,
[data-testid="stMainBlockContainer"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {{
  background-color: var(--paper) !important;
  color: var(--ink) !important;
}}

[data-testid="stPopoverBody"] {{
  background-color: var(--surface) !important;
  border: 1px solid var(--line) !important;
  border-color: var(--line) !important;
  color: var(--ink) !important;
  border-radius: 8px !important;
  padding: 16px !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15) !important;
}}

[data-testid="stPopoverBody"] * {{
  color: var(--ink);
}}

.popover-user-name {{
  font-size: 15px !important;
  font-weight: 600 !important;
  color: var(--ink) !important;
  line-height: 1.3 !important;
  margin-bottom: 2px !important;
  text-align: left !important;
}}

[data-testid="stPopoverBody"] [data-testid="stCaptionContainer"],
[data-testid="stPopoverBody"] [data-testid="stCaptionContainer"] p {{
  font-size: 13px !important;
  color: var(--ink-soft) !important;
  line-height: 1.3 !important;
  margin-top: 0 !important;
  margin-bottom: 12px !important;
  text-align: left !important;
}}

/* Popover menu items (Administração items and user Sair button) */
[data-testid="stPopoverBody"] button,
[data-testid="stPopoverBody"] button[kind="tertiary"],
[data-testid="stPopoverBody"] [data-testid*="stBaseButton-tertiary"] {{
  justify-content: flex-start !important;
  text-align: left !important;
  width: 100% !important;
  height: 40px !important;
  min-height: 40px !important;
  padding: 0 12px !important;
  border: none !important;
  background: transparent !important;
  background-color: transparent !important;
  color: var(--ink) !important;
  border-radius: 6px !important;
  gap: 8px !important;
}}

[data-testid="stPopoverBody"] button:hover,
[data-testid="stPopoverBody"] button[kind="tertiary"]:hover,
[data-testid="stPopoverBody"] [data-testid*="stBaseButton-tertiary"]:hover {{
  background: var(--blue-tint) !important;
  background-color: var(--blue-tint) !important;
  color: var(--ink) !important;
}}

[data-testid="stPopoverBody"] button [data-testid="stMarkdownContainer"],
[data-testid="stPopoverBody"] button [data-testid="stMarkdownContainer"] p,
[data-testid="stPopoverBody"] button > div,
[data-testid="stPopoverBody"] button div {{
  justify-content: flex-start !important;
  text-align: left !important;
  display: flex !important;
  align-items: center !important;
  color: inherit !important;
}}

[data-testid="stPopoverBody"] button:hover *,
[data-testid="stPopoverBody"] button:hover p,
[data-testid="stPopoverBody"] button:hover [data-testid="stIconMaterial"] {{
  color: var(--ink) !important;
  fill: currentColor !important;
}}

[data-testid="stPopoverBody"] button [data-testid="stIconMaterial"] {{
  color: inherit !important;
  fill: currentColor !important;
}}

/* Popover segmented control override */
[data-testid="stPopoverBody"] [data-testid="stButtonGroup"] {{
  width: 100% !important;
  margin: 4px 0 !important;
}}

[data-testid="stPopoverBody"] [data-testid="stButtonGroup"] > div {{
  width: 100% !important;
  background-color: var(--surface) !important;
  border: 1px solid var(--line) !important;
  display: flex !important;
}}

[data-testid="stPopoverBody"] [data-testid="stButtonGroup"] button {{
  justify-content: center !important;
  text-align: center !important;
  height: 38px !important;
  min-height: 38px !important;
  padding: 0 12px !important;
  font-size: 14px !important;
  width: auto !important;
  flex: 1 1 0 !important;
  border: 1px solid var(--line) !important;
}}

[data-testid="stPopoverBody"] [data-testid="stButtonGroup"] button [data-testid="stMarkdownContainer"],
[data-testid="stPopoverBody"] [data-testid="stButtonGroup"] button [data-testid="stMarkdownContainer"] p,
[data-testid="stPopoverBody"] [data-testid="stButtonGroup"] button > div {{
  justify-content: center !important;
  text-align: center !important;
}}

[data-testid="stPopoverBody"] [data-testid="stButtonGroup"] button[aria-checked="false"] {{
  background: var(--surface) !important;
  background-color: var(--surface) !important;
  color: var(--ink) !important;
  border: 1px solid var(--line) !important;
}}

[data-testid="stPopoverBody"] [data-testid="stButtonGroup"] button[aria-checked="false"]:hover {{
  background: var(--blue-tint) !important;
  background-color: var(--blue-tint) !important;
  color: var(--ink) !important;
}}

[data-testid="stPopoverBody"] [data-testid="stButtonGroup"] button[aria-checked="true"],
[data-testid="stPopoverBody"] [data-testid="stButtonGroup"] button[data-selected="true"] {{
  background: var(--blue-tint) !important;
  background-color: var(--blue-tint) !important;
  color: var(--blue) !important;
  border: 1px solid var(--blue) !important;
  font-weight: 600 !important;
}}

[data-testid="stPopoverBody"] [data-testid="stButtonGroup"] button[aria-checked="true"] *,
[data-testid="stPopoverBody"] [data-testid="stButtonGroup"] button[aria-checked="true"] p,
[data-testid="stPopoverBody"] [data-testid="stButtonGroup"] button[aria-checked="true"] span,
[data-testid="stPopoverBody"] [data-testid="stButtonGroup"] button[aria-checked="true"] [data-testid="stIconMaterial"],
[data-testid="stPopoverBody"] [data-testid="stButtonGroup"] button[data-selected="true"] *,
[data-testid="stPopoverBody"] [data-testid="stButtonGroup"] button[data-selected="true"] p,
[data-testid="stPopoverBody"] [data-testid="stButtonGroup"] button[data-selected="true"] span,
[data-testid="stPopoverBody"] [data-testid="stButtonGroup"] button[data-selected="true"] [data-testid="stIconMaterial"] {{
  color: var(--blue) !important;
  fill: var(--blue) !important;
}}

/* Textos e tipografia geral */
p, span, label, h1, h2, h3, h4, h5, h6,
[data-testid="stMarkdownContainer"] p,
[data-testid="stText"],
[data-testid="stWidgetLabel"] label,
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] {{
  color: var(--ink) !important;
}}

[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p,
.page-helper,
.login-helper,
.strip-turma,
.strip-col-om,
.total-label,
small {{
  color: var(--ink-soft) !important;
}}

/* Botões primários */
button[kind="primary"],
[data-testid="baseButton-primary"],
[data-testid="stBaseButton-primary"],
[data-testid="stBaseButton-primaryFormSubmit"],
[data-testid="stFormSubmitButton"] > button,
[data-testid="stFormSubmitButton"] button {{
  background-color: {btn_primary_bg} !important;
  color: #FFFFFF !important;
  border: 1px solid {btn_primary_bg} !important;
}}

button[kind="primary"]:hover,
[data-testid="baseButton-primary"]:hover,
[data-testid="stBaseButton-primary"]:hover,
[data-testid="stBaseButton-primaryFormSubmit"]:hover,
[data-testid="stFormSubmitButton"] > button:hover,
[data-testid="stFormSubmitButton"] button:hover {{
  background-color: {btn_primary_hover} !important;
  border-color: {btn_primary_hover} !important;
  color: #FFFFFF !important;
}}

button[kind="primary"] *,
[data-testid="baseButton-primary"] *,
[data-testid="stBaseButton-primary"] *,
[data-testid="stBaseButton-primaryFormSubmit"] *,
[data-testid="stFormSubmitButton"] button * {{
  color: #FFFFFF !important;
  fill: #FFFFFF !important;
}}

/* Botões secundários */
button[kind="secondary"],
[data-testid="baseButton-secondary"],
[data-testid="stBaseButton-secondary"] {{
  background-color: var(--surface) !important;
  color: var(--ink) !important;
  border: 1px solid var(--line) !important;
}}

button[kind="secondary"]:hover,
[data-testid="baseButton-secondary"]:hover,
[data-testid="stBaseButton-secondary"]:hover {{
  background-color: var(--paper) !important;
  border-color: var(--line) !important;
  color: var(--ink) !important;
}}

/* Botões terciários */
button[kind="tertiary"],
[data-testid="baseButton-tertiary"],
[data-testid="stBaseButton-tertiary"] {{
  background-color: transparent !important;
  color: var(--ink-soft) !important;
  border: 1px solid transparent !important;
}}

button[kind="tertiary"]:hover,
[data-testid="baseButton-tertiary"]:hover,
[data-testid="stBaseButton-tertiary"]:hover {{
  background-color: var(--late-tint) !important;
  color: var(--late) !important;
}}


/* Botões desabilitados */
button:disabled,
button[disabled],
[data-testid*="stBaseButton"]:disabled {{
  opacity: 0.5 !important;
  cursor: not-allowed !important;
  background-color: var(--surface) !important;
  color: var(--ink-soft) !important;
  border-color: var(--line) !important;
}}

/* Campos de entrada e formulários */
[data-testid="stTextInputRootElement"],
[data-testid="stTextAreaRootElement"],
[data-testid="stNumberInputContainer"],
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div,
[data-testid="stDateInput"] [data-baseweb="input"],
[data-baseweb="input"],
[data-baseweb="textarea"],
[data-baseweb="select"] > div,
div[data-baseweb="input"] {{
  background-color: var(--surface) !important;
  border: 1px solid var(--line) !important;
  color: var(--ink) !important;
}}

[data-testid="stTextInputRootElement"]:focus-within,
[data-testid="stTextAreaRootElement"]:focus-within,
[data-testid="stNumberInputContainer"]:focus-within,
[data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div:focus-within,
[data-testid="stDateInput"] [data-baseweb="input"]:focus-within,
[data-baseweb="input"]:focus-within,
[data-baseweb="textarea"]:focus-within,
[data-baseweb="select"] > div:focus-within,
div[data-baseweb="input"]:focus-within {{
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 2px var(--blue-tint) !important;
}}

[data-testid="stTextInputRootElement"] input,
[data-testid="stTextAreaRootElement"] textarea,
[data-testid="stNumberInputContainer"] input,
[data-testid="stSelectbox"] [data-baseweb="select"] div,
[data-testid="stSelectbox"] [data-baseweb="select"] span,
[data-testid="stMultiSelect"] [data-baseweb="select"] div,
[data-testid="stMultiSelect"] [data-baseweb="select"] span,
[data-testid="stDateInput"] [data-baseweb="input"] input,
div[data-baseweb="select"] div,
div[data-baseweb="select"] span,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea,
[data-baseweb="base-input"],
[data-baseweb="base-input"] input,
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {{
  background-color: transparent !important;
  color: var(--ink) !important;
  -webkit-text-fill-color: var(--ink) !important;
}}

::placeholder,
::-webkit-input-placeholder,
:-ms-input-placeholder {{
  color: var(--ink-soft) !important;
  opacity: 1 !important;
  -webkit-text-fill-color: var(--ink-soft) !important;
}}

/* Botões +/- do number_input e alternador de visibilidade de senha */
[data-testid="stNumberInputStepDown"],
[data-testid="stNumberInputStepUp"] {{
  background-color: var(--surface) !important;
  color: var(--ink) !important;
}}

[data-testid="stNumberInputStepDown"]:hover,
[data-testid="stNumberInputStepUp"]:hover {{
  background-color: var(--blue-tint) !important;
  color: var(--ink) !important;
}}

[data-testid="stNumberInputStepDown"] svg,
[data-testid="stNumberInputStepUp"] svg {{
  fill: currentColor !important;
}}

[data-testid="stNumberInput"] button,
[data-baseweb="input"] button,
[data-testid="stTextInput"] button,
button[aria-label="Toggle password visibility"] {{
  background-color: transparent !important;
  color: var(--ink-soft) !important;
  border: none !important;
}}

[data-testid="stNumberInput"] button svg,
[data-baseweb="input"] button svg,
[data-testid="stTextInput"] button svg,
button[aria-label="Toggle password visibility"] svg {{
  fill: currentColor !important;
}}

[data-testid="stNumberInput"] button:hover,
[data-baseweb="input"] button:hover,
[data-testid="stTextInput"] button:hover,
button[aria-label="Toggle password visibility"]:hover {{
  color: var(--ink) !important;
  background-color: var(--blue-tint) !important;
}}

/* Dropdowns e Menus Abertos (BaseWeb Select / Popover) */
[data-baseweb="select"] span,
[data-baseweb="select"] div {{
  color: var(--ink) !important;
}}

[data-baseweb="select"] svg {{
  fill: var(--ink-soft) !important;
}}

[data-baseweb="popover"],
[data-baseweb="popover"] > div,
[data-baseweb="menu"],
ul[role="listbox"],
[role="listbox"] {{
  background-color: var(--surface) !important;
  border: 1px solid var(--line) !important;
  color: var(--ink) !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3) !important;
}}

[role="option"],
li[role="option"] {{
  background-color: var(--surface) !important;
  color: var(--ink) !important;
}}

[role="option"]:hover,
[role="option"][aria-selected="true"],
[role="option"]:focus,
li[role="option"]:hover,
li[role="option"][aria-selected="true"] {{
  background-color: var(--blue-tint) !important;
  color: var(--blue) !important;
}}

[role="option"] *,
li[role="option"] * {{
  color: inherit !important;
}}

/* Segmented Control / Pills */
[data-testid="stButtonGroup"] > div,
[data-testid="stSegmentedControl"] > div {{
  background-color: var(--surface) !important;
  border: 1px solid var(--line) !important;
}}

[data-testid="stButtonGroup"] button[aria-checked="false"],
[data-testid="stSegmentedControl"] button[aria-checked="false"] {{
  background: var(--surface) !important;
  background-color: var(--surface) !important;
  color: var(--ink) !important;
  border: 1px solid var(--line) !important;
}}

[data-testid="stButtonGroup"] button[aria-checked="false"]:hover,
[data-testid="stSegmentedControl"] button[aria-checked="false"]:hover {{
  background: var(--blue-tint) !important;
  background-color: var(--blue-tint) !important;
}}

[data-testid="stButtonGroup"] button[aria-checked="false"] *,
[data-testid="stSegmentedControl"] button[aria-checked="false"] * {{
  color: inherit !important;
}}

[data-testid="stButtonGroup"] button[aria-checked="true"],
[data-testid="stSegmentedControl"] button[aria-checked="true"],
[data-testid="stSegmentedControl"] button[data-checked="true"] {{
  background: var(--blue-tint) !important;
  background-color: var(--blue-tint) !important;
  color: var(--blue) !important;
  border: 1px solid var(--blue) !important;
  font-weight: 600 !important;
}}

[data-testid="stButtonGroup"] button[aria-checked="true"] *,
[data-testid="stSegmentedControl"] button[aria-checked="true"] *,
[data-testid="stSegmentedControl"] button[data-checked="true"] * {{
  color: inherit !important;
  fill: currentColor !important;
}}

/* Abas (Tabs) */
[data-baseweb="tab-list"] {{
  border-bottom: 1px solid var(--line) !important;
  background-color: transparent !important;
}}

[data-baseweb="tab"] {{
  color: var(--ink-soft) !important;
  background-color: transparent !important;
}}

[data-baseweb="tab"]:hover {{
  color: var(--ink) !important;
}}

[data-baseweb="tab"][aria-selected="true"] {{
  color: var(--blue) !important;
}}

[data-baseweb="tab-highlight"] {{
  background-color: var(--blue) !important;
}}

[data-baseweb="tab-border"] {{
  background-color: var(--line) !important;
}}

/* Expander */
[data-testid="stExpander"] {{
  background-color: var(--surface) !important;
  border: 1px solid var(--line) !important;
}}

[data-testid="stExpander"] details {{
  background-color: var(--surface) !important;
}}

[data-testid="stExpander"] summary {{
  background-color: var(--surface) !important;
  color: var(--ink) !important;
}}

[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span {{
  color: var(--ink) !important;
}}

[data-testid="stExpander"] summary svg {{
  fill: var(--ink-soft) !important;
}}

[data-testid="stExpander"] summary:hover {{
  color: var(--blue) !important;
}}

[data-testid="stExpander"] summary:hover p,
[data-testid="stExpander"] summary:hover span {{
  color: var(--blue) !important;
}}

[data-testid="stExpander"] summary:hover svg {{
  fill: var(--blue) !important;
}}

[data-testid="stExpanderDetails"] {{
  background-color: var(--surface) !important;
  border-top: 1px solid var(--line) !important;
}}

/* File Uploader Dropzone */
[data-testid="stFileUploaderDropzone"] {{
  background-color: var(--surface) !important;
  border: 1px dashed var(--line) !important;
  color: var(--ink-soft) !important;
}}

[data-testid="stFileUploaderDropzone"]:hover {{
  border-color: var(--blue) !important;
  background-color: var(--blue-tint) !important;
}}

[data-testid="stFileUploaderDropzone"] * {{
  color: var(--ink-soft) !important;
}}

[data-testid="stFileUploaderDropzone"] button,
[data-testid="stFileUploaderDropzone"] [data-testid="baseButton-secondary"],
[data-testid="stFileUploaderDropzone"] [data-testid="stBaseButton-secondary"] {{
  background-color: var(--surface) !important;
  color: var(--ink) !important;
  border: 1px solid var(--line) !important;
}}

[data-testid="stFileUploaderDropzone"] button *,
[data-testid="stFileUploaderDropzone"] [data-testid="baseButton-secondary"] *,
[data-testid="stFileUploaderDropzone"] [data-testid="stBaseButton-secondary"] * {{
  color: var(--ink) !important;
}}

[data-testid="stFileUploaderDropzone"] button:hover,
[data-testid="stFileUploaderDropzone"] [data-testid="baseButton-secondary"]:hover,
[data-testid="stFileUploaderDropzone"] [data-testid="stBaseButton-secondary"]:hover {{
  background-color: var(--paper) !important;
  border-color: var(--line) !important;
  color: var(--ink) !important;
}}

[data-testid="stFileUploaderFileData"] {{
  background-color: var(--surface) !important;
  border: 1px solid var(--line) !important;
  color: var(--ink) !important;
}}

/* Alertas e Notificações (st.info, st.warning, st.error, st.success) */
[data-testid="stAlertContainer"],
[data-testid="stAlert"] {{
  border-radius: 6px !important;
  font-size: 14px !important;
}}

[data-testid="stAlertContainer"]:has([data-testid="stAlertContentInfo"]),
[data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]) [data-testid="stAlertContainer"],
[data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]),
[data-test-variant="info"] [data-testid="stAlertContainer"],
[data-test-variant="info"] {{
  background-color: var(--blue-tint) !important;
  color: var(--blue) !important;
  border: 1px solid var(--blue) !important;
}}

[data-testid="stAlertContainer"]:has([data-testid="stAlertContentWarning"]),
[data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) [data-testid="stAlertContainer"],
[data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]),
[data-test-variant="warning"] [data-testid="stAlertContainer"],
[data-test-variant="warning"] {{
  background-color: var(--soon-tint) !important;
  color: var(--soon) !important;
  border: 1px solid var(--soon) !important;
}}

[data-testid="stAlertContainer"]:has([data-testid="stAlertContentError"]),
[data-testid="stAlert"]:has([data-testid="stAlertContentError"]) [data-testid="stAlertContainer"],
[data-testid="stAlert"]:has([data-testid="stAlertContentError"]),
[data-test-variant="error"] [data-testid="stAlertContainer"],
[data-test-variant="error"] {{
  background-color: var(--late-tint) !important;
  color: var(--late) !important;
  border: 1px solid var(--late) !important;
}}

[data-testid="stAlertContainer"]:has([data-testid="stAlertContentSuccess"]),
[data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) [data-testid="stAlertContainer"],
[data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]),
[data-test-variant="success"] [data-testid="stAlertContainer"],
[data-test-variant="success"] {{
  background-color: var(--ok-tint) !important;
  color: var(--ok) !important;
  border: 1px solid var(--ok) !important;
}}

[data-testid="stAlertContainer"] [data-testid="stMarkdownContainer"] p,
[data-testid="stAlertContainer"] p,
[data-testid="stAlertContainer"] span,
[data-testid="stAlert"] [data-testid="stMarkdownContainer"] p,
[data-testid="stAlert"] p,
[data-testid="stAlert"] span {{
  color: inherit !important;
}}

[data-testid="stAlertContainer"] svg,
[data-testid="stAlertContainer"] [data-testid="stIconMaterial"],
[data-testid="stAlert"] svg,
[data-testid="stAlert"] [data-testid="stIconMaterial"] {{
  fill: currentColor !important;
  color: currentColor !important;
}}

/* Toasts */
[data-testid="stToast"] {{
  background-color: var(--surface) !important;
  border: 1px solid var(--line) !important;
  color: var(--ink) !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3) !important;
}}

[data-testid="stToast"] p,
[data-testid="stToast"] span {{
  color: var(--ink) !important;
}}

/* Tooltips e ícones de ajuda */
[data-testid="stTooltipIcon"],
[data-testid="stTooltipHoverTarget"],
.stTooltipIcon,
.stTooltipHoverTarget {{
  background: none !important;
  background-color: transparent !important;
  color: var(--ink-soft) !important;
}}

[data-testid="stTooltipIcon"] button,
[data-testid="stTooltipHoverTarget"] button,
.stTooltipIcon button,
.stTooltipHoverTarget button {{
  background: none !important;
  background-color: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
  min-height: auto !important;
  height: auto !important;
  width: auto !important;
  color: var(--ink-soft) !important;
}}

[data-testid="stTooltipIcon"] button:hover,
[data-testid="stTooltipHoverTarget"] button:hover,
.stTooltipIcon button:hover,
.stTooltipHoverTarget button:hover {{
  background: none !important;
  background-color: transparent !important;
  color: var(--ink) !important;
}}

[data-testid="stTooltipIcon"] svg,
[data-testid="stTooltipHoverTarget"] svg,
.stTooltipIcon svg,
.stTooltipHoverTarget svg {{
  background: none !important;
  background-color: transparent !important;
  fill: none !important;
  stroke: var(--ink-soft) !important;
  color: var(--ink-soft) !important;
}}

[data-testid="stTooltipIcon"] svg *,
[data-testid="stTooltipHoverTarget"] svg *,
.stTooltipIcon svg *,
.stTooltipHoverTarget svg *,
[data-testid="stTooltipIcon"] svg circle,
[data-testid="stTooltipHoverTarget"] svg circle,
[data-testid="stTooltipIcon"] svg path,
[data-testid="stTooltipHoverTarget"] svg path,
[data-testid="stTooltipIcon"] svg line,
[data-testid="stTooltipHoverTarget"] svg line {{
  fill: none !important;
  stroke: inherit !important;
}}

[data-testid="stTooltipIcon"]:hover svg,
[data-testid="stTooltipIcon"] button:hover svg,
[data-testid="stTooltipHoverTarget"]:hover svg,
[data-testid="stTooltipHoverTarget"] button:hover svg,
.stTooltipIcon:hover svg,
.stTooltipIcon button:hover svg,
.stTooltipHoverTarget:hover svg,
.stTooltipHoverTarget button:hover svg {{
  stroke: var(--ink) !important;
  color: var(--ink) !important;
}}

[data-testid="stTooltipContent"],
[role="tooltip"],
[data-baseweb="tooltip"] {{
  background-color: var(--surface) !important;
  color: var(--ink) !important;
  border: 1px solid var(--line) !important;
}}

/* Checkbox */
[data-testid="stCheckbox"] label span,
[data-baseweb="checkbox"] label span {{
  color: var(--ink) !important;
}}

[data-testid="stCheckbox"] div[role="checkbox"],
[data-baseweb="checkbox"] span[aria-checked="false"],
[data-baseweb="checkbox"] > div:first-child {{
  border: 1px solid var(--line) !important;
  border-color: var(--line) !important;
  background-color: var(--surface) !important;
}}

[data-testid="stCheckbox"] div[role="checkbox"][aria-checked="true"],
[data-baseweb="checkbox"] span[aria-checked="true"],
[data-testid="stCheckbox"] input[type="checkbox"]:checked + div {{
  background-color: var(--blue) !important;
  border-color: var(--blue) !important;
}}

/* Calendário */
.cal-cell {{
  background-color: var(--surface) !important;
  border-color: var(--line) !important;
}}

.cal-cell-out {{
  background-color: var(--paper) !important;
  color: var(--none) !important;
}}

.cal-cell-today {{
  border: 2px solid var(--blue) !important;
  box-shadow: inset 0 0 0 1px var(--blue) !important;
}}

.cal-day-num {{
  color: var(--ink) !important;
}}

/* Caixas do painel e faixas de cursos */
.andamento-container,
[data-testid="stForm"] {{
  background-color: var(--surface) !important;
  border-color: var(--line) !important;
}}

[class*="st-key-faixa_"]:not([class*="st-key-faixa_header"]),
.strip-compact {{
  background-color: var(--surface) !important;
  border-top-color: var(--line) !important;
  border-right-color: var(--line) !important;
  border-bottom-color: var(--line) !important;
}}

.andamento-col {{
  background-color: var(--paper) !important;
}}

/* Barras de rolagem */
html,
body,
[data-testid="stMain"],
* {{
  scrollbar-width: thin;
  scrollbar-color: {scrollbar_thumb} var(--paper);
}}

::-webkit-scrollbar {{
  width: 10px;
  height: 10px;
  background: var(--paper);
}}

::-webkit-scrollbar-track {{
  background: var(--paper) !important;
}}

::-webkit-scrollbar-thumb {{
  background: {scrollbar_thumb} !important;
  border-radius: 999px;
  border: 2px solid var(--paper) !important;
}}

::-webkit-scrollbar-thumb:hover {{
  background: {scrollbar_thumb_hover} !important;
}}

::-webkit-scrollbar-corner {{
  background: var(--paper) !important;
}}

/* Links */
a, [data-testid="stMarkdownContainer"] a {{
  color: var(--blue) !important;
}}
"""


def load_css() -> None:
    """Carrega fontes do Google Fonts, arquivo de estilos customizado e tokens do tema ativo."""
    tema = init_theme()

    fonts_link = (
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Barlow:wght@400;500;600&display=swap" rel="stylesheet">'
    )
    st.markdown(fonts_link, unsafe_allow_html=True)

    css_path = Path("assets/style.css")
    try:
        if css_path.exists():
            with open(css_path, "r", encoding="utf-8") as f:
                css = f.read()
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except Exception as e:
        logger.error(f"Erro ao carregar CSS: {e}")

    # Injeta tokens e estilos do tema selecionado (emitted every run after the main stylesheet)
    theme_css = get_theme_css(tema)
    st.markdown(f"<style>{theme_css}</style>", unsafe_allow_html=True)


def init_session_state() -> None:
    """Inicializa variáveis de sessão do Streamlit."""
    try:
        if 'data_manager' not in st.session_state:
            st.session_state.data_manager = DataManager()
            logger.info("DataManager inicializado")

        if 'json_importer' not in st.session_state:
            st.session_state.json_importer = JSONImporter()

        if 'dashboard' not in st.session_state:
            st.session_state.dashboard = Dashboard()

        if 'backup_manager' not in st.session_state:
            st.session_state.backup_manager = BackupManager()

        if 'auth_manager' not in st.session_state:
            st.session_state.auth_manager = AuthManager()
            logger.info("AuthManager inicializado")

        if 'calendar_view' not in st.session_state:
            st.session_state.calendar_view = CalendarView()

        if 'pagina' not in st.session_state:
            st.session_state.pagina = "painel"

        if 'cursos_limite' not in st.session_state:
            st.session_state.cursos_limite = 25

        if 'filtro_status' not in st.session_state:
            st.session_state.filtro_status = "Todos"

    except Exception as e:
        logger.error(f"Erro ao inicializar session state: {e}")
        show_error("Ocorreu um erro ao inicializar os serviços do sistema.", details=str(e))


def clear_cache() -> None:
    """Limpa o cache de dados do Streamlit."""
    st.cache_data.clear()
    logger.info("Cache limpo")


def verificar_permissao(permissao: str) -> bool:
    """Verifica se o usuário autenticado possui a permissão informada."""
    auth = st.session_state.auth_manager
    if not auth.autenticado:
        return False
    return auth.pode(permissao)


# =============================================================================
# PÁGINA DE LOGIN
# =============================================================================

def render_login_page() -> bool:
    """
    Renderiza página de login centralizada em coluna de 400px de largura sobre --paper.
    """
    st.markdown("""
    <style>
    .main > div {
        padding-top: 5vh !important;
    }
    </style>
    """, unsafe_allow_html=True)

    col_l, col_center, col_r = st.columns([1, 1.2, 1])

    with col_center:
        with st.container(key="login_wrapper"):
            col_hdr, col_theme_login = st.columns([5, 1])
            with col_hdr:
                st.markdown("""
                <div class="login-header">
                  <h1 class="login-title">Controle de Cursos</h1>
                  <p class="login-helper">Entre com seu usuário para acessar as indicações.</p>
                </div>
                """, unsafe_allow_html=True)
            with col_theme_login:
                tema_login = st.session_state.get("tema", "Claro")
                icon_login = ":material/dark_mode:" if tema_login == "Claro" else ":material/light_mode:"
                help_txt = "Alternar para tema escuro" if tema_login == "Claro" else "Alternar para tema claro"
                if st.button(icon_login, key="btn_login_tema", help=help_txt, type="tertiary", use_container_width=True):
                    novo_tema = "Escuro" if tema_login == "Claro" else "Claro"
                    st.session_state["tema"] = novo_tema
                    st.session_state["tema_switch"] = novo_tema
                    st.query_params["tema"] = novo_tema
                    st.rerun()

            with st.form("login_form", clear_on_submit=False):
                username = st.text_input(
                    "Usuário",
                    placeholder="Digite seu usuário",
                    key="login_username"
                )
                password = st.text_input(
                    "Senha",
                    type="password",
                    placeholder="Digite sua senha",
                    key="login_password"
                )

                submitted = st.form_submit_button(
                    "Entrar",
                    type="primary",
                    use_container_width=True,
                    icon=":material/login:"
                )

                if submitted:
                    if username and password:
                        auth = st.session_state.auth_manager
                        sucesso, msg = auth.login(username, password)
                        if sucesso:
                            st.session_state.pagina = "painel"
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.warning("Preencha o usuário e a senha.")

    return st.session_state.auth_manager.autenticado


# =============================================================================
# HANDLERS DE AÇÕES
# =============================================================================

def handle_excluir_curso(index: int) -> None:
    """Handler para exclusão de curso com validação de permissão."""
    if not verificar_permissao('excluir_curso'):
        show_error("Sem permissão para excluir cursos.")
        return

    try:
        limpar_confirmacoes_exclusao()
        sucesso, msg = st.session_state.data_manager.excluir_curso(index)
        if sucesso:
            limpar_confirmacoes_exclusao()
            st.toast("Curso excluído.", icon=":material/check_circle:")
            clear_cache()
            st.rerun()
        else:
            show_error(msg)
    except Exception as e:
        logger.error(f"Erro ao excluir curso {index}: {e}")
        show_error("Erro ao excluir curso.", details=str(e))


def handle_importar_json(cursos_validos: List[Dict]) -> None:
    """Handler para importação de cursos via arquivo JSON."""
    if not verificar_permissao('criar_curso'):
        show_error("Sem permissão para importar cursos.")
        return

    try:
        importados, erros = st.session_state.json_importer.importar_cursos(
            cursos_validos, st.session_state.data_manager
        )

        if importados > 0:
            st.toast(f"{importados} curso(s) importado(s) com sucesso.", icon=":material/check_circle:")
            st.session_state.backup_manager.criar_backup()
            clear_cache()
            st.rerun()

        if erros:
            for erro in erros:
                show_error(erro)

    except Exception as e:
        logger.error(f"Erro na importação: {e}")
        show_error("Erro ao importar cursos.", details=str(e))


def handle_restaurar_backup(caminho_backup: str) -> None:
    """Handler para restauração de cópia de segurança (backup)."""
    # Limpa chaves de confirmação
    for k in list(st.session_state.keys()):
        if str(k).startswith("confirm_restore_"):
            del st.session_state[k]

    if not verificar_permissao('fazer_backup'):
        show_error("Sem permissão para restaurar backups.")
        return

    try:
        sucesso, msg = st.session_state.backup_manager.restaurar_backup(caminho_backup)
        if sucesso:
            st.toast("Backup restaurado com sucesso.", icon=":material/check_circle:")
            clear_cache()
            st.rerun()
        else:
            show_error(msg)
    except Exception as e:
        logger.error(f"Erro ao restaurar backup: {e}")
        show_error("Erro ao restaurar backup.", details=str(e))


# =============================================================================
# PÁGINAS DO SISTEMA
# =============================================================================

def render_pagina_painel() -> None:
    """Renderiza a página Painel (Dashboard)."""
    pode_criar = verificar_permissao('criar_curso')
    acao_novo = {
        "label": "Novo curso",
        "icon": ":material/add:",
        "pagina": "novo_curso",
        "key": "btn_hdr_novo_curso_painel"
    } if pode_criar else None

    page_header("Painel", "Visão geral dos prazos e andamento das indicações.", acao=acao_novo)

    if not verificar_permissao('ver_dashboard'):
        st.error("Sem permissão para visualizar o painel.")
        return

    try:
        df = st.session_state.data_manager.carregar_dados()
        st.session_state.dashboard.mostrar_dashboard(df)
    except Exception as e:
        logger.error(f"Erro no painel: {e}")
        show_error("Erro ao carregar o painel.", details=str(e))


def render_pagina_cursos() -> None:
    """
    Renderiza a lista de cursos em fichas de progresso com filtros segmentados,
    ordenação por vencimento e paginação em blocos de 25.
    """
    pode_criar = verificar_permissao('criar_curso')
    acao_novo = {
        "label": "Novo curso",
        "icon": ":material/add:",
        "pagina": "novo_curso",
        "key": "btn_hdr_novo_curso_cursos"
    } if pode_criar else None

    page_header("Cursos", "Fichas de progresso com prazos e etapas das indicações.", acao=acao_novo)

    if not verificar_permissao('ver_cursos'):
        st.error("Sem permissão para visualizar cursos.")
        return

    try:
        df = st.session_state.data_manager.carregar_dados()

        if df.empty:
            show_info("Nenhum curso cadastrado ainda. Use a página 'Novo curso' para adicionar.")
            return

        hoje = date.today()

        # Contagens para os botões segmentados de status
        c_atrasados = 0
        c_urgentes = 0
        c_no_prazo = 0
        c_sem_prazo = 0
        c_concluidos = 0

        for _, r in df.iterrows():
            if curso_concluido(r):
                c_concluidos += 1
                continue
            d = parse_data(r.get('Fim da indicação da SIAT'))
            if d is None:
                c_sem_prazo += 1
            else:
                dias = (d - hoje).days
                if dias < 0:
                    c_atrasados += 1
                elif dias <= 5:
                    c_urgentes += 1
                else:
                    c_no_prazo += 1

        counts_status = {
            "Todos": len(df),
            "Atrasados": c_atrasados,
            "Próximos 5 dias": c_urgentes,
            "No prazo": c_no_prazo,
            "Sem prazo": c_sem_prazo,
            "Concluídos": c_concluidos
        }

        # Barra de ferramentas
        col_busca, col_estado = st.columns([2, 1], gap="small")
        with col_busca:
            termo_busca = st.text_input(
                "Buscar cursos",
                placeholder="Buscar por código, turma ou SIGAD",
                key="input_busca_cursos",
                label_visibility="collapsed"
            )

        with col_estado:
            opcoes_etapa = [
                "Todas as etapas",
                "solicitar voluntários",
                "fazer indicação",
                "ver vagas escalantes",
                "Concluído",
                "Sem etapa"
            ]
            etapa_sel = st.selectbox(
                "Etapa",
                opcoes_etapa,
                index=0,
                key="select_filtro_etapa",
                label_visibility="collapsed"
            )

        # Filtro segmentado de status
        def formatar_status_label(opt: str) -> str:
            count = counts_status.get(opt, 0)
            return f"{opt} {count}"

        opcoes_status = list(counts_status.keys())
        default_status = st.session_state.get("filtro_status", "Todos")
        if default_status not in opcoes_status:
            default_status = "Todos"

        status_sel = st.segmented_control(
            "Filtro de prazo",
            options=opcoes_status,
            default=default_status,
            format_func=formatar_status_label,
            key="segmented_status_filter",
            label_visibility="collapsed"
        )
        if not status_sel:
            status_sel = "Todos"
        st.session_state.filtro_status = status_sel

        # Reset de paginação quando os filtros mudam
        sig_atual = (
            termo_busca.strip() if termo_busca else "",
            etapa_sel,
            status_sel
        )
        if st.session_state.get("_filtros_sig") != sig_atual:
            st.session_state["_filtros_sig"] = sig_atual
            st.session_state.cursos_limite = 25

        # Filtragem dos dados
        df_filtrado = df.copy()

        # 1. Filtro textual
        if termo_busca and termo_busca.strip():
            termo = termo_busca.strip().lower()
            df_filtrado = df_filtrado[df_filtrado.apply(
                lambda r: any(termo in str(val).lower() for val in r.values if pd.notna(val)),
                axis=1
            )]

        # 2. Filtro de status
        if status_sel == "Atrasados":
            df_filtrado = df_filtrado[df_filtrado.apply(
                lambda r: (not curso_concluido(r)) and parse_data(r.get('Fim da indicação da SIAT')) is not None and (parse_data(r.get('Fim da indicação da SIAT')) - hoje).days < 0,
                axis=1
            )]
        elif status_sel == "Próximos 5 dias":
            df_filtrado = df_filtrado[df_filtrado.apply(
                lambda r: (not curso_concluido(r)) and parse_data(r.get('Fim da indicação da SIAT')) is not None and 0 <= (parse_data(r.get('Fim da indicação da SIAT')) - hoje).days <= 5,
                axis=1
            )]
        elif status_sel == "No prazo":
            df_filtrado = df_filtrado[df_filtrado.apply(
                lambda r: (not curso_concluido(r)) and parse_data(r.get('Fim da indicação da SIAT')) is not None and (parse_data(r.get('Fim da indicação da SIAT')) - hoje).days > 5,
                axis=1
            )]
        elif status_sel == "Sem prazo":
            df_filtrado = df_filtrado[df_filtrado.apply(
                lambda r: (not curso_concluido(r)) and parse_data(r.get('Fim da indicação da SIAT')) is None,
                axis=1
            )]
        elif status_sel == "Concluídos":
            df_filtrado = df_filtrado[df_filtrado.apply(curso_concluido, axis=1)]

        # 3. Filtro de etapa
        if etapa_sel != "Todas as etapas":
            if etapa_sel == "Sem etapa":
                df_filtrado = df_filtrado[df_filtrado.apply(
                    lambda r: not curso_concluido(r) and not limpar_valor(r.get('Estado')),
                    axis=1
                )]
            elif etapa_sel == "Concluído":
                df_filtrado = df_filtrado[df_filtrado.apply(curso_concluido, axis=1)]
            else:
                norm_sel = etapa_sel.strip().lower()
                df_filtrado = df_filtrado[df_filtrado.apply(
                    lambda r: not curso_concluido(r) and limpar_valor(r.get('Estado')).strip().lower() == norm_sel,
                    axis=1
                )]

        if df_filtrado.empty:
            show_info("Nenhum curso encontrado. Ajuste a busca ou os filtros.")
            return

        # Ordenação por vencimento (atrasados e prazos mais próximos primeiro, sem prazo depois, concluídos por último)
        def chave_ordenacao(item):
            idx, r = item
            concluido = curso_concluido(r)
            d_siat = parse_data(r.get('Fim da indicação da SIAT'))
            cod = str(r.get('Curso', ''))

            if not concluido:
                if d_siat is not None:
                    return (0, d_siat, cod)
                else:
                    return (1, date.max, cod)
            else:
                d_conc = parse_data(r.get('DATA_DA_CONCLUSAO')) or date.max
                return (2, d_conc, cod)

        itens_ordenados = list(df_filtrado.iterrows())
        itens_ordenados.sort(key=chave_ordenacao)

        # Paginação
        total_encontrados = len(itens_ordenados)
        limite = st.session_state.get("cursos_limite", 25)
        exibir_itens = itens_ordenados[:limite]

        st.markdown(
            f'<div style="font-size: 13px; color: var(--ink-soft); margin: 0.75rem 0 0.5rem 0; font-variant-numeric: tabular-nums;">'
            f'Mostrando {len(exibir_itens)} de {total_encontrados} {plural(total_encontrados, "curso", "cursos")}</div>',
            unsafe_allow_html=True
        )

        can_edit = verificar_permissao('editar_curso')
        can_delete = verificar_permissao('excluir_curso')

        def on_edit_curso(idx_edit: int) -> None:
            st.session_state.curso_editando = idx_edit
            st.session_state.pagina = "editar"
            st.rerun()

        render_cabecalho_cursos()

        for idx, row in exibir_itens:
            render_faixa_curso(
                row=row,
                idx=idx,
                on_edit=on_edit_curso,
                on_delete=handle_excluir_curso,
                can_edit=can_edit,
                can_delete=can_delete
            )

        # Botão de paginação
        if total_encontrados > limite:
            mais_qtd = min(25, total_encontrados - limite)
            if st.button(
                f"Mostrar mais {mais_qtd}",
                key="btn_mostrar_mais",
                type="secondary",
                icon=":material/expand_more:",
                use_container_width=True
            ):
                st.session_state.cursos_limite = limite + 25
                st.rerun()

    except Exception as e:
        logger.error(f"Erro na lista de cursos: {e}")
        show_error("Erro ao carregar os cursos.", details=str(e))


def render_pagina_novo_curso() -> None:
    """Renderiza a página de cadastro de novo curso."""
    page_header("Novo curso", "Preencha as informações da indicação e do curso.")

    if not verificar_permissao('criar_curso'):
        st.error("Sem permissão para criar cursos.")
        return

    try:
        resultado = render_form_novo_curso(
            st.session_state.data_manager,
            st.session_state.backup_manager
        )
        sucesso, msg = resultado

        if sucesso:
            st.toast(msg or "Curso salvo.", icon=":material/check_circle:")
            clear_cache()
        elif msg:
            if "AVISO" in msg:
                show_warning(msg.replace("AVISO: ", ""))
            else:
                show_error(msg)

    except Exception as e:
        logger.error(f"Erro no formulário de novo curso: {e}")
        show_error("Erro ao exibir formulário.", details=str(e))


def render_pagina_editar_curso() -> None:
    """
    Renderiza a edição do curso selecionado (ou fallback por lista se acessado diretamente).
    """
    page_header("Editar curso", "Atualize as informações do curso e prazos.")

    if not verificar_permissao('editar_curso'):
        st.error("Sem permissão para editar cursos.")
        return

    col_voltar, _ = st.columns([2, 8])
    with col_voltar:
        if st.button("Voltar para cursos", key="btn_voltar_de_editar", icon=":material/arrow_back:", type="secondary"):
            st.session_state.pagina = "cursos"
            st.session_state.curso_editando = None
            st.rerun()

    try:
        df = st.session_state.data_manager.carregar_dados()

        if df.empty:
            show_info("Nenhum curso cadastrado para editar.")
            return

        idx_editando = st.session_state.get("curso_editando")

        # Fallback de seleção se não houver curso definido
        if idx_editando is None or idx_editando < 0 or idx_editando >= len(df):
            opcoes = [f"{row['Curso']} - {row['Turma']}" for _, row in df.iterrows()]
            curso_selecionado = st.selectbox(
                "Selecione o curso",
                opcoes,
                key="select_editar_curso_fallback"
            )
            idx_editando = opcoes.index(curso_selecionado) if curso_selecionado else 0

        curso_atual = df.iloc[idx_editando]

        resultado = render_form_editar_curso(
            curso_atual,
            idx_editando,
            st.session_state.data_manager,
            list(df.columns)
        )

        sucesso, msg = resultado
        if sucesso:
            st.toast("Alterações salvas.", icon=":material/check_circle:")
            clear_cache()
            st.session_state.pagina = "cursos"
            st.session_state.curso_editando = None
            st.rerun()
        elif msg:
            show_error(msg)

    except Exception as e:
        logger.error(f"Erro na edição de curso: {e}")
        show_error("Erro ao editar curso.", details=str(e))


def render_pagina_calendario() -> None:
    """Renderiza a página Calendário de Prazos."""
    page_header("Calendário", "Visualização mensal dos prazos da SIAT, chefia e conclusões.")

    if not verificar_permissao('ver_cursos'):
        st.error("Sem permissão para visualizar o calendário.")
        return

    try:
        df = st.session_state.data_manager.carregar_dados()

        if df.empty:
            show_info("Nenhum dado para exibir no calendário.")
            return

        st.session_state.calendar_view.render(df)

    except Exception as e:
        logger.error(f"Erro no calendário: {e}")
        show_error("Erro ao carregar o calendário.", details=str(e))


def render_pagina_importar_json() -> None:
    """Renderiza a página de importação de arquivo JSON."""
    page_header("Importar cursos", "Envie o arquivo JSON com os cursos e datas.")

    if not verificar_permissao('criar_curso'):
        st.error("Sem permissão para importar cursos.")
        return

    try:
        arquivo_json = st.file_uploader(
            "Selecione o arquivo JSON",
            type=['json'],
            key="upload_json",
            label_visibility="collapsed"
        )

        if arquivo_json is None:
            return

        dados, erro = st.session_state.json_importer.carregar_json(arquivo_json.getvalue())
        if erro:
            show_error(erro)
            return

        cursos_validos, cursos_invalidos = st.session_state.json_importer.validar_json(dados)
        resumo = st.session_state.json_importer.get_resumo_validacao()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total", resumo['total'])
        with col2:
            st.metric("Válidos", resumo['validos'])
        with col3:
            st.metric("Inválidos", resumo['invalidos'])

        if cursos_validos:
            st.markdown('<div class="section-title">Cursos válidos</div>', unsafe_allow_html=True)
            for curso in cursos_validos:
                st.write(f"- {curso.get('Curso', 'Sem nome')} - {curso.get('Turma', 'Sem turma')}")

        if cursos_invalidos:
            st.markdown('<div class="section-title">Cursos inválidos</div>', unsafe_allow_html=True)
            for item in cursos_invalidos:
                show_error(f"{item['curso']}: {item['erro']}")

        if cursos_validos:
            if st.button("Importar cursos válidos", key="btn_importar_confirmar", type="primary", icon=":material/upload:"):
                handle_importar_json(cursos_validos)

    except Exception as e:
        logger.error(f"Erro na importação JSON: {e}")
        show_error("Erro ao processar JSON.", details=str(e))


def render_pagina_backup() -> None:
    """Renderiza a página de gerenciamento de backups."""
    page_header("Backup", "Cópias internas da base de cursos.")

    if not verificar_permissao('fazer_backup'):
        st.error("Sem permissão para acessar backups.")
        return

    try:
        st.markdown('<div class="section-title">Criar backup</div>', unsafe_allow_html=True)
        if verificar_permissao('fazer_backup'):
            if st.button("Criar backup agora", key="btn_criar_backup", type="primary", icon=":material/save:"):
                with st.spinner("Criando backup..."):
                    sucesso, msg = st.session_state.backup_manager.criar_backup()
                    if sucesso:
                        st.toast("Backup criado com sucesso.", icon=":material/check_circle:")
                        st.rerun()
                    else:
                        show_error(msg)
        else:
            st.info("Apenas administradores podem criar novos backups.")

        st.markdown('<div class="section-title" style="margin-top: 1.5rem;">Backups disponíveis</div>', unsafe_allow_html=True)
        backups = st.session_state.backup_manager.listar_backups()

        if not backups:
            show_info("Nenhum backup criado até o momento.")
        else:
            for backup in backups:
                btn_slug = re.sub(r'[^a-zA-Z0-9_]', '_', backup['nome'])
                confirm_key = f"confirm_restore_{btn_slug}"
                em_confirmacao = st.session_state.get(confirm_key, False)

                col1, col2, col3 = st.columns([4, 2, 2], gap="small")

                with col1:
                    st.write(backup['nome'])

                with col2:
                    data_fmt = backup['data'].strftime('%d/%m/%Y %H:%M')
                    tamanho_kb = backup['tamanho'] / 1024
                    st.caption(f"{data_fmt} • {tamanho_kb:.1f} KB")

                with col3:
                    if verificar_permissao('fazer_backup'):
                        if not em_confirmacao:
                            btn_key = f"restore_{btn_slug}"
                            if st.button("Restaurar", key=btn_key, icon=":material/restore:", type="secondary", use_container_width=True):
                                st.session_state[confirm_key] = True
                                st.rerun()
                        else:
                            st.caption("Aguardando confirmação")
                    else:
                        st.caption("Apenas visualização")

                if em_confirmacao:
                    st.warning(f"Restaurar {backup['nome']}? A base atual será substituída (um backup de segurança é criado antes).")
                    c_conf1, c_conf2, _ = st.columns([2, 1, 3], gap="small")
                    with c_conf1:
                        if st.button("Confirmar restauração", key=f"btn_confirm_{btn_slug}", type="primary", icon=":material/check:", use_container_width=True):
                            st.session_state[confirm_key] = False
                            handle_restaurar_backup(backup['caminho'])
                    with c_conf2:
                        if st.button("Cancelar", key=f"btn_cancel_{btn_slug}", type="secondary", use_container_width=True):
                            st.session_state[confirm_key] = False
                            st.rerun()

    except Exception as e:
        logger.error(f"Erro na página de backup: {e}")
        show_error("Erro ao carregar backups.", details=str(e))


def render_pagina_usuarios() -> None:
    """Renderiza a página de gerenciamento de usuários (administração)."""
    page_header("Usuários", "Gerenciamento de acessos e permissões do sistema.")

    auth = st.session_state.auth_manager
    if not auth.permissoes.gerenciar_usuarios:
        st.error("Apenas administradores podem acessar esta página.")
        return

    try:
        tab_lista, tab_novo, tab_editar, tab_senha = st.tabs([
            "Lista",
            "Novo usuário",
            "Editar usuário",
            "Alterar senha"
        ])

        with tab_lista:
            df_usuarios = auth.listar_usuarios()

            if df_usuarios.empty:
                show_info("Nenhum usuário cadastrado.")
            else:
                nivel_map = {
                    "admin": "Administrador",
                    "editor": "Editor",
                    "viewer": "Visualizador"
                }
                linhas_html = []
                for _, row in df_usuarios.iterrows():
                    user_val = html.escape(str(row.get('username') or ''))
                    nome_val = html.escape(str(row.get('nome') or ''))
                    email_val = html.escape(str(row.get('email') or ''))
                    raw_nivel = str(row.get('nivel_acesso') or '')
                    nivel_val = html.escape(nivel_map.get(raw_nivel, raw_nivel.capitalize()))
                    ativo_val = bool(row.get('ativo', True))
                    status_html = '<span class="pill pill-ok">Ativo</span>' if ativo_val else '<span class="pill pill-late">Inativo</span>'
                    ult = row.get('ultimo_login')
                    if pd.notna(ult) and ult:
                        try:
                            ult_str = pd.to_datetime(ult).strftime('%d/%m/%Y %H:%M')
                        except Exception:
                            ult_str = str(ult)
                    else:
                        ult_str = "-"
                    ult_val = html.escape(ult_str)

                    linhas_html.append(
                        f'<tr style="border-bottom: 1px solid var(--line); color: var(--ink);">'
                        f'<td style="padding: 10px 12px; font-weight: 500;">{user_val}</td>'
                        f'<td style="padding: 10px 12px;">{nome_val}</td>'
                        f'<td style="padding: 10px 12px;">{email_val}</td>'
                        f'<td style="padding: 10px 12px;">{nivel_val}</td>'
                        f'<td style="padding: 10px 12px;">{status_html}</td>'
                        f'<td style="padding: 10px 12px; font-variant-numeric: tabular-nums;">{ult_val}</td>'
                        f'</tr>'
                    )

                tabela_html = (
                    '<div style="overflow-x: auto; width: 100%; margin-bottom: 1.5rem;">'
                    '<table style="width: 100%; border-collapse: collapse; text-align: left; font-family: var(--font-body); font-size: 14px;">'
                    '<thead>'
                    '<tr style="border-bottom: 2px solid var(--line);">'
                    '<th style="padding: 8px 12px; color: var(--ink-soft); font-size: 13px; font-weight: 600;">Usuário</th>'
                    '<th style="padding: 8px 12px; color: var(--ink-soft); font-size: 13px; font-weight: 600;">Nome</th>'
                    '<th style="padding: 8px 12px; color: var(--ink-soft); font-size: 13px; font-weight: 600;">E-mail</th>'
                    '<th style="padding: 8px 12px; color: var(--ink-soft); font-size: 13px; font-weight: 600;">Nível</th>'
                    '<th style="padding: 8px 12px; color: var(--ink-soft); font-size: 13px; font-weight: 600;">Status</th>'
                    '<th style="padding: 8px 12px; color: var(--ink-soft); font-size: 13px; font-weight: 600;">Último acesso</th>'
                    '</tr>'
                    '</thead>'
                    '<tbody>'
                    f'{"".join(linhas_html)}'
                    '</tbody>'
                    '</table>'
                    '</div>'
                )
                st.markdown(tabela_html, unsafe_allow_html=True)

                st.markdown('<div class="section-title">Ações</div>', unsafe_allow_html=True)
                col1, col2 = st.columns(2)

                with col1:
                    usuarios_ativos = df_usuarios[df_usuarios['ativo'] == True]['username'].tolist()
                    if usuarios_ativos:
                        username_bloquear = st.selectbox(
                            "Usuário para desativar",
                            usuarios_ativos,
                            key="select_bloquear"
                        )
                        if st.button("Desativar usuário", key="btn_desativar", icon=":material/block:", type="secondary"):
                            sucesso, msg = auth.desativar_usuario(username_bloquear)
                            if sucesso:
                                st.toast(msg, icon=":material/check_circle:")
                                st.rerun()
                            else:
                                show_error(msg)

                with col2:
                    username_reset = st.selectbox(
                        "Usuário para redefinir senha",
                        df_usuarios['username'].tolist(),
                        key="select_reset"
                    )
                    nova_senha_reset = st.text_input(
                        "Nova senha",
                        type="password",
                        key="senha_reset"
                    )
                    if st.button("Redefinir senha", key="btn_reset", icon=":material/lock_reset:", type="secondary"):
                        if nova_senha_reset:
                            sucesso, msg = auth.redefinir_senha(username_reset, nova_senha_reset)
                            if sucesso:
                                show_success(msg)
                            else:
                                show_error(msg)
                        else:
                            show_error("Digite a nova senha.")

        with tab_novo:
            with st.form("form_novo_usuario"):
                st.markdown('<div class="section-title">Criar novo usuário</div>', unsafe_allow_html=True)

                novo_username = st.text_input("Nome de usuário *")
                novo_nome = st.text_input("Nome completo *")
                novo_email = st.text_input("E-mail *")
                novo_nivel = st.selectbox(
                    "Nível de acesso *",
                    ["admin", "editor", "viewer"],
                    index=2,
                    format_func=lambda x: {
                        "admin": "Administrador (acesso total)",
                        "editor": "Editor (criação e edição de cursos)",
                        "viewer": "Visualizador (apenas leitura)"
                    }[x]
                )
                nova_senha = st.text_input("Senha inicial *", type="password")

                submitted = st.form_submit_button("Criar usuário", type="primary", icon=":material/person_add:")

                if submitted:
                    if all([novo_username, novo_nome, novo_email, nova_senha]):
                        sucesso, msg = auth.criar_usuario(
                            novo_username, novo_nome, novo_email,
                            novo_nivel, nova_senha
                        )
                        if sucesso:
                            st.toast(msg, icon=":material/check_circle:")
                            st.rerun()
                        else:
                            show_error(msg)
                    else:
                        show_error("Preencha todos os campos obrigatórios marcados com asterisco (*).")

        with tab_editar:
            st.markdown('<div class="section-title">Editar usuário</div>', unsafe_allow_html=True)
            df_usuarios_edit = auth.listar_usuarios()

            if df_usuarios_edit.empty:
                show_info("Nenhum usuário cadastrado.")
            else:
                usuario_selecionado = st.selectbox(
                    "Selecione o usuário para editar",
                    df_usuarios_edit['username'].tolist(),
                    key="select_editar"
                )

                usuario_atual = df_usuarios_edit[df_usuarios_edit['username'] == usuario_selecionado].iloc[0]

                with st.form("form_editar_usuario"):
                    col1, col2 = st.columns(2)

                    with col1:
                        edit_username = st.text_input(
                            "Usuário (login) *",
                            value=usuario_atual['username']
                        )
                        edit_nome = st.text_input(
                            "Nome completo *",
                            value=usuario_atual['nome']
                        )

                    with col2:
                        edit_email = st.text_input(
                            "E-mail *",
                            value=usuario_atual['email']
                        )
                        niveis_acesso = ["admin", "editor", "viewer"]
                        nivel_salvo = usuario_atual.get('nivel_acesso')
                        nivel_idx = niveis_acesso.index(nivel_salvo) if nivel_salvo in niveis_acesso else 2

                        edit_nivel = st.selectbox(
                            "Nível de acesso *",
                            niveis_acesso,
                            index=nivel_idx,
                            format_func=lambda x: {
                                "admin": "Administrador",
                                "editor": "Editor",
                                "viewer": "Visualizador"
                            }.get(x, str(x))
                        )

                    submitted = st.form_submit_button("Salvar alterações", type="primary", icon=":material/save:")

                    if submitted:
                        if all([edit_username, edit_nome, edit_email]):
                            sucesso, msg = auth.editar_usuario(
                                usuario_selecionado,
                                edit_username,
                                edit_nome,
                                edit_email,
                                edit_nivel
                            )
                            if sucesso:
                                st.toast(msg, icon=":material/check_circle:")
                                st.rerun()
                            else:
                                show_error(msg)
                        else:
                            show_error("Preencha todos os campos obrigatórios.")

        with tab_senha:
            st.markdown('<div class="section-title">Alterar minha senha</div>', unsafe_allow_html=True)

            with st.form("form_alterar_senha"):
                senha_atual = st.text_input("Senha atual", type="password")
                senha_nova = st.text_input("Nova senha", type="password")
                senha_confirmar = st.text_input("Confirmar nova senha", type="password")

                submitted = st.form_submit_button("Alterar senha", type="primary", icon=":material/key:")

                if submitted:
                    if senha_nova != senha_confirmar:
                        show_error("As senhas informadas não coincidem.")
                    elif len(senha_nova) < 6:
                        show_error("A senha deve ter no mínimo 6 caracteres.")
                    else:
                        sucesso, msg = auth.alterar_senha(
                            auth.usuario_atual['username'],
                            senha_atual,
                            senha_nova
                        )
                        if sucesso:
                            show_success(msg)
                        else:
                            show_error(msg)

    except Exception as e:
        logger.error(f"Erro na aba de usuários: {e}")
        show_error("Erro ao carregar usuários.", details=str(e))


# =============================================================================
# FLUXO PRINCIPAL
# =============================================================================

def main():
    """Ponto de entrada da aplicação Streamlit."""
    st.set_page_config(
        page_title=Settings.PAGE_TITLE,
        page_icon=Settings.PAGE_ICON,
        layout=Settings.PAGE_LAYOUT,
        initial_sidebar_state="collapsed"
    )

    load_css()
    init_session_state()

    auth = st.session_state.auth_manager

    # Se não estiver autenticado, exibe tela de login
    if not auth.autenticado:
        render_login_page()
        return

    # Renderiza a barra de navegação superior persistente
    pagina_selecionada = render_topbar(auth, st.session_state.data_manager)

    # Roteamento de páginas
    if pagina_selecionada == "painel":
        render_pagina_painel()
    elif pagina_selecionada == "cursos":
        render_pagina_cursos()
    elif pagina_selecionada == "novo_curso":
        render_pagina_novo_curso()
    elif pagina_selecionada == "editar":
        render_pagina_editar_curso()
    elif pagina_selecionada == "calendario":
        render_pagina_calendario()
    elif pagina_selecionada == "importar":
        render_pagina_importar_json()
    elif pagina_selecionada == "backup":
        render_pagina_backup()
    elif pagina_selecionada == "usuarios":
        render_pagina_usuarios()
    else:
        render_pagina_painel()


if __name__ == "__main__":
    main()
