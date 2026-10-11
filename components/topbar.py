"""
Módulo de barra de navegação superior persistente (Top Bar).

Substitui a barra lateral esquerda por uma barra de navegação superior centralizada,
mantendo todas as regras de permissão, contagem de prazos vencidos e troca de tema.
"""

import html
from typing import Optional
import streamlit as st

from utils.validators import calcular_metricas_prazos
from components.ui import limpar_confirmacoes_exclusao


def navegar_para(destino: str) -> None:
    """Navega para a página destino limpando confirmações pendentes."""
    limpar_confirmacoes_exclusao()
    for k in list(st.session_state.keys()):
        if str(k).startswith("confirm_restore_"):
            del st.session_state[k]
    st.session_state["pagina"] = destino
    st.rerun()


def render_topbar(auth_manager, data_manager) -> str:
    """
    Renderiza a barra de navegação superior persistente alinhada com o conteúdo.

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
    pagina_anterior = st.session_state.get("_topbar_pagina_anterior")
    if pagina_anterior != pagina_atual:
        limpar_confirmacoes_exclusao()
        for k in list(st.session_state.keys()):
            if str(k).startswith("confirm_restore_"):
                del st.session_state[k]
        st.session_state["_topbar_pagina_anterior"] = pagina_atual

    # Permissões
    pode_painel = auth_manager.pode('ver_dashboard')
    pode_cursos = auth_manager.pode('ver_cursos')
    pode_calendario = auth_manager.pode('ver_cursos')

    pode_importar = auth_manager.pode('criar_curso')
    pode_backup = auth_manager.pode('fazer_backup')
    pode_usuarios = auth_manager.pode('gerenciar_usuarios')
    pode_admin = pode_importar or pode_backup or pode_usuarios

    # Obter contagem de atrasados para o pill
    atrasados = 0
    if pode_cursos:
        try:
            df_dados = data_manager.carregar_dados()
            metricas = calcular_metricas_prazos(df_dados)
            atrasados = metricas.get('atrasados', 0)
        except Exception:
            atrasados = 0

    # Dados do usuário atual
    usuario_atual = auth_manager.usuario_atual or {}
    nome_usuario = html.escape(str(usuario_atual.get('nome', 'Usuário')))
    nivel_raw = usuario_atual.get('nivel_acesso', 'viewer')
    nivel_map = {
        'admin': 'Administrador',
        'editor': 'Editor',
        'viewer': 'Visualizador'
    }
    nivel_label = html.escape(nivel_map.get(nivel_raw, str(nivel_raw).capitalize()))

    admin_ativo = (pagina_atual in ["importar", "backup", "usuarios"])

    with st.container(key="topbar", horizontal=True, horizontal_alignment="distribute",
                      vertical_alignment="center", gap="medium"):
        # LEFT group
        with st.container(horizontal=True, vertical_alignment="center", gap="small", width="content", key="topbar_left"):
            st.markdown('<span class="topbar-brand">Controle de Cursos</span>', unsafe_allow_html=True)
            if pode_painel:
                if st.button("Painel", key=f"nav_painel{'_ativo' if pagina_atual=='painel' else ''}", type="tertiary"):
                    navegar_para("painel")
            if pode_cursos:
                rotulo = f"Cursos :red-badge[{atrasados}]" if atrasados > 0 else "Cursos"
                if st.button(rotulo, key=f"nav_cursos{'_ativo' if pagina_atual=='cursos' else ''}", type="tertiary"):
                    navegar_para("cursos")
            if pode_calendario:
                if st.button("Calendário", key=f"nav_calendario{'_ativo' if pagina_atual=='calendario' else ''}", type="tertiary"):
                    navegar_para("calendario")
        # RIGHT group
        with st.container(horizontal=True, vertical_alignment="center", gap="small", width="content", key="topbar_right"):
            if pode_admin:
                with st.popover("Administração", type="tertiary", icon=":material/settings:",
                                key=f"topbar_admin{'_ativo' if admin_ativo else ''}"):
                    if pode_importar:
                        if st.button(
                            "Importar cursos",
                            key="topbar_admin_importar",
                            icon=":material/upload_file:",
                            type="tertiary",
                            width="stretch"
                        ):
                            navegar_para("importar")

                    if pode_backup:
                        if st.button(
                            "Backup",
                            key="topbar_admin_backup",
                            icon=":material/save:",
                            type="tertiary",
                            width="stretch"
                        ):
                            navegar_para("backup")

                    if pode_usuarios:
                        if st.button(
                            "Usuários",
                            key="topbar_admin_usuarios",
                            icon=":material/group:",
                            type="tertiary",
                            width="stretch"
                        ):
                            navegar_para("usuarios")

            with st.popover(nome_usuario, type="tertiary", icon=":material/account_circle:", key="topbar_user"):
                st.markdown(
                    f'<div class="popover-user-name">{nome_usuario}</div>',
                    unsafe_allow_html=True
                )
                st.caption(nivel_label)

                tema_sessao = st.session_state.get("tema", "Claro")
                if st.session_state.get("tema_switch") != tema_sessao:
                    st.session_state["tema_switch"] = tema_sessao

                def _on_tema_change():
                    sel = st.session_state.get("tema_switch")
                    if sel in ["Claro", "Escuro"]:
                        st.session_state["tema"] = sel
                        st.query_params["tema"] = sel
                    else:
                        st.session_state["tema_switch"] = st.session_state.get("tema", "Claro")

                st.segmented_control(
                    "Tema",
                    options=["Claro", "Escuro"],
                    key="tema_switch",
                    format_func=lambda x: f":material/{'light_mode' if x == 'Claro' else 'dark_mode'}: {x}",
                    label_visibility="collapsed",
                    on_change=_on_tema_change,
                    width="stretch"
                )

                st.divider()

                if st.button(
                    "Sair",
                    key="btn_topbar_sair",
                    icon=":material/logout:",
                    type="tertiary",
                    width="stretch"
                ):
                    auth_manager.logout()
                    st.session_state.clear()
                    st.rerun()

    return st.session_state["pagina"]
