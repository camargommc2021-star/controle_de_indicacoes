"""
Módulo de cards para exibição de cursos e métricas.

Fornece funções para renderizar cards visuais de cursos com status colorido,
métricas de resumo e indicadores de prazo.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from typing import Optional, Dict, Any


# ============================================
# CORES E CONFIGURAÇÕES
# ============================================

# ============================================
# CORES E CONFIGURAÇÕES - Design System v2.0
# ============================================

# Cores do novo design system
CORES_PRIMARIAS = {
    'primary-50': '#eff6ff',
    'primary-100': '#dbeafe',
    'primary-200': '#bfdbfe',
    'primary-500': '#3b82f6',
    'primary-600': '#2563eb',
    'primary-700': '#1d4ed8',
}

CORES_STATUS = {
    'success': '#10b981',
    'success-light': '#d1fae5',
    'warning': '#f59e0b',
    'warning-light': '#fef3c7',
    'danger': '#ef4444',
    'danger-light': '#fee2e2',
    'info': '#06b6d4',
    'info-light': '#cffafe',
    'gray': '#6b7280',
    'gray-light': '#f3f4f6',
}

CORES_ESTADO = {
    'solicitar voluntários': CORES_STATUS['danger'],
    'fazer indicação': CORES_STATUS['warning'],
    'ver vagas escalantes': CORES_STATUS['info'],
    'Concluído': CORES_STATUS['success'],
    'Sem estado': CORES_STATUS['gray'],
}

CORES_PRIORIDADE = {
    'Alta': CORES_STATUS['danger'],
    'Média': CORES_STATUS['warning'],
    'Baixa': CORES_STATUS['success'],
}


def get_cor_prazo(data_str: str | date | None) -> str:
    """
    Retorna a cor baseada nos dias restantes.
    
    Args:
        data_str: Data no formato DD/MM/AAAA ou objeto date
        
    Returns:
        Código hex da cor correspondente ao prazo
    """
    try:
        if not data_str:
            return CORES_STATUS['gray']
        
        if isinstance(data_str, str):
            data = datetime.strptime(data_str, "%d/%m/%Y").date()
        else:
            data = data_str
        
        hoje = date.today()
        dias_restantes = (data - hoje).days
        
        if dias_restantes < 0:
            return CORES_STATUS['danger']  # Atrasado
        elif dias_restantes <= 3:
            return CORES_STATUS['danger']  # Urgente
        elif dias_restantes <= 7:
            return CORES_STATUS['warning']  # Atenção
        elif dias_restantes <= 14:
            return CORES_STATUS['info']  # Próximo
        else:
            return CORES_STATUS['success']  # Tranquilo
    except:
        return CORES_STATUS['gray']


def get_status_prazo(data_str: str | date | None) -> str:
    """
    Retorna o texto de status baseado nos dias restantes.
    
    Args:
        data_str: Data no formato DD/MM/AAAA ou objeto date
        
    Returns:
        Texto descritivo do status do prazo
    """
    try:
        if not data_str:
            return "Sem data"
        
        if isinstance(data_str, str):
            data = datetime.strptime(data_str, "%d/%m/%Y").date()
        else:
            data = data_str
        
        hoje = date.today()
        dias_restantes = (data - hoje).days
        
        if dias_restantes < 0:
            return f"Atrasado ({abs(dias_restantes)} dias)"
        elif dias_restantes == 0:
            return "Vence HOJE"
        else:
            return f"{dias_restantes} dias restantes"
    except:
        return "Data inválida"


def get_cor_prazo_chefia(data_str: str | date | None) -> str:
    """
    Retorna a cor para prazo da chefia.
    
    Args:
        data_str: Data no formato DD/MM/AAAA ou objeto date
        
    Returns:
        Código hex da cor
    """
    try:
        if not data_str:
            return CORES_STATUS['gray']
        
        if isinstance(data_str, str):
            data = datetime.strptime(data_str, "%d/%m/%Y").date()
        else:
            data = data_str
        
        hoje = date.today()
        dias_restantes = (data - hoje).days
        
        if dias_restantes <= 5 and dias_restantes >= 0:
            return CORES_STATUS['warning']  # Prazo chefia próximo
        elif dias_restantes < 0:
            return CORES_STATUS['danger']  # Atrasado
        else:
            return CORES_STATUS['gray']  # Tranquilo
    except:
        return CORES_STATUS['gray']


# ============================================
# CARDS DE CURSO
# ============================================

def render_curso_card(
    curso: Dict[str, Any],
    index: int,
    on_delete: Optional[callable] = None
) -> None:
    """
    Renderiza um card completo de curso com todas as informações.
    
    Args:
        curso: Dicionário com dados do curso
        index: Índice do curso (para keys únicas)
        on_delete: Callback opcional para exclusão (recebe o index)
    """
    curso_nome = curso.get('Curso', 'Sem nome')
    turma = curso.get('Turma', 'N/A')
    vagas = curso.get('Vagas', 0)
    estado = curso.get('Estado', 'Sem estado')
    prioridade = curso.get('Prioridade', '')
    data_siat = curso.get('Fim da indicação da SIAT', '')
    prazo_chefia = curso.get('Prazo dado pela chefia', '')
    
    cor_estado = CORES_ESTADO.get(estado, '#95a5a6')
    cor_chefia = get_cor_prazo_chefia(prazo_chefia) if prazo_chefia else None
    
    col1, col2, col3, col4 = st.columns([3, 1, 2, 1])
    
    with col1:
        st.write(f"**{curso_nome}**")
        st.caption(f"Turma: {turma}")
        render_priority_badge(prioridade)
    
    with col2:
        st.write(f"👥 {vagas} vagas")
    
    with col3:
        # Alerta de prazo SIAT
        if data_siat:
            cor_prazo = get_cor_prazo(data_siat)
            dias_restantes = get_status_prazo(data_siat)
            st.markdown(
                f"<span style='color: {cor_prazo};'>⏰ {dias_restantes}</span>",
                unsafe_allow_html=True
            )
        
        # Alerta de prazo Chefia
        if prazo_chefia and cor_chefia == "#9b59b6":
            st.markdown(
                f"<span style='color: #9b59b6; font-weight: bold;'>🟣 Prazo Chefia: {prazo_chefia}</span>",
                unsafe_allow_html=True
            )
        elif prazo_chefia:
            st.caption(f"Chefia: {prazo_chefia}")
    
    with col4:
        if on_delete:
            if st.button("🗑️", key=f"del_{index}"):
                on_delete(index)
    
    st.markdown("---")


def render_curso_card_compact(
    curso: Dict[str, Any],
    index: int,
    on_delete: Optional[callable] = None
) -> None:
    """
    Renderiza um card compacto de curso (para listas de concluídos).
    
    Args:
        curso: Dicionário com dados do curso
        index: Índice do curso
        on_delete: Callback opcional para exclusão
    """
    curso_nome = curso.get('Curso', 'Sem nome')
    turma = curso.get('Turma', 'N/A')
    vagas = curso.get('Vagas', 0)
    data_conclusao = curso.get('DATA_DA_CONCLUSAO', '')
    
    col1, col2, col3 = st.columns([4, 2, 1])
    
    with col1:
        st.write(f"**{curso_nome}**")
        st.caption(f"Turma: {turma}")
    
    with col2:
        st.write(f"👥 {vagas} vagas")
        conclusao_str = str(data_conclusao).strip()
        if conclusao_str and conclusao_str.lower() != 'nan':
            st.success(f"✅ Concluído em: {data_conclusao}")
    
    with col3:
        if on_delete:
            if st.button("🗑️", key=f"del_conc_{index}"):
                on_delete(index)
    
    st.markdown("---")


# ============================================
# BADGES E INDICADORES
# ============================================

def render_status_badge(estado: str) -> None:
    """
    Renderiza um badge de status simples.
    
    Args:
        estado: Nome do estado do curso
    """
    cor = CORES_ESTADO.get(estado, CORES_STATUS['gray'])
    st.markdown(
        f"""
        <span style="
            color: {cor};
            font-size: 0.8rem;
            font-weight: 500;
            padding: 2px 8px;
            background: {cor}15;
            border-radius: 4px;
        ">{estado}</span>
        """,
        unsafe_allow_html=True
    )


def render_priority_badge(prioridade: str) -> None:
    """
    Renderiza um badge de prioridade simples.
    
    Args:
        prioridade: Alta, Média ou Baixa
    """
    if not prioridade:
        return
    
    cor = CORES_PRIORIDADE.get(prioridade, CORES_STATUS['gray'])
    st.markdown(
        f"<span style='color: {cor}; font-size: 0.8rem; font-weight: 500;'>● {prioridade}</span>",
        unsafe_allow_html=True
    )


def render_prazo_indicator(
    data_str: str | date | None,
    label: str = "⏰"
) -> None:
    """
    Renderiza um indicador visual de prazo.
    
    Args:
        data_str: Data do prazo
        label: Label opcional antes do texto
    """
    if not data_str:
        st.caption(f"{label} Sem data definida")
        return
    
    cor = get_cor_prazo(data_str)
    status = get_status_prazo(data_str)
    
    st.markdown(
        f"<span style='color: {cor}; font-weight: 500;'>{label} {status}</span>",
        unsafe_allow_html=True
    )


# ============================================
# CARDS DE MÉTRICAS
# ============================================

def render_metric_card(
    label: str,
    value: int | str,
    icon: str = "",
    delta: Optional[str] = None,
    help_text: Optional[str] = None
) -> None:
    """
    Renderiza um card de métrica simples.
    
    Args:
        label: Título da métrica
        value: Valor a ser exibido
        icon: Ícone do card
        delta: Texto opcional de variação
        help_text: Texto de ajuda opcional
    """
    if help_text:
        st.metric(label=f"{icon} {label}" if icon else label, value=value, delta=delta, help=help_text)
    else:
        st.metric(label=f"{icon} {label}" if icon else label, value=value, delta=delta)


def render_metric_cards_row(
    metrics: list[Dict[str, Any]]
) -> None:
    """
    Renderiza uma linha de cards de métricas.
    
    Args:
        metrics: Lista de dicionários com keys: label, value, icon, delta, help
    """
    cols = st.columns(len(metrics))
    
    for idx, metric in enumerate(metrics):
        with cols[idx]:
            render_metric_card(
                label=metric.get('label', ''),
                value=metric.get('value', 0),
                icon=metric.get('icon', '📊'),
                delta=metric.get('delta'),
                help_text=metric.get('help')
            )


def render_estado_summary(df: pd.DataFrame) -> None:
    """
    Renderiza cards de resumo por estado.
    
    Args:
        df: DataFrame com dados dos cursos
    """
    if df.empty or 'Estado' not in df.columns:
        return
    
    estados = df['Estado'].value_counts().to_dict()
    
    st.subheader("📊 Resumo por Estado")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card("Solicitar Voluntários", estados.get('solicitar voluntários', 0))
    with col2:
        render_metric_card("Fazer Indicação", estados.get('fazer indicação', 0))
    with col3:
        render_metric_card("Ver Vagas Escalantes", estados.get('ver vagas escalantes', 0))
    with col4:
        render_metric_card("Concluídos", estados.get('Concluído', 0))
