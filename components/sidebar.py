"""
Módulo de barra lateral persistente para navegação do sistema.

Implementa a navegação por botões no sidebar com indicação de página ativa,
contagem de cursos atrasados no botão de cursos e controle de permissões.
"""

import html
import streamlit as st

from utils.validators import calcular_metricas_prazos
from components.ui import limpar_confirmacoes_exclusao


def render_sidebar(data_manager, auth_manager) -> str:
    """
    Renderiza a navegação persistente no sidebar.
    
    Retorna:
        str: ID da página selecionada
    """
    if not auth_manager.autenticado:
        return ""

    # Determina a página inicial padrão
    if "pagina" not in st.session_state:
        if auth_manager.pode('ver_dashboard'):
            st.session_state["pagina"] = "painel"
        elif auth_manager.pode('ver_cursos'):
            st.session_state["pagina"] = "cursos"
        else:
            st.session_state["pagina"] = "painel"

    pagina_atual = st.session_state["pagina"]

    # Limpa confirmações pendentes se a página mudou
    pagina_anterior = st.session_state.get("_sidebar_pagina_anterior")
    if pagina_anterior != pagina_atual:
        limpar_confirmacoes_exclusao()
        st.session_state["_sidebar_pagina_anterior"] = pagina_atual

    def navegar_para(destino: str) -> None:
        limpar_confirmacoes_exclusao()
        st.session_state["pagina"] = destino
        st.rerun()

    # Garante que a barra lateral inicie expandida após o login
    if not st.session_state.get("_sidebar_auto_expanded", False):
        st.session_state["_sidebar_auto_expanded"] = True
        st.markdown("""
        <img src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg'/>" onerror="
            const collapseBtn = window.parent.document.querySelector('[data-testid=\\'stSidebarCollapsedControl\\'] button') || document.querySelector('[data-testid=\\'stSidebarCollapsedControl\\'] button');
            if (collapseBtn) { collapseBtn.click(); }
            this.remove();
        " style="display:none;" />
        """, unsafe_allow_html=True)

    with st.sidebar:
        # Bloco de Marca
        st.markdown("""
        <div class="sidebar-brand">
          <div class="sidebar-brand-title">Controle de Cursos</div>
          <div class="sidebar-brand-subtitle">Indicações e prazos</div>
        </div>
        """, unsafe_allow_html=True)

        # Grupo: Rotina
        st.markdown('<div class="nav-group-label">Rotina</div>', unsafe_allow_html=True)

        if auth_manager.pode('ver_dashboard'):
            ativo = (pagina_atual == "painel")
            if st.button(
                "Painel",
                key="btn_nav_painel",
                icon=":material/dashboard:",
                type="primary" if ativo else "secondary",
                use_container_width=True
            ):
                navegar_para("painel")

        if auth_manager.pode('ver_cursos'):
            # Obter contagem de atrasados para o badge
            df_dados = data_manager.carregar_dados()
            metricas = calcular_metricas_prazos(df_dados)
            atrasados = metricas.get('atrasados', 0)

            # Rótulo com número vermelho via markdown do Streamlit
            if atrasados > 0:
                label_cursos = f"Cursos :red[{atrasados}]"
            else:
                label_cursos = "Cursos"

            ativo = (pagina_atual == "cursos")
            if st.button(
                label_cursos,
                key="btn_nav_cursos",
                icon=":material/format_list_bulleted:",
                type="primary" if ativo else "secondary",
                use_container_width=True
            ):
                navegar_para("cursos")

        if auth_manager.pode('criar_curso'):
            ativo = (pagina_atual == "novo_curso")
            if st.button(
                "Novo curso",
                key="btn_nav_novo_curso",
                icon=":material/add_circle:",
                type="primary" if ativo else "secondary",
                use_container_width=True
            ):
                navegar_para("novo_curso")

        if auth_manager.pode('ver_cursos'):
            ativo = (pagina_atual == "calendario")
            if st.button(
                "Calendário",
                key="btn_nav_calendario",
                icon=":material/calendar_month:",
                type="primary" if ativo else "secondary",
                use_container_width=True
            ):
                navegar_para("calendario")

        # Grupo: Administração (apenas se o usuário tiver permissão para ao menos uma opção)
        pode_importar = auth_manager.pode('criar_curso')
        pode_backup = auth_manager.pode('ver_cursos')
        pode_usuarios = auth_manager.permissoes.gerenciar_usuarios

        if pode_importar or pode_backup or pode_usuarios:
            st.markdown('<div class="nav-group-label" style="margin-top: 1.25rem;">Administração</div>', unsafe_allow_html=True)

            if pode_importar:
                ativo = (pagina_atual == "importar")
                if st.button(
                    "Importar cursos",
                    key="btn_nav_importar",
                    icon=":material/upload_file:",
                    type="primary" if ativo else "secondary",
                    use_container_width=True
                ):
                    navegar_para("importar")

            if pode_backup:
                ativo = (pagina_atual == "backup")
                if st.button(
                    "Backup",
                    key="btn_nav_backup",
                    icon=":material/save:",
                    type="primary" if ativo else "secondary",
                    use_container_width=True
                ):
                    navegar_para("backup")

            if pode_usuarios:
                ativo = (pagina_atual == "usuarios")
                if st.button(
                    "Usuários",
                    key="btn_nav_usuarios",
                    icon=":material/group:",
                    type="primary" if ativo else "secondary",
                    use_container_width=True
                ):
                    navegar_para("usuarios")

        # Bloco do Usuário no Rodapé
        usuario_atual = auth_manager.usuario_atual or {}
        nome_usuario = html.escape(str(usuario_atual.get('nome', 'Usuário')))
        nivel_raw = usuario_atual.get('nivel_acesso', 'viewer')
        nivel_map = {
            'admin': 'Administrador',
            'editor': 'Editor',
            'viewer': 'Visualizador'
        }
        nivel_label = html.escape(nivel_map.get(nivel_raw, str(nivel_raw).capitalize()))

        st.markdown(f"""
        <div class="sidebar-user-block">
          <div class="sidebar-user-name">{nome_usuario}</div>
          <div class="sidebar-user-role">{nivel_label}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Sair", key="btn_nav_sair", icon=":material/logout:", type="secondary", use_container_width=True):
            auth_manager.logout()
            st.session_state.clear()
            st.rerun()

    return st.session_state["pagina"]
