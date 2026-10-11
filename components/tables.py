"""
Módulo de tabelas auxiliares.
"""

from typing import Optional, Callable
import streamlit as st
import pandas as pd

from components.ui import render_faixa_curso


def render_tabela_cursos(
    df: pd.DataFrame,
    on_delete: Optional[Callable[[int], None]] = None,
    show_actions: bool = True
) -> None:
    """Renderiza tabela simplificada de cursos."""
    if df.empty:
        st.info("Nenhum curso encontrado.")
        return

    colunas_exibir = ['Curso', 'Turma', 'Vagas', 'Estado', 'Prioridade']
    colunas_disponiveis = [c for c in colunas_exibir if c in df.columns]

    st.dataframe(
        df[colunas_disponiveis] if colunas_disponiveis else df,
        use_container_width=True,
        hide_index=True
    )
