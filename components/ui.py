"""
Componentes de interface compartilhados e utilitários de apresentação.

Conceito de design: Fichas de progresso (flight progress strips).
Todos os textos em português brasileiro, em estilo frase, sem emojis decorativos.
"""

import html
import re
from datetime import date
from typing import Optional, Tuple, Dict, Any
import streamlit as st
import pandas as pd

from utils.validators import parse_data, limpar_valor, curso_concluido


def limpar_confirmacoes_exclusao() -> None:
    """Limpa todas as chaves de confirmação de exclusão do session_state."""
    keys_to_del = [k for k in list(st.session_state.keys()) if str(k).startswith("confirm_del_")]
    for k in keys_to_del:
        del st.session_state[k]


# =============================================================================
# CABEÇALHOS DE PÁGINA
# =============================================================================

def page_header(
    titulo: str,
    ajuda: Optional[str] = None,
    acao: Optional[Dict[str, Any]] = None
) -> None:
    """
    Renderiza cabeçalho de página com título em Barlow Condensed 32/700 e ink,
    texto de ajuda opcional abaixo e botão de ação primária opcional à direita.
    Alinhado à esquerda na margem do container.
    """
    safe_titulo = html.escape(titulo)
    safe_ajuda = html.escape(ajuda) if ajuda else None

    with st.container(key="page_header_container"):
        if acao:
            col_titulo, col_acao = st.columns([5, 1.2], vertical_alignment="bottom")
            with col_titulo:
                html_parts = [
                    '<div class="page-header">',
                    f'<h1 class="page-title">{safe_titulo}</h1>',
                ]
                if safe_ajuda:
                    html_parts.append(f'<p class="page-helper">{safe_ajuda}</p>')
                html_parts.append('</div>')
                st.markdown("".join(html_parts), unsafe_allow_html=True)
            with col_acao:
                btn_label = acao.get("label", "Novo curso")
                btn_icon = acao.get("icon", ":material/add:")
                btn_key = acao.get("key", "btn_page_header_action")
                if st.button(
                    btn_label,
                    key=btn_key,
                    icon=btn_icon,
                    type="primary",
                    use_container_width=True
                ):
                    if "on_click" in acao and callable(acao["on_click"]):
                        acao["on_click"]()
                    elif "pagina" in acao:
                        limpar_confirmacoes_exclusao()
                        for k in list(st.session_state.keys()):
                            if str(k).startswith("confirm_restore_"):
                                del st.session_state[k]
                        st.session_state["pagina"] = acao["pagina"]
                        st.rerun()
        else:
            html_parts = [
                '<div class="page-header">',
                f'<h1 class="page-title">{safe_titulo}</h1>',
            ]
            if safe_ajuda:
                html_parts.append(f'<p class="page-helper">{safe_ajuda}</p>')
            html_parts.append('</div>')
            st.markdown("".join(html_parts), unsafe_allow_html=True)


def page_title(titulo: str, ajuda: Optional[str] = None) -> None:
    """Wrapper de compatibilidade para page_header."""
    page_header(titulo, ajuda)


# =============================================================================
# STATUS DO CURSO E DATAS
# =============================================================================

def status_do_curso(row: Any) -> Tuple[str, Optional[int]]:
    """
    Retorna o status de prazo do curso e os dias restantes.
    
    Retorno:
        Tuple: (status, dias)
        onde status é um de: 'concluido', 'atrasado', 'urgente', 'no_prazo', 'sem_prazo'
    """
    if curso_concluido(row):
        return "concluido", 0

    raw_siat = None
    if hasattr(row, 'get'):
        raw_siat = row.get('Fim da indicação da SIAT')
    elif hasattr(row, '__getitem__'):
        try:
            raw_siat = row['Fim da indicação da SIAT']
        except Exception:
            pass

    data = parse_data(raw_siat)
    if data is None:
        return "sem_prazo", None

    hoje = date.today()
    dias = (data - hoje).days

    if dias < 0:
        return "atrasado", dias
    elif dias <= 5:
        return "urgente", dias
    else:
        return "no_prazo", dias


def plural(n: Any, singular: str, plural: str) -> str:
    """Retorna a forma singular ou plural de acordo com a quantidade informada."""
    try:
        val = int(n)
    except (ValueError, TypeError):
        val = 0
    return singular if abs(val) == 1 else plural


def texto_relativo_prazo(status: str, dias: Optional[int]) -> str:
    """Retorna o texto descritivo relativo ao prazo."""
    if status == "concluido":
        return "concluído"
    if status == "sem_prazo" or dias is None:
        return "sem prazo"
    if status == "atrasado":
        dias_abs = abs(dias)
        return f"vencido há {dias_abs} {plural(dias_abs, 'dia', 'dias')}"
    if status == "urgente":
        if dias == 0:
            return "vence hoje"
        return f"vence em {dias} {plural(dias, 'dia', 'dias')}"
    return f"vence em {dias} {plural(dias, 'dia', 'dias')}"


def obter_classe_borda(status: str) -> str:
    """Retorna a classe CSS para a borda esquerda de 6px da ficha."""
    mapeamento = {
        "atrasado": "strip-edge-late",
        "urgente": "strip-edge-soon",
        "no_prazo": "strip-edge-ok",
        "sem_prazo": "strip-edge-none",
        "concluido": "strip-edge-concluido",
    }
    return mapeamento.get(status, "strip-edge-none")


def obter_classe_texto_prazo(status: str) -> str:
    """Retorna a classe CSS de cor para o texto relativo ao prazo."""
    mapeamento = {
        "atrasado": "late",
        "urgente": "soon",
        "no_prazo": "ok",
        "sem_prazo": "none",
        "concluido": "ok",
    }
    return mapeamento.get(status, "none")


def formatar_etapa_pill(estado_raw: Any, is_concluido: bool) -> str:
    """Gera o HTML do pill de etapa com fundo tint e texto colorido."""
    if is_concluido:
        return '<span class="pill pill-ok">Concluído</span>'

    estado = limpar_valor(estado_raw)
    if not estado:
        return '<span class="pill pill-none">Sem etapa</span>'

    norm = estado.strip().lower()
    if norm == "solicitar voluntários" or norm == "solicitar voluntarios":
        return '<span class="pill pill-late">Solicitar voluntários</span>'
    elif norm == "fazer indicação" or norm == "fazer indicacao":
        return '<span class="pill pill-soon">Fazer indicação</span>'
    elif norm == "ver vagas escalantes":
        return '<span class="pill pill-blue">Ver vagas escalantes</span>'
    elif norm.startswith("conclu"):
        return '<span class="pill pill-ok">Concluído</span>'
    else:
        return f'<span class="pill pill-muted">{html.escape(estado)}</span>'


# =============================================================================
# FICHAS DE PROGRESSO (FLIGHT PROGRESS STRIPS)
# =============================================================================

# Configuração de colunas das fichas e do cabeçalho da lista de cursos
COLUNAS_FAIXA_PESOS = [2.2, 2.0, 1.0, 1.6, 2.0, 1.4]
COLUNAS_FAIXA_GAP = "small"


def render_faixa_curso(
    row: pd.Series,
    idx: int,
    on_edit: Optional[callable] = None,
    on_delete: Optional[callable] = None,
    can_edit: bool = True,
    can_delete: bool = True
) -> None:
    """
    Renderiza um curso como uma ficha horizontal de progresso (flight progress strip)
    em grid proporcional cobrindo toda a largura.
    
    Ações (Editar e Excluir) são renderizadas com widgets nativos st.button na coluna direita,
    com confirmação de exclusão em linha.
    """
    curso_codigo = limpar_valor(row.get('Curso')) or 'S/ CÓD'
    turma = limpar_valor(row.get('Turma')) or 'S/ Turma'
    om_executora = limpar_valor(row.get('OM_Executora'))

    # Vagas
    vagas_raw = row.get('Vagas', 0)
    try:
        vagas = int(vagas_raw) if pd.notna(vagas_raw) and str(vagas_raw).strip() not in ('', 'nan') else 0
    except (ValueError, TypeError):
        vagas = 0

    status, dias = status_do_curso(row)
    rel_texto = texto_relativo_prazo(status, dias)
    classe_prazo = obter_classe_texto_prazo(status)

    # Data SIAT formatada
    raw_siat = row.get('Fim da indicação da SIAT')
    dt_siat = parse_data(raw_siat)
    if dt_siat:
        data_str = dt_siat.strftime('%d/%m/%Y')
    elif raw_siat and str(raw_siat).strip() and str(raw_siat).strip().lower() != 'nan':
        data_str = str(raw_siat).strip()
    else:
        data_str = "Sem data"

    is_concluido = (status == "concluido")
    pill_etapa_html = formatar_etapa_pill(row.get('Estado'), is_concluido)

    # Escaping de valores para inserção no HTML
    safe_codigo = html.escape(curso_codigo)
    safe_turma = html.escape(turma)
    safe_data = html.escape(data_str)
    safe_rel = html.escape(rel_texto)
    safe_om = html.escape(om_executora) if om_executora else ""
    vagas_texto = plural(vagas, "vaga", "vagas")

    sanitized_codigo = re.sub(r'[^a-zA-Z0-9_]', '_', str(curso_codigo))
    sanitized_turma = re.sub(r'[^a-zA-Z0-9_]', '_', str(turma))
    key_confirm = f"confirm_del_{idx}_{sanitized_codigo}_{sanitized_turma}"
    confirmando = st.session_state.get(key_confirm, False)

    with st.container(border=True, key=f"faixa_{status}_{idx}"):
        if confirmando:
            col_msg, col_sim, col_nao = st.columns([6, 2, 2], vertical_alignment="center")
            with col_msg:
                st.warning(f"Excluir o curso {safe_codigo}?")
            with col_sim:
                if st.button("Confirmar exclusão", key=f"sim_del_{idx}", type="primary", use_container_width=True):
                    limpar_confirmacoes_exclusao()
                    if on_delete:
                        on_delete(idx)
            with col_nao:
                if st.button("Cancelar", key=f"nao_del_{idx}", type="secondary", use_container_width=True):
                    limpar_confirmacoes_exclusao()
                    st.rerun()
        else:
            col_curso, col_prazo, col_vagas, col_etapa, col_om, col_actions = st.columns(
                COLUNAS_FAIXA_PESOS,
                gap=COLUNAS_FAIXA_GAP,
                vertical_alignment="center"
            )
            with col_curso:
                st.markdown(
                    f'<div class="strip-col-code">'
                    f'<span class="strip-course-code">{safe_codigo}</span>'
                    f'<span class="strip-turma">Turma {safe_turma}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            with col_prazo:
                st.markdown(
                    f'<div class="strip-col-prazo">'
                    f'<span class="strip-prazo-date">{safe_data}</span>'
                    f'<span class="strip-prazo-rel {classe_prazo}">{safe_rel}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            with col_vagas:
                st.markdown(
                    f'<div class="strip-col-vagas">'
                    f'<span class="strip-vagas-num">{vagas}</span> {vagas_texto}'
                    f'</div>',
                    unsafe_allow_html=True
                )
            with col_etapa:
                st.markdown(
                    f'<div class="strip-col-etapa">{pill_etapa_html}</div>',
                    unsafe_allow_html=True
                )
            with col_om:
                om_display = f'<div class="strip-col-om" title="OM executora">{safe_om}</div>' if safe_om else '<div class="strip-col-om"></div>'
                st.markdown(om_display, unsafe_allow_html=True)
            with col_actions:
                col_btn_edit, col_btn_del = st.columns([1, 0.35], gap="small", vertical_alignment="center")
                with col_btn_edit:
                    if can_edit:
                        if st.button("Editar", key=f"btn_edit_{idx}", icon=":material/edit:", type="secondary", use_container_width=True):
                            if on_edit:
                                on_edit(idx)
                with col_btn_del:
                    if can_delete:
                        if st.button("", key=f"btn_del_{idx}", icon=":material/delete:", type="tertiary", help="Excluir curso", use_container_width=True):
                            limpar_confirmacoes_exclusao()
                            st.session_state[key_confirm] = True
                            st.rerun()


def render_cabecalho_cursos() -> None:
    """
    Renderiza linha de cabeçalho da tabela de cursos com os mesmos pesos de coluna
    das faixas de curso, em estilo de texto ink-soft 13px sentence case.
    """
    with st.container(border=True, key="faixa_header"):
        col_curso, col_prazo, col_vagas, col_etapa, col_om, col_actions = st.columns(
            COLUNAS_FAIXA_PESOS,
            gap=COLUNAS_FAIXA_GAP,
            vertical_alignment="center"
        )
        with col_curso:
            st.markdown('<div class="table-header-col">Curso</div>', unsafe_allow_html=True)
        with col_prazo:
            st.markdown('<div class="table-header-col">Prazo SIAT</div>', unsafe_allow_html=True)
        with col_vagas:
            st.markdown('<div class="table-header-col">Vagas</div>', unsafe_allow_html=True)
        with col_etapa:
            st.markdown('<div class="table-header-col">Etapa</div>', unsafe_allow_html=True)
        with col_om:
            st.markdown('<div class="table-header-col">OM executora</div>', unsafe_allow_html=True)
        with col_actions:
            st.markdown('<div class="table-header-col"></div>', unsafe_allow_html=True)


def render_faixa_compacta(row: pd.Series) -> str:
    """Gera o HTML de uma ficha compacta para uso nas colunas da fila de prazos do Painel."""
    curso_codigo = html.escape(limpar_valor(row.get('Curso')) or 'S/ CÓD')
    turma = html.escape(limpar_valor(row.get('Turma')) or 'S/ Turma')
    
    status, dias = status_do_curso(row)
    rel_texto = html.escape(texto_relativo_prazo(status, dias))
    classe_borda = obter_classe_borda(status)
    classe_prazo = obter_classe_texto_prazo(status)

    vagas_raw = row.get('Vagas', 0)
    try:
        vagas = int(vagas_raw) if pd.notna(vagas_raw) and str(vagas_raw).strip() not in ('', 'nan') else 0
    except (ValueError, TypeError):
        vagas = 0

    vagas_texto = plural(vagas, "vaga", "vagas")

    return f"""
    <div class="strip-compact {classe_borda}">
      <div class="strip-compact-left">
        <span class="strip-compact-code">{curso_codigo}</span>
        <span class="strip-compact-turma">Turma {turma}</span>
      </div>
      <div class="strip-compact-right">
        <div class="strip-prazo-rel {classe_prazo}">{rel_texto}</div>
        <div class="strip-compact-vagas">{vagas} {vagas_texto}</div>
      </div>
    </div>
    """


# =============================================================================
# ANDAMENTO DAS INDICAÇÕES E TOTAIS (PAINEL)
# =============================================================================

def render_andamento_indicacoes(
    df: pd.DataFrame,
    total_cursos: Optional[int] = None,
    total_vagas: Optional[int] = None
) -> None:
    """
    Renderiza a sequência horizontal de 4 etapas ordenadas com contagens,
    mais o bloco lateral de 'Sem estado', distribuídos uniformemente em 5 colunas iguais,
    com linha de totais alinhada à direita no rodapé da caixa.
    """
    if df.empty or 'Estado' not in df.columns:
        contagens = {"solicitar": 0, "indicacao": 0, "escalantes": 0, "concluido": 0, "sem_estado": 0}
    else:
        c_solicitar = 0
        c_indicacao = 0
        c_escalantes = 0
        c_concluido = 0
        c_sem_estado = 0

        for _, row in df.iterrows():
            if curso_concluido(row):
                c_concluido += 1
                continue

            estado = limpar_valor(row.get('Estado'))
            if not estado:
                c_sem_estado += 1
                continue

            norm = estado.strip().lower()
            if norm in ("solicitar voluntários", "solicitar voluntarios"):
                c_solicitar += 1
            elif norm in ("fazer indicação", "fazer indicacao"):
                c_indicacao += 1
            elif norm == "ver vagas escalantes":
                c_escalantes += 1
            elif norm.startswith("conclu"):
                c_concluido += 1
            else:
                c_sem_estado += 1

        contagens = {
            "solicitar": c_solicitar,
            "indicacao": c_indicacao,
            "escalantes": c_escalantes,
            "concluido": c_concluido,
            "sem_estado": c_sem_estado,
        }

    if total_cursos is None:
        total_cursos = len(df) if df is not None else 0

    if total_vagas is None:
        total_vagas = 0
        if df is not None and not df.empty and 'Vagas' in df.columns:
            total_vagas = int(pd.to_numeric(df['Vagas'], errors='coerce').fillna(0).sum())

    html_andamento = f"""
    <div class="andamento-container">
      <div class="andamento-title">Andamento das indicações</div>
      <div class="andamento-grid">
        <div class="andamento-col">
          <div class="step-header">
            <span class="step-badge">1</span>
            <span class="step-label">Solicitar voluntários</span>
          </div>
          <div class="step-count">{contagens['solicitar']}</div>
        </div>
        <div class="andamento-col">
          <div class="step-header">
            <span class="step-badge">2</span>
            <span class="step-label">Fazer indicação</span>
          </div>
          <div class="step-count">{contagens['indicacao']}</div>
        </div>
        <div class="andamento-col">
          <div class="step-header">
            <span class="step-badge">3</span>
            <span class="step-label">Ver vagas escalantes</span>
          </div>
          <div class="step-count">{contagens['escalantes']}</div>
        </div>
        <div class="andamento-col">
          <div class="step-header">
            <span class="step-badge">4</span>
            <span class="step-label">Concluído</span>
          </div>
          <div class="step-count">{contagens['concluido']}</div>
        </div>
        <div class="andamento-col andamento-col-sem-estado">
          <div class="step-header">
            <span class="step-badge step-badge-muted">—</span>
            <span class="step-label">Sem estado</span>
          </div>
          <div class="step-count text-muted">{contagens['sem_estado']}</div>
        </div>
      </div>
      <div class="andamento-footer">
        <div class="total-item">
          <span class="total-label">Cursos cadastrados</span>
          <span class="total-num">{total_cursos}</span>
        </div>
        <div class="total-item">
          <span class="total-label">Vagas ofertadas</span>
          <span class="total-num">{total_vagas}</span>
        </div>
      </div>
    </div>
    """
    st.markdown(html_andamento, unsafe_allow_html=True)


def render_totais_painel(total_cursos: int, total_vagas: int) -> None:
    """
    Renderiza a linha inferior de totais rotulados lado a lado:
    'Cursos cadastrados 127' e 'Vagas ofertadas 723'.
    """
    html_totais = f"""
    <div class="totals-row">
      <div class="total-item">
        <span class="total-label">Cursos cadastrados</span>
        <span class="total-num">{total_cursos}</span>
      </div>
      <div class="total-item">
        <span class="total-label">Vagas ofertadas</span>
        <span class="total-num">{total_vagas}</span>
      </div>
    </div>
    """
    st.markdown(html_totais, unsafe_allow_html=True)
