"""
Módulo de tabelas de dados para cursos.

Fornece funções para renderizar tabelas interativas com filtros,
paginação e ações.
"""

import streamlit as st
import pandas as pd
from typing import Optional, Callable, List, Dict, Any
from datetime import datetime, date

from utils.validators import parse_data, limpar_valor, curso_concluido


# ============================================
# TABELAS DE CURSOS
# ============================================

def render_tabela_cursos(
    df: pd.DataFrame,
    on_delete: Optional[Callable[[int], None]] = None,
    show_actions: bool = True
) -> None:
    """
    Renderiza tabela completa de cursos com formatação.
    
    Args:
        df: DataFrame com dados dos cursos
        on_delete: Callback para exclusão (recebe índice)
        show_actions: Se deve mostrar coluna de ações
    """
    if df.empty:
        st.info("📋 Nenhum curso encontrado.")
        return
    
    # Configurar colunas para exibição
    colunas_exibir = ['Curso', 'Turma', 'Vagas', 'Estado', 'Prioridade']
    colunas_disponiveis = [c for c in colunas_exibir if c in df.columns]
    
    # Estilizar DataFrame
    def colorir_estado(val):
        cores = {
            'solicitar voluntários': 'background-color: #e74c3c; color: white;',
            'fazer indicação': 'background-color: #f1c40f; color: black;',
            'ver vagas escalantes': 'background-color: #3498db; color: white;',
            'Concluído': 'background-color: #2ecc71; color: white;',
        }
        return cores.get(val, '')
    
    # Exibir tabela
    st.dataframe(
        df[colunas_disponiveis] if colunas_disponiveis else df,
        use_container_width=True,
        hide_index=True
    )


def render_tabela_cursos_filtrada(
    data_manager,
    termo_busca: str = "",
    filtro_estado: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Renderiza tabela de cursos com filtros aplicados.
    
    Args:
        data_manager: Instância do DataManager
        termo_busca: Termo para busca textual
        filtro_estado: Lista de estados para filtrar
        
    Returns:
        DataFrame filtrado
    """
    df = data_manager.carregar_dados()
    
    if termo_busca:
        df = data_manager.buscar_curso(termo_busca)
    
    if filtro_estado and 'Estado' in df.columns:
        df = df[df['Estado'].isin(filtro_estado)]
    
    return df


def render_lista_cursos_por_estado(
    df: pd.DataFrame,
    on_delete: Optional[Callable[[int], None]] = None
) -> None:
    """
    Renderiza lista de cursos agrupados por estado com expanders.
    
    Args:
        df: DataFrame com cursos ativos (não concluídos)
        on_delete: Callback para exclusão
    """
    if df.empty:
        return
    
    estados_ordenados = ['solicitar voluntários', 'fazer indicação', 'ver vagas escalantes', 'Sem estado']
    cores_estado = {
        'solicitar voluntários': '#e74c3c',
        'fazer indicação': '#f1c40f',
        'ver vagas escalantes': '#3498db',
        'Sem estado': '#95a5a6'
    }
    
    # Verificar se existe coluna Estado
    if 'Estado' not in df.columns:
        df['Estado'] = 'Sem estado'
    
    # Preencher estados vazios/NaN
    df['Estado'] = df['Estado'].fillna('Sem estado')
    df['Estado'] = df['Estado'].replace('', 'Sem estado')
    
    for estado in estados_ordenados:
        df_estado = df[df['Estado'] == estado]
        
        if not df_estado.empty:
            cor = cores_estado.get(estado, '#95a5a6')
            
            with st.expander(f"{estado.upper()} ({len(df_estado)} cursos)", expanded=True):
                st.markdown(f"""
                <div style="border-left: 4px solid {cor}; padding-left: 10px; margin-bottom: 10px;">
                    <h4 style="color: {cor};">{estado}</h4>
                </div>
                """, unsafe_allow_html=True)
                
                for idx, row in df_estado.iterrows():
                    _render_linha_curso(row, idx, on_delete)


def _render_linha_curso(
    row: pd.Series,
    index: int,
    on_delete: Optional[Callable[[int], None]] = None
) -> None:
    """
    Renderiza uma linha de curso na lista.
    
    Args:
        row: Série com dados do curso
        index: Índice do curso
        on_delete: Callback para exclusão
    """
    curso_nome = limpar_valor(row.get('Curso')) or 'Sem nome'
    turma = limpar_valor(row.get('Turma')) or 'N/A'
    vagas_raw = row.get('Vagas', 0)
    try:
        vagas = int(vagas_raw) if pd.notna(vagas_raw) and str(vagas_raw).strip() not in ('', 'nan') else 0
    except (ValueError, TypeError):
        vagas = 0
    raw_data_siat = row.get('Fim da indicação da SIAT')
    raw_prazo_chefia = row.get('Prazo dado pela chefia')
    prioridade = limpar_valor(row.get('Prioridade'))
    
    # Calcular cores de prazo
    cor_prazo = "#95a5a6"
    dias_texto = ""
    dt_siat = parse_data(raw_data_siat)
    if dt_siat is not None:
        hoje = date.today()
        dias_restantes = (dt_siat - hoje).days
        
        if dias_restantes < 0:
            cor_prazo = "#e74c3c"
            dias_texto = f"Atrasado ({abs(dias_restantes)} dias)"
        elif dias_restantes == 0:
            cor_prazo = "#f1c40f"
            dias_texto = "Vence HOJE"
        elif dias_restantes <= 5:
            cor_prazo = "#f1c40f"
            dias_texto = f"{dias_restantes} dias restantes"
        elif dias_restantes <= 10:
            cor_prazo = "#3498db"
            dias_texto = f"{dias_restantes} dias restantes"
        else:
            cor_prazo = "#2ecc71"
            dias_texto = f"{dias_restantes} dias restantes"
    
    # Cor do prazo da chefia
    cor_chefia = "#95a5a6"
    dt_chefia = parse_data(raw_prazo_chefia)
    prazo_chefia_str = dt_chefia.strftime('%d/%m/%Y') if dt_chefia else limpar_valor(raw_prazo_chefia)
    if dt_chefia is not None:
        hoje = date.today()
        dias_chefia = (dt_chefia - hoje).days
        if 0 <= dias_chefia <= 7:
            cor_chefia = "#9b59b6"
        elif dias_chefia < 0:
            cor_chefia = "#e74c3c"
    
    col1, col2, col3, col4 = st.columns([3, 1, 2, 1])
    
    with col1:
        st.write(f"**{curso_nome}**")
        st.caption(f"Turma: {turma}")
        # Mostrar prioridade
        if prioridade == 'Alta':
            st.markdown("<span style='color: #e74c3c; font-size: 0.8em;'>🔴 Prioridade Alta</span>", unsafe_allow_html=True)
        elif prioridade == 'Média':
            st.markdown("<span style='color: #f1c40f; font-size: 0.8em;'>🟡 Prioridade Média</span>", unsafe_allow_html=True)
        elif prioridade == 'Baixa':
            st.markdown("<span style='color: #2ecc71; font-size: 0.8em;'>🟢 Prioridade Baixa</span>", unsafe_allow_html=True)
    
    with col2:
        st.write(f"👥 {vagas} vagas")
    
    with col3:
        if curso_concluido(row):
            st.markdown("<span style='color: #2ecc71;'>✅ Concluído</span>", unsafe_allow_html=True)
        elif dt_siat is not None:
            st.markdown(f"<span style='color: {cor_prazo};'>⏰ {dias_texto}</span>", unsafe_allow_html=True)
        
        if prazo_chefia_str and cor_chefia == "#9b59b6":
            st.markdown(f"<span style='color: #9b59b6; font-weight: bold;'>🟣 Prazo Chefia: {prazo_chefia_str}</span>", unsafe_allow_html=True)
        elif prazo_chefia_str:
            st.caption(f"Chefia: {prazo_chefia_str}")
    
    with col4:
        if on_delete:
            if st.button("🗑️", key=f"del_table_{index}"):
                on_delete(index)
    
    st.markdown("---")


def render_cursos_concluidos(
    df: pd.DataFrame,
    on_delete: Optional[Callable[[int], None]] = None
) -> None:
    """
    Renderiza seção de cursos concluídos em expander.
    
    Args:
        df: DataFrame com cursos concluídos
        on_delete: Callback para exclusão
    """
    if df.empty:
        return
    
    with st.expander(f"VER CURSOS CONCLUÍDOS ({len(df)})", expanded=False):
        for idx, row in df.iterrows():
            curso_nome = limpar_valor(row.get('Curso')) or 'Sem nome'
            turma = limpar_valor(row.get('Turma')) or 'N/A'
            vagas_raw = row.get('Vagas', 0)
            try:
                vagas = int(vagas_raw) if pd.notna(vagas_raw) and str(vagas_raw).strip() not in ('', 'nan') else 0
            except (ValueError, TypeError):
                vagas = 0
            dt_conclusao = parse_data(row.get('DATA_DA_CONCLUSAO'))
            conclusao_str = dt_conclusao.strftime('%d/%m/%Y') if dt_conclusao else limpar_valor(row.get('DATA_DA_CONCLUSAO'))
            
            col1, col2, col3 = st.columns([4, 2, 1])
            
            with col1:
                st.write(f"**{curso_nome}**")
                st.caption(f"Turma: {turma}")
            
            with col2:
                st.write(f"👥 {vagas} vagas")
                if conclusao_str:
                    st.success(f"✅ Concluído em: {conclusao_str}")
            
            with col3:
                if on_delete:
                    if st.button("🗑️", key=f"del_conc_{idx}"):
                        on_delete(idx)
            
            st.markdown("---")


# ============================================
# COMPONENTES DE FILTRO
# ============================================

def render_filtros_cursos(
    col_layout: List[float] = [3, 2, 2]
) -> tuple:
    """
    Renderiza componentes de filtro para cursos.
    
    Args:
        col_layout: Proporção das colunas
        
    Returns:
        Tupla (termo_busca, filtro_estado)
    """
    cols = st.columns(col_layout)
    
    with cols[0]:
        termo_busca = st.text_input("🔍 Buscar curso", placeholder="Digite para buscar...")
    
    with cols[1]:
        estados = ['Todos', 'solicitar voluntários', 'fazer indicação', 'ver vagas escalantes', 'Concluído']
        estado_selecionado = st.selectbox("Filtrar por estado", estados)
    
    with cols[2]:
        prioridades = ['Todas', 'Alta', 'Média', 'Baixa']
        prioridade_selecionada = st.selectbox("Filtrar por prioridade", prioridades)
    
    filtro_estado = None if estado_selecionado == 'Todos' else [estado_selecionado]
    
    return termo_busca, filtro_estado

