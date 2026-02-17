"""
Módulo de tabelas de dados para cursos e FICs.

Fornece funções para renderizar tabelas interativas com filtros,
paginação e ações.
"""

import streamlit as st
import pandas as pd
from typing import Optional, Callable, List, Dict, Any
from datetime import datetime, date


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


def render_lista_cursos_por_estado(
    df: pd.DataFrame,
    on_delete: Optional[Callable[[int], None]] = None
) -> None:
    """
    Renderiza lista de cursos agrupados por estado.
    
    Args:
        df: DataFrame com dados dos cursos
        on_delete: Callback para exclusão (recebe índice)
    """
    if df.empty:
        show_empty_state("cursos")
        return
    
    # Ordem de prioridade dos estados
    estados_ordenados = [
        'solicitar voluntários',
        'fazer indicação',
        'ver vagas escalantes',
        'Sem estado'
    ]
    
    # Cores por estado
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
    curso_nome = row.get('Curso', 'Sem nome')
    turma = row.get('Turma', 'N/A')
    vagas = row.get('Vagas', 0)
    data_siat = row.get('Fim da indicação da SIAT', '')
    prazo_chefia = row.get('Prazo dado pela chefia', '')
    prioridade = row.get('Prioridade', '')
    
    # Calcular cores de prazo
    cor_prazo = "#95a5a6"
    dias_texto = ""
    if data_siat:
        try:
            if isinstance(data_siat, str):
                data = datetime.strptime(data_siat, "%d/%m/%Y").date()
            else:
                data = data_siat
            hoje = date.today()
            dias_restantes = (data - hoje).days
            
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
        except:
            dias_texto = "Data inválida"
    
    # Cor do prazo da chefia
    cor_chefia = "#95a5a6"
    if prazo_chefia:
        try:
            if isinstance(prazo_chefia, str):
                data_chefia = datetime.strptime(prazo_chefia, "%d/%m/%Y").date()
            else:
                data_chefia = prazo_chefia
            hoje = date.today()
            dias_chefia = (data_chefia - hoje).days
            
            if dias_chefia <= 7 and dias_chefia >= 0:
                cor_chefia = "#9b59b6"
            elif dias_chefia < 0:
                cor_chefia = "#e74c3c"
        except:
            pass
    
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
        if data_siat:
            st.markdown(f"<span style='color: {cor_prazo};'>⏰ {dias_texto}</span>", unsafe_allow_html=True)
        
        if prazo_chefia and cor_chefia == "#9b59b6":
            st.markdown(f"<span style='color: #9b59b6; font-weight: bold;'>🟣 Prazo Chefia: {prazo_chefia}</span>", unsafe_allow_html=True)
        elif prazo_chefia:
            st.caption(f"Chefia: {prazo_chefia}")
    
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
            curso_nome = row.get('Curso', 'Sem nome')
            turma = row.get('Turma', 'N/A')
            vagas = row.get('Vagas', 0)
            data_conclusao = row.get('DATA_DA_CONCLUSAO', '')
            
            col1, col2, col3 = st.columns([4, 2, 1])
            
            with col1:
                st.write(f"**{curso_nome}**")
                st.caption(f"Turma: {turma}")
            
            with col2:
                st.write(f"👥 {vagas} vagas")
                conclusao_str = str(data_conclusao).strip()
                if conclusao_str and conclusao_str.lower() != 'nan':
                    st.success(f"✅ Concluído em: {data_conclusao}")
            
            with col3:
                if on_delete:
                    if st.button("🗑️", key=f"del_conc_{idx}"):
                        on_delete(idx)
            
            st.markdown("---")


# ============================================
# TABELAS DE FIC
# ============================================

def render_tabela_fics(
    df: pd.DataFrame,
    fic_manager,
    fic_word_filler,
    show_download: bool = True
) -> None:
    """
    Renderiza tabela de FICs com ações.
    
    Args:
        df: DataFrame com dados dos FICs
        fic_manager: Instância do FICManager
        fic_word_filler: Instância do FICWordFiller
        show_download: Se deve mostrar botão de download
    """
    if df.empty:
        st.info("📋 Nenhum FIC cadastrado.")
        return
    
    st.markdown(f"**Total: {len(df)} FIC(s)**")
    
    for idx, row in df.iterrows():
        with st.expander(f"{row['ID']} - {row['Curso']} - {row['Nome_Completo']}"):
            render_fic_card(row, fic_manager, fic_word_filler, show_download)


def render_fic_card(
    row: pd.Series,
    fic_manager,
    fic_word_filler,
    show_download: bool = True
) -> None:
    """
    Renderiza card individual de FIC.
    
    Args:
        row: Série com dados do FIC
        fic_manager: Instância do FICManager
        fic_word_filler: Instância do FICWordFiller
        show_download: Se deve mostrar botão de download
    """
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        st.write(f"**Curso:** {row['Curso']}")
        st.write(f"**Turma:** {row['Turma']}")
        st.write(f"**Criado em:** {row['Data_Criacao']}")
    
    with col2:
        st.write(f"**Indicado:** {row['Posto_Graduacao']} {row['Nome_Completo']}")
        st.write(f"**OM:** {row['OM_Indicado']}")
    
    with col3:
        if show_download:
            fic_data = fic_manager.buscar_fic(row['ID'])
            if fic_data:
                word_buffer = fic_word_filler.preencher_fic(fic_data)
                st.download_button(
                    label="📄 Word",
                    data=word_buffer.getvalue(),
                    file_name=f"FIC_{row['ID']}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key=f"download_fic_{row['ID']}"
                )


def render_tabela_fics_filtrada(
    fic_manager,
    filtro_curso: str = "",
    filtro_nome: str = ""
) -> pd.DataFrame:
    """
    Renderiza tabela de FICs com filtros aplicados.
    
    Args:
        fic_manager: Instância do FICManager
        filtro_curso: Filtro por código do curso
        filtro_nome: Filtro por nome do indicado
        
    Returns:
        DataFrame filtrado
    """
    df = fic_manager.carregar_fics()
    
    if not df.empty:
        if filtro_curso:
            df = df[df['Curso'].str.contains(filtro_curso, case=False, na=False)]
        if filtro_nome:
            df = df[df['Nome_Completo'].str.contains(filtro_nome, case=False, na=False)]
    
    return df


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


def render_filtros_fic() -> tuple:
    """
    Renderiza componentes de filtro para FICs.
    
    Returns:
        Tupla (filtro_curso, filtro_nome)
    """
    col_filtro1, col_filtro2 = st.columns(2)
    
    with col_filtro1:
        filtro_curso = st.text_input("Filtrar por Curso", key="filtro_fic_curso")
    with col_filtro2:
        filtro_nome = st.text_input("Filtrar por Nome", key="filtro_fic_nome")
    
    return filtro_curso, filtro_nome
