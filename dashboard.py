"""
Módulo de exibição do Painel (Dashboard).

Conceito de design: Fila de prazos com 3 seções compactas,
andamento das indicações como sequência horizontal de etapas
e linha inferior de totais rotulados.
"""

from datetime import date, timedelta
import streamlit as st
import pandas as pd

from components.ui import (
    render_faixa_compacta,
    render_andamento_indicacoes,
    render_totais_painel
)
from utils.validators import parse_data, curso_concluido


class Dashboard:
    """Gerenciador de apresentação do Painel."""

    def __init__(self):
        pass

    def mostrar_dashboard(self, df: pd.DataFrame) -> None:
        """Renderiza a visualização principal do painel."""
        if df is None or df.empty:
            st.info("Nenhum dado disponível para o painel.")
            return

        hoje = date.today()
        data_30_dias = (hoje + timedelta(days=30)).strftime('%d/%m/%Y')

        # Filtrar cursos ativos (excluir concluídos)
        cursos_ativos = []
        for idx, row in df.iterrows():
            if not curso_concluido(row):
                dt_siat = parse_data(row.get('Fim da indicação da SIAT'))
                dias = (dt_siat - hoje).days if dt_siat else None
                cursos_ativos.append({
                    'index': idx,
                    'row': row,
                    'dt_siat': dt_siat,
                    'dias': dias
                })

        # Divisão da fila de prazos
        vencidos = [c for c in cursos_ativos if c['dias'] is not None and c['dias'] < 0]
        urgentes = [c for c in cursos_ativos if c['dias'] is not None and 0 <= c['dias'] <= 5]
        proximas_semanas = [c for c in cursos_ativos if c['dias'] is not None and 6 <= c['dias'] <= 30]

        # Ordenações:
        # Vencidos: mais recentemente vencidos primeiro (dias mais próximos de 0)
        vencidos.sort(key=lambda x: x['dias'], reverse=True)
        # Próximos 5 dias: prazo mais próximo primeiro
        urgentes.sort(key=lambda x: x['dias'])
        # Próximas semanas: prazo mais próximo primeiro
        proximas_semanas.sort(key=lambda x: x['dias'])

        # Seção Superior: Fila de prazos (3 colunas compactas com mesma altura visual)
        st.markdown('<div class="section-title" style="margin-top: 0; margin-bottom: 0.75rem;">Fila de prazos</div>', unsafe_allow_html=True)
        col_vencidos, col_urgentes, col_semanas = st.columns(3, gap="medium")

        # Coluna 1: Vencidos
        with col_vencidos:
            count_vencidos = len(vencidos)
            with st.container(border=True, key="fila_card_vencidos"):
                st.markdown(f"""
                <div class="fila-header">
                  <div class="fila-title">Vencidos</div>
                  <div class="big-number late">{count_vencidos}</div>
                </div>
                """, unsafe_allow_html=True)

                with st.container(key="fila_lista_vencidos"):
                    if not vencidos:
                        st.markdown('<div class="empty-strip-msg">Nenhum prazo nesta janela.</div>', unsafe_allow_html=True)
                    else:
                        strips_html = "".join(render_faixa_compacta(c['row']) for c in vencidos[:5])
                        st.markdown(strips_html, unsafe_allow_html=True)

                if st.button("Ver todos", key="btn_ver_vencidos", icon=":material/arrow_forward:", type="secondary", use_container_width=True):
                    st.session_state["filtro_status"] = "Atrasados"
                    st.session_state["cursos_limite"] = 25
                    st.session_state["pagina"] = "cursos"
                    st.rerun()

        # Coluna 2: Próximos 5 dias
        with col_urgentes:
            count_urgentes = len(urgentes)
            with st.container(border=True, key="fila_card_urgentes"):
                st.markdown(f"""
                <div class="fila-header">
                  <div class="fila-title">Próximos 5 dias</div>
                  <div class="big-number soon">{count_urgentes}</div>
                </div>
                """, unsafe_allow_html=True)

                with st.container(key="fila_lista_urgentes"):
                    if not urgentes:
                        st.markdown('<div class="empty-strip-msg">Nenhum prazo nesta janela.</div>', unsafe_allow_html=True)
                    else:
                        strips_html = "".join(render_faixa_compacta(c['row']) for c in urgentes[:5])
                        st.markdown(strips_html, unsafe_allow_html=True)

                if st.button("Ver todos", key="btn_ver_urgentes", icon=":material/arrow_forward:", type="secondary", use_container_width=True):
                    st.session_state["filtro_status"] = "Próximos 5 dias"
                    st.session_state["cursos_limite"] = 25
                    st.session_state["pagina"] = "cursos"
                    st.rerun()

        # Coluna 3: Próximas semanas (6-30 dias)
        with col_semanas:
            count_semanas = len(proximas_semanas)
            with st.container(border=True, key="fila_card_semanas"):
                st.markdown(f"""
                <div class="fila-header">
                  <div class="fila-title">Próximas semanas</div>
                  <div class="big-number ok">{count_semanas}</div>
                </div>
                """, unsafe_allow_html=True)

                with st.container(key="fila_lista_semanas"):
                    msg_vazio = f"Nenhum outro prazo até {data_30_dias}"
                    if not proximas_semanas:
                        st.markdown(f'<div class="empty-strip-msg">{msg_vazio}</div>', unsafe_allow_html=True)
                    else:
                        strips_html = "".join(render_faixa_compacta(c['row']) for c in proximas_semanas[:5])
                        if len(proximas_semanas) < 5:
                            strips_html += f'<div class="empty-strip-msg">{msg_vazio}</div>'
                        st.markdown(strips_html, unsafe_allow_html=True)

                if st.button("Ver todos", key="btn_ver_semanas", icon=":material/arrow_forward:", type="secondary", use_container_width=True):
                    st.session_state["filtro_status"] = "No prazo"
                    st.session_state["cursos_limite"] = 25
                    st.session_state["pagina"] = "cursos"
                    st.rerun()

        # Seção Central: Andamento das indicações com totais no rodapé
        vagas_total = 0
        if 'Vagas' in df.columns:
            vagas_total = int(pd.to_numeric(df['Vagas'], errors='coerce').fillna(0).sum())

        render_andamento_indicacoes(df, total_cursos=len(df), total_vagas=vagas_total)
