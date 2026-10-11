"""
Módulo de formulários para cadastro e edição de cursos.

Fornece funções para renderizar formulários de entrada de dados
para cadastro e edição de cursos.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, Any, Tuple

from utils.validators import parse_data, limpar_valor


# ============================================
# FORMULÁRIOS DE CURSO
# ============================================

def render_form_novo_curso(
    data_manager,
    backup_manager
) -> Tuple[bool, str]:
    """
    Renderiza formulário de cadastro de novo curso.
    
    Args:
        data_manager: Instância do DataManager
        backup_manager: Instância do BackupManager
        
    Returns:
        Tupla (sucesso, mensagem)
    """
    resultado = (False, "")
    
    with st.form("form_novo_curso"):
        col1, col2 = st.columns(2)
        
        with col1:
            curso = st.text_input("Nome do Curso *", placeholder="Ex: AAC001")
            turma = st.text_input("Turma *", placeholder="Ex: TU 01")
            vagas = st.number_input("Vagas", min_value=0, value=0)
            estado = st.selectbox(
                "Estado",
                ['solicitar voluntários', 'fazer indicação', 'ver vagas escalantes', 'Concluído']
            )
            prioridade = st.selectbox("Prioridade", ['Alta', 'Média', 'Baixa'])
        
        with col2:
            data_siat = st.text_input(
                "Fim da indicação SIAT * (DD/MM/AAAA)",
                placeholder="Ex: 15/12/2024"
            )
            num_sigad = st.text_input("Número do SIGAD")
            om_executora = st.text_input("OM Executora")
            notas = st.text_area("Notas")
        
        # Campo de vagas por OM
        st.markdown("---")
        vagas_om = st.text_area(
            "Vagas por OM (opcional)",
            placeholder="Ex: CRCEA-SE: 3 vagas\nAPP-SP: 2 vagas\nGCC: 1 vaga",
            help="Informe as vagas por organização militar"
        )
        
        salvar_mesmo_assim = st.checkbox(
            "Salvar mesmo assim",
            value=False,
            help="Permite salvar mesmo se já existir um curso cadastrado com o mesmo nome e turma"
        )
        
        submitted = st.form_submit_button("💾 Salvar Curso")
        
        if submitted:
            if not curso or not turma or not data_siat:
                resultado = (False, "Preencha todos os campos obrigatórios (*)")
            else:
                # Preparar dados
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
                
                # Adicionar vagas por OM
                if vagas_om:
                    novo_curso['Notas'] = (
                        f"{notas}\n\nVagas por OM:\n{vagas_om}" 
                        if notas else f"Vagas por OM:\n{vagas_om}"
                    )
                
                # Salvar
                sucesso, msg = data_manager.adicionar_curso(novo_curso, permitir_duplicado=salvar_mesmo_assim)
                if sucesso:
                    backup_manager.criar_backup()
                    resultado = (True, msg)
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
    Renderiza formulário de edição de curso.
    
    Args:
        curso_atual: Série pandas com dados do curso atual
        idx_curso: Índice do curso na base
        data_manager: Instância do DataManager
        df_columns: Lista de colunas do DataFrame
        
    Returns:
        Tupla (sucesso, mensagem)
    """
    resultado = (False, "")
    
    with st.form("form_editar_curso"):
        col1, col2 = st.columns(2)
        
        estados_list = ['solicitar voluntários', 'fazer indicação', 'ver vagas escalantes', 'Concluído']
        prioridade_list = ['Alta', 'Média', 'Baixa']
        
        estado_atual = curso_atual.get('Estado', 'solicitar voluntários')
        prioridade_atual = curso_atual.get('Prioridade', 'Média')
        
        with col1:
            curso = st.text_input("Nome do Curso", value=limpar_valor(curso_atual.get('Curso')))
            turma = st.text_input("Turma", value=limpar_valor(curso_atual.get('Turma')))
            vagas_num = pd.to_numeric(curso_atual.get('Vagas'), errors='coerce')
            vagas_val = int(0 if pd.isna(vagas_num) else max(0, int(vagas_num)))
            vagas = st.number_input(
                "Vagas",
                min_value=0,
                value=vagas_val
            )
            estado = st.selectbox(
                "Estado",
                estados_list,
                index=estados_list.index(estado_atual) if estado_atual in estados_list else 0
            )
            prioridade = st.selectbox(
                "Prioridade",
                prioridade_list,
                index=prioridade_list.index(prioridade_atual) if prioridade_atual in prioridade_list else 1
            )
            dt_siat = parse_data(curso_atual.get('Fim da indicação da SIAT'))
            data_siat_val = dt_siat.strftime('%d/%m/%Y') if dt_siat else limpar_valor(curso_atual.get('Fim da indicação da SIAT'))
            data_siat = st.text_input(
                "Fim da indicação SIAT (DD/MM/AAAA)",
                value=data_siat_val
            )
        
        with col2:
            num_sigad = st.text_input(
                "Número do SIGAD",
                value=limpar_valor(curso_atual.get('Numero do SIGAD'))
            )
            om_executora = st.text_input(
                "OM Executora",
                value=limpar_valor(curso_atual.get('OM_Executora'))
            )
            dt_chefia = parse_data(curso_atual.get('Prazo dado pela chefia'))
            prazo_chefia_val = dt_chefia.strftime('%d/%m/%Y') if dt_chefia else limpar_valor(curso_atual.get('Prazo dado pela chefia'))
            prazo_chefia = st.text_input(
                "Prazo dado pela chefia (DD/MM/AAAA)",
                value=prazo_chefia_val
            )
            sigad_origem = st.text_input(
                "SIGAD que originou (opcional)",
                value=limpar_valor(curso_atual.get('SIGAD que originou'))
            )
            notas = st.text_area(
                "Notas",
                value=limpar_valor(curso_atual.get('Notas'))
            )
            
            # Mostrar data de conclusão (se existir)
            dt_conclusao = parse_data(curso_atual.get('DATA_DA_CONCLUSAO'))
            conclusao_str = dt_conclusao.strftime('%d/%m/%Y') if dt_conclusao else limpar_valor(curso_atual.get('DATA_DA_CONCLUSAO'))
            if conclusao_str:
                st.info(f"📅 Data de Conclusão: {conclusao_str}")
        
        submitted = st.form_submit_button("💾 Atualizar Curso")
        
        if submitted:
            # Preparar dados atualizados
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
            
            # Se o estado for "Concluído" e não tiver data de conclusão
            if estado == 'Concluído':
                if not conclusao_str:
                    curso_atualizado['DATA_DA_CONCLUSAO'] = datetime.now().strftime('%d/%m/%Y')
                else:
                    curso_atualizado['DATA_DA_CONCLUSAO'] = conclusao_str
            
            # Manter valores de OM existentes
            for col in df_columns:
                if col.startswith('OM_') and col != 'OM_Executora':
                    curso_atualizado[col] = curso_atual.get(col, '')
            
            # Atualizar
            sucesso, msg = data_manager.atualizar_curso(idx_curso, curso_atualizado)
            resultado = (sucesso, msg)
    
    return resultado
