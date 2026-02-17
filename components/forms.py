"""
Módulo de formulários para cadastro e edição.

Fornece funções para renderizar formulários de entrada de dados
para cursos e FICs (Ficha de Indicação de Candidato).
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, Any, Tuple


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
                sucesso, msg = data_manager.adicionar_curso(novo_curso)
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
            curso = st.text_input("Nome do Curso", value=curso_atual.get('Curso', ''))
            turma = st.text_input("Turma", value=curso_atual.get('Turma', ''))
            vagas = st.number_input(
                "Vagas",
                min_value=0,
                value=int(curso_atual.get('Vagas', 0)) if pd.notna(curso_atual.get('Vagas', 0)) else 0
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
            data_siat = st.text_input(
                "Fim da indicação SIAT (DD/MM/AAAA)",
                value=str(curso_atual.get('Fim da indicação da SIAT', ''))
            )
        
        with col2:
            num_sigad = st.text_input(
                "Número do SIGAD",
                value=str(curso_atual.get('Numero do SIGAD', ''))
            )
            om_executora = st.text_input(
                "OM Executora",
                value=str(curso_atual.get('OM_Executora', ''))
            )
            prazo_chefia = st.text_input(
                "Prazo dado pela chefia (DD/MM/AAAA)",
                value=str(curso_atual.get('Prazo dado pela chefia', ''))
            )
            sigad_origem = st.text_input(
                "SIGAD que originou (opcional)",
                value=str(curso_atual.get('SIGAD que originou', ''))
            )
            notas = st.text_area(
                "Notas",
                value=str(curso_atual.get('Notas', ''))
            )
            
            # Mostrar data de conclusão (se existir)
            data_conclusao = curso_atual.get('DATA_DA_CONCLUSAO', '')
            conclusao_str = str(data_conclusao).strip()
            if conclusao_str and conclusao_str.lower() != 'nan':
                st.info(f"📅 Data de Conclusão: {data_conclusao}")
        
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
                if not conclusao_str or conclusao_str.lower() == 'nan':
                    curso_atualizado['DATA_DA_CONCLUSAO'] = datetime.now().strftime('%d/%m/%Y')
                else:
                    curso_atualizado['DATA_DA_CONCLUSAO'] = data_conclusao
            
            # Manter valores de OM existentes
            for col in df_columns:
                if col.startswith('OM_') and col != 'OM_Executora':
                    curso_atualizado[col] = curso_atual.get(col, '')
            
            # Atualizar
            sucesso, msg = data_manager.atualizar_curso(idx_curso, curso_atualizado)
            resultado = (sucesso, msg)
    
    return resultado


# ============================================
# FORMULÁRIOS DE FIC
# ============================================

def _render_fic_fields(
    fic_atual: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Renderiza apenas os campos do formulário FIC (sem o wrapper de formulário).
    
    Esta função é usada internamente por render_form_fic e render_form_editar_fic.
    
    Args:
        fic_atual: Dados do FIC atual (para edição)
        
    Returns:
        Dicionário com todos os valores dos campos
    """
    valores = {}
    
    # Seção 1: Dados do Curso
    with st.expander("📚 Dados do Curso", expanded=True):
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            curso = st.text_input(
                "Código do Curso *",
                value=fic_atual.get('Curso', '') if fic_atual else '',
                placeholder="Ex: CILE-MOD I"
            )
            turma = st.text_input(
                "Turma *",
                value=fic_atual.get('Turma', '') if fic_atual else '',
                placeholder="Ex: 01/2026"
            )
            local_gt = st.text_input(
                "Local do Curso GT *",
                value=fic_atual.get('Local_GT', '') if fic_atual else '',
                placeholder="Ex: FEAR"
            )
        with col_c2:
            comando = st.text_input(
                "Comando *",
                value=fic_atual.get('Comando', '') if fic_atual else '',
                placeholder="Ex: DECEA"
            )
            data_inicio_pres = st.text_input(
                "Data Início (Presencial)",
                value=fic_atual.get('Data_Inicio_Presencial', '') if fic_atual else '',
                placeholder="DD/MM/AAAA"
            )
            data_term_pres = st.text_input(
                "Data Término (Presencial)",
                value=fic_atual.get('Data_Termino_Presencial', '') if fic_atual else '',
                placeholder="DD/MM/AAAA"
            )
        
        ppd_options = ["", "SIM", "NÃO"]
        ppd_index = ppd_options.index(fic_atual.get('PPD_Civil', '')) if fic_atual and fic_atual.get('PPD_Civil', '') in ppd_options else 0
        ppd_civil = st.selectbox("PPD (para civis)", ppd_options, index=ppd_index)
    
    # Seção 2: Dados Pessoais
    with st.expander("👤 Dados Pessoais", expanded=True):
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            posto_grad = st.text_input(
                "Posto/Graduação *",
                value=fic_atual.get('Posto_Graduacao', '') if fic_atual else '',
                placeholder="Ex: 1S"
            )
            nome_completo = st.text_input(
                "Nome Completo *",
                value=fic_atual.get('Nome_Completo', '') if fic_atual else '',
                placeholder="Nome completo do candidato"
            )
            om_indicado = st.text_input(
                "OM do Indicado *",
                value=fic_atual.get('OM_Indicado', '') if fic_atual else '',
                placeholder="Ex: CRCEA-SE"
            )
        with col_p2:
            cpf = st.text_input(
                "CPF",
                value=fic_atual.get('CPF', '') if fic_atual else '',
                placeholder="000.000.000-00"
            )
            saram = st.text_input(
                "SARAM",
                value=fic_atual.get('SARAM', '') if fic_atual else '',
                placeholder="000000-0"
            )
            email = st.text_input(
                "E-mail",
                value=fic_atual.get('Email', '') if fic_atual else ''
            )
            telefone = st.text_input(
                "Telefone",
                value=fic_atual.get('Telefone', '') if fic_atual else '',
                placeholder="(00) 00000-0000"
            )
    
    # Seção 3: Dados Funcionais
    with st.expander("💼 Dados Funcionais", expanded=True):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            funcao_atual = st.text_input(
                "Função Atual",
                value=fic_atual.get('Funcao_Atual', '') if fic_atual else '',
                placeholder="Ex: SUPERVISOR DO APP-SP"
            )
            data_ult_promo = st.text_input(
                "Data Última Promoção",
                value=fic_atual.get('Data_Ultima_Promocao', '') if fic_atual else '',
                placeholder="DD/MM/AAAA"
            )
        with col_f2:
            funcao_apos = st.text_input(
                "Função Após Curso",
                value=fic_atual.get('Funcao_Apos_Curso', '') if fic_atual else ''
            )
            tempo_servico = st.text_input(
                "Tempo de Serviço",
                value=fic_atual.get('Tempo_Servico', '') if fic_atual else '',
                placeholder="Ex: 18 ANOS e 11 MESES"
            )
        
        pre_req_options = ["SIM", "NÃO"]
        pre_req_index = pre_req_options.index(fic_atual.get('Pre_Requisitos', 'SIM')) if fic_atual and fic_atual.get('Pre_Requisitos') in pre_req_options else 0
        pre_requisitos = st.selectbox("Possui Pré-requisitos?", pre_req_options, index=pre_req_index)
    
    # Seção 4: Questionário
    with st.expander("❓ Questionário", expanded=True):
        sim_nao = ["SIM", "NÃO"]
        
        curso_mapeado_index = sim_nao.index(fic_atual.get('Curso_Mapeado', 'SIM')) if fic_atual and fic_atual.get('Curso_Mapeado') in sim_nao else 0
        progressao_index = sim_nao.index(fic_atual.get('Progressao_Carreira', 'SIM')) if fic_atual and fic_atual.get('Progressao_Carreira') in sim_nao else 0
        comunicado_index = sim_nao.index(fic_atual.get('Comunicado_Indicado', 'SIM')) if fic_atual and fic_atual.get('Comunicado_Indicado') in sim_nao else 0
        outro_imp_index = ["NÃO", "SIM"].index(fic_atual.get('Outro_Impedimento', 'NÃO')) if fic_atual and fic_atual.get('Outro_Impedimento') in ["NÃO", "SIM"] else 0
        
        curso_mapeado = st.selectbox("Curso mapeado no posto de trabalho?", sim_nao, index=curso_mapeado_index, key="q1")
        progressao = st.selectbox("Faz parte da progressão individual?", sim_nao, index=progressao_index, key="q2")
        comunicado = st.selectbox("Foi comunicado e confirmou não ter impedimentos?", sim_nao, index=comunicado_index, key="q3")
        outro_impedimento = st.selectbox("Tem outro impedimento?", ["NÃO", "SIM"], index=outro_imp_index, key="q4")
        
        col_q1, col_q2 = st.columns(2)
        with col_q1:
            curso_ant_index = ["NÃO", "SIM"].index(fic_atual.get('Curso_Anterior', 'NÃO')) if fic_atual and fic_atual.get('Curso_Anterior') in ["NÃO", "SIM"] else 0
            curso_anterior = st.selectbox("Já realizou o curso anteriormente?", ["NÃO", "SIM"], index=curso_ant_index, key="q5")
        with col_q2:
            ano_curso_ant_value = fic_atual.get('Ano_Curso_Anterior', '') if fic_atual and curso_anterior == "SIM" else ''
            ano_curso_ant = st.text_input("Em que ano?", value=ano_curso_ant_value, placeholder="AAAA")
        
        ciencia_index = sim_nao.index(fic_atual.get('Ciencia_Dedicacao_EAD', 'SIM')) if fic_atual and fic_atual.get('Ciencia_Dedicacao_EAD') in sim_nao else 0
        ciencia_ead = st.selectbox("Chefe ciente da dedicação exclusiva (EAD)?", sim_nao, index=ciencia_index, key="q6")
    
    # Seção 5: Justificativa e Assinaturas
    with st.expander("📝 Justificativa e Assinaturas", expanded=True):
        justificativa_value = fic_atual.get('Justificativa_Chefe', '') if fic_atual else ''
        justificativa = st.text_area(
            "Justificativa do Chefe Imediato *",
            height=100,
            value=justificativa_value,
            placeholder="Descreva a justificativa para a indicação..."
        )
        
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            nome_chefe = st.text_input(
                "Nome do Chefe do COP *",
                value=fic_atual.get('Nome_Chefe_COP', '') if fic_atual else ''
            )
            posto_chefe = st.text_input(
                "Posto/Graduação do Chefe *",
                value=fic_atual.get('Posto_Chefe_COP', '') if fic_atual else ''
            )
        with col_a2:
            nome_dacta = st.text_input(
                "Nome do Responsável DACTA *",
                value=fic_atual.get('Nome_Responsavel_DACTA', '') if fic_atual else ''
            )
            posto_dacta = st.text_input(
                "Posto/Graduação DACTA *",
                value=fic_atual.get('Posto_Responsavel_DACTA', '') if fic_atual else ''
            )
    
    submitted = st.form_submit_button("💾 Salvar FIC")
    
    if submitted:
        # Validar campos obrigatórios
        campos_obrigatorios = {
            'Curso': curso,
            'Turma': turma,
            'Local_GT': local_gt,
            'Comando': comando,
            'Posto_Graduacao': posto_grad,
            'Nome_Completo': nome_completo,
            'OM_Indicado': om_indicado,
            'Justificativa_Chefe': justificativa,
            'Nome_Chefe_COP': nome_chefe,
            'Nome_Responsavel_DACTA': nome_dacta
        }
        
        campos_vazios = [k for k, v in campos_obrigatorios.items() if not v or not str(v).strip()]
        
        if campos_vazios:
            resultado = (False, f"Preencha os campos obrigatórios: {', '.join(campos_vazios)}", None)
        else:
            # Preparar dados
            dados_fic = {
                'Curso': curso,
                'Turma': turma,
                'Local_GT': local_gt,
                'Comando': comando,
                'Data_Inicio_Presencial': data_inicio_pres,
                'Data_Termino_Presencial': data_term_pres,
                'PPD_Civil': ppd_civil,
                'Posto_Graduacao': posto_grad,
                'Nome_Completo': nome_completo,
                'OM_Indicado': om_indicado,
                'CPF': cpf,
                'SARAM': saram,
                'Email': email,
                'Telefone': telefone,
                'Funcao_Atual': funcao_atual,
                'Data_Ultima_Promocao': data_ult_promo,
                'Funcao_Apos_Curso': funcao_apos,
                'Tempo_Servico': tempo_servico,
                'Pre_Requisitos': pre_requisitos,
                'Curso_Mapeado': curso_mapeado,
                'Progressao_Carreira': progressao,
                'Comunicado_Indicado': comunicado,
                'Outro_Impedimento': outro_impedimento,
                'Curso_Anterior': curso_anterior,
                'Ano_Curso_Anterior': ano_curso_ant if curso_anterior == "SIM" else "",
                'Ciencia_Dedicacao_EAD': ciencia_ead,
                'Justificativa_Chefe': justificativa,
                'Nome_Chefe_COP': nome_chefe,
                'Posto_Chefe_COP': posto_chefe,
                'Nome_Responsavel_DACTA': nome_dacta,
                'Posto_Responsavel_DACTA': posto_dacta
            }
            
            resultado = (True, "", dados_fic)
    
    return resultado


def render_form_editar_fic(
    fic_atual: Dict[str, Any],
    fic_id: str,
    fic_manager,
    fic_word_filler
) -> Tuple[bool, str, Optional[Dict[str, Any]], bool]:
    """
    Renderiza formulário específico para edição de FIC existente.
    
    Args:
        fic_atual: Dados do FIC atual
        fic_id: ID do FIC
        fic_manager: Instância do FICManager
        fic_word_filler: Instância do FICWordFiller
        
    Returns:
        Tupla (sucesso, mensagem, dados_fic, excluir)
    """
    resultado = (False, "", None, False)
    
    with st.form("form_editar_fic"):
        st.markdown(f"**Editando FIC:** {fic_id}")
        
        # Reutilizar o formulário base
        success, msg, dados_fic = render_form_fic(fic_manager, fic_word_filler, fic_atual)
        
        # Botões
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            submitted = st.form_submit_button("💾 Atualizar FIC")
        with col_btn2:
            if st.form_submit_button("🗑️ Excluir FIC"):
                sucesso, msg_del = fic_manager.excluir_fic(fic_id)
                resultado = (sucesso, msg_del, None, True)
                return resultado
        
        if submitted and success:
            resultado = (True, "FIC atualizado com sucesso!", dados_fic, False)
        elif not success and msg:
            resultado = (False, msg, None, False)
    
    return resultado


# ============================================
# FORMULÁRIO FIC COM AUTOCOMPLETE DE PESSOAS
# ============================================

def render_form_fic_com_autocomplete(
    fic_manager,
    pessoas_manager,
    fic_word_filler,
    fic_atual: Optional[Dict[str, Any]] = None
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Renderiza formulário FIC com autocomplete de pessoas cadastradas.
    
    Esta função permite selecionar uma pessoa do cadastro para preencher
    automaticamente os campos pessoais, mantendo a possibilidade de edição.
    
    Args:
        fic_manager: Instância do FICManager
        pessoas_manager: Instância do PessoasManager
        fic_word_filler: Instância do FICWordFiller
        fic_atual: Dados do FIC atual (para edição)
        
    Returns:
        Tupla (sucesso, mensagem, dados_fic)
    """
    resultado = (False, "", None)
    
    # Inicializar session state para dados da pessoa selecionada
    if 'pessoa_selecionada_fic' not in st.session_state:
        st.session_state.pessoa_selecionada_fic = None
    
    # Seção de busca de pessoa
    st.markdown("### 🔍 Buscar Pessoa Cadastrada")
    st.markdown("Selecione uma pessoa do cadastro para preencher automaticamente os dados:")
    
    # Obter lista de nomes formatados para o selectbox
    nomes_formatados = pessoas_manager.obter_nomes_formatados()
    
    # Adicionar opção vazia no início
    opcoes_nomes = ["-- Digitar manualmente --"] + nomes_formatados
    
    col_busca1, col_busca2 = st.columns([3, 1])
    
    with col_busca1:
        nome_selecionado = st.selectbox(
            "Selecione uma pessoa:",
            options=opcoes_nomes,
            index=0,
            key="select_pessoa_fic"
        )
    
    with col_busca2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Limpar Seleção", key="btn_limpar_pessoa"):
            st.session_state.pessoa_selecionada_fic = None
            st.rerun()
    
    # Buscar dados da pessoa selecionada
    pessoa_dados = None
    if nome_selecionado and nome_selecionado != "-- Digitar manualmente --":
        # Extrair nome (remove posto/graduação se presente)
        if " - " in nome_selecionado:
            nome_puro = nome_selecionado.split(" - ", 1)[1]
        else:
            nome_puro = nome_selecionado
        
        pessoa_dados = pessoas_manager.buscar_pessoa_exata(nome_puro)
        st.session_state.pessoa_selecionada_fic = pessoa_dados
    
    # Mostrar informações da pessoa selecionada
    if pessoa_dados:
        with st.expander("📋 Dados da Pessoa Selecionada", expanded=True):
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.write(f"**Nome:** {pessoa_dados.get('Nome_Completo', '')}")
                st.write(f"**Posto/Grad:** {pessoa_dados.get('Posto_Graduacao', '')}")
                st.write(f"**OM:** {pessoa_dados.get('OM_Indicado', '')}")
            with col_info2:
                st.write(f"**CPF:** {pessoa_dados.get('CPF', '')}")
                st.write(f"**SARAM:** {pessoa_dados.get('SARAM', '')}")
                st.write(f"**Função:** {pessoa_dados.get('Funcao_Atual', '')}")
    
    st.markdown("---")
    st.markdown("### 📝 Formulário FIC")
    
    # Função auxiliar para obter valor - prioriza pessoa selecionada, depois fic_atual
    def get_valor(campo_pessoa: str, campo_fic: str = None) -> str:
        """Obtém valor do campo, priorizando pessoa selecionada."""
        if campo_fic is None:
            campo_fic = campo_pessoa
        
        # Se há pessoa selecionada, usar dados dela
        if pessoa_dados:
            return str(pessoa_dados.get(campo_pessoa, ''))
        
        # Se há FIC atual (edição), usar dados dele
        if fic_atual:
            return fic_atual.get(campo_fic, '')
        
        return ''
    
    # Renderizar formulário
    with st.form("form_fic_autocomplete"):
        valores = {}
        
        # Seção 1: Dados do Curso
        with st.expander("📚 Dados do Curso", expanded=True):
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                curso = st.text_input(
                    "Código do Curso *",
                    value=fic_atual.get('Curso', '') if fic_atual else '',
                    placeholder="Ex: CILE-MOD I"
                )
                turma = st.text_input(
                    "Turma *",
                    value=fic_atual.get('Turma', '') if fic_atual else '',
                    placeholder="Ex: 01/2026"
                )
                local_gt = st.text_input(
                    "Local do Curso GT *",
                    value=fic_atual.get('Local_GT', '') if fic_atual else '',
                    placeholder="Ex: FEAR"
                )
            with col_c2:
                comando = st.text_input(
                    "Comando *",
                    value=fic_atual.get('Comando', '') if fic_atual else '',
                    placeholder="Ex: DECEA"
                )
                data_inicio_pres = st.text_input(
                    "Data Início (Presencial)",
                    value=fic_atual.get('Data_Inicio_Presencial', '') if fic_atual else '',
                    placeholder="DD/MM/AAAA"
                )
                data_term_pres = st.text_input(
                    "Data Término (Presencial)",
                    value=fic_atual.get('Data_Termino_Presencial', '') if fic_atual else '',
                    placeholder="DD/MM/AAAA"
                )
            
            ppd_options = ["", "SIM", "NÃO"]
            ppd_index = ppd_options.index(fic_atual.get('PPD_Civil', '')) if fic_atual and fic_atual.get('PPD_Civil', '') in ppd_options else 0
            ppd_civil = st.selectbox("PPD (para civis)", ppd_options, index=ppd_index)
        
        # Seção 2: Dados Pessoais (com autocomplete)
        with st.expander("👤 Dados Pessoais", expanded=True):
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                posto_grad = st.text_input(
                    "Posto/Graduação *",
                    value=get_valor('Posto_Graduacao'),
                    placeholder="Ex: 1S"
                )
                nome_completo = st.text_input(
                    "Nome Completo *",
                    value=get_valor('Nome_Completo'),
                    placeholder="Nome completo do candidato"
                )
                om_indicado = st.text_input(
                    "OM do Indicado *",
                    value=get_valor('OM_Indicado'),
                    placeholder="Ex: CRCEA-SE"
                )
            with col_p2:
                cpf = st.text_input(
                    "CPF",
                    value=get_valor('CPF'),
                    placeholder="000.000.000-00"
                )
                saram = st.text_input(
                    "SARAM",
                    value=get_valor('SARAM'),
                    placeholder="000000-0"
                )
                email = st.text_input(
                    "E-mail",
                    value=get_valor('Email'),
                    placeholder="email@fab.mil.br"
                )
                telefone = st.text_input(
                    "Telefone",
                    value=get_valor('Telefone'),
                    placeholder="(00) 00000-0000"
                )
        
        # Seção 3: Dados Funcionais (com autocomplete)
        with st.expander("💼 Dados Funcionais", expanded=True):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                funcao_atual = st.text_input(
                    "Função Atual",
                    value=get_valor('Funcao_Atual'),
                    placeholder="Ex: SUPERVISOR DO APP-SP"
                )
                data_ult_promo = st.text_input(
                    "Data Última Promoção",
                    value=get_valor('Data_Ultima_Promocao'),
                    placeholder="DD/MM/AAAA"
                )
            with col_f2:
                funcao_apos = st.text_input(
                    "Função Após Curso",
                    value=fic_atual.get('Funcao_Apos_Curso', '') if fic_atual else '',
                    placeholder="Função após conclusão do curso"
                )
                tempo_servico = st.text_input(
                    "Tempo de Serviço",
                    value=get_valor('Tempo_Servico'),
                    placeholder="Ex: 18 ANOS e 11 MESES"
                )
            
            pre_req_options = ["SIM", "NÃO"]
            pre_req_index = pre_req_options.index(fic_atual.get('Pre_Requisitos', 'SIM')) if fic_atual and fic_atual.get('Pre_Requisitos') in pre_req_options else 0
            pre_requisitos = st.selectbox("Possui Pré-requisitos?", pre_req_options, index=pre_req_index)
        
        # Seção 4: Questionário
        with st.expander("❓ Questionário", expanded=True):
            sim_nao = ["SIM", "NÃO"]
            
            curso_mapeado_index = sim_nao.index(fic_atual.get('Curso_Mapeado', 'SIM')) if fic_atual and fic_atual.get('Curso_Mapeado') in sim_nao else 0
            progressao_index = sim_nao.index(fic_atual.get('Progressao_Carreira', 'SIM')) if fic_atual and fic_atual.get('Progressao_Carreira') in sim_nao else 0
            comunicado_index = sim_nao.index(fic_atual.get('Comunicado_Indicado', 'SIM')) if fic_atual and fic_atual.get('Comunicado_Indicado') in sim_nao else 0
            outro_imp_index = ["NÃO", "SIM"].index(fic_atual.get('Outro_Impedimento', 'NÃO')) if fic_atual and fic_atual.get('Outro_Impedimento') in ["NÃO", "SIM"] else 0
            
            curso_mapeado = st.selectbox("Curso mapeado no posto de trabalho?", sim_nao, index=curso_mapeado_index, key="q1_auto")
            progressao = st.selectbox("Faz parte da progressão individual?", sim_nao, index=progressao_index, key="q2_auto")
            comunicado = st.selectbox("Foi comunicado e confirmou não ter impedimentos?", sim_nao, index=comunicado_index, key="q3_auto")
            outro_impedimento = st.selectbox("Tem outro impedimento?", ["NÃO", "SIM"], index=outro_imp_index, key="q4_auto")
            
            col_q1, col_q2 = st.columns(2)
            with col_q1:
                curso_ant_index = ["NÃO", "SIM"].index(fic_atual.get('Curso_Anterior', 'NÃO')) if fic_atual and fic_atual.get('Curso_Anterior') in ["NÃO", "SIM"] else 0
                curso_anterior = st.selectbox("Já realizou o curso anteriormente?", ["NÃO", "SIM"], index=curso_ant_index, key="q5_auto")
            with col_q2:
                ano_curso_ant_value = fic_atual.get('Ano_Curso_Anterior', '') if fic_atual and curso_anterior == "SIM" else ''
                ano_curso_ant = st.text_input("Em que ano?", value=ano_curso_ant_value, placeholder="AAAA")
            
            ciencia_index = sim_nao.index(fic_atual.get('Ciencia_Dedicacao_EAD', 'SIM')) if fic_atual and fic_atual.get('Ciencia_Dedicacao_EAD') in sim_nao else 0
            ciencia_ead = st.selectbox("Chefe ciente da dedicação exclusiva (EAD)?", sim_nao, index=ciencia_index, key="q6_auto")
        
        # Seção 5: Justificativa e Assinaturas
        with st.expander("📝 Justificativa e Assinaturas", expanded=True):
            justificativa_value = fic_atual.get('Justificativa_Chefe', '') if fic_atual else ''
            justificativa = st.text_area(
                "Justificativa do Chefe Imediato *",
                height=100,
                value=justificativa_value,
                placeholder="Descreva a justificativa para a indicação..."
            )
            
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                nome_chefe = st.text_input(
                    "Nome do Chefe do COP *",
                    value=fic_atual.get('Nome_Chefe_COP', '') if fic_atual else ''
                )
                posto_chefe = st.text_input(
                    "Posto/Graduação do Chefe *",
                    value=fic_atual.get('Posto_Chefe_COP', '') if fic_atual else ''
                )
            with col_a2:
                nome_dacta = st.text_input(
                    "Nome do Responsável DACTA *",
                    value=fic_atual.get('Nome_Responsavel_DACTA', '') if fic_atual else ''
                )
                posto_dacta = st.text_input(
                    "Posto/Graduação DACTA *",
                    value=fic_atual.get('Posto_Responsavel_DACTA', '') if fic_atual else ''
                )
        
        submitted = st.form_submit_button("💾 Salvar FIC")
        
        if submitted:
            # Validar campos obrigatórios
            campos_obrigatorios = {
                'Curso': curso,
                'Turma': turma,
                'Local_GT': local_gt,
                'Comando': comando,
                'Posto_Graduacao': posto_grad,
                'Nome_Completo': nome_completo,
                'OM_Indicado': om_indicado,
                'Justificativa_Chefe': justificativa,
                'Nome_Chefe_COP': nome_chefe,
                'Nome_Responsavel_DACTA': nome_dacta
            }
            
            campos_vazios = [k for k, v in campos_obrigatorios.items() if not v or not str(v).strip()]
            
            if campos_vazios:
                resultado = (False, f"Preencha os campos obrigatórios: {', '.join(campos_vazios)}", None)
            else:
                # Preparar dados
                dados_fic = {
                    'Curso': curso,
                    'Turma': turma,
                    'Local_GT': local_gt,
                    'Comando': comando,
                    'Data_Inicio_Presencial': data_inicio_pres,
                    'Data_Termino_Presencial': data_term_pres,
                    'PPD_Civil': ppd_civil,
                    'Posto_Graduacao': posto_grad,
                    'Nome_Completo': nome_completo,
                    'OM_Indicado': om_indicado,
                    'CPF': cpf,
                    'SARAM': saram,
                    'Email': email,
                    'Telefone': telefone,
                    'Funcao_Atual': funcao_atual,
                    'Data_Ultima_Promocao': data_ult_promo,
                    'Funcao_Apos_Curso': funcao_apos,
                    'Tempo_Servico': tempo_servico,
                    'Pre_Requisitos': pre_requisitos,
                    'Curso_Mapeado': curso_mapeado,
                    'Progressao_Carreira': progressao,
                    'Comunicado_Indicado': comunicado,
                    'Outro_Impedimento': outro_impedimento,
                    'Curso_Anterior': curso_anterior,
                    'Ano_Curso_Anterior': ano_curso_ant if curso_anterior == "SIM" else "",
                    'Ciencia_Dedicacao_EAD': ciencia_ead,
                    'Justificativa_Chefe': justificativa,
                    'Nome_Chefe_COP': nome_chefe,
                    'Posto_Chefe_COP': posto_chefe,
                    'Nome_Responsavel_DACTA': nome_dacta,
                    'Posto_Responsavel_DACTA': posto_dacta
                }
                
                resultado = (True, "", dados_fic)
    
    return resultado
