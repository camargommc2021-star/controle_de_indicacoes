"""
Módulo de sidebar para navegação e filtros globais.

Fornece funções para renderizar o menu lateral, filtros globais
e status do sistema.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from typing import Optional, List, Dict, Any, Callable


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
        
        if st.button(f"{icon} {label}", key=f"nav_{key}", use_container_width=True):
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
    
    # Alertas de prazo
    if 'Fim da indicação da SIAT' in df.columns:
        hoje = date.today()
        atrasados = 0
        urgentes = 0
        chefia_proximo = 0
        
        for _, row in df.iterrows():
            # Verificar prazo SIAT
            data_str = row.get('Fim da indicação da SIAT')
            if data_str and pd.notna(data_str):
                try:
                    if isinstance(data_str, str):
                        data = datetime.strptime(data_str, "%d/%m/%Y").date()
                    else:
                        data = data_str
                    
                    dias = (data - hoje).days
                    if dias < 0:
                        atrasados += 1
                    elif dias <= 5:
                        urgentes += 1
                except:
                    pass
            
            # Verificar prazo chefia
            prazo_chefia = row.get('Prazo dado pela chefia')
            if prazo_chefia and pd.notna(prazo_chefia):
                try:
                    if isinstance(prazo_chefia, str):
                        data_chefia = datetime.strptime(prazo_chefia, "%d/%m/%Y").date()
                    else:
                        data_chefia = prazo_chefia
                    
                    dias_chefia = (data_chefia - hoje).days
                    if 0 <= dias_chefia <= 7:
                        chefia_proximo += 1
                except:
                    pass
        
        # Exibir alertas
        if atrasados > 0:
            st.error(f"⛔ {atrasados} prazo(s) atrasado(s)")
        if urgentes > 0:
            st.warning(f"⚠️ {urgentes} prazo(s) urgente(s)")
        if chefia_proximo > 0:
            st.info(f"🟣 {chefia_proximo} prazo(s) chefia próximo")


def render_resumo_estatisticas(data_manager) -> None:
    """
    Renderiza estatísticas detalhadas na sidebar.
    
    Args:
        data_manager: Instância do DataManager
    """
    df = data_manager.carregar_dados()
    
    if df.empty or 'Estado' not in df.columns:
        return
    
    st.subheader("📊 Estatísticas")
    
    estados = df['Estado'].value_counts().to_dict()
    
    # Container com estatísticas
    with st.container():
        cols = st.columns(2)
        
        with cols[0]:
            st.caption("Pendentes")
            solicitando = estados.get('solicitar voluntários', 0)
            indicacao = estados.get('fazer indicação', 0)
            st.write(f"📝 Solicitar: {solicitando}")
            st.write(f"👥 Indicar: {indicacao}")
        
        with cols[1]:
            st.caption("Status")
            escalantes = estados.get('ver vagas escalantes', 0)
            concluidos = estados.get('Concluído', 0)
            st.write(f"👀 Escalantes: {escalantes}")
            st.write(f"✅ Concluídos: {concluidos}")


# ============================================
# MENU RÁPIDO
# ============================================

def render_menu_rapido(
    actions: List[Dict[str, Any]]
) -> None:
    """
    Renderiza menu de ações rápidas na sidebar.
    
    Args:
        actions: Lista de ações com 'label', 'icon', 'callback'
    """
    st.subheader("⚡ Ações Rápidas")
    
    for action in actions:
        icon = action.get('icon', '•')
        label = action.get('label', 'Ação')
        callback = action.get('callback')
        key = action.get('key', f"quick_{label.lower().replace(' ', '_')}")
        
        if callback and st.button(f"{icon} {label}", key=key, use_container_width=True):
            callback()


def render_atalhos_teclado(atalhos: Dict[str, str]) -> None:
    """
    Renderiza seção de atalhos de teclado na sidebar.
    
    Args:
        atalhos: Dicionário de atalho: descrição
    """
    with st.expander("⌨️ Atalhos"):
        for atalho, descricao in atalhos.items():
            st.caption(f"**{atalho}** - {descricao}")


# ============================================
# STATUS DO SISTEMA
# ============================================

def render_status_sistema(
    backup_manager,
    show_last_backup: bool = True,
    show_storage: bool = True
) -> None:
    """
    Renderiza status do sistema na sidebar.
    
    Args:
        backup_manager: Instância do BackupManager
        show_last_backup: Se deve mostrar último backup
        show_storage: Se deve mostrar uso de armazenamento
    """
    st.subheader("🖥️ Sistema")
    
    if show_last_backup:
        backups = backup_manager.listar_backups()
        if backups:
            ultimo = backups[0]
            st.caption(f"Último backup: {ultimo['data'].strftime('%d/%m/%Y %H:%M')}")
        else:
            st.caption("⚠️ Nenhum backup criado")
    
    if show_storage:
        backups = backup_manager.listar_backups()
        total_size = sum(b['tamanho'] for b in backups)
        st.caption(f"💾 Backups: {len(backups)} arquivos ({total_size / 1024:.1f} KB)")


# ============================================
# COMPONENTES DE USUÁRIO
# ============================================

def render_user_section(
    user_name: str = "Usuário",
    user_role: str = "Administrador"
) -> None:
    """
    Renderiza seção do usuário na sidebar.
    
    Args:
        user_name: Nome do usuário
        user_role: Função/cargo do usuário
    """
    st.markdown("---")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("👤")
    
    with col2:
        st.write(f"**{user_name}**")
        st.caption(user_role)


def render_footer_links(links: List[Dict[str, str]]) -> None:
    """
    Renderiza links no footer da sidebar.
    
    Args:
        links: Lista de dicionários com 'label' e 'url'
    """
    st.markdown("---")
    
    for link in links:
        label = link.get('label', 'Link')
        url = link.get('url', '#')
        st.markdown(f"[{label}]({url})")
