"""
Módulo de formulários para cadastro e edição de cursos.

Organiza os campos em seções com títulos padronizados e sem emojis.
"""

from datetime import datetime
from typing import Tuple
import streamlit as st
import pandas as pd

from utils.validators import parse_data, limpar_valor


def render_form_novo_curso(
    data_manager,
    backup_manager
) -> Tuple[bool, str]:
    """
    Renderiza formulário de cadastro de novo curso.
    
    Retorna:
        Tuple[bool, str]: (sucesso, mensagem)
    """
    resultado = (False, "")

    with st.form("form_novo_curso"):
        # Seção 1: Identificação
        st.markdown('<div class="section-title">Identificação</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            curso = st.text_input("Nome do curso *", placeholder="Ex: AAC001")
        with col2:
            turma = st.text_input("Turma *", placeholder="Ex: TU 01")
        with col3:
            om_executora = st.text_input("OM executora", placeholder="Ex: DACTA")

        # Seção 2: Prazos
        st.markdown('<div class="section-title">Prazos</div>', unsafe_allow_html=True)
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            data_siat = st.text_input(
                "Fim da indicação SIAT * (dd/mm/aaaa)",
                placeholder="dd/mm/aaaa"
            )
        with col_p2:
            num_sigad = st.text_input("Número do SIGAD", placeholder="Ex: 67200.001234/2024-00")

        # Seção 3: Vagas
        st.markdown('<div class="section-title">Vagas</div>', unsafe_allow_html=True)
        col_v1, col_v2 = st.columns([1, 2])
        with col_v1:
            vagas = st.number_input("Vagas", min_value=0, value=0)
        with col_v2:
            vagas_om = st.text_area(
                "Vagas por OM (opcional)",
                placeholder="Ex: CRCEA-SE: 3 vagas\nAPP-SP: 2 vagas",
                help="Informe o detalhamento de vagas por organização militar."
            )

        # Seção 4: Andamento
        st.markdown('<div class="section-title">Andamento</div>', unsafe_allow_html=True)
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            estado = st.selectbox(
                "Estado",
                ['solicitar voluntários', 'fazer indicação', 'ver vagas escalantes', 'Concluído']
            )
        with col_a2:
            prioridade = st.selectbox("Prioridade", ['Alta', 'Média', 'Baixa'], index=1)

        notas = st.text_area("Notas", placeholder="Observações e apontamentos adicionais.")

        st.markdown("<hr style='margin: 1.25rem 0;'>", unsafe_allow_html=True)

        salvar_mesmo_assim = st.checkbox(
            "Salvar mesmo se já existir curso com o mesmo nome e turma",
            value=False,
            help="Permite salvar mesmo se já existir um curso cadastrado com o mesmo nome e turma."
        )

        submitted = st.form_submit_button("Salvar curso", type="primary", icon=":material/save:")

        if submitted:
            if not curso or not turma or not data_siat:
                resultado = (False, "Preencha todos os campos obrigatórios marcados com asterisco (*).")
            else:
                novo_curso = {
                    'Curso': curso,
                    'Turma': turma,
                    'Vagas': vagas,
                    'Estado': estado,
                    'Prioridade': prioridade,
                    'Fim da indicação da SIAT': data_siat,
                    'Numero do SIGAD': num_sigad,
                    'OM_Executora': om_executora,
                    'Notas': notas
                }

                if vagas_om:
                    novo_curso['Notas'] = (
                        f"{notas}\n\nVagas por OM:\n{vagas_om}"
                        if notas else f"Vagas por OM:\n{vagas_om}"
                    )

                sucesso, msg = data_manager.adicionar_curso(novo_curso, permitir_duplicado=salvar_mesmo_assim)
                if sucesso:
                    backup_manager.criar_backup()
                    resultado = (True, "Curso salvo.")
                else:
                    resultado = (False, msg)

    return resultado


def render_form_editar_curso(
    curso_atual: pd.Series,
    idx_curso: int,
    data_manager,
    df_columns: list
) -> Tuple[bool, str]:
    """
    Renderiza formulário de edição de curso existente.
    
    Retorna:
        Tuple[bool, str]: (sucesso, mensagem)
    """
    resultado = (False, "")

    with st.form("form_editar_curso"):
        # Seção 1: Identificação
        st.markdown('<div class="section-title">Identificação</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            curso = st.text_input("Nome do curso", value=limpar_valor(curso_atual.get('Curso')))
        with col2:
            turma = st.text_input("Turma", value=limpar_valor(curso_atual.get('Turma')))
        with col3:
            om_executora = st.text_input("OM executora", value=limpar_valor(curso_atual.get('OM_Executora')))

        # Seção 2: Prazos
        st.markdown('<div class="section-title">Prazos</div>', unsafe_allow_html=True)
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            dt_siat = parse_data(curso_atual.get('Fim da indicação da SIAT'))
            data_siat_val = dt_siat.strftime('%d/%m/%Y') if dt_siat else limpar_valor(curso_atual.get('Fim da indicação da SIAT'))
            data_siat = st.text_input(
                "Fim da indicação SIAT (dd/mm/aaaa)",
                value=data_siat_val,
                placeholder="dd/mm/aaaa"
            )

            dt_chefia = parse_data(curso_atual.get('Prazo dado pela chefia'))
            prazo_chefia_val = dt_chefia.strftime('%d/%m/%Y') if dt_chefia else limpar_valor(curso_atual.get('Prazo dado pela chefia'))
            prazo_chefia = st.text_input(
                "Prazo dado pela chefia (dd/mm/aaaa)",
                value=prazo_chefia_val,
                placeholder="dd/mm/aaaa"
            )

        with col_p2:
            num_sigad = st.text_input(
                "Número do SIGAD",
                value=limpar_valor(curso_atual.get('Numero do SIGAD'))
            )
            sigad_origem = st.text_input(
                "SIGAD que originou (opcional)",
                value=limpar_valor(curso_atual.get('SIGAD que originou'))
            )

        # Seção 3: Vagas
        st.markdown('<div class="section-title">Vagas</div>', unsafe_allow_html=True)
        vagas_num = pd.to_numeric(curso_atual.get('Vagas'), errors='coerce')
        vagas_val = int(0 if pd.isna(vagas_num) else max(0, int(vagas_num)))
        vagas = st.number_input("Vagas", min_value=0, value=vagas_val)

        # Seção 4: Andamento
        st.markdown('<div class="section-title">Andamento</div>', unsafe_allow_html=True)
        estados_list = ['solicitar voluntários', 'fazer indicação', 'ver vagas escalantes', 'Concluído']
        prioridade_list = ['Alta', 'Média', 'Baixa']

        estado_atual = curso_atual.get('Estado', 'solicitar voluntários')
        prioridade_atual = curso_atual.get('Prioridade', 'Média')

        col_a1, col_a2 = st.columns(2)
        with col_a1:
            estado = st.selectbox(
                "Estado",
                estados_list,
                index=estados_list.index(estado_atual) if estado_atual in estados_list else 0
            )
        with col_a2:
            prioridade = st.selectbox(
                "Prioridade",
                prioridade_list,
                index=prioridade_list.index(prioridade_atual) if prioridade_atual in prioridade_list else 1
            )

        notas = st.text_area(
            "Notas",
            value=limpar_valor(curso_atual.get('Notas'))
        )

        dt_conclusao = parse_data(curso_atual.get('DATA_DA_CONCLUSAO'))
        conclusao_str = dt_conclusao.strftime('%d/%m/%Y') if dt_conclusao else limpar_valor(curso_atual.get('DATA_DA_CONCLUSAO'))
        if conclusao_str:
            st.info(f"Data de conclusão registrada: {conclusao_str}")

        st.markdown("<hr style='margin: 1.25rem 0;'>", unsafe_allow_html=True)

        submitted = st.form_submit_button("Salvar alterações", type="primary", icon=":material/save:")

        if submitted:
            curso_atualizado = {
                'Curso': curso,
                'Turma': turma,
                'Vagas': vagas,
                'Estado': estado,
                'Prioridade': prioridade,
                'Fim da indicação da SIAT': data_siat,
                'Numero do SIGAD': num_sigad,
                'OM_Executora': om_executora,
                'Prazo dado pela chefia': prazo_chefia,
                'SIGAD que originou': sigad_origem,
                'Notas': notas
            }

            if estado == 'Concluído':
                if not conclusao_str:
                    curso_atualizado['DATA_DA_CONCLUSAO'] = datetime.now().strftime('%d/%m/%Y')
                else:
                    curso_atualizado['DATA_DA_CONCLUSAO'] = conclusao_str

            for col in df_columns:
                if col.startswith('OM_') and col != 'OM_Executora':
                    curso_atualizado[col] = curso_atual.get(col, '')

            sucesso, msg = data_manager.atualizar_curso(idx_curso, curso_atualizado)
            if sucesso:
                resultado = (True, "Alterações salvas.")
            else:
                resultado = (False, msg)

    return resultado
