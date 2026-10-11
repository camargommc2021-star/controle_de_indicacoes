"""
Controle de Indicações - Aplicativo Principal

Sistema para gerenciamento de cursos.
Oferece funcionalidades para cadastro de cursos,
importação de dados, backup, LOGIN e CALENDÁRIO.

NOVIDADES v2.0:
- Sistema de Login com níveis de acesso (Admin/Editor/Viewer)
- Visualização em Calendário dos prazos
- Controle de permissões por funcionalidade

Usage:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List

# =============================================================================
# CONFIGURAÇÕES E CONSTANTES
# =============================================================================

from config import Settings, Columns, Choices, Messages, paths, colors

# =============================================================================
# LOGGER
# =============================================================================

from utils.logger import get_logger

logger = get_logger(__name__)

# =============================================================================
# COMPONENTES UI
# =============================================================================

from components import (
    show_success,
    show_error,
    show_warning,
    show_info,
    show_empty_state,
    show_validation_errors,
    render_sidebar,
    render_form_novo_curso,
    render_form_editar_curso,
    render_tabela_cursos,
    render_lista_cursos_por_estado,
    render_cursos_concluidos,
    render_metric_card,
)

from components.cards import get_cor_prazo, get_status_prazo
from components.calendar_view import CalendarView

# =============================================================================
# MANAGERS
# =============================================================================

from data_manager import DataManager
from dashboard import Dashboard
from backup_manager import BackupManager
from json_import import JSONImporter
from managers.auth_manager import AuthManager, NivelAcesso

# =============================================================================
# VALIDADORES
# =============================================================================

from utils.validators import (
    is_valid_date,
    validate_curso,
    sanitize_string,
)


# =============================================================================
# CONSTANTES DE UI
# =============================================================================

ICONS = {
    'dashboard': '📊',
    'lista': '📋',
    'novo': '➕',
    'editar': '✏️',
    'importar': '📥',
    'backup': '💾',
    'calendario': '📅',
    'usuarios': '👥',
    'login': '🔐',
    'logout': '🚪',
}


# =============================================================================
# FUNÇÕES DE CONFIGURAÇÃO
# =============================================================================

def load_css() -> None:
    """Carrega o CSS customizado."""
    css_path = Path("assets/style.css")
    
    try:
        if css_path.exists():
            with open(css_path, "r", encoding="utf-8") as f:
                css = f.read()
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except Exception as e:
        logger.error(f"Erro ao carregar CSS: {e}")


def init_session_state() -> None:
    """Inicializa variáveis de sessão do Streamlit."""
    try:
        if 'data_manager' not in st.session_state:
            st.session_state.data_manager = DataManager()
            logger.info("DataManager inicializado")
            
        if 'json_importer' not in st.session_state:
            st.session_state.json_importer = JSONImporter()
            
        if 'dashboard' not in st.session_state:
            st.session_state.dashboard = Dashboard()
            
        if 'backup_manager' not in st.session_state:
            st.session_state.backup_manager = BackupManager()
            
        # Auth Manager
        if 'auth_manager' not in st.session_state:
            st.session_state.auth_manager = AuthManager()
            logger.info("AuthManager inicializado")
        
        # Calendar View
        if 'calendar_view' not in st.session_state:
            st.session_state.calendar_view = CalendarView()
            
    except Exception as e:
        logger.error(f"Erro ao inicializar session state: {e}")
        show_error(Messages.ERROR_GENERIC, details=str(e))


# =============================================================================
# FUNÇÕES DE LOGIN/AUTH
# =============================================================================

def render_login_page() -> bool:
    """
    Renderiza página de login simples e funcional.
    """
    # Ocultar sidebar
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none !important;}
    .main > div {padding-top: 5rem !important;}
    </style>
    """, unsafe_allow_html=True)
    
    # Container centralizado
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        # Logo e título
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">🎓</div>
            <h1 style="color: #334155; margin: 0; font-size: 1.5rem;">Controle de Cursos</h1>
            <p style="color: #64748b; margin-top: 0.3rem; font-size: 0.9rem;">Sistema de Gestão de Indicações</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Formulário de login
        with st.form("login_form", clear_on_submit=False):
            st.subheader("Acesso ao Sistema")
            
            username = st.text_input(
                "Usuário",
                placeholder="Digite seu usuário",
                key="login_username"
            )
            
            password = st.text_input(
                "Senha",
                type="password",
                placeholder="Digite sua senha",
                key="login_password"
            )
            
            submitted = st.form_submit_button("Entrar", use_container_width=True, type="primary")
            
            if submitted:
                if username and password:
                    auth = st.session_state.auth_manager
                    sucesso, msg = auth.login(username, password)
                    
                    if sucesso:
                        st.success(msg)
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("Preencha usuário e senha")
    
    return st.session_state.auth_manager.autenticado


def render_header():
    """Renderiza o header limpo com informações do usuário."""
    auth = st.session_state.auth_manager
    
    if not auth.autenticado:
        return
    
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        st.title("📚 Controle de Cursos")
    
    with col2:
        nivel = auth.usuario_atual['nivel_acesso']
        nivel_label = {'admin': 'Admin', 'editor': 'Editor', 'viewer': 'Viewer'}.get(nivel, nivel)
        
        st.markdown(f"""
        <div style='text-align: right; padding-top: 0.5rem;'>
            <div style='font-size: 0.9rem; color: #64748b;'>
                {auth.usuario_atual['nome']}
            </div>
            <div style='font-size: 0.8rem; color: #94a3b8;'>
                {nivel_label}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("Sair", use_container_width=True):
            auth.logout()
            st.rerun()
    
    st.divider()


def verificar_permissao(permissao: str) -> bool:
    """
    Verifica se usuário tem permissão.
    
    Args:
        permissao: Nome da permissão
        
    Returns:
        True se tem permissão
    """
    auth = st.session_state.auth_manager
    if not auth.autenticado:
        return False
    return auth.pode(permissao)


# =============================================================================
# FUNÇÕES DE DADOS COM CACHE
# =============================================================================

@st.cache_data(ttl=60, show_spinner=False)
def carregar_dados_cursos() -> pd.DataFrame:
    """Carrega dados dos cursos com cache."""
    try:
        dm = DataManager()
        return dm.carregar_dados()
    except Exception as e:
        logger.error(f"Erro ao carregar cursos: {e}")
        return pd.DataFrame()


def clear_cache() -> None:
    """Limpa o cache de dados."""
    st.cache_data.clear()
    logger.info("Cache limpo")


# =============================================================================
# HANDLERS DE AÇÕES
# =============================================================================

def handle_excluir_curso(index: int) -> None:
    """Handler para exclusão de curso."""
    if not verificar_permissao('excluir_curso'):
        show_error("Sem permissão para excluir cursos")
        return
    
    try:
        sucesso, msg = st.session_state.data_manager.excluir_curso(index)
        if sucesso:
            show_success(msg)
            clear_cache()
            st.rerun()
        else:
            show_error(msg)
    except Exception as e:
        logger.error(f"Erro ao excluir curso {index}: {e}")
        show_error(Messages.ERROR_GENERIC, details=str(e))


def handle_importar_json(cursos_validos: List[Dict]) -> None:
    """Handler para importação de cursos via JSON."""
    if not verificar_permissao('criar_curso'):
        show_error("Sem permissão para importar cursos")
        return
        
    try:
        importados, erros = st.session_state.json_importer.importar_cursos(
            cursos_validos, st.session_state.data_manager
        )
        
        if importados > 0:
            show_success(f"{importados} curso(s) importado(s) com sucesso!")
            st.session_state.backup_manager.criar_backup()
            clear_cache()
            st.rerun()
        
        if erros:
            for erro in erros:
                show_error(erro)
                
    except Exception as e:
        logger.error(f"Erro na importação: {e}")
        show_error("Erro ao importar cursos", details=str(e))


def handle_restaurar_backup(caminho_backup: str) -> None:
    """Handler para restauração de backup."""
    if not verificar_permissao('fazer_backup'):
        show_error("Sem permissão para restaurar backups")
        return
        
    try:
        sucesso, msg = st.session_state.backup_manager.restaurar_backup(caminho_backup)
        if sucesso:
            show_success(msg)
            clear_cache()
            st.rerun()
        else:
            show_error(msg)
    except Exception as e:
        logger.error(f"Erro ao restaurar backup: {e}")
        show_error("Erro ao restaurar backup", details=str(e))


# =============================================================================
# SEÇÕES DAS ABAS
# =============================================================================

def render_tab_dashboard() -> None:
    """Renderiza a aba de Dashboard."""
    st.header(f"{ICONS['dashboard']} Dashboard")
    
    if not verificar_permissao('ver_dashboard'):
        st.error("Sem permissão para visualizar dashboard")
        return
    
    try:
        df = st.session_state.data_manager.carregar_dados()
        
        if df.empty:
            show_info("Nenhum curso cadastrado ainda. Use a aba 'Novo Curso' para adicionar.")
            return
        
        st.session_state.dashboard.mostrar_dashboard(df)
        
        st.subheader(f"{ICONS['lista']} Cursos por Estado")
        if 'Estado' in df.columns:
            from components.cards import render_estado_summary
            render_estado_summary(df)
            
    except Exception as e:
        logger.error(f"Erro no dashboard: {e}")
        show_error("Erro ao carregar dashboard", details=str(e))


def render_tab_lista_cursos() -> None:
    """Renderiza a aba de Lista de Cursos."""
    st.header(f"{ICONS['lista']} Lista de Cursos")
    
    if not verificar_permissao('ver_cursos'):
        st.error("Sem permissão para visualizar cursos")
        return
    
    try:
        termo_busca = st.text_input(
            "🔍 Buscar curso",
            placeholder="Digite para buscar...",
            key="busca_cursos"
        )
        
        df = st.session_state.data_manager.carregar_dados()
        
        if termo_busca:
            df = st.session_state.data_manager.buscar_curso(termo_busca)
        
        if df.empty:
            show_info("Nenhum curso encontrado.")
            return
        
        df_ativos = df[df['Estado'] != 'Concluído'].copy() if 'Estado' in df.columns else df.copy()
        df_concluidos = df[df['Estado'] == 'Concluído'].copy() if 'Estado' in df.columns else pd.DataFrame()
        
        if not df_ativos.empty:
            st.subheader(f"{ICONS['lista']} Cursos em Andamento")
            render_lista_cursos_por_estado(df_ativos, handle_excluir_curso)
        
        if not df_concluidos.empty:
            st.markdown("---")
            st.subheader(f"✅ Cursos Concluídos")
            render_cursos_concluidos(df_concluidos, handle_excluir_curso)
            
    except Exception as e:
        logger.error(f"Erro na lista de cursos: {e}")
        show_error("Erro ao carregar cursos", details=str(e))


def render_tab_novo_curso() -> None:
    """Renderiza a aba de Novo Curso."""
    st.header(f"{ICONS['novo']} Novo Curso")
    
    if not verificar_permissao('criar_curso'):
        st.error("Sem permissão para criar cursos")
        return
    
    try:
        resultado = render_form_novo_curso(
            st.session_state.data_manager,
            st.session_state.backup_manager
        )
        
        sucesso, msg = resultado
        
        if sucesso:
            show_success(msg)
            clear_cache()
        elif msg:
            if "AVISO" in msg:
                show_warning(msg.replace("AVISO: ", ""))
            else:
                show_error(msg)
                
    except Exception as e:
        logger.error(f"Erro ao renderizar formulário de novo curso: {e}")
        show_error("Erro ao exibir formulário", details=str(e))


def render_tab_editar_curso() -> None:
    """Renderiza a aba de Editar Curso."""
    st.header(f"{ICONS['editar']} Editar Curso")
    
    if not verificar_permissao('editar_curso'):
        st.error("Sem permissão para editar cursos")
        return
    
    try:
        df = st.session_state.data_manager.carregar_dados()
        
        if df.empty:
            show_info("Nenhum curso cadastrado para editar.")
            return
        
        opcoes = [f"{row['Curso']} - {row['Turma']}" for _, row in df.iterrows()]
        
        curso_selecionado = st.selectbox(
            "Selecione o curso",
            opcoes,
            key="select_editar_curso"
        )
        
        if curso_selecionado:
            idx_curso = opcoes.index(curso_selecionado)
            curso_atual = df.iloc[idx_curso]
            
            resultado = render_form_editar_curso(
                curso_atual,
                idx_curso,
                st.session_state.data_manager,
                list(df.columns)
            )
            
            sucesso, msg = resultado
            
            if sucesso:
                show_success(msg)
                clear_cache()
                st.rerun()
            elif msg:
                show_error(msg)
                
    except Exception as e:
        logger.error(f"Erro na edição de curso: {e}")
        show_error("Erro ao editar curso", details=str(e))


def render_tab_calendario() -> None:
    """Renderiza a aba de Calendário."""
    st.header(f"{ICONS['calendario']} Calendário de Prazos")
    
    if not verificar_permissao('ver_cursos'):
        st.error("Sem permissão para visualizar calendário")
        return
    
    try:
        df_cursos = st.session_state.data_manager.carregar_dados()
        
        if df_cursos.empty:
            show_info("Nenhum dado para exibir no calendário.")
            return
        
        # Usar o componente de calendário apenas com cursos
        cal = CalendarView(modo="mensal")
        cal.render(df_cursos)
        
    except Exception as e:
        logger.error(f"Erro no calendário: {e}")
        show_error("Erro ao carregar calendário", details=str(e))


def render_tab_importar_json() -> None:
    """Renderiza a aba de Importar JSON."""
    st.header(f"{ICONS['importar']} Importar JSON")
    
    if not verificar_permissao('criar_curso'):
        st.error("Sem permissão para importar cursos")
        return
    
    try:
        arquivo_json = st.file_uploader(
            "Selecione o arquivo JSON",
            type=['json'],
            key="upload_json"
        )
        
        if arquivo_json is None:
            return
        
        dados, erro = st.session_state.json_importer.carregar_json(arquivo_json.getvalue())
        
        if erro:
            show_error(erro)
            return
        
        cursos_validos, cursos_invalidos = st.session_state.json_importer.validar_json(dados)
        resumo = st.session_state.json_importer.get_resumo_validacao()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total", resumo['total'])
        with col2:
            st.metric("✅ Válidos", resumo['validos'])
        with col3:
            st.metric("❌ Inválidos", resumo['invalidos'])
        
        if cursos_validos:
            st.subheader("✅ Cursos Válidos")
            for curso in cursos_validos:
                st.write(f"- {curso.get('Curso', 'Sem nome')} - {curso.get('Turma', 'N/A')}")
        
        if cursos_invalidos:
            st.subheader("❌ Cursos Inválidos")
            for item in cursos_invalidos:
                show_error(f"{item['curso']}: {item['erro']}")
        
        if cursos_validos and st.button(f"{ICONS['importar']} Importar Cursos Válidos", key="btn_importar"):
            handle_importar_json(cursos_validos)
            
    except Exception as e:
        logger.error(f"Erro na importação JSON: {e}")
        show_error("Erro ao processar JSON", details=str(e))


def render_tab_backup() -> None:
    """Renderiza a aba de Backup."""
    st.header(f"{ICONS['backup']} Gerenciamento de Backups")
    
    if not verificar_permissao('ver_cursos'):
        st.error("Sem permissão")
        return
    
    try:
        st.subheader(f"{ICONS['backup']} Criar Backup")
        if verificar_permissao('fazer_backup'):
            if st.button(f"{ICONS['backup']} Criar Backup Agora", key="btn_backup"):
                with st.spinner("Criando backup..."):
                    sucesso, msg = st.session_state.backup_manager.criar_backup()
                    if sucesso:
                        show_success(msg)
                        st.rerun()
                    else:
                        show_error(msg)
        else:
            st.info("Apenas admins podem criar backups")
        
        st.subheader(f"{ICONS['lista']} Backups Disponíveis")
        backups = st.session_state.backup_manager.listar_backups()
        
        if not backups:
            show_info("Nenhum backup criado ainda.")
        else:
            for backup in backups:
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.write(f"💾 {backup['nome']}")
                
                with col2:
                    data_fmt = backup['data'].strftime('%d/%m/%Y %H:%M')
                    tamanho_kb = backup['tamanho'] / 1024
                    st.caption(f"{data_fmt} - {tamanho_kb:.1f} KB")
                
                with col3:
                    if verificar_permissao('fazer_backup'):
                        btn_key = f"restore_{backup['nome'].replace('.', '_')}"
                        if st.button("🔄 Restaurar", key=btn_key):
                            handle_restaurar_backup(backup['caminho'])
                    else:
                        st.caption("Apenas view")
                        
    except Exception as e:
        logger.error(f"Erro na aba backup: {e}")
        show_error("Erro ao carregar backups", details=str(e))


def render_tab_usuarios() -> None:
    """Renderiza a aba de Gerenciamento de Usuários (Admin apenas)."""
    st.header(f"{ICONS['usuarios']} Gerenciamento de Usuários")
    
    auth = st.session_state.auth_manager
    
    if not auth.permissoes.gerenciar_usuarios:
        st.error("Apenas administradores podem acessar esta página")
        return
    
    try:
        # Abas de gerenciamento
        tab_lista, tab_novo, tab_editar, tab_senha = st.tabs([
            "📋 Lista",
            "➕ Novo",
            "✏️ Editar",
            "🔑 Senhas"
        ])
        
        with tab_lista:
            df_usuarios = auth.listar_usuarios()
            
            if df_usuarios.empty:
                show_info("Nenhum usuário cadastrado")
            else:
                st.dataframe(
                    df_usuarios,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Ações por usuário
                st.subheader("Ações")
                col1, col2 = st.columns(2)
                
                with col1:
                    username_bloquear = st.selectbox(
                        "Usuário para desativar",
                        df_usuarios[df_usuarios['ativo'] == True]['username'].tolist(),
                        key="select_bloquear"
                    )
                    if st.button("🚫 Desativar Usuário", key="btn_desativar"):
                        sucesso, msg = auth.desativar_usuario(username_bloquear)
                        if sucesso:
                            show_success(msg)
                            st.rerun()
                        else:
                            show_error(msg)
                
                with col2:
                    username_reset = st.selectbox(
                        "Usuário para resetar senha",
                        df_usuarios['username'].tolist(),
                        key="select_reset"
                    )
                    nova_senha_reset = st.text_input(
                        "Nova senha",
                        type="password",
                        key="senha_reset"
                    )
                    if st.button("🔄 Redefinir Senha", key="btn_reset"):
                        if nova_senha_reset:
                            sucesso, msg = auth.redefinir_senha(username_reset, nova_senha_reset)
                            if sucesso:
                                show_success(msg)
                            else:
                                show_error(msg)
                        else:
                            show_error("Digite uma nova senha")
        
        with tab_novo:
            with st.form("form_novo_usuario"):
                st.subheader("Criar Novo Usuário")
                
                novo_username = st.text_input("Nome de usuário*")
                novo_nome = st.text_input("Nome completo*")
                novo_email = st.text_input("Email*")
                novo_nivel = st.selectbox(
                    "Nível de acesso*",
                    ["admin", "editor", "viewer"],
                    format_func=lambda x: {
                        "admin": "🔴 Administrador (Acesso total)",
                        "editor": "🟡 Editor (CRUD cursos)",
                        "viewer": "🟢 Visualizador (Apenas leitura)"
                    }[x]
                )
                nova_senha = st.text_input("Senha inicial*", type="password")
                
                submitted = st.form_submit_button("Criar Usuário", type="primary")
                
                if submitted:
                    if all([novo_username, novo_nome, novo_email, nova_senha]):
                        sucesso, msg = auth.criar_usuario(
                            novo_username, novo_nome, novo_email,
                            novo_nivel, nova_senha
                        )
                        if sucesso:
                            show_success(msg)
                            st.rerun()
                        else:
                            show_error(msg)
                    else:
                        show_error("Preencha todos os campos obrigatórios")
        
        with tab_editar:
            st.subheader("Editar Usuário")
            
            df_usuarios_edit = auth.listar_usuarios()
            
            if df_usuarios_edit.empty:
                show_info("Nenhum usuário cadastrado")
            else:
                # Selecionar usuário para editar
                usuario_selecionado = st.selectbox(
                    "Selecione o usuário para editar",
                    df_usuarios_edit['username'].tolist(),
                    key="select_editar"
                )
                
                # Carregar dados do usuário selecionado
                usuario_atual = df_usuarios_edit[df_usuarios_edit['username'] == usuario_selecionado].iloc[0]
                
                with st.form("form_editar_usuario"):
                    st.markdown("##### Dados do Usuário")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        edit_username = st.text_input(
                            "Username (Login)*",
                            value=usuario_atual['username']
                        )
                        edit_nome = st.text_input(
                            "Nome completo*",
                            value=usuario_atual['nome']
                        )
                    
                    with col2:
                        edit_email = st.text_input(
                            "Email*",
                            value=usuario_atual['email']
                        )
                        edit_nivel = st.selectbox(
                            "Nível de acesso*",
                            ["admin", "editor", "viewer"],
                            index=["admin", "editor", "viewer"].index(usuario_atual['nivel_acesso']),
                            format_func=lambda x: {
                                "admin": "🔴 Administrador",
                                "editor": "🟡 Editor",
                                "viewer": "🟢 Visualizador"
                            }[x]
                        )
                    
                    st.markdown("---")
                    st.caption("*Campos obrigatórios")
                    
                    submitted = st.form_submit_button("💾 Salvar Alterações", type="primary")
                    
                    if submitted:
                        if all([edit_username, edit_nome, edit_email]):
                            sucesso, msg = auth.editar_usuario(
                                usuario_selecionado,  # username atual
                                edit_username,        # novo username
                                edit_nome,
                                edit_email,
                                edit_nivel
                            )
                            if sucesso:
                                show_success(msg)
                                st.rerun()
                            else:
                                show_error(msg)
                        else:
                            show_error("Preencha todos os campos obrigatórios")
        
        with tab_senha:
            st.subheader("Alterar Minha Senha")
            
            with st.form("form_alterar_senha"):
                senha_atual = st.text_input("Senha atual", type="password")
                senha_nova = st.text_input("Nova senha", type="password")
                senha_confirmar = st.text_input("Confirmar nova senha", type="password")
                
                submitted = st.form_submit_button("Alterar Senha", type="primary")
                
                if submitted:
                    if senha_nova != senha_confirmar:
                        show_error("As senhas não coincidem")
                    elif len(senha_nova) < 6:
                        show_error("Senha deve ter no mínimo 6 caracteres")
                    else:
                        sucesso, msg = auth.alterar_senha(
                            auth.usuario_atual['username'],
                            senha_atual,
                            senha_nova
                        )
                        if sucesso:
                            show_success(msg)
                        else:
                            show_error(msg)
                            
    except Exception as e:
        logger.error(f"Erro na aba usuários: {e}")
        show_error("Erro ao carregar usuários", details=str(e))


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Função principal do aplicativo."""
    st.set_page_config(
        page_title=Settings.PAGE_TITLE,
        page_icon=Settings.PAGE_ICON,
        layout=Settings.PAGE_LAYOUT,
        initial_sidebar_state="expanded"
    )
    
    load_css()
    init_session_state()
    
    auth = st.session_state.auth_manager
    
    # Verificar se está autenticado
    if not auth.autenticado:
        render_login_page()
        return
    
    # Renderizar header com infos do usuário
    render_header()
    
    # Sidebar
    render_sidebar(st.session_state.data_manager)
    
    # Definir abas baseadas nas permissões
    abas_disponiveis = []
    
    if auth.pode('ver_dashboard'):
        abas_disponiveis.append(("📊 Dashboard", render_tab_dashboard))
    
    if auth.pode('ver_cursos'):
        abas_disponiveis.append(("📋 Lista de Cursos", render_tab_lista_cursos))
    
    if auth.pode('criar_curso'):
        abas_disponiveis.append(("➕ Novo Curso", render_tab_novo_curso))
    
    if auth.pode('editar_curso'):
        abas_disponiveis.append(("✏️ Editar Curso", render_tab_editar_curso))
    
    # Calendário disponível para quem pode ver cursos
    if auth.pode('ver_cursos'):
        abas_disponiveis.append(("📅 Calendário", render_tab_calendario))
    
    if auth.pode('criar_curso'):
        abas_disponiveis.append(("📥 Importar JSON", render_tab_importar_json))
    
    abas_disponiveis.append(("💾 Backup", render_tab_backup))
    
    # Aba de usuários apenas para admins
    if auth.permissoes.gerenciar_usuarios:
        abas_disponiveis.append(("👥 Usuários", render_tab_usuarios))
    
    # Criar tabs
    tabs = st.tabs([nome for nome, _ in abas_disponiveis])
    
    # Renderizar cada aba
    for tab, (_, render_func) in zip(tabs, abas_disponiveis):
        with tab:
            render_func()


if __name__ == "__main__":
    main()
