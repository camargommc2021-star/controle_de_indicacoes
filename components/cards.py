"""
Módulo de cartões e indicadores auxiliares.
Todos os textos sem decorações de emoji.
"""

from typing import Optional, Dict, Any
import streamlit as st
import pandas as pd

from components.ui import status_do_curso, formatar_etapa_pill
from utils.validators import limpar_valor, curso_concluido


def render_metric_card(
    label: str,
    value: int | str,
    delta: Optional[str] = None,
    help_text: Optional[str] = None
) -> None:
    """Renderiza um cartão de métrica simples sem emojis."""
    st.metric(label=label, value=value, delta=delta, help=help_text)


def render_estado_summary(df: pd.DataFrame) -> None:
    """Renderiza resumo por estado."""
    if df.empty or 'Estado' not in df.columns:
        return

    estados = df['Estado'].value_counts().to_dict()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("Solicitar voluntários", estados.get('solicitar voluntários', 0))
    with col2:
        render_metric_card("Fazer indicação", estados.get('fazer indicação', 0))
    with col3:
        render_metric_card("Ver vagas escalantes", estados.get('ver vagas escalantes', 0))
    with col4:
        render_metric_card("Concluídos", estados.get('Concluído', 0))
