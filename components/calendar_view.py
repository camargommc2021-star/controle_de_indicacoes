"""
Componente de Visualização em Calendário.

Este módulo fornece uma visualização de calendário para os prazos
de cursos, com navegação mensal/semanal e indicadores visuais.

Usage:
    from components.calendar_view import CalendarView
    
    cal = CalendarView()
    cal.render(dados_cursos)
"""

import calendar
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

import streamlit as st
import pandas as pd

from config import colors
from utils.logger import get_logger
from utils.validators import parse_data

logger = get_logger(__name__)


# ============================================================================
# DATACLASSES E ENUMS
# ============================================================================

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
    titulo: str
    tipo: TipoEvento
    descricao: str = ""
    cor: str = "#4CAF50"
    id_referencia: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Converte para dicionário."""
        return {
            'data': self.data,
            'titulo': self.titulo,
            'tipo': self.tipo.value,
            'descricao': self.descricao,
            'cor': self.cor,
            'id_referencia': self.id_referencia
        }


# ============================================================================
# CLASSE PRINCIPAL
# ============================================================================

class CalendarView:
    """
    Componente de visualização em calendário.
    
    Exibe prazos de cursos em formato de calendário mensal,
    com indicadores visuais de status e navegação intuitiva.
    
    Attributes:
        mes_atual: Mês sendo exibido
        ano_atual: Ano sendo exibido
    """
    
    # Cores para cada tipo de evento
    CORES_EVENTO = {
        TipoEvento.CURSO_PRAZO_SIAT: "#FF9800",      # Laranja
        TipoEvento.CURSO_PRAZO_CHEFIA: "#2196F3",    # Azul
        TipoEvento.CURSO_CONCLUSAO: "#4CAF50",       # Verde
        TipoEvento.CURSO_RECEBIMENTO: "#607D8B",     # Cinza azulado
    }
    
    # Cores para status de prazo
    CORES_STATUS = {
        'ok': "#4CAF50",        # Verde
        'atencao': "#FFC107",   # Amarelo
        'urgente': "#F44336",   # Vermelho
        'vencido': "#9E9E9E",   # Cinza
    }
    
    def __init__(self):
        """Inicializa o calendário."""
        self.data_atual = date.today()
        
        # Inicializar estado da sessão para navegação
        if 'cal_mes' not in st.session_state:
            st.session_state.cal_mes = self.data_atual.month
        if 'cal_ano' not in st.session_state:
            st.session_state.cal_ano = self.data_atual.year
        
        self.mes_atual = st.session_state.cal_mes
        self.ano_atual = st.session_state.cal_ano
        
        logger.debug("CalendarView inicializado")
    
    # ====================================================================
    # MÉTODOS DE CONVERSÃO DE DADOS
    # ====================================================================
    
    def converter_cursos_para_eventos(self, df_cursos: pd.DataFrame) -> List[EventoCalendario]:
        """
        Converte DataFrame de cursos em lista de eventos.
        
        Args:
            df_cursos: DataFrame com dados dos cursos
            
        Returns:
            Lista de EventoCalendario
        """
        eventos = []
        
        if df_cursos.empty:
            return eventos
        
        for idx, row in df_cursos.iterrows():
            curso_nome = row.get('Curso', f'Curso {idx}')
            
            # Prazo da SIAT
            data = parse_data(row.get('Fim da indicação da SIAT'))
            if data:
                cor = self._calcular_cor_prazo(data)
                eventos.append(EventoCalendario(
                    data=data,
                    titulo=f"📋 {curso_nome}",
                    tipo=TipoEvento.CURSO_PRAZO_SIAT,
                    descricao=f"Fim da indicação da SIAT: {curso_nome}",
                    cor=cor,
                    id_referencia=str(idx)
                ))
            
            # Prazo da Chefia
            data = parse_data(row.get('Prazo dado pela chefia'))
            if data:
                cor = self._calcular_cor_prazo(data)
                eventos.append(EventoCalendario(
                    data=data,
                    titulo=f"👔 {curso_nome}",
                    tipo=TipoEvento.CURSO_PRAZO_CHEFIA,
                    descricao=f"Prazo da Chefia: {curso_nome}",
                    cor=cor,
                    id_referencia=str(idx)
                ))
            
            # Data de conclusão
            data = parse_data(row.get('DATA_DA_CONCLUSAO'))
            if data:
                eventos.append(EventoCalendario(
                    data=data,
                    titulo=f"✅ {curso_nome}",
                    tipo=TipoEvento.CURSO_CONCLUSAO,
                    descricao=f"Conclusão: {curso_nome}",
                    cor=self.CORES_EVENTO[TipoEvento.CURSO_CONCLUSAO],
                    id_referencia=str(idx)
                ))
            
            # Recebimento SIGAD
            data = parse_data(row.get('Recebimento do SIGAD com as vagas'))
            if data:
                eventos.append(EventoCalendario(
                    data=data,
                    titulo=f"📨 {curso_nome}",
                    tipo=TipoEvento.CURSO_RECEBIMENTO,
                    descricao=f"Recebimento SIGAD: {curso_nome}",
                    cor=self.CORES_EVENTO[TipoEvento.CURSO_RECEBIMENTO],
                    id_referencia=str(idx)
                ))
        
        return eventos
    

    def _parse_data(self, valor: Any) -> Optional[date]:
        """
        Tenta converter qualquer valor em date usando o helper centralizado parse_data.
        
        Args:
            valor: Valor a ser convertido
            
        Returns:
            date ou None
        """
        return parse_data(valor)
    
    def _calcular_cor_prazo(self, data_prazo: date) -> str:
        """
        Calcula a cor baseada na proximidade do prazo.
        
        Args:
            data_prazo: Data do prazo
            
        Returns:
            Código hexadecimal da cor
        """
        hoje = date.today()
        dias_restantes = (data_prazo - hoje).days
        
        if dias_restantes < 0:
            return self.CORES_STATUS['vencido']
        elif dias_restantes <= 2:
            return self.CORES_STATUS['urgente']
        elif dias_restantes <= 5:
            return self.CORES_STATUS['atencao']
        else:
            return self.CORES_STATUS['ok']
    
    # ====================================================================
    # RENDERIZAÇÃO
    # ====================================================================
    
    def render(self, df_cursos: pd.DataFrame):
        """
        Renderiza o calendário completo.
        
        Args:
            df_cursos: DataFrame com cursos
        """
        # Converter dados em eventos
        eventos = self.converter_cursos_para_eventos(df_cursos)
        
        # Renderizar controles
        self._render_controles()
        
        # Renderizar calendário mensal
        self._render_calendario_mensal(eventos)
        
        # Renderizar legenda
        self._render_legenda()
        
        # Renderizar lista de eventos do mês
        self._render_eventos_mes(eventos)
    
    def _render_controles(self):
        """Renderiza controles de navegação."""
        col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
        
        with col1:
            if st.button("◀", key="cal_prev"):
                self._navegar_anterior()
        
        with col2:
            meses = list(calendar.month_name)[1:]
            mes_selecionado = st.selectbox(
                "Mês",
                meses,
                index=st.session_state.cal_mes - 1,
                key="cal_select_mes",
                label_visibility="collapsed"
            )
            st.session_state.cal_mes = meses.index(mes_selecionado) + 1
        
        with col3:
            ano_selecionado = st.number_input(
                "Ano",
                min_value=2020,
                max_value=2100,
                value=st.session_state.cal_ano,
                key="cal_select_ano",
                label_visibility="collapsed"
            )
            st.session_state.cal_ano = int(ano_selecionado)
        
        with col4:
            if st.button("▶", key="cal_next"):
                self._navegar_proximo()
        
        # Botão para ir ao mês atual
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📅 Ir para Mês Atual", width="stretch", key="cal_hoje"):
                st.session_state.cal_mes = date.today().month
                st.session_state.cal_ano = date.today().year
                st.rerun()
    
    def _navegar_anterior(self):
        """Navega para o mês anterior."""
        if st.session_state.cal_mes == 1:
            st.session_state.cal_mes = 12
            st.session_state.cal_ano -= 1
        else:
            st.session_state.cal_mes -= 1
        st.rerun()
    
    def _navegar_proximo(self):
        """Navega para o próximo mês."""
        if st.session_state.cal_mes == 12:
            st.session_state.cal_mes = 1
            st.session_state.cal_ano += 1
        else:
            st.session_state.cal_mes += 1
        st.rerun()
    
    def _render_calendario_mensal(self, eventos: List[EventoCalendario]):
        """
        Renderiza calendário mensal.
        
        Args:
            eventos: Lista de eventos para exibir
        """
        # Criar calendário
        cal = calendar.Calendar()
        dias_mes = cal.monthdayscalendar(
            st.session_state.cal_ano, 
            st.session_state.cal_mes
        )
        
        # Agrupar eventos por dia
        eventos_por_dia: Dict[int, List[EventoCalendario]] = {}
        for ev in eventos:
            if ev.data.month == st.session_state.cal_mes and ev.data.year == st.session_state.cal_ano:
                dia = ev.data.day
                if dia not in eventos_por_dia:
                    eventos_por_dia[dia] = []
                eventos_por_dia[dia].append(ev)
        
        # CSS customizado para o calendário
        st.markdown("""
        <style>
        .cal-header {
            background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
            padding: 8px;
            text-align: center;
            font-weight: bold;
            border-radius: 4px 4px 0 0;
        }
        .cal-day-header {
            background-color: #e5e7eb;
            padding: 8px;
            text-align: center;
            font-weight: bold;
            font-size: 0.85em;
        }
        .cal-day {
            background-color: white;
            border: 1px solid #e5e7eb;
            padding: 4px;
            min-height: 80px;
            vertical-align: top;
        }
        .cal-day-out {
            background-color: #f3f4f6;
            color: #9ca3af;
        }
        .cal-day-today {
            background-color: #dbeafe;
            border: 2px solid #3b82f6;
        }
        .cal-event {
            font-size: 0.75em;
            padding: 2px 4px;
            margin: 2px 0;
            border-radius: 3px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            cursor: pointer;
            color: white;
            font-weight: 500;
        }
        .cal-day-number {
            font-weight: bold;
            margin-bottom: 4px;
            font-size: 0.9em;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Cabeçalho do calendário
        mes_nome = calendar.month_name[st.session_state.cal_mes]
        st.markdown(f"<h3 style='text-align: center;'>{mes_nome} {st.session_state.cal_ano}</h3>", 
                   unsafe_allow_html=True)
        
        # Criar grid do calendário
        dias_semana = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']
        
        # Cabeçalhos
        cols = st.columns(7)
        for i, dia in enumerate(dias_semana):
            with cols[i]:
                st.markdown(f"<div class='cal-day-header'>{dia}</div>", unsafe_allow_html=True)
        
        # Dias
        hoje = date.today()
        for semana in dias_mes:
            cols = st.columns(7)
            for i, dia in enumerate(semana):
                with cols[i]:
                    if dia == 0:
                        # Dia fora do mês
                        st.markdown("<div class='cal-day cal-day-out'>&nbsp;</div>", 
                                   unsafe_allow_html=True)
                    else:
                        # Verificar se é hoje
                        eh_hoje = (dia == hoje.day and 
                                  st.session_state.cal_mes == hoje.month and 
                                  st.session_state.cal_ano == hoje.year)
                        
                        classe = "cal-day"
                        if eh_hoje:
                            classe += " cal-day-today"
                        
                        # Eventos do dia
                        eventos_dia = eventos_por_dia.get(dia, [])
                        eventos_html = ""
                        for ev in eventos_dia[:3]:  # Max 3 eventos visíveis
                            eventos_html += f"<div class='cal-event' style='background-color: {ev.cor};'>{ev.titulo}</div>"
                        
                        if len(eventos_dia) > 3:
                            eventos_html += f"<div style='font-size: 0.7em; color: #666;'>+{len(eventos_dia)-3} mais</div>"
                        
                        html = f"""
                        <div class='{classe}'>
                            <div class='cal-day-number'>{dia}</div>
                            {eventos_html}
                        </div>
                        """
                        st.markdown(html, unsafe_allow_html=True)
    
    def _render_legenda(self):
        """Renderiza legenda de cores e tipos."""
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Status dos Prazos:**")
            for nome, cor in self.CORES_STATUS.items():
                label = {
                    'ok': '🟢 No prazo (>5 dias)',
                    'atencao': '🟡 Atenção (3-5 dias)',
                    'urgente': '🔴 Urgente (0-2 dias)',
                    'vencido': '⚪ Vencido'
                }[nome]
                st.markdown(f"<span style='color: {cor};'>●</span> {label}", unsafe_allow_html=True)
        
        with col2:
            st.markdown("**Tipos de Eventos:**")
            for tipo, cor in self.CORES_EVENTO.items():
                label = {
                    TipoEvento.CURSO_PRAZO_SIAT: '📋 Prazo SIAT',
                    TipoEvento.CURSO_PRAZO_CHEFIA: '👔 Prazo Chefia',
                    TipoEvento.CURSO_CONCLUSAO: '✅ Conclusão',
                    TipoEvento.CURSO_RECEBIMENTO: '📨 Recebimento SIGAD'
                }[tipo]
                st.markdown(f"<span style='color: {cor};'>●</span> {label}", unsafe_allow_html=True)
    
    def _render_eventos_mes(self, eventos: List[EventoCalendario]):
        """Renderiza lista detalhada de eventos do mês."""
        st.markdown("---")
        st.subheader(f"📋 Eventos de {calendar.month_name[st.session_state.cal_mes]}")
        
        # Filtrar eventos do mês
        eventos_mes = [ev for ev in eventos 
                      if ev.data.month == st.session_state.cal_mes 
                      and ev.data.year == st.session_state.cal_ano]
        
        if not eventos_mes:
            st.info("Nenhum evento neste mês")
            return
        
        # Ordenar por data
        eventos_mes.sort(key=lambda x: x.data)
        
        # Agrupar por data
        eventos_por_data: Dict[date, List[EventoCalendario]] = {}
        for ev in eventos_mes:
            if ev.data not in eventos_por_data:
                eventos_por_data[ev.data] = []
            eventos_por_data[ev.data].append(ev)
        
        # Exibir em expanders
        for data_ev, lista_eventos in sorted(eventos_por_data.items()):
            dia_semana = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'][data_ev.weekday()]
            with st.expander(f"📅 {dia_semana}, {data_ev.strftime('%d/%m/%Y')} ({len(lista_eventos)} eventos)"):
                for ev in lista_eventos:
                    col1, col2 = st.columns([0.1, 0.9])
                    with col1:
                        st.markdown(f"<div style='width: 20px; height: 20px; background-color: {ev.cor}; border-radius: 50%;'></div>", 
                                   unsafe_allow_html=True)
                    with col2:
                        st.write(f"**{ev.titulo}**")
                        st.caption(ev.descricao)
