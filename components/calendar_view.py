"""
Componente de Visualização em Calendário.

Este módulo fornece uma visualização de calendário para os prazos
de cursos e FICs, com navegação mensal/semanal e indicadores visuais.

Usage:
    from components.calendar_view import CalendarView
    
    cal = CalendarView()
    cal.render(dados_cursos)
"""

import calendar
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

import streamlit as st
import pandas as pd

from config import colors
from utils.logger import get_logger

logger = get_logger(__name__)


# ============================================================================
# DATACLASSES E ENUMS
# ============================================================================

class TipoEvento(Enum):
    """Tipos de eventos no calendário."""
    CURSO_PRAZO_SIAT = "prazo_siat"
    CURSO_PRAZO_CHEFIA = "prazo_chefia"
    CURSO_CONCLUSAO = "conclusao"
    FIC_DATA = "fic_data"
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
    
    Exibe prazos de cursos em formato de calendário mensal ou semanal,
    com indicadores visuais de status e navegação intuitiva.
    
    Attributes:
        modo: 'mensal' ou 'semanal'
        mes_atual: Mês sendo exibido
        ano_atual: Ano sendo exibido
    """
    
    # Cores para cada tipo de evento
    CORES_EVENTO = {
        TipoEvento.CURSO_PRAZO_SIAT: "#FF9800",      # Laranja
        TipoEvento.CURSO_PRAZO_CHEFIA: "#2196F3",    # Azul
        TipoEvento.CURSO_CONCLUSAO: "#4CAF50",       # Verde
        TipoEvento.FIC_DATA: "#9C27B0",              # Roxo
        TipoEvento.CURSO_RECEBIMENTO: "#607D8B",     # Cinza azulado
    }
    
    # Cores para status de prazo
    CORES_STATUS = {
        'ok': "#4CAF50",        # Verde
        'atencao': "#FFC107",   # Amarelo
        'urgente': "#F44336",   # Vermelho
        'vencido': "#9E9E9E",   # Cinza
    }
    
    def __init__(self, modo: str = "mensal"):
        """
        Inicializa o calendário.
        
        Args:
            modo: 'mensal' ou 'semanal'
        """
        self.modo = modo.lower()
        self.data_atual = date.today()
        
        # Inicializar estado da sessão para navegação
        if 'cal_mes' not in st.session_state:
            st.session_state.cal_mes = self.data_atual.month
        if 'cal_ano' not in st.session_state:
            st.session_state.cal_ano = self.data_atual.year
        if 'cal_modo' not in st.session_state:
            st.session_state.cal_modo = self.modo
        
        self.mes_atual = st.session_state.cal_mes
        self.ano_atual = st.session_state.cal_ano
        
        logger.debug(f"CalendarView inicializado: {self.modo}")
    
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
            if pd.notna(row.get('Fim da indicação da SIAT')):
                try:
                    data = self._parse_data(row['Fim da indicação da SIAT'])
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
                except:
                    pass
            
            # Prazo da Chefia
            if pd.notna(row.get('Prazo dado pela chefia')):
                try:
                    data = self._parse_data(row['Prazo dado pela chefia'])
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
                except:
                    pass
            
            # Data de conclusão
            if pd.notna(row.get('DATA DA CONCLUSÃO')):
                try:
                    data = self._parse_data(row['DATA DA CONCLUSÃO'])
                    if data:
                        eventos.append(EventoCalendario(
                            data=data,
                            titulo=f"✅ {curso_nome}",
                            tipo=TipoEvento.CURSO_CONCLUSAO,
                            descricao=f"Conclusão: {curso_nome}",
                            cor=self.CORES_EVENTO[TipoEvento.CURSO_CONCLUSAO],
                            id_referencia=str(idx)
                        ))
                except:
                    pass
            
            # Recebimento SIGAD
            if pd.notna(row.get('Recebimento do SIGAD com as vagas')):
                try:
                    data = self._parse_data(row['Recebimento do SIGAD com as vagas'])
                    if data:
                        eventos.append(EventoCalendario(
                            data=data,
                            titulo=f"📨 {curso_nome}",
                            tipo=TipoEvento.CURSO_RECEBIMENTO,
                            descricao=f"Recebimento SIGAD: {curso_nome}",
                            cor=self.CORES_EVENTO[TipoEvento.CURSO_RECEBIMENTO],
                            id_referencia=str(idx)
                        ))
                except:
                    pass
        
        return eventos
    
    def converter_fics_para_eventos(self, df_fics: pd.DataFrame) -> List[EventoCalendario]:
        """
        Converte DataFrame de FICs em lista de eventos.
        
        Args:
            df_fics: DataFrame com dados dos FICs
            
        Returns:
            Lista de EventoCalendario
        """
        eventos = []
        
        if df_fics.empty:
            return eventos
        
        for idx, row in df_fics.iterrows():
            pessoa = row.get('nome', f'Pessoa {idx}')
            
            # Data de emissão/cadastro do FIC
            if pd.notna(row.get('data_criacao')):
                try:
                    data = self._parse_data(row['data_criacao'])
                    if data:
                        eventos.append(EventoCalendario(
                            data=data,
                            titulo=f"📄 FIC: {pessoa}",
                            tipo=TipoEvento.FIC_DATA,
                            descricao=f"FIC cadastrado: {pessoa}",
                            cor=self.CORES_EVENTO[TipoEvento.FIC_DATA],
                            id_referencia=f"fic_{idx}"
                        ))
                except:
                    pass
        
        return eventos
    
    def _parse_data(self, valor: Any) -> Optional[date]:
        """
        Tenta converter qualquer valor em date.
        
        Args:
            valor: Valor a ser convertido
            
        Returns:
            date ou None
        """
        if pd.isna(valor):
            return None
        
        if isinstance(valor, date):
            return valor
        
        if isinstance(valor, datetime):
            return valor.date()
        
        # Tentar formatos comuns
        formatos = [
            "%d/%m/%Y",
            "%Y-%m-%d",
            "%d-%m-%Y",
            "%m/%d/%Y",
            "%Y/%m/%d",
        ]
        
        for fmt in formatos:
            try:
                return datetime.strptime(str(valor), fmt).date()
            except:
                continue
        
        # Tentar com pandas
        try:
            return pd.to_datetime(valor).date()
        except:
            return None
    
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
    
    def render(self, df_cursos: pd.DataFrame, df_fics: Optional[pd.DataFrame] = None):
        """
        Renderiza o calendário completo.
        
        Args:
            df_cursos: DataFrame com cursos
            df_fics: DataFrame opcional com FICs
        """
        # Converter dados em eventos
        eventos = self.converter_cursos_para_eventos(df_cursos)
        
        if df_fics is not None:
            eventos.extend(self.converter_fics_para_eventos(df_fics))
        
        # Renderizar controles
        self._render_controles()
        
        # Renderizar calendário baseado no modo
        if st.session_state.cal_modo == "mensal":
            self._render_calendario_mensal(eventos)
        else:
            self._render_calendario_semanal(eventos)
        
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
                max_value=2030,
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
            if st.button("📅 Ir para Mês Atual", use_container_width=True, key="cal_hoje"):
                st.session_state.cal_mes = date.today().month
                st.session_state.cal_ano = date.today().year
                st.rerun()
        
        # Seleção de modo
        modo = st.radio(
            "Visualização",
            ["Mensal", "Semanal"],
            horizontal=True,
            key="cal_modo_radio"
        )
        st.session_state.cal_modo = modo.lower()
    
    def _navegar_anterior(self):
        """Navega para o período anterior."""
        if st.session_state.cal_modo == "mensal":
            if st.session_state.cal_mes == 1:
                st.session_state.cal_mes = 12
                st.session_state.cal_ano -= 1
            else:
                st.session_state.cal_mes -= 1
        else:
            # Modo semanal - subtrair 7 dias (implementação simplificada)
            pass
        st.rerun()
    
    def _navegar_proximo(self):
        """Navega para o próximo período."""
        if st.session_state.cal_modo == "mensal":
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
    
    def _render_calendario_semanal(self, eventos: List[EventoCalendario]):
        """
        Renderiza calendário semanal (simplificado).
        
        Args:
            eventos: Lista de eventos
        """
        # Calcular semana atual
        hoje = date.today()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        
        st.markdown(f"<h3 style='text-align: center;'>Semana de {inicio_semana.strftime('%d/%m/%Y')}</h3>", 
                   unsafe_allow_html=True)
        
        # Agrupar eventos por dia da semana
        eventos_semana: Dict[int, List[EventoCalendario]] = {i: [] for i in range(7)}
        
        for ev in eventos:
            for i in range(7):
                dia_semana = inicio_semana + timedelta(days=i)
                if ev.data == dia_semana:
                    eventos_semana[i].append(ev)
        
        dias_nomes = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        
        for i in range(7):
            dia_atual = inicio_semana + timedelta(days=i)
            eh_hoje = dia_atual == hoje
            
            with st.container():
                if eh_hoje:
                    st.markdown(f"#### 📍 **{dias_nomes[i]}** ({dia_atual.strftime('%d/%m')})")
                else:
                    st.markdown(f"#### {dias_nomes[i]} ({dia_atual.strftime('%d/%m')})")
                
                eventos_dia = eventos_semana[i]
                if eventos_dia:
                    for ev in eventos_dia:
                        self._render_evento_card(ev)
                else:
                    st.caption("Nenhum evento")
                
                st.divider()
    
    def _render_evento_card(self, evento: EventoCalendario):
        """Renderiza um card de evento."""
        cor_hex = evento.cor.lstrip('#')
        r, g, b = tuple(int(cor_hex[i:i+2], 16) for i in (0, 2, 4))
        
        st.markdown(f"""
        <div style='
            background-color: {evento.cor}20;
            border-left: 4px solid {evento.cor};
            padding: 8px 12px;
            margin: 4px 0;
            border-radius: 4px;
        '>
            <div style='font-weight: bold; color: {evento.cor};'>{evento.titulo}</div>
            <div style='font-size: 0.85em; color: #666;'>{evento.descricao}</div>
        </div>
        """, unsafe_allow_html=True)
    
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
                    TipoEvento.FIC_DATA: '📄 FIC',
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
