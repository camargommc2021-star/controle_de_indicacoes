"""
Módulo de sidebar para navegação e filtros globais.

Fornece funções para renderizar o menu lateral, filtros globais
e status do sistema.
"""

import streamlit as st
import pandas as pd
from typing import Optional, List, Dict, Any

from utils.validators import calcular_metricas_prazos


# ============================================
# SIDEBAR PRINCIPAL
# ============================================

def render_sidebar(
    data_manager,
    menu_items: Optional[List[Dict[str, str]]] = None,
    show_resumo: bool = True,
    show_filtros: bool = False
) -> None:
    """
    Renderiza sidebar completa.
    
    Args:
        data_manager: Instância do DataManager
        menu_items: Lista de itens de menu opcional
        show_resumo: Se deve mostrar resumo de cursos
        show_filtros: Se deve mostrar filtros globais
    """
    with st.sidebar:
        # Título
        st.title("📚 Controle de Cursos")
        st.markdown("---")
        
        # Menu de navegação (opcional)
        if menu_items:
            render_menu_navigation(menu_items)
            st.markdown("---")
        
        # Filtros globais
        if show_filtros:
            render_filtros_globais()
            st.markdown("---")
        
        # Resumo do sistema
        if show_resumo:
            render_status_resumo(data_manager)
            st.markdown("---")
        
        # Footer
        st.caption("Desenvolvido para controle de cursos militares")


def render_menu_navigation(
    items: List[Dict[str, str]]
) -> Optional[str]:
    """
    Renderiza menu de navegação na sidebar.
    
    Args:
        items: Lista de dicionários com 'label', 'icon' e 'key'
        
    Returns:
        Key do item selecionado ou None
    """
    st.subheader("🧭 Navegação")
    
    selected = None
    
    for item in items:
        icon = item.get('icon', '•')
        label = item.get('label', 'Item')
        key = item.get('key', label.lower().replace(' ', '_'))
        
        if st.button(f"{icon} {label}", key=f"nav_{key}", width="stretch"):
            selected = key
    
    return selected


# ============================================
# FILTROS GLOBAIS
# ============================================

def render_filtros_globais() -> Dict[str, Any]:
    """
    Renderiza filtros globais na sidebar.
    
    Returns:
        Dicionário com filtros selecionados
    """
    st.subheader("🔍 Filtros")
    
    filtros = {}
    
    # Filtro por estado
    estados = ['Todos', 'solicitar voluntários', 'fazer indicação', 'ver vagas escalantes', 'Concluído']
    filtros['estado'] = st.selectbox("Estado", estados, key="sidebar_filtro_estado")
    
    # Filtro por prioridade
    prioridades = ['Todas', 'Alta', 'Média', 'Baixa']
    filtros['prioridade'] = st.selectbox("Prioridade", prioridades, key="sidebar_filtro_prioridade")
    
    # Filtro de prazo
    st.caption("⏰ Alertas de Prazo")
    filtros['mostrar_atrasados'] = st.checkbox("Atrasados", value=True, key="sidebar_atrasados")
    filtros['mostrar_urgentes'] = st.checkbox("Urgentes (≤5 dias)", value=True, key="sidebar_urgentes")
    
    return filtros


def render_filtro_busca(
    placeholder: str = "Buscar curso...",
    key: str = "sidebar_busca"
) -> str:
    """
    Renderiza campo de busca na sidebar.
    
    Args:
        placeholder: Placeholder do campo
        key: Key única do componente
        
    Returns:
        Termo de busca digitado
    """
    return st.text_input("🔍 Buscar", placeholder=placeholder, key=key)


# ============================================
# STATUS E RESUMO
# ============================================

def render_status_resumo(data_manager) -> None:
    """
    Renderiza resumo de status na sidebar.
    
    Args:
        data_manager: Instância do DataManager
    """
    df = data_manager.carregar_dados()
    
    # Total de cursos
    st.metric("Total de Cursos", len(df))
    
    # Alertas de prazo usando helper compartilhado
    metricas = calcular_metricas_prazos(df)
    atrasados = metricas['atrasados']
    urgentes = metricas['urgentes']
    chefia_proximo = metricas['chefia_proximo']
    
    # Exibir alertas
    if atrasados > 0:
        st.error(f"⛔ {atrasados} prazo(s) atrasado(s)")
    if urgentes > 0:
        st.warning(f"⚠️ {urgentes} prazo(s) urgente(s)")
    if chefia_proximo > 0:
        st.info(f"🟣 {chefia_proximo} prazo(s) chefia próximo")

