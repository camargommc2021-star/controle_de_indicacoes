"""
Componente de visualização em calendário.

Exibe prazos e eventos de cursos em formato de calendário mensal,
utilizando o sistema de design sem emojis decorativos.
"""

import calendar
import html
from datetime import date
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

import streamlit as st
import pandas as pd

from utils.logger import get_logger
from utils.validators import parse_data, limpar_valor, curso_concluido
from components.ui import plural

logger = get_logger(__name__)

MESES_PT = [
    '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
]

DIAS_SEMANA_PT = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']


class TipoEvento(Enum):
    """Tipos de eventos no calendário."""
    CURSO_PRAZO_SIAT = "prazo_siat"
    CURSO_PRAZO_CHEFIA = "prazo_chefia"
    CURSO_CONCLUSAO = "conclusao"
    CURSO_RECEBIMENTO = "recebimento"


@dataclass
class EventoCalendario:
    """Representa um evento no calendário."""
    data: date
    codigo: str
    turma: str
    tipo: TipoEvento
    descricao: str = ""
    status_prazo: str = "ok"  # 'late', 'soon', 'ok', 'none'
    id_referencia: Optional[str] = None


class CalendarView:
    """Componente de visualização em calendário dos prazos."""

    def __init__(self):
        """Inicializa o calendário e o estado de navegação."""
        self.data_atual = date.today()

        if 'cal_mes' not in st.session_state:
            st.session_state.cal_mes = self.data_atual.month
        if 'cal_ano' not in st.session_state:
            st.session_state.cal_ano = max(2000, min(2100, self.data_atual.year))
        if 'cal_mes_select' not in st.session_state:
            st.session_state.cal_mes_select = MESES_PT[st.session_state.cal_mes]
        if 'cal_ano_input' not in st.session_state:
            st.session_state.cal_ano_input = st.session_state.cal_ano

        self.mes_atual = st.session_state.cal_mes
        self.ano_atual = st.session_state.cal_ano

    def converter_cursos_para_eventos(self, df_cursos: pd.DataFrame) -> List[EventoCalendario]:
        """Converte DataFrame de cursos em lista de eventos."""
        eventos = []

        if df_cursos is None or df_cursos.empty:
            return eventos

        hoje = date.today()

        for idx, row in df_cursos.iterrows():
            codigo = limpar_valor(row.get('Curso')) or f'Curso {idx}'
            turma = limpar_valor(row.get('Turma')) or ''
            concluido = curso_concluido(row)

            # Prazo SIAT
            data_siat = parse_data(row.get('Fim da indicação da SIAT'))
            if data_siat:
                if concluido:
                    status_prazo = "ok"
                else:
                    dias = (data_siat - hoje).days
                    if dias < 0:
                        status_prazo = "late"
                    elif dias <= 5:
                        status_prazo = "soon"
                    else:
                        status_prazo = "ok"

                eventos.append(EventoCalendario(
                    data=data_siat,
                    codigo=codigo,
                    turma=turma,
                    tipo=TipoEvento.CURSO_PRAZO_SIAT,
                    descricao=f"Prazo SIAT: {codigo} (Turma {turma})",
                    status_prazo=status_prazo,
                    id_referencia=str(idx)
                ))

            # Prazo Chefia
            data_chefia = parse_data(row.get('Prazo dado pela chefia'))
            if data_chefia:
                if concluido:
                    status_prazo = "ok"
                else:
                    dias = (data_chefia - hoje).days
                    if dias < 0:
                        status_prazo = "late"
                    elif dias <= 5:
                        status_prazo = "soon"
                    else:
                        status_prazo = "ok"

                eventos.append(EventoCalendario(
                    data=data_chefia,
                    codigo=codigo,
                    turma=turma,
                    tipo=TipoEvento.CURSO_PRAZO_CHEFIA,
                    descricao=f"Prazo da chefia: {codigo} (Turma {turma})",
                    status_prazo=status_prazo,
                    id_referencia=str(idx)
                ))

            # Data de conclusão
            data_conc = parse_data(row.get('DATA_DA_CONCLUSAO'))
            if data_conc:
                eventos.append(EventoCalendario(
                    data=data_conc,
                    codigo=codigo,
                    turma=turma,
                    tipo=TipoEvento.CURSO_CONCLUSAO,
                    descricao=f"Conclusão: {codigo} (Turma {turma})",
                    status_prazo="ok",
                    id_referencia=str(idx)
                ))

            # Recebimento SIGAD
            data_sigad = parse_data(row.get('Recebimento do SIGAD com as vagas'))
            if data_sigad:
                eventos.append(EventoCalendario(
                    data=data_sigad,
                    codigo=codigo,
                    turma=turma,
                    tipo=TipoEvento.CURSO_RECEBIMENTO,
                    descricao=f"Recebimento SIGAD: {codigo} (Turma {turma})",
                    status_prazo="none",
                    id_referencia=str(idx)
                ))

        return eventos

    def render(self, df_cursos: pd.DataFrame) -> None:
        """Renderiza a visualização do calendário."""
        eventos = self.converter_cursos_para_eventos(df_cursos)

        self._render_controles()
        self._render_calendario_mensal(eventos)
        self._render_legenda()
        self._render_eventos_mes(eventos)

    @staticmethod
    def _navegar_anterior() -> None:
        """Navega para o mês anterior."""
        mes = st.session_state.get("cal_mes", date.today().month)
        ano = st.session_state.get("cal_ano", date.today().year)
        if mes == 1:
            if ano > 2000:
                mes = 12
                ano -= 1
        else:
            mes -= 1
        st.session_state["cal_mes"] = mes
        st.session_state["cal_ano"] = ano
        st.session_state["cal_mes_select"] = MESES_PT[mes]
        st.session_state["cal_ano_input"] = ano

    @staticmethod
    def _navegar_proximo() -> None:
        """Navega para o próximo mês."""
        mes = st.session_state.get("cal_mes", date.today().month)
        ano = st.session_state.get("cal_ano", date.today().year)
        if mes == 12:
            if ano < 2100:
                mes = 1
                ano += 1
        else:
            mes += 1
        st.session_state["cal_mes"] = mes
        st.session_state["cal_ano"] = ano
        st.session_state["cal_mes_select"] = MESES_PT[mes]
        st.session_state["cal_ano_input"] = ano

    @staticmethod
    def _navegar_hoje() -> None:
        """Navega para o mês atual."""
        hoje = date.today()
        mes = hoje.month
        ano = max(2000, min(2100, hoje.year))
        st.session_state["cal_mes"] = mes
        st.session_state["cal_ano"] = ano
        st.session_state["cal_mes_select"] = MESES_PT[mes]
        st.session_state["cal_ano_input"] = ano

    @staticmethod
    def _on_change_mes() -> None:
        """Atualiza cal_mes a partir do widget cal_mes_select."""
        sel = st.session_state.get("cal_mes_select")
        if sel in MESES_PT and sel:
            st.session_state["cal_mes"] = MESES_PT.index(sel)

    @staticmethod
    def _on_change_ano() -> None:
        """Atualiza cal_ano a partir do widget cal_ano_input."""
        try:
            val = int(st.session_state.get("cal_ano_input", 2026))
            val = max(2000, min(2100, val))
            st.session_state["cal_ano"] = val
            st.session_state["cal_ano_input"] = val
        except Exception:
            pass

    def _render_controles(self) -> None:
        """Renderiza os controles de navegação com ícones materiais."""
        hoje = date.today()
        if "cal_mes" not in st.session_state:
            st.session_state["cal_mes"] = hoje.month
        if "cal_ano" not in st.session_state:
            st.session_state["cal_ano"] = max(2000, min(2100, hoje.year))
        if "cal_mes_select" not in st.session_state:
            st.session_state["cal_mes_select"] = MESES_PT[st.session_state["cal_mes"]]
        if "cal_ano_input" not in st.session_state:
            st.session_state["cal_ano_input"] = st.session_state["cal_ano"]

        col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 1, 2], gap="small")

        with col1:
            st.button(
                "Anterior",
                key="cal_prev",
                icon=":material/chevron_left:",
                use_container_width=True,
                on_click=self._navegar_anterior
            )

        with col2:
            meses_nomes = MESES_PT[1:]
            st.selectbox(
                "Mês",
                meses_nomes,
                key="cal_mes_select",
                on_change=self._on_change_mes,
                label_visibility="collapsed"
            )

        with col3:
            st.number_input(
                "Ano",
                min_value=2000,
                max_value=2100,
                step=1,
                key="cal_ano_input",
                on_change=self._on_change_ano,
                label_visibility="collapsed"
            )

        with col4:
            st.button(
                "Próximo",
                key="cal_next",
                icon=":material/chevron_right:",
                use_container_width=True,
                on_click=self._navegar_proximo
            )

        with col5:
            st.button(
                "Mês atual",
                key="cal_hoje",
                icon=":material/today:",
                use_container_width=True,
                on_click=self._navegar_hoje
            )

    def _render_calendario_mensal(self, eventos: List[EventoCalendario]) -> None:
        """Renderiza a grade mensal."""
        cal = calendar.Calendar(firstweekday=6)  # Domingo = 6
        dias_mes = cal.monthdayscalendar(
            st.session_state.cal_ano,
            st.session_state.cal_mes
        )

        eventos_por_dia: Dict[int, List[EventoCalendario]] = {}
        for ev in eventos:
            if ev.data.month == st.session_state.cal_mes and ev.data.year == st.session_state.cal_ano:
                dia = ev.data.day
                eventos_por_dia.setdefault(dia, []).append(ev)

        mes_nome = MESES_PT[st.session_state.cal_mes]
        st.markdown(
            f'<div style="text-align: center; margin: 1.25rem 0 0.75rem 0;">'
            f'<span style="font-family: var(--font-condensed); font-size: 24px; font-weight: 600; color: var(--ink);">'
            f'{mes_nome} {st.session_state.cal_ano}</span></div>',
            unsafe_allow_html=True
        )

        # Cabeçalho dos dias da semana
        header_cols = "".join(f'<div class="cal-weekday">{d}</div>' for d in DIAS_SEMANA_PT)
        st.markdown(f'<div class="cal-header-row">{header_cols}</div>', unsafe_allow_html=True)

        hoje = date.today()

        # Grade de semanas
        for semana in dias_mes:
            cols_html = []
            for dia in semana:
                if dia == 0:
                    cols_html.append('<div class="cal-cell cal-cell-out"></div>')
                else:
                    eh_hoje = (
                        dia == hoje.day and
                        st.session_state.cal_mes == hoje.month and
                        st.session_state.cal_ano == hoje.year
                    )
                    classe_hoje = " cal-cell-today" if eh_hoje else ""

                    ev_do_dia = eventos_por_dia.get(dia, [])
                    chips_html = []
                    for ev in ev_do_dia[:3]:
                        safe_cod = html.escape(ev.codigo)
                        chips_html.append(f'<div class="cal-chip {ev.status_prazo}">{safe_cod}</div>')

                    if len(ev_do_dia) > 3:
                        mais = len(ev_do_dia) - 3
                        chips_html.append(f'<div style="font-size: 12px; color: var(--ink-soft); font-variant-numeric: tabular-nums;">+{mais}</div>')

                    chips_bloco = "".join(chips_html)
                    cols_html.append(
                        f'<div class="cal-cell{classe_hoje}">'
                        f'<div class="cal-day-num">{dia}</div>'
                        f'{chips_bloco}'
                        f'</div>'
                    )

            linha_html = "".join(cols_html)
            st.markdown(f'<div class="cal-grid">{linha_html}</div>', unsafe_allow_html=True)

    def _render_legenda(self) -> None:
        """Renderiza a legenda com pills estilizas."""
        st.markdown("<hr style='margin: 1.5rem 0;'>", unsafe_allow_html=True)

        html_legenda = """
        <div style="display: flex; flex-wrap: wrap; gap: 24px; align-items: center; justify-content: space-between;">
          <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
            <span style="font-size: 13px; font-weight: 600; color: var(--ink);">Status:</span>
            <span class="pill pill-ok">No prazo (>5 dias)</span>
            <span class="pill pill-soon">Atenção (0 a 5 dias)</span>
            <span class="pill pill-late">Vencido</span>
          </div>
          <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
            <span style="font-size: 13px; font-weight: 600; color: var(--ink);">Eventos:</span>
            <span class="pill pill-muted">Prazo SIAT</span>
            <span class="pill pill-muted">Prazo da chefia</span>
            <span class="pill pill-ok">Conclusão</span>
            <span class="pill pill-none">Recebimento SIGAD</span>
          </div>
        </div>
        """
        st.markdown(html_legenda, unsafe_allow_html=True)

    def _render_eventos_mes(self, eventos: List[EventoCalendario]) -> None:
        """Renderiza lista detalhada dos eventos do mês."""
        eventos_mes = [
            ev for ev in eventos
            if ev.data.month == st.session_state.cal_mes and ev.data.year == st.session_state.cal_ano
        ]

        if not eventos_mes:
            return

        st.markdown("<div class='section-title' style='margin-top: 1.5rem;'>Eventos do mês</div>", unsafe_allow_html=True)

        eventos_mes.sort(key=lambda x: x.data)
        eventos_por_data: Dict[date, List[EventoCalendario]] = {}
        for ev in eventos_mes:
            eventos_por_data.setdefault(ev.data, []).append(ev)

        dias_semana_curtos = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']

        for data_ev, lista in sorted(eventos_por_data.items()):
            ds = dias_semana_curtos[data_ev.weekday()]
            data_fmt = data_ev.strftime('%d/%m/%Y')
            qtd = len(lista)
            termo = plural(qtd, "evento", "eventos")

            with st.expander(f"{ds}, {data_fmt} ({qtd} {termo})"):
                for ev in lista:
                    col_code, col_desc = st.columns([2, 8])
                    with col_code:
                        st.markdown(f'<span class="pill pill-{ev.status_prazo}">{html.escape(ev.codigo)}</span>', unsafe_allow_html=True)
                    with col_desc:
                        st.write(ev.descricao)
