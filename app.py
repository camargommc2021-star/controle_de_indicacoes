"""
Controle de Indicações - Aplicativo Principal

Sistema para controle de cursos militares, indicações e seus prazos (SIAT, SIGAD, OM).
Interface redesenhada no conceito 'fichas de progresso' (flight progress strips),
sem emojis decorativos, com linguagem direta e padrão visual austero.
"""

from pathlib import Path
from typing import Dict, List, Optional
import streamlit as st
import pandas as pd
from datetime import date

# =============================================================================
# CONFIGURAÇÕES E CONSTANTES
# =============================================================================

from config import Settings, Messages

# =============================================================================
# LOGGER
# =============================================================================

from utils.logger import get_logger

logger = get_logger(__name__)

# =============================================================================
# COMPONENTES UI
# =============================================================================

from components import (
    page_title,
    show_success,
    show_error,
    show_warning,
    show_info,
    render_faixa_curso,
    render_cabecalho_cursos,
    render_form_novo_curso,
    render_form_editar_curso,
    render_sidebar,
    CalendarView,
    plural,
    limpar_confirmacoes_exclusao,
)

# =============================================================================
# MANAGERS E VALIDADORES
# =============================================================================

from data_manager import DataManager
from dashboard import Dashboard
from backup_manager import BackupManager
from json_import import JSONImporter
from managers.auth_manager import AuthManager
from utils.validators import parse_data, limpar_valor, curso_concluido


# =============================================================================
# CARREGAMENTO DE RECURSOS E SESSÃO
# =============================================================================

def load_css() -> None:
    """Carrega fontes do Google Fonts e o arquivo de estilos customizado."""
    fonts_link = (
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Barlow:wght@400;500;600&display=swap" rel="stylesheet">'
    )
    st.markdown(fonts_link, unsafe_allow_html=True)

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

        if 'auth_manager' not in st.session_state:
            st.session_state.auth_manager = AuthManager()
            logger.info("AuthManager inicializado")

        if 'calendar_view' not in st.session_state:
            st.session_state.calendar_view = CalendarView()

        if 'pagina' not in st.session_state:
            st.session_state.pagina = "painel"

        if 'cursos_limite' not in st.session_state:
            st.session_state.cursos_limite = 25

        if 'filtro_status' not in st.session_state:
            st.session_state.filtro_status = "Todos"

    except Exception as e:
        logger.error(f"Erro ao inicializar session state: {e}")
        show_error("Ocorreu um erro ao inicializar os serviços do sistema.", details=str(e))


def clear_cache() -> None:
    """Limpa o cache de dados do Streamlit."""
    st.cache_data.clear()
    logger.info("Cache limpo")


def verificar_permissao(permissao: str) -> bool:
    """Verifica se o usuário autenticado possui a permissão informada."""
    auth = st.session_state.auth_manager
    if not auth.autenticado:
        return False
    return auth.pode(permissao)


# =============================================================================
# PÁGINA DE LOGIN
# =============================================================================

def render_login_page() -> bool:
    """
    Renderiza página de login centralizada em coluna de 400px de largura sobre --paper.
    """
    st.markdown("""
    <style>
    [data-testid="stSidebar"],
    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }
    .main > div {
        padding-top: 5vh !important;
    }
    </style>
    """, unsafe_allow_html=True)

    col_l, col_center, col_r = st.columns([1, 1.2, 1])

    with col_center:
        with st.container(key="login_wrapper"):
            st.markdown("""
            <div class="login-header">
              <h1 class="login-title">Controle de Cursos</h1>
              <p class="login-helper">Entre com seu usuário para acessar as indicações.</p>
            </div>
            """, unsafe_allow_html=True)

            with st.form("login_form", clear_on_submit=False):
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

                submitted = st.form_submit_button(
                    "Entrar",
                    type="primary",
                    use_container_width=True,
                    icon=":material/login:"
                )

                if submitted:
                    if username and password:
                        auth = st.session_state.auth_manager
                        sucesso, msg = auth.login(username, password)
                        if sucesso:
                            st.session_state.pagina = "painel"
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.warning("Preencha o usuário e a senha.")

    return st.session_state.auth_manager.autenticado


# =============================================================================
# HANDLERS DE AÇÕES
# =============================================================================

def handle_excluir_curso(index: int) -> None:
    """Handler para exclusão de curso com validação de permissão."""
    if not verificar_permissao('excluir_curso'):
        show_error("Sem permissão para excluir cursos.")
        return

    try:
        limpar_confirmacoes_exclusao()
        sucesso, msg = st.session_state.data_manager.excluir_curso(index)
        if sucesso:
            limpar_confirmacoes_exclusao()
            st.toast("Curso excluído.", icon=":material/check_circle:")
            clear_cache()
            st.rerun()
        else:
            show_error(msg)
    except Exception as e:
        logger.error(f"Erro ao excluir curso {index}: {e}")
        show_error("Erro ao excluir curso.", details=str(e))


def handle_importar_json(cursos_validos: List[Dict]) -> None:
    """Handler para importação de cursos via arquivo JSON."""
    if not verificar_permissao('criar_curso'):
        show_error("Sem permissão para importar cursos.")
        return

    try:
        importados, erros = st.session_state.json_importer.importar_cursos(
            cursos_validos, st.session_state.data_manager
        )

        if importados > 0:
            st.toast(f"{importados} curso(s) importado(s) com sucesso.", icon=":material/check_circle:")
            st.session_state.backup_manager.criar_backup()
            clear_cache()
            st.rerun()

        if erros:
            for erro in erros:
                show_error(erro)

    except Exception as e:
        logger.error(f"Erro na importação: {e}")
        show_error("Erro ao importar cursos.", details=str(e))


def handle_restaurar_backup(caminho_backup: str) -> None:
    """Handler para restauração de cópia de segurança (backup)."""
    if not verificar_permissao('fazer_backup'):
        show_error("Sem permissão para restaurar backups.")
        return

    try:
        sucesso, msg = st.session_state.backup_manager.restaurar_backup(caminho_backup)
        if sucesso:
            st.toast("Backup restaurado com sucesso.", icon=":material/check_circle:")
            clear_cache()
            st.rerun()
        else:
            show_error(msg)
    except Exception as e:
        logger.error(f"Erro ao restaurar backup: {e}")
        show_error("Erro ao restaurar backup.", details=str(e))


# =============================================================================
# PÁGINAS DO SISTEMA
# =============================================================================

def render_pagina_painel() -> None:
    """Renderiza a página Painel (Dashboard)."""
    page_title("Painel", "Visão geral dos prazos e andamento das indicações.")

    if not verificar_permissao('ver_dashboard'):
        st.error("Sem permissão para visualizar o painel.")
        return

    try:
        df = st.session_state.data_manager.carregar_dados()
        st.session_state.dashboard.mostrar_dashboard(df)
    except Exception as e:
        logger.error(f"Erro no painel: {e}")
        show_error("Erro ao carregar o painel.", details=str(e))


def render_pagina_cursos() -> None:
    """
    Renderiza a lista de cursos em fichas de progresso com filtros segmentados,
    ordenação por vencimento e paginação em blocos de 25.
    """
    page_title("Cursos", "Fichas de progresso com prazos e etapas das indicações.")

    if not verificar_permissao('ver_cursos'):
        st.error("Sem permissão para visualizar cursos.")
        return

    try:
        df = st.session_state.data_manager.carregar_dados()

        if df.empty:
            show_info("Nenhum curso cadastrado ainda. Use a página 'Novo curso' para adicionar.")
            return

        hoje = date.today()

        # Contagens para os botões segmentados de status
        c_atrasados = 0
        c_urgentes = 0
        c_no_prazo = 0
        c_sem_prazo = 0
        c_concluidos = 0

        for _, r in df.iterrows():
            if curso_concluido(r):
                c_concluidos += 1
                continue
            d = parse_data(r.get('Fim da indicação da SIAT'))
            if d is None:
                c_sem_prazo += 1
            else:
                dias = (d - hoje).days
                if dias < 0:
                    c_atrasados += 1
                elif dias <= 5:
                    c_urgentes += 1
                else:
                    c_no_prazo += 1

        counts_status = {
            "Todos": len(df),
            "Atrasados": c_atrasados,
            "Próximos 5 dias": c_urgentes,
            "No prazo": c_no_prazo,
            "Sem prazo": c_sem_prazo,
            "Concluídos": c_concluidos
        }

        # Barra de ferramentas
        col_busca, col_estado = st.columns([7, 3], gap="small")
        with col_busca:
            termo_busca = st.text_input(
                "Buscar cursos",
                placeholder="Buscar por código, turma ou SIGAD",
                key="input_busca_cursos",
                label_visibility="collapsed"
            )

        with col_estado:
            opcoes_etapa = [
                "Todas as etapas",
                "solicitar voluntários",
                "fazer indicação",
                "ver vagas escalantes",
                "Concluído",
                "Sem etapa"
            ]
            etapa_sel = st.selectbox(
                "Etapa",
                opcoes_etapa,
                index=0,
                key="select_filtro_etapa",
                label_visibility="collapsed"
            )

        # Filtro segmentado de status
        def formatar_status_label(opt: str) -> str:
            count = counts_status.get(opt, 0)
            return f"{opt} {count}"

        opcoes_status = list(counts_status.keys())
        default_status = st.session_state.get("filtro_status", "Todos")
        if default_status not in opcoes_status:
            default_status = "Todos"

        status_sel = st.segmented_control(
            "Filtro de prazo",
            options=opcoes_status,
            default=default_status,
            format_func=formatar_status_label,
            key="segmented_status_filter",
            label_visibility="collapsed"
        )
        if not status_sel:
            status_sel = "Todos"
        st.session_state.filtro_status = status_sel

        # Reset de paginação quando os filtros mudam
        sig_atual = (
            termo_busca.strip() if termo_busca else "",
            etapa_sel,
            status_sel
        )
        if st.session_state.get("_filtros_sig") != sig_atual:
            st.session_state["_filtros_sig"] = sig_atual
            st.session_state.cursos_limite = 25

        # Filtragem dos dados
        df_filtrado = df.copy()

        # 1. Filtro textual
        if termo_busca and termo_busca.strip():
            termo = termo_busca.strip().lower()
            df_filtrado = df_filtrado[df_filtrado.apply(
                lambda r: any(termo in str(val).lower() for val in r.values if pd.notna(val)),
                axis=1
            )]

        # 2. Filtro de status
        if status_sel == "Atrasados":
            df_filtrado = df_filtrado[df_filtrado.apply(
                lambda r: (not curso_concluido(r)) and parse_data(r.get('Fim da indicação da SIAT')) is not None and (parse_data(r.get('Fim da indicação da SIAT')) - hoje).days < 0,
                axis=1
            )]
        elif status_sel == "Próximos 5 dias":
            df_filtrado = df_filtrado[df_filtrado.apply(
                lambda r: (not curso_concluido(r)) and parse_data(r.get('Fim da indicação da SIAT')) is not None and 0 <= (parse_data(r.get('Fim da indicação da SIAT')) - hoje).days <= 5,
                axis=1
            )]
        elif status_sel == "No prazo":
            df_filtrado = df_filtrado[df_filtrado.apply(
                lambda r: (not curso_concluido(r)) and parse_data(r.get('Fim da indicação da SIAT')) is not None and (parse_data(r.get('Fim da indicação da SIAT')) - hoje).days > 5,
                axis=1
            )]
        elif status_sel == "Sem prazo":
            df_filtrado = df_filtrado[df_filtrado.apply(
                lambda r: (not curso_concluido(r)) and parse_data(r.get('Fim da indicação da SIAT')) is None,
                axis=1
            )]
        elif status_sel == "Concluídos":
            df_filtrado = df_filtrado[df_filtrado.apply(curso_concluido, axis=1)]

        # 3. Filtro de etapa
        if etapa_sel != "Todas as etapas":
            if etapa_sel == "Sem etapa":
                df_filtrado = df_filtrado[df_filtrado.apply(
                    lambda r: not curso_concluido(r) and not limpar_valor(r.get('Estado')),
                    axis=1
                )]
            elif etapa_sel == "Concluído":
                df_filtrado = df_filtrado[df_filtrado.apply(curso_concluido, axis=1)]
            else:
                norm_sel = etapa_sel.strip().lower()
                df_filtrado = df_filtrado[df_filtrado.apply(
                    lambda r: not curso_concluido(r) and limpar_valor(r.get('Estado')).strip().lower() == norm_sel,
                    axis=1
                )]

        if df_filtrado.empty:
            show_info("Nenhum curso encontrado. Ajuste a busca ou os filtros.")
            return

        # Ordenação por vencimento (atrasados e prazos mais próximos primeiro, sem prazo depois, concluídos por último)
        def chave_ordenacao(item):
            idx, r = item
            concluido = curso_concluido(r)
            d_siat = parse_data(r.get('Fim da indicação da SIAT'))
            cod = str(r.get('Curso', ''))

            if not concluido:
                if d_siat is not None:
                    return (0, d_siat, cod)
                else:
                    return (1, date.max, cod)
            else:
                d_conc = parse_data(r.get('DATA_DA_CONCLUSAO')) or date.max
                return (2, d_conc, cod)

        itens_ordenados = list(df_filtrado.iterrows())
        itens_ordenados.sort(key=chave_ordenacao)

        # Paginação
        total_encontrados = len(itens_ordenados)
        limite = st.session_state.get("cursos_limite", 25)
        exibir_itens = itens_ordenados[:limite]

        st.markdown(
            f'<div style="font-size: 13px; color: var(--ink-soft); margin: 0.75rem 0 0.5rem 0; font-variant-numeric: tabular-nums;">'
            f'Mostrando {len(exibir_itens)} de {total_encontrados} {plural(total_encontrados, "curso", "cursos")}</div>',
            unsafe_allow_html=True
        )

        can_edit = verificar_permissao('editar_curso')
        can_delete = verificar_permissao('excluir_curso')

        def on_edit_curso(idx_edit: int) -> None:
            st.session_state.curso_editando = idx_edit
            st.session_state.pagina = "editar"
            st.rerun()

        render_cabecalho_cursos()

        for idx, row in exibir_itens:
            render_faixa_curso(
                row=row,
                idx=idx,
                on_edit=on_edit_curso,
                on_delete=handle_excluir_curso,
                can_edit=can_edit,
                can_delete=can_delete
            )

        # Botão de paginação
        if total_encontrados > limite:
            mais_qtd = min(25, total_encontrados - limite)
            if st.button(
                f"Mostrar mais {mais_qtd}",
                key="btn_mostrar_mais",
                type="secondary",
                icon=":material/expand_more:",
                use_container_width=True
            ):
                st.session_state.cursos_limite = limite + 25
                st.rerun()

    except Exception as e:
        logger.error(f"Erro na lista de cursos: {e}")
        show_error("Erro ao carregar os cursos.", details=str(e))


def render_pagina_novo_curso() -> None:
    """Renderiza a página de cadastro de novo curso."""
    page_title("Novo curso", "Preencha as informações da indicação e do curso.")

    if not verificar_permissao('criar_curso'):
        st.error("Sem permissão para criar cursos.")
        return

    try:
        resultado = render_form_novo_curso(
            st.session_state.data_manager,
            st.session_state.backup_manager
        )
        sucesso, msg = resultado

        if sucesso:
            st.toast(msg or "Curso salvo.", icon=":material/check_circle:")
            clear_cache()
        elif msg:
            if "AVISO" in msg:
                show_warning(msg.replace("AVISO: ", ""))
            else:
                show_error(msg)

    except Exception as e:
        logger.error(f"Erro no formulário de novo curso: {e}")
        show_error("Erro ao exibir formulário.", details=str(e))


def render_pagina_editar_curso() -> None:
    """
    Renderiza a edição do curso selecionado (ou fallback por lista se acessado diretamente).
    """
    page_title("Editar curso", "Atualize as informações do curso e prazos.")

    if not verificar_permissao('editar_curso'):
        st.error("Sem permissão para editar cursos.")
        return

    col_voltar, _ = st.columns([2, 8])
    with col_voltar:
        if st.button("Voltar para cursos", key="btn_voltar_de_editar", icon=":material/arrow_back:", type="secondary"):
            st.session_state.pagina = "cursos"
            st.session_state.curso_editando = None
            st.rerun()

    try:
        df = st.session_state.data_manager.carregar_dados()

        if df.empty:
            show_info("Nenhum curso cadastrado para editar.")
            return

        idx_editando = st.session_state.get("curso_editando")

        # Fallback de seleção se não houver curso definido
        if idx_editando is None or idx_editando < 0 or idx_editando >= len(df):
            opcoes = [f"{row['Curso']} - {row['Turma']}" for _, row in df.iterrows()]
            curso_selecionado = st.selectbox(
                "Selecione o curso",
                opcoes,
                key="select_editar_curso_fallback"
            )
            idx_editando = opcoes.index(curso_selecionado) if curso_selecionado else 0

        curso_atual = df.iloc[idx_editando]

        resultado = render_form_editar_curso(
            curso_atual,
            idx_editando,
            st.session_state.data_manager,
            list(df.columns)
        )

        sucesso, msg = resultado
        if sucesso:
            st.toast(msg or "Alterações salvas.", icon=":material/check_circle:")
            clear_cache()
            st.rerun()
        elif msg:
            show_error(msg)

    except Exception as e:
        logger.error(f"Erro na edição de curso: {e}")
        show_error("Erro ao editar curso.", details=str(e))


def render_pagina_calendario() -> None:
    """Renderiza a página Calendário de Prazos."""
    page_title("Calendário", "Visualização mensal dos prazos da SIAT, chefia e conclusões.")

    if not verificar_permissao('ver_cursos'):
        st.error("Sem permissão para visualizar o calendário.")
        return

    try:
        df = st.session_state.data_manager.carregar_dados()

        if df.empty:
            show_info("Nenhum dado para exibir no calendário.")
            return

        st.session_state.calendar_view.render(df)

    except Exception as e:
        logger.error(f"Erro no calendário: {e}")
        show_error("Erro ao carregar o calendário.", details=str(e))


def render_pagina_importar_json() -> None:
    """Renderiza a página de importação de arquivo JSON."""
    page_title("Importar cursos", "Envie o arquivo JSON com os cursos e datas.")

    if not verificar_permissao('criar_curso'):
        st.error("Sem permissão para importar cursos.")
        return

    try:
        arquivo_json = st.file_uploader(
            "Selecione o arquivo JSON",
            type=['json'],
            key="upload_json",
            label_visibility="collapsed"
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
            st.metric("Válidos", resumo['validos'])
        with col3:
            st.metric("Inválidos", resumo['invalidos'])

        if cursos_validos:
            st.markdown('<div class="section-title">Cursos válidos</div>', unsafe_allow_html=True)
            for curso in cursos_validos:
                st.write(f"- {curso.get('Curso', 'Sem nome')} - {curso.get('Turma', 'Sem turma')}")

        if cursos_invalidos:
            st.markdown('<div class="section-title">Cursos inválidos</div>', unsafe_allow_html=True)
            for item in cursos_invalidos:
                show_error(f"{item['curso']}: {item['erro']}")

        if cursos_validos:
            if st.button("Importar cursos válidos", key="btn_importar_confirmar", type="primary", icon=":material/upload:"):
                handle_importar_json(cursos_validos)

    except Exception as e:
        logger.error(f"Erro na importação JSON: {e}")
        show_error("Erro ao processar JSON.", details=str(e))


def render_pagina_backup() -> None:
    """Renderiza a página de gerenciamento de backups."""
    page_title("Backup", "Cópias internas da base de cursos.")

    if not verificar_permissao('ver_cursos'):
        st.error("Sem permissão para acessar backups.")
        return

    try:
        st.markdown('<div class="section-title">Criar backup</div>', unsafe_allow_html=True)
        if verificar_permissao('fazer_backup'):
            if st.button("Criar backup agora", key="btn_criar_backup", type="primary", icon=":material/save:"):
                with st.spinner("Criando backup..."):
                    sucesso, msg = st.session_state.backup_manager.criar_backup()
                    if sucesso:
                        st.toast("Backup criado com sucesso.", icon=":material/check_circle:")
                        st.rerun()
                    else:
                        show_error(msg)
        else:
            st.info("Apenas administradores podem criar novos backups.")

        st.markdown('<div class="section-title" style="margin-top: 1.5rem;">Backups disponíveis</div>', unsafe_allow_html=True)
        backups = st.session_state.backup_manager.listar_backups()

        if not backups:
            show_info("Nenhum backup criado até o momento.")
        else:
            for backup in backups:
                col1, col2, col3 = st.columns([4, 2, 2], gap="small")

                with col1:
                    st.write(backup['nome'])

                with col2:
                    data_fmt = backup['data'].strftime('%d/%m/%Y %H:%M')
                    tamanho_kb = backup['tamanho'] / 1024
                    st.caption(f"{data_fmt} • {tamanho_kb:.1f} KB")

                with col3:
                    if verificar_permissao('fazer_backup'):
                        btn_key = f"restore_{backup['nome'].replace('.', '_')}"
                        if st.button("Restaurar", key=btn_key, icon=":material/restore:", type="secondary", use_container_width=True):
                            handle_restaurar_backup(backup['caminho'])
                    else:
                        st.caption("Apenas visualização")

    except Exception as e:
        logger.error(f"Erro na página de backup: {e}")
        show_error("Erro ao carregar backups.", details=str(e))


def render_pagina_usuarios() -> None:
    """Renderiza a página de gerenciamento de usuários (administração)."""
    page_title("Usuários", "Gerenciamento de acessos e permissões do sistema.")

    auth = st.session_state.auth_manager
    if not auth.permissoes.gerenciar_usuarios:
        st.error("Apenas administradores podem acessar esta página.")
        return

    try:
        tab_lista, tab_novo, tab_editar, tab_senha = st.tabs([
            "Lista",
            "Novo usuário",
            "Editar usuário",
            "Alterar senha"
        ])

        with tab_lista:
            df_usuarios = auth.listar_usuarios()

            if df_usuarios.empty:
                show_info("Nenhum usuário cadastrado.")
            else:
                st.dataframe(df_usuarios, use_container_width=True, hide_index=True)

                st.markdown('<div class="section-title">Ações</div>', unsafe_allow_html=True)
                col1, col2 = st.columns(2)

                with col1:
                    usuarios_ativos = df_usuarios[df_usuarios['ativo'] == True]['username'].tolist()
                    if usuarios_ativos:
                        username_bloquear = st.selectbox(
                            "Usuário para desativar",
                            usuarios_ativos,
                            key="select_bloquear"
                        )
                        if st.button("Desativar usuário", key="btn_desativar", icon=":material/block:", type="secondary"):
                            sucesso, msg = auth.desativar_usuario(username_bloquear)
                            if sucesso:
                                st.toast(msg, icon=":material/check_circle:")
                                st.rerun()
                            else:
                                show_error(msg)

                with col2:
                    username_reset = st.selectbox(
                        "Usuário para redefinir senha",
                        df_usuarios['username'].tolist(),
                        key="select_reset"
                    )
                    nova_senha_reset = st.text_input(
                        "Nova senha",
                        type="password",
                        key="senha_reset"
                    )
                    if st.button("Redefinir senha", key="btn_reset", icon=":material/lock_reset:", type="secondary"):
                        if nova_senha_reset:
                            sucesso, msg = auth.redefinir_senha(username_reset, nova_senha_reset)
                            if sucesso:
                                show_success(msg)
                            else:
                                show_error(msg)
                        else:
                            show_error("Digite a nova senha.")

        with tab_novo:
            with st.form("form_novo_usuario"):
                st.markdown('<div class="section-title">Criar novo usuário</div>', unsafe_allow_html=True)

                novo_username = st.text_input("Nome de usuário *")
                novo_nome = st.text_input("Nome completo *")
                novo_email = st.text_input("E-mail *")
                novo_nivel = st.selectbox(
                    "Nível de acesso *",
                    ["admin", "editor", "viewer"],
                    format_func=lambda x: {
                        "admin": "Administrador (acesso total)",
                        "editor": "Editor (criação e edição de cursos)",
                        "viewer": "Visualizador (apenas leitura)"
                    }[x]
                )
                nova_senha = st.text_input("Senha inicial *", type="password")

                submitted = st.form_submit_button("Criar usuário", type="primary", icon=":material/person_add:")

                if submitted:
                    if all([novo_username, novo_nome, novo_email, nova_senha]):
                        sucesso, msg = auth.criar_usuario(
                            novo_username, novo_nome, novo_email,
                            novo_nivel, nova_senha
                        )
                        if sucesso:
                            st.toast(msg, icon=":material/check_circle:")
                            st.rerun()
                        else:
                            show_error(msg)
                    else:
                        show_error("Preencha todos os campos obrigatórios marcados com asterisco (*).")

        with tab_editar:
            st.markdown('<div class="section-title">Editar usuário</div>', unsafe_allow_html=True)
            df_usuarios_edit = auth.listar_usuarios()

            if df_usuarios_edit.empty:
                show_info("Nenhum usuário cadastrado.")
            else:
                usuario_selecionado = st.selectbox(
                    "Selecione o usuário para editar",
                    df_usuarios_edit['username'].tolist(),
                    key="select_editar"
                )

                usuario_atual = df_usuarios_edit[df_usuarios_edit['username'] == usuario_selecionado].iloc[0]

                with st.form("form_editar_usuario"):
                    col1, col2 = st.columns(2)

                    with col1:
                        edit_username = st.text_input(
                            "Usuário (login) *",
                            value=usuario_atual['username']
                        )
                        edit_nome = st.text_input(
                            "Nome completo *",
                            value=usuario_atual['nome']
                        )

                    with col2:
                        edit_email = st.text_input(
                            "E-mail *",
                            value=usuario_atual['email']
                        )
                        niveis_acesso = ["admin", "editor", "viewer"]
                        nivel_salvo = usuario_atual.get('nivel_acesso')
                        nivel_idx = niveis_acesso.index(nivel_salvo) if nivel_salvo in niveis_acesso else 2

                        edit_nivel = st.selectbox(
                            "Nível de acesso *",
                            niveis_acesso,
                            index=nivel_idx,
                            format_func=lambda x: {
                                "admin": "Administrador",
                                "editor": "Editor",
                                "viewer": "Visualizador"
                            }.get(x, str(x))
                        )

                    submitted = st.form_submit_button("Salvar alterações", type="primary", icon=":material/save:")

                    if submitted:
                        if all([edit_username, edit_nome, edit_email]):
                            sucesso, msg = auth.editar_usuario(
                                usuario_selecionado,
                                edit_username,
                                edit_nome,
                                edit_email,
                                edit_nivel
                            )
                            if sucesso:
                                st.toast(msg, icon=":material/check_circle:")
                                st.rerun()
                            else:
                                show_error(msg)
                        else:
                            show_error("Preencha todos os campos obrigatórios.")

        with tab_senha:
            st.markdown('<div class="section-title">Alterar minha senha</div>', unsafe_allow_html=True)

            with st.form("form_alterar_senha"):
                senha_atual = st.text_input("Senha atual", type="password")
                senha_nova = st.text_input("Nova senha", type="password")
                senha_confirmar = st.text_input("Confirmar nova senha", type="password")

                submitted = st.form_submit_button("Alterar senha", type="primary", icon=":material/key:")

                if submitted:
                    if senha_nova != senha_confirmar:
                        show_error("As senhas informadas não coincidem.")
                    elif len(senha_nova) < 6:
                        show_error("A senha deve ter no mínimo 6 caracteres.")
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
        logger.error(f"Erro na aba de usuários: {e}")
        show_error("Erro ao carregar usuários.", details=str(e))


# =============================================================================
# FLUXO PRINCIPAL
# =============================================================================

def main():
    """Ponto de entrada da aplicação Streamlit."""
    st.set_page_config(
        page_title=Settings.PAGE_TITLE,
        page_icon=Settings.PAGE_ICON,
        layout=Settings.PAGE_LAYOUT,
        initial_sidebar_state="expanded"
    )

    load_css()
    init_session_state()

    auth = st.session_state.auth_manager

    # Se não estiver autenticado, exibe tela de login
    if not auth.autenticado:
        render_login_page()
        return

    # Renderiza a barra lateral persistente
    pagina_selecionada = render_sidebar(st.session_state.data_manager, auth)

    # Roteamento de páginas
    if pagina_selecionada == "painel":
        render_pagina_painel()
    elif pagina_selecionada == "cursos":
        render_pagina_cursos()
    elif pagina_selecionada == "novo_curso":
        render_pagina_novo_curso()
    elif pagina_selecionada == "editar":
        render_pagina_editar_curso()
    elif pagina_selecionada == "calendario":
        render_pagina_calendario()
    elif pagina_selecionada == "importar":
        render_pagina_importar_json()
    elif pagina_selecionada == "backup":
        render_pagina_backup()
    elif pagina_selecionada == "usuarios":
        render_pagina_usuarios()
    else:
        render_pagina_painel()


if __name__ == "__main__":
    main()
