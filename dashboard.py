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
        st.markdown('<div class="section-title" style="margin-top: 0; margin-bottom: 16px;">Fila de prazos</div>', unsafe_allow_html=True)
        cards = [
            ("Vencidos", "late", "Atrasados", vencidos, len(vencidos), "Nenhum prazo nesta janela."),
            ("Próximos 5 dias", "soon", "Próximos 5 dias", urgentes, len(urgentes), "Nenhum prazo nesta janela."),
            ("Próximas semanas", "ok", "No prazo", proximas_semanas, len(proximas_semanas), f"Nenhum outro prazo até {data_30_dias}"),
        ]
        key_suffixes = ["vencidos", "urgentes", "semanas"]

        with st.container(horizontal=True, gap="medium", key="fila_row"):
            for n, (titulo, cor_classe, filtro, itens, total, vazio) in enumerate(cards):
                btn_key = key_suffixes[n]
                with st.container(border=True, key=f"fila_card_{n}", height="stretch", width="stretch"):
                    with st.container(horizontal=True, horizontal_alignment="distribute", vertical_alignment="center", key=f"fila_head_{n}"):
                        st.markdown(f'<span class="fila-titulo">{titulo}</span>', unsafe_allow_html=True)
                        if st.button("Ver todos", key=f"btn_ver_{btn_key}", type="tertiary",
                                     icon=":material/arrow_forward:", icon_position="right"):
                            st.session_state["filtro_status"] = filtro
                            st.session_state["cursos_limite"] = 25
                            st.session_state["pagina"] = "cursos"
                            st.rerun()

                    st.markdown(f'<div class="big-number {cor_classe}">{total}</div>', unsafe_allow_html=True)

                    if not itens:
                        st.markdown(f'<p class="empty-strip-msg">{vazio}</p>', unsafe_allow_html=True)
                    else:
                        strips_html = "".join(render_faixa_compacta(c['row']) for c in itens[:5])
                        if btn_key == "semanas" and len(itens) < 5:
                            strips_html += f'<p class="empty-strip-msg">{vazio}</p>'
                        st.markdown(strips_html, unsafe_allow_html=True)

        # Seção Central: Andamento das indicações com totais no rodapé
        vagas_total = 0
        if 'Vagas' in df.columns:
            vagas_total = int(pd.to_numeric(df['Vagas'], errors='coerce').fillna(0).sum())

        render_andamento_indicacoes(df, total_cursos=len(df), total_vagas=vagas_total)
