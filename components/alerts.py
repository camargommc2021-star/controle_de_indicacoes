"""
Módulo de alertas e mensagens padronizadas.

Fornece funções para exibir mensagens de sucesso, erro, aviso e info
de forma padronizada em toda a aplicação.
"""

import streamlit as st
from typing import Optional, List, Dict, Any


# ============================================
# ALERTAS BÁSICOS
# ============================================

def show_success(
    message: str,
    icon: str = "✅",
    duration: Optional[int] = None
) -> None:
    """
    Exibe mensagem de sucesso padronizada.
    
    Args:
        message: Texto da mensagem
        icon: Ícone a ser exibido
        duration: Duração em segundos (não implementado no Streamlit)
    """
    st.success(f"{icon} {message}")


def show_error(
    message: str,
    icon: str = "❌",
    details: Optional[str] = None
) -> None:
    """
    Exibe mensagem de erro padronizada.
    
    Args:
        message: Texto do erro
        icon: Ícone a ser exibido
        details: Detalhes adicionais do erro (exibidos em expander)
    """
    st.error(f"{icon} {message}")
    
    if details:
        with st.expander("Ver detalhes do erro"):
            st.code(details)


def show_warning(
    message: str,
    icon: str = "⚠️"
) -> None:
    """
    Exibe mensagem de aviso padronizada.
    
    Args:
        message: Texto do aviso
        icon: Ícone a ser exibido
    """
    st.warning(f"{icon} {message}")


def show_info(
    message: str,
    icon: str = "ℹ️"
) -> None:
    """
    Exibe mensagem informativa padronizada.
    
    Args:
        message: Texto da informação
        icon: Ícone a ser exibido
    """
    st.info(f"{icon} {message}")


# ============================================
# ALERTAS ESPECIALIZADOS
# ============================================

def show_validation_errors(
    errors: List[str],
    title: str = "Corrija os seguintes erros:"
) -> None:
    """
    Exibe lista de erros de validação.
    
    Args:
        errors: Lista de mensagens de erro
        title: Título do alerta
    """
    if not errors:
        return
    
    with st.container():
        st.error(f"⚠️ {title}")
        for error in errors:
            st.markdown(f"- {error}")


def show_empty_state(
    title: str = "Nenhum dado encontrado",
    message: str = "Comece adicionando um novo item.",
    icon: str = "📋",
    action_label: Optional[str] = None,
    action_callback: Optional[callable] = None
) -> None:
    """
    Exibe estado vazio com mensagem amigável.
    
    Args:
        title: Título do estado vazio
        message: Mensagem descritiva
        icon: Ícone grande
        action_label: Label do botão de ação (opcional)
        action_callback: Função a ser chamada ao clicar no botão
    """
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">{icon}</div>
            <h3 style="color: #666;">{title}</h3>
            <p style="color: #888;">{message}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if action_label and action_callback:
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
    """
    Exibe diálogo de confirmação.
    
    Args:
        title: Título do diálogo
        message: Mensagem de confirmação
        on_confirm: Função chamada ao confirmar
        on_cancel: Função chamada ao cancelar
        confirm_text: Texto do botão confirmar
        cancel_text: Texto do botão cancelar
        key: Key única para o diálogo
        
    Returns:
        True se confirmado, False caso contrário
    """
    st.warning(f"⚠️ {title}")
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


# ============================================
# ALERTAS DE SISTEMA
# ============================================

def show_backup_success(nome_backup: str) -> None:
    """
    Exibe mensagem de sucesso na criação de backup.
    
    Args:
        nome_backup: Nome do arquivo de backup criado
    """
    show_success(f"Backup '{nome_backup}' criado com sucesso!", icon="💾")


def show_import_summary(
    total: int,
    validos: int,
    invalidos: int,
    erros: Optional[List[str]] = None
) -> None:
    """
    Exibe resumo de importação.
    
    Args:
        total: Total de itens processados
        validos: Quantidade de itens válidos
        invalidos: Quantidade de itens inválidos
        erros: Lista de mensagens de erro
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total", total)
    with col2:
        st.metric("✅ Válidos", validos)
    with col3:
        st.metric("❌ Inválidos", invalidos)
    
    if erros and invalidos > 0:
        with st.expander("Ver erros"):
            for erro in erros:
                st.error(erro)


def show_loading_spinner(
    message: str = "Processando...",
    func: Optional[callable] = None
) -> Any:
    """
    Exibe spinner de carregamento.
    
    Args:
        message: Mensagem a ser exibida
        func: Função opcional a ser executada dentro do spinner
        
    Returns:
        Resultado da função se fornecida
    """
    with st.spinner(message):
        if func:
            return func()


# ============================================
# ALERTAS DE CURSO
# ============================================

def show_curso_salvo(curso_nome: str, is_new: bool = True) -> None:
    """
    Exibe mensagem de curso salvo.
    
    Args:
        curso_nome: Nome do curso
        is_new: Se é um curso novo ou atualização
    """
    acao = "cadastrado" if is_new else "atualizado"
    show_success(f"Curso '{curso_nome}' {acao} com sucesso!")


def show_curso_excluido(curso_nome: str) -> None:
    """
    Exibe mensagem de curso excluído.
    
    Args:
        curso_nome: Nome do curso
    """
    show_success(f"Curso '{curso_nome}' excluído com sucesso!")


# ============================================
# TOAST NOTIFICATIONS
# ============================================

def show_toast(
    message: str,
    type_: str = "info"
) -> None:
    """
    Exibe notificação toast (se suportado pela versão do Streamlit).
    
    Args:
        message: Mensagem a ser exibida
        type_: Tipo da notificação (info, success, warning, error)
    """
    try:
        if type_ == "success":
            st.toast(message, icon="✅")
        elif type_ == "error":
            st.toast(message, icon="❌")
        elif type_ == "warning":
            st.toast(message, icon="⚠️")
        else:
            st.toast(message, icon="ℹ️")
    except AttributeError:
        # Fallback para versões sem toast
        pass
