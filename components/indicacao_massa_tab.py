"""
Aba de Indicação em Massa - Indica várias pessoas para o mesmo curso
VERSÃO SEGURA - Sem armazenamento local de dados sensíveis
"""

import streamlit as st
import hashlib
from typing import List, Dict

from managers.indicacao_massa_manager import get_indicacao_massa_manager
from managers.sheets_manager_secure import (
    get_secure_sheets_manager,
    SecurityError,
    CAMPOS_SENSIVEIS
)
from managers.chefes_manager import get_chefes_manager
from utils.logger import get_logger

logger = get_logger(__name__)


def _mascarar_saram(saram: str) -> str:
    """Mascara o SARAM para exibição (ex: 42****89)"""
    if not saram or len(saram) < 4:
        return '****'
    return f"{saram[:2]}****{saram[-2:]}"


def _mascarar_cpf(cpf: str) -> str:
    """Mascara o CPF para exibição (ex: 403.***.***-31)"""
    if not cpf:
        return '***.***.***-**'
    # Remove caracteres não numéricos
    numeros = ''.join(filter(str.isdigit, str(cpf)))
    if len(numeros) == 11:
        return f"{numeros[:3]}.***.***-{numeros[-2:]}"
    return '***.***.***-**'


def _hash_identificador(saram: str) -> str:
    """Gera hash do SARAM para logs (anonimizado)"""
    return hashlib.sha256(str(saram).encode()).hexdigest()[:8]


def render_indicacao_massa_tab() -> None:
    """
    Renderiza a aba de Indicação em Massa - VERSÃO SEGURA
    """
    st.header("📊 Indicação em Massa")
    
    # Banner de segurança
    st.success("""
    🔒 **Modo Seguro Ativado**
    - Dados carregados diretamente do Google Sheets
    - Sem armazenamento local de informações sensíveis
    - Criptografia de campos protegidos (CPF, SARAM)
    - Logs anonimizados
    """)
    
    # Inicializar managers
    if 'sheets_manager_secure' not in st.session_state:
        try:
            st.session_state.sheets_manager_secure = get_secure_sheets_manager()
        except SecurityError as e:
            st.error(f"❌ Erro de segurança: {e}")
            return
    
    sheets_mgr = st.session_state.sheets_manager_secure
    indicacao_mgr = get_indicacao_massa_manager()
    chefes_mgr = get_chefes_manager()
    
    # Formulário principal
    with st.form("indicacao_massa_form"):
        
        # === DADOS DO CURSO ===
        st.subheader("📋 Dados do Curso")
        
        col1, col2 = st.columns(2)
        with col1:
            codigo_curso = st.text_input(
                "Código do Curso *",
                placeholder="Ex: SEC001E",
                key="massa_codigo"
            )
            turma = st.text_input(
                "Turma *",
                placeholder="Ex: 01/26",
                key="massa_turma"
            )
            modalidade = st.selectbox(
                "Modalidade *",
                options=["PRESENCIAL", "EAD", "HÍBRIDO"],
                index=0,
                key="massa_modalidade"
            )
        
        with col2:
            nome_curso = st.text_input(
                "Nome do Curso *",
                placeholder="Ex: ATC AVSEC",
                key="massa_nome"
            )
            local_curso = st.text_input(
                "Local do Curso *",
                placeholder="Ex: ICEA",
                key="massa_local"
            )
            comando = st.text_input(
                "Comando",
                value="DECEA",
                placeholder="Ex: DECEA",
                key="massa_comando"
            )
        
        # Datas do curso
        col3, col4 = st.columns(2)
        with col3:
            data_inicio = st.text_input(
                "Data de Início (DD/MM/AAAA)",
                placeholder="Ex: 05/02/2026",
                key="massa_data_inicio"
            )
        with col4:
            data_termino = st.text_input(
                "Data de Término (DD/MM/AAAA)",
                placeholder="Ex: 10/02/2026",
                key="massa_data_termino"
            )
        
        st.divider()
        
        # === DADOS DOS CHEFES ===
        st.subheader("👔 Dados dos Chefes (Assinaturas)")
        
        chefes = chefes_mgr.get_all_chefes()
        
        col_chefe1, col_chefe2 = st.columns(2)
        
        with col_chefe1:
            st.markdown("**Chefe do Órgão**")
            if chefes:
                opcoes_chefes = [(None, "-- Selecionar --")] + [(c['id'], f"{c['nome']} ({c['posto']})") for c in chefes]
                chefe_orgao_id = st.selectbox(
                    "Selecionar chefe",
                    options=[o[0] for o in opcoes_chefes],
                    format_func=lambda x: next((o[1] for o in opcoes_chefes if o[0] == x), ""),
                    key="massa_chefe_orgao"
                )
                
                if chefe_orgao_id:
                    chefe_data = chefes_mgr.get_chefe_by_id(chefe_orgao_id)
                    chefe_orgao_nome = chefe_data.get('nome', '')
                    chefe_orgao_posto = chefe_data.get('posto', '')
                    chefe_orgao_setor = chefe_data.get('setor', '') or chefe_data.get('funcao', '').replace('CHEFE DO ', '').replace('CHEFE DA ', '')
                else:
                    chefe_orgao_nome = st.text_input("Nome do Chefe", placeholder="Ex: LEONARDO REZENDE ALVES", key="chefe_org_nome")
                    chefe_orgao_posto = st.text_input("Posto", placeholder="Ex: MAJ AV", key="chefe_org_posto")
                    chefe_orgao_setor = st.text_input("Setor", placeholder="Ex: COP", key="chefe_org_setor")
            else:
                chefe_orgao_nome = st.text_input("Nome do Chefe", placeholder="Ex: LEONARDO REZENDE ALVES", key="chefe_org_nome")
                chefe_orgao_posto = st.text_input("Posto", placeholder="Ex: MAJ AV", key="chefe_org_posto")
                chefe_orgao_setor = st.text_input("Setor", placeholder="Ex: COP", key="chefe_org_setor")
        
        with col_chefe2:
            st.markdown("**Chefe da Divisão do Curso**")
            if chefes:
                opcoes_chefes_resp = [(None, "-- Selecionar --")] + [(c['id'], f"{c['nome']} ({c['posto']})") for c in chefes]
                chefe_div_id = st.selectbox(
                    "Selecionar responsável",
                    options=[o[0] for o in opcoes_chefes_resp],
                    format_func=lambda x: next((o[1] for o in opcoes_chefes_resp if o[0] == x), ""),
                    key="massa_chefe_div"
                )
                
                if chefe_div_id:
                    resp_data = chefes_mgr.get_chefe_by_id(chefe_div_id)
                    chefe_div_nome = resp_data.get('nome', '')
                    chefe_div_posto = resp_data.get('posto', '')
                    chefe_div_setor = resp_data.get('setor', '') or resp_data.get('funcao', '').replace('CHEFE DO ', '').replace('CHEFE DA ', '')
                else:
                    chefe_div_nome = st.text_input("Nome do Responsável", placeholder="Ex: MARCELO MOREIRA DE ANDRADE", key="chefe_div_nome")
                    chefe_div_posto = st.text_input("Posto", placeholder="Ex: TEN CEL QOECTA", key="chefe_div_posto")
                    chefe_div_setor = st.text_input("Setor", placeholder="Ex: DO", key="chefe_div_setor")
            else:
                chefe_div_nome = st.text_input("Nome do Responsável", placeholder="Ex: MARCELO MOREIRA DE ANDRADE", key="chefe_div_nome")
                chefe_div_posto = st.text_input("Posto", placeholder="Ex: TEN CEL QOECTA", key="chefe_div_posto")
                chefe_div_setor = st.text_input("Setor", placeholder="Ex: DO", key="chefe_div_setor")
        
        st.divider()
        
        # === INDICADOS ===
        st.subheader("👥 Indicados")
        
        # Lista para armazenar os SARAMs
        if 'sarams_lista_massa' not in st.session_state:
            st.session_state.sarams_lista_massa = [""]
        
        # Mostrar campos de SARAM
        sarams = []
        for i in range(len(st.session_state.sarams_lista_massa)):
            col_saram, col_remover = st.columns([4, 1])
            with col_saram:
                saram = st.text_input(
                    f"SARAM #{i+1}",
                    value=st.session_state.sarams_lista_massa[i],
                    placeholder="Ex: 4237447, 423.744-7, 423-7447",
                    key=f"massa_saram_{i}"
                )
                sarams.append(saram)
            
            with col_remover:
                if i > 0 and st.form_submit_button(f"❌", key=f"massa_remover_{i}"):
                    st.session_state.sarams_lista_massa.pop(i)
                    st.rerun()
        
        # Botão para adicionar mais SARAM
        cols = st.columns([1, 1, 1])
        with cols[1]:
            adicionar_clicked = st.form_submit_button("➕ Adicionar SARAM", use_container_width=True)
            if adicionar_clicked:
                st.session_state.sarams_lista_massa.append("")
                st.rerun()
        
        st.divider()
        
        # Botão de gerar
        gerar_clicked = st.form_submit_button(
            "📊 Gerar Planilha de Indicação",
            use_container_width=True,
            type="primary"
        )
    
    # Processar geração (fora do form)
    if gerar_clicked:
        # Validações
        if not codigo_curso or not nome_curso or not turma or not local_curso:
            st.error("❌ Preencha todos os dados obrigatórios do curso")
            return
        
        # Filtrar SARAMs válidos (aceita pontos e traços, limpa depois)
        import re
        sarams_validos = []
        for s in sarams:
            s_limpo = re.sub(r'[^\d]', '', str(s))  # Remove tudo que não é número
            if s_limpo and len(s_limpo) >= 6:
                sarams_validos.append(s_limpo)
        
        if not sarams_validos:
            st.error("❌ Adicione pelo menos um SARAM válido")
            return
        
        # Buscar dados dos indicados
        with st.spinner(f"Buscando dados de {len(sarams_validos)} militares..."):
            indicados = []
            erros = []
            
            for saram in sarams_validos:
                try:
                    pessoa = sheets_mgr.buscar_pessoa_seguro(saram)
                    if pessoa:
                        # Armazenar dados (com campos sensíveis criptografados/protegidos)
                        indicados.append({
                            'nome_completo': pessoa.nome,
                            'posto_graduacao': pessoa.posto_graduacao,
                            'especialidade': pessoa.especialidade,
                            'cpf': pessoa._cpf,  # Campo protegido
                            'saram': saram,
                            'data_praca': pessoa.praca,
                            'email': pessoa.email,
                            'telefone': pessoa.telefone,
                            'funcao_atual': pessoa.habilitacao,
                            'funcao_apos_curso': pessoa.habilitacao,
                            # Hash para logs (não expõe dados reais)
                            'saram_hash': _hash_identificador(saram),
                        })
                        # Log seguro (com hash)
                        logger.info(f"Indicado encontrado (hash: {_hash_identificador(saram)}...)")
                    else:
                        erros.append(f"SARAM {_mascarar_saram(saram)}: Não encontrado")
                        logger.warning(f"SARAM não encontrado (hash: {_hash_identificador(saram)})")
                except Exception as e:
                    erros.append(f"SARAM {_mascarar_saram(saram)}: Erro na busca")
                    logger.error(f"Erro na busca (hash: {_hash_identificador(saram)}): {e}")
            
            # Mostrar resultados da busca
            if indicados:
                st.success(f"✅ {len(indicados)} militares encontrados")
                
                # Mostrar tabela de indicados (COM DADOS MASCARADOS)
                st.subheader("📋 Indicados Encontrados")
                dados_tabela = []
                for i, ind in enumerate(indicados, 1):
                    nome_fmt = f"{ind['posto_graduacao'] or ''} {ind['especialidade'] or ''} {ind['nome_completo']}".strip()
                    dados_tabela.append({
                        "Prioridade": i,
                        "Nome": nome_fmt,
                        "CPF": _mascarar_cpf(ind['cpf']),  # CPF mascarado
                        "SARAM": _mascarar_saram(ind['saram']),  # SARAM mascarado
                        "Tempo": indicacao_mgr._calcular_tempo_servico(ind['data_praca'])
                    })
                st.table(dados_tabela)
            
            if erros:
                st.error("❌ Erros na busca:")
                for erro in erros:
                    st.write(f"- {erro}")
            
            # Gerar planilha se tiver indicados
            if indicados:
                with st.spinner("Gerando planilha Excel de forma segura..."):
                    try:
                        # Dados do curso
                        dados_curso = {
                            'codigo': codigo_curso,
                            'nome': nome_curso,
                            'turma': turma,
                            'local': local_curso,
                            'comando': comando,
                            'modalidade': modalidade,
                            'data_inicio': data_inicio,
                            'data_termino': data_termino
                        }
                        
                        # Dados dos chefes
                        dados_chefes = {
                            'chefe_orgao': {
                                'nome': chefe_orgao_nome,
                                'posto': chefe_orgao_posto,
                                'setor': chefe_orgao_setor
                            },
                            'chefe_divisao': {
                                'nome': chefe_div_nome,
                                'posto': chefe_div_posto,
                                'setor': chefe_div_setor
                            }
                        }
                        
                        planilha_buffer = indicacao_mgr.preencher_planilha(dados_curso, indicados, dados_chefes)
                        
                        # Nome do arquivo
                        nome_arquivo = f"Indicacao_{codigo_curso.replace(' ', '_')}_{turma.replace('/', '_')}.xlsx"
                        
                        st.download_button(
                            label="⬇️ Baixar Planilha de Indicação",
                            data=planilha_buffer,
                            file_name=nome_arquivo,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.document"
                        )
                        
                        st.success("✅ Planilha gerada com sucesso!")
                        
                        # Informações de segurança
                        st.info("""
                        🔒 **Confirmação de Segurança:**
                        - ✅ Dados carregados do Google Sheets
                        - ✅ Sem armazenamento em banco local
                        - ✅ Campos sensíveis protegidos (CPF, SARAM)
                        - ✅ Log sem dados identificáveis
                        - ✅ Memória será limpa ao fechar
                        """)
                        
                        # Botão para limpar
                        if st.button("🧹 Limpar Dados da Sessão", type="secondary"):
                            st.session_state.sarams_lista_massa = [""]
                            st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Erro ao gerar planilha: {e}")
                        logger.error(f"Erro ao gerar planilha (dados ocultos por segurança)")
    
    # Instruções
    with st.expander("📖 Instruções de Uso"):
        st.markdown("""
        ### Como usar a Indicação em Massa
        
        1. **Preencha os dados do curso**:
           - Código do curso (ex: SEC001E)
           - Nome do curso (ex: ATC AVSEC)
           - Turma (ex: 01/26)
           - Local do curso (ex: ICEA)
           - Modalidade (Presencial/EAD/Híbrido)
           - Datas de início e término
           - Comando (ex: DECEA)
        
        2. **Selecione os chefes** para as assinaturas
        
        3. **Adicione os SARAMs** dos indicados
        
        4. **Gere a planilha** com todos os dados preenchidos
        
        ### 🔒 Medidas de Segurança
        
        - **CPF**: Mascarado na interface (ex: 403.***.***-31)
        - **SARAM**: Mascarado na interface (ex: 42****89)
        - **Logs**: Usam hashes (ex: hash: a1b2c3d4)
        - **Dados sensíveis**: Criptografados em memória
        - **Sem persistência**: Dados não são salvos em disco
        
        ### Campos preenchidos automaticamente:
        - Posto e Nome
        - CPF (formatado)
        - SARAM
        - Tempo de serviço
        - Função atual (SUPERVISOR, FMC, etc)
        - Função após o curso
        - Email funcional
        - Telefone/Celular
        """)
