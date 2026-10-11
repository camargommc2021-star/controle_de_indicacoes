"""
Módulo de alertas e mensagens padronizadas.

Fornece funções para exibir mensagens de sucesso, erro, aviso e informação
de forma padronizada em toda a aplicação, sem decorações de emoji.
"""

import html
import streamlit as st
from typing import Optional, List, Any


def show_success(
    message: str,
    icon: Optional[str] = ":material/check_circle:",
    duration: Optional[int] = None
) -> None:
    """Exibe mensagem de sucesso padronizada."""
    if icon:
        st.success(message, icon=icon)
    else:
        st.success(message)


def show_error(
    message: str,
    icon: Optional[str] = ":material/error:",
    details: Optional[str] = None
) -> None:
    """Exibe mensagem de erro padronizada."""
    if icon:
        st.error(message, icon=icon)
    else:
        st.error(message)

    if details:
        with st.expander("Detalhes do erro"):
            st.code(details)


def show_warning(
    message: str,
    icon: Optional[str] = ":material/warning:"
) -> None:
    """Exibe mensagem de aviso padronizada."""
    if icon:
        st.warning(message, icon=icon)
    else:
        st.warning(message)


def show_info(
    message: str,
    icon: Optional[str] = ":material/info:"
) -> None:
    """Exibe mensagem informativa padronizada."""
    if icon:
        st.info(message, icon=icon)
    else:
        st.info(message)


def show_validation_errors(
    errors: List[str],
    title: str = "Corrija os seguintes erros:"
) -> None:
    """Exibe lista de erros de validação."""
    if not errors:
        return

    with st.container():
        st.error(title, icon=":material/error:")
        for error in errors:
            st.markdown(f"- {error}")


def show_empty_state(
    title: str = "Nenhum dado encontrado",
    message: str = "Ajuste os filtros ou cadastre um novo item.",
    action_label: Optional[str] = None,
    action_callback: Optional[callable] = None
) -> None:
    """Exibe estado vazio com mensagem limpa."""
    safe_title = html.escape(str(title))
    safe_message = html.escape(str(message))
    st.markdown(f"""
    <div style="text-align: center; padding: 2.5rem 1rem;">
        <h3 style="color: var(--ink); margin-bottom: 0.5rem; font-size: 1.1rem;">{safe_title}</h3>
        <p style="color: var(--ink-soft); font-size: 0.95rem;">{safe_message}</p>
    </div>
    """, unsafe_allow_html=True)

    if action_label and action_callback:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(action_label, use_container_width=True):
                action_callback()


def show_confirm_dialog(
    title: str,
    message: str,
    on_confirm: callable,
    on_cancel: Optional[callable] = None,
    confirm_text: str = "Confirmar",
    cancel_text: str = "Cancelar",
    key: str = "confirm_dialog"
) -> bool:
    """Exibe diálogo de confirmação."""
    st.warning(title, icon=":material/warning:")
    st.write(message)

    col1, col2 = st.columns(2)
    confirmed = False

    with col1:
        if st.button(confirm_text, key=f"{key}_confirm", type="primary"):
            on_confirm()
            confirmed = True

    with col2:
        if st.button(cancel_text, key=f"{key}_cancel"):
            if on_cancel:
                on_cancel()

    return confirmed


def show_backup_success(nome_backup: str) -> None:
    """Exibe mensagem de sucesso na criação de backup."""
    show_success(f"Backup '{nome_backup}' criado com sucesso.")


def show_import_summary(
    total: int,
    validos: int,
    invalidos: int,
    erros: Optional[List[str]] = None
) -> None:
    """Exibe resumo de importação com rótulos limpos."""
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total", total)
    with col2:
        st.metric("Válidos", validos)
    with col3:
        st.metric("Inválidos", invalidos)

    if erros and invalidos > 0:
        with st.expander("Ver erros"):
            for erro in erros:
                st.error(erro)


def show_loading_spinner(
    message: str = "Processando...",
    func: Optional[callable] = None
) -> Any:
    """Exibe indicador de carregamento."""
    with st.spinner(message):
        if func:
            return func()


def show_curso_salvo(curso_nome: str, is_new: bool = True) -> None:
    """Exibe mensagem de curso salvo."""
    acao = "cadastrado" if is_new else "atualizado"
    show_success(f"Curso '{curso_nome}' {acao} com sucesso.")


def show_curso_excluido(curso_nome: str) -> None:
    """Exibe mensagem de curso excluído."""
    show_success(f"Curso '{curso_nome}' excluído com sucesso.")


def show_toast(
    message: str,
    type_: str = "info"
) -> None:
    """Exibe notificação toast sem emojis."""
    try:
        icon_map = {
            "success": ":material/check_circle:",
            "error": ":material/error:",
            "warning": ":material/warning:",
            "info": ":material/info:"
        }
        icon = icon_map.get(type_, ":material/info:")
        st.toast(message, icon=icon)
    except (AttributeError, TypeError):
        pass
