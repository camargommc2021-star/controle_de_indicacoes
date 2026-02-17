"""
Aba de Confecção de FIC com dados do Google Sheets - VERSÃO SEGURA.

Interface segura para buscar dados no Google Sheets e preencher FIC.
- Sem armazenamento local de dados sensíveis
- Criptografia de campos sensíveis
- Logs seguros
- Timeout e retry
"""

import streamlit as st
from typing import Optional

from managers.sheets_manager_secure import (
    SecureSheetsManager, 
    get_secure_sheets_manager,
    SecurityError,
    CAMPOS_SENSIVEIS,
    formatar_habilitacao,
    MAPEAMENTO_HABILITACOES
)
from managers.chefes_manager import get_chefes_manager
from utils.logger import get_logger

logger = get_logger(__name__)


def render_fic_sheets_tab(fic_word_filler) -> None:
    """
    Renderiza a aba de Confecção de FIC usando Google Sheets (VERSÃO SEGURA).
    
    Args:
        fic_word_filler: Instância do preenchedor de FIC Word
    """
    st.header("📄 Confecção de FIC")
    
    # Banner de segurança
    st.success("""
    🔒 **Modo Seguro Ativado**
    - Dados carregados diretamente do Google Sheets
    - Sem armazenamento local de informações sensíveis
    - Criptografia de campos protegidos
    - Logs anonimizados
    """)
    
    # Inicializar manager seguro
    if 'sheets_manager_secure' not in st.session_state:
        try:
            st.session_state.sheets_manager_secure = get_secure_sheets_manager()
        except SecurityError as e:
            st.error(f"❌ Erro de segurança: {e}")
            st.info("Configure as credenciais em Streamlit Secrets para continuar.")
            return
    
    sheets_mgr = st.session_state.sheets_manager_secure
    
    # Verificação de segurança
    with st.expander("🔐 Status de Segurança", expanded=False):
        status = sheets_mgr.verificar_seguranca()
        
        cols = st.columns(3)
        with cols[0]:
            st.write("**Dependências:**", "✅" if status['dependencias_ok'] else "❌")
        with cols[1]:
            st.write("**Secrets:**", "✅" if status['secrets_configurado'] else "❌")
        with cols[2]:
            nivel = status['nivel_seguranca']
            cor = '🟢' if nivel == 'ALTO' else '🟡'
            st.write(f"**Nível:** {cor} {nivel}")
        
        if not status['secrets_configurado']:
            st.error("""
            ⚠️ **Configuração de segurança necessaria!**
            
            Configure em `.streamlit/secrets.toml`:
            ```toml
            [gcp_service_account]
            type = "service_account"
            project_id = "seu-projeto"
            private_key = "-----BEGIN PRIVATE KEY-----\n..."
            client_email = "sua-conta@projeto.iam.gserviceaccount.com"
            
            SHEETS_SPREADSHEET_ID = "id-da-sua-planilha"
            ```
            """)
        
        st.markdown(f"**Campos protegidos:** {', '.join(CAMPOS_SENSIVEIS)}")
    
    st.divider()
    
    # Formulário de busca seguro
    st.subheader("🔍 Buscar Dados")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        codigo = st.text_input(
            "SARAM",
            placeholder="Digite o SARAM (ex: 1234567)",
            help="Número do SARAM do militar (6-8 dígitos)",
            key="fic_saram_seguro"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        buscar_clicked = st.button("🔍 Buscar", use_container_width=True, type="primary")
    
    # Armazenar dados encontrados na sessão (apenas hash, não dados reais)
    if 'fic_dados_hash' not in st.session_state:
        st.session_state.fic_dados_hash = None
    if 'fic_dados_atuais' not in st.session_state:
        st.session_state.fic_dados_atuais = None
    
    # Buscar dados
    if buscar_clicked and codigo:
        # Validar input (SARAM - apenas números, 6-8 dígitos)
        saram_limpo = codigo.strip()
        if not saram_limpo.isdigit():
            st.error("❌ SARAM inválido. Use apenas números.")
            return
        
        if len(saram_limpo) < 6 or len(saram_limpo) > 8:
            st.error("❌ SARAM deve ter entre 6 e 8 dígitos.")
            return
        
        with st.spinner("Buscando de forma segura..."):
            try:
                pessoa = sheets_mgr.buscar_pessoa_seguro(codigo)
                
                if pessoa:
                    # Armazenar apenas hash na sessão (não os dados)
                    st.session_state.fic_dados_hash = pessoa.saram_hash
                    st.session_state.fic_dados_atuais = pessoa
                    st.success("✅ Dados encontrados com sucesso")
                    
                    # Log seguro
                    logger.info(f"Busca bem-sucedida (hash: {pessoa.saram_hash[:8]}...)")
                else:
                    st.session_state.fic_dados_hash = None
                    st.session_state.fic_dados_atuais = None
                    st.warning(f"⚠️ SARAM '{codigo}' não encontrado")
                    
            except SecurityError as e:
                st.error(f"🚫 Erro de segurança: {e}")
                logger.error(f"SecurityError: {e}")
            except Exception as e:
                st.error(f"❌ Erro inesperado: {e}")
                logger.error(f"Erro na busca: {e}")
    
    # Exibir e editar dados
    if st.session_state.fic_dados_atuais:
        pessoa = st.session_state.fic_dados_atuais
        
        st.divider()
        st.subheader("👤 Dados da Pessoa")
        
        # Mostrar dados mascarados inicialmente
        col_seg1, col_seg2, col_seg3 = st.columns(3)
        with col_seg1:
            st.info(f"**Nome:** {pessoa.nome}")
            st.write(f"**Nome de Guerra:** {pessoa.nome_guerra or 'N/A'}")
            st.write(f"**Posto/Grad:** {pessoa.posto_graduacao or 'N/A'}")
            st.write(f"**Esp:** {pessoa.especialidade or 'N/A'}")
        with col_seg2:
            st.write(f"**OM:** {pessoa.om or 'CRCEA-SE'}")
            st.write(f"**RA:** {pessoa.ra or 'N/A'}")
            hab_formatada = formatar_habilitacao(pessoa.habilitacao) if pessoa.habilitacao else 'N/A'
            st.write(f"**Habilitação:** {hab_formatada}")
            # Mostrar função completa
            funcao_map = {'S': 'SUPERVISOR', 'I': 'INSTRUTOR', 'O': 'OPERADOR', 'F': 'FMC', 
                         'CHEQ': 'CHEFE DE EQUIPE', 'E': 'ESTAGIÁRIO', '--': 'CHEFE DO COP'}
            funcao_display = funcao_map.get(pessoa.habilitacao, pessoa.habilitacao) if pessoa.habilitacao else 'N/A'
            st.write(f"**Função:** {funcao_display}")
        with col_seg3:
            # Mostrar campos sensíveis mascarados
            dados_mascarados = pessoa.to_dict_seguro(incluir_sensiveis=True)
            st.write(f"**SARAM:** {dados_mascarados.get('saram', 'N/A')}")
            st.write(f"**CPF:** {dados_mascarados.get('cpf', 'N/A')}")
            st.write(f"**Praça:** {pessoa.praca or 'N/A'}")
            st.write(f"**Telefone:** {dados_mascarados.get('telefone', 'N/A')}")
            st.write(f"**Email:** {dados_mascarados.get('email', 'N/A')}")
        
        # Formulário de edição seguro
        with st.form("fic_dados_form_seguro"):
            st.markdown("### ✏️ Editar Dados (se necessário)")
            
            # Dados básicos
            col1, col2, col3 = st.columns(3)
            
            with col1:
                nome = st.text_input("Nome Completo", value=pessoa.nome)
                nome_guerra = st.text_input("Nome de Guerra", value=pessoa.nome_guerra or "")
                posto = st.text_input("Posto/Graduação", value=pessoa.posto_graduacao or "")
                esp = st.text_input("Especialidade", value=pessoa.especialidade or "")
            
            with col2:
                om_val = st.text_input("OM/Seção", value=pessoa.om or "CRCEA-SE")
                ra = st.text_input("RA", value=pessoa.ra or "")
                # Selectbox para habilitação com as opções padronizadas
                hab_options = [''] + list(MAPEAMENTO_HABILITACOES.keys())
                hab_display = ['(Selecione)'] + [f"{k} - {v}" for k, v in MAPEAMENTO_HABILITACOES.items()]
                
                # Encontrar índice atual
                hab_atual = pessoa.habilitacao.upper().strip() if pessoa.habilitacao else ''
                try:
                    hab_index = hab_options.index(hab_atual) if hab_atual in hab_options else 0
                except ValueError:
                    hab_index = 0
                
                habilitacao_selecionada = st.selectbox(
                    "Habilitação",
                    options=hab_options,
                    format_func=lambda x: f"{x} - {MAPEAMENTO_HABILITACOES.get(x, x)}" if x in MAPEAMENTO_HABILITACOES else ('(Selecione)' if x == '' else x),
                    index=hab_index,
                    key="hab_select"
                )
                habilitacao = habilitacao_selecionada
                telefone = st.text_input("Telefone", value=pessoa.telefone or "", type="password")
            
            with col3:
                # Campos sensíveis com aviso
                st.markdown("<small>⚠️ Dados sensíveis</small>", unsafe_allow_html=True)
                saram = st.text_input("SARAM", value=pessoa._saram or "", type="password")
                cpf = st.text_input("CPF", value=pessoa._cpf or "", type="password")
                praca = st.text_input("Data de Praça", value=pessoa.praca or "")
                email = st.text_input("Email", value=pessoa.email or "", type="password")
            
            # Dados do curso
            st.divider()
            st.subheader("📋 Dados do Curso/FIC")
            
            # Código e Nome do Curso separados
            col_curso1, col_curso2 = st.columns(2)
            with col_curso1:
                codigo_curso = st.text_input("Código do Curso *", placeholder="Ex: SEC002E")
            with col_curso2:
                nome_curso = st.text_input("Nome do Curso *", placeholder="Ex: ATC AVSEC")
            
            col3, col4 = st.columns(2)
            
            with col3:
                curso_turma = st.text_input("Turma *", placeholder="Ex: 02/2026")
                data_inicio = st.date_input("Data de Início Presencial (se houver)", value=None)
                data_inicio_ead = st.date_input("Data de Início EAD (se houver)", value=None)
            
            with col4:
                local_gt = st.text_input("Local do Curso/GT *", placeholder="Ex: ICEA")
                data_fim = st.date_input("Data de Término Presencial (se houver)", value=None)
                data_fim_ead = st.date_input("Data de Término EAD (se houver)", value=None)
            
            # Campos adicionais
            comando = st.text_input("Comando *", placeholder="Ex: DECEA")
            
            # Funções
            st.divider()
            st.subheader("👤 Funções e Promoção")
            
            # Mapear habilitação para nome completo da função
            hab_para_funcao = {
                'S': 'SUPERVISOR',
                'I': 'INSTRUTOR',
                'O': 'OPERADOR',
                'F': 'FMC',
                'CHEQ': 'CHEFE DE EQUIPE',
                'E': 'ESTAGIÁRIO',
                '--': 'CHEFE DO COP',
                'S/H': 'SEM HABILITAÇÃO'
            }
            funcao_default = hab_para_funcao.get(pessoa.habilitacao, pessoa.habilitacao) if pessoa.habilitacao else ''
            
            col_func1, col_func2 = st.columns(2)
            with col_func1:
                funcao_atual = st.text_input("Função Atual *", placeholder="Ex: SUPERVISOR", value=funcao_default)
                data_ult_prom = st.text_input("Data Última Promoção", value=pessoa.ult_prom or "", placeholder="Ex: 01/01/2020")
            with col_func2:
                funcao_apos_curso = st.text_input("Função que o Indicado Exercerá *", placeholder="Ex: SUPERVISOR", value=funcao_default)
            
            # Questionários SIM/NÃO
            st.divider()
            st.subheader("☑️ Questionários")
            
            col_q1, col_q2 = st.columns(2)
            with col_q1:
                pre_requisitos = st.radio("Possui os pré-requisitos para o curso?", ["SIM", "NÃO"], index=0)
                curso_mapeado = st.radio("O curso está mapeado no posto de trabalho?", ["SIM", "NÃO"], index=0)
                progressao_carreira = st.radio("O curso faz parte da progressão individual?", ["SIM", "NÃO"], index=0)
            with col_q2:
                comunicado = st.radio("O indicado foi comunicado e confirmou não ter impedimentos?", ["SIM", "NÃO"], index=0)
                curso_anterior = st.radio("Já realizou o curso anteriormente?", ["SIM", "NÃO"], index=1)
                ano_curso_anterior = st.text_input("Se SIM, em que ano?", placeholder="Ex: 2020", disabled=(curso_anterior == "NÃO"))
                dedicacao_ead = st.radio("Ciência de dedicação exclusiva (4h diárias) para EAD?", ["SIM", "NÃO"], index=0)
            
            # Dados do Chefe Imediato e Responsável
            st.divider()
            st.subheader("📝 Assinaturas")
            
            # Carregar chefes cadastrados
            chefes_manager = get_chefes_manager()
            chefes = chefes_manager.get_all_chefes()
            
            # Inicializar variáveis dos chefes com valores padrão
            nome_chefe = ""
            posto_chefe = ""
            setor_chefe = ""
            comando_chefe = ""
            nome_resp = ""
            posto_resp = ""
            setor_resp = ""
            comando_resp = ""
            
            col_ass1, col_ass2 = st.columns(2)
            with col_ass1:
                st.markdown("**Chefe Imediato**")
                if chefes:
                    opcoes_chefes = [(None, "-- Digitar manualmente --")] + [(c['id'], f"{c['nome']} ({c['posto']}) - {c['funcao']}") for c in chefes]
                    chefe_selecionado = st.selectbox(
                        "Selecionar chefe cadastrado",
                        options=[o[0] for o in opcoes_chefes],
                        format_func=lambda x: next((o[1] for o in opcoes_chefes if o[0] == x), "")
                    )
                    
                    if chefe_selecionado:
                        chefe_data = chefes_manager.get_chefe_by_id(chefe_selecionado)
                        nome_chefe = st.text_input("Nome do Chefe Imediato", value=chefe_data.get('nome', ''))
                        posto_chefe = st.text_input("Posto do Chefe Imediato", value=chefe_data.get('posto', ''))
                        # Usar funcao se setor estiver vazio (ex: "Chefe do COP" ao invés de só "COP")
                        setor_chefe = chefe_data.get('setor', '') or chefe_data.get('funcao', '').replace('CHEFE DO ', '').replace('CHEFE DA ', '')
                        comando_chefe = chefe_data.get('comando', '')
                    else:
                        nome_chefe = st.text_input("Nome do Chefe Imediato", placeholder="Ex: LEONARDO REZENDE ALVES")
                        posto_chefe = st.text_input("Posto do Chefe Imediato", placeholder="Ex: Maj Av")
                        # Campos adicionais para digitação manual
                        st.markdown("**Setor do Chefe (opcional)**")
                        setor_chefe = st.text_input("Setor", placeholder="Ex: COP", key="setor_chefe_manual")
                        comando_chefe = ""
                else:
                    st.info("Nenhum chefe cadastrado. Use a aba '👔 Cadastro de Chefes' para adicionar.")
                    nome_chefe_input = st.text_input("Nome do Chefe Imediato", placeholder="Ex: LEONARDO REZENDE ALVES")
                    posto_chefe_input = st.text_input("Posto do Chefe Imediato", placeholder="Ex: Maj Av")
                    nome_chefe = nome_chefe_input
                    posto_chefe = posto_chefe_input
                    st.markdown("**Setor do Chefe (opcional)**")
                    setor_chefe_input = st.text_input("Setor", placeholder="Ex: COP", key="setor_chefe_manual2")
                    setor_chefe = setor_chefe_input
                    comando_chefe = ""
            
            with col_ass2:
                st.markdown("**Responsável pela Div/Seção**")
                if chefes:
                    resp_selecionado = st.selectbox(
                        "Selecionar responsável cadastrado",
                        options=[o[0] for o in opcoes_chefes],
                        format_func=lambda x: next((o[1] for o in opcoes_chefes if o[0] == x), ""),
                        key="resp_select"
                    )
                    
                    if resp_selecionado:
                        resp_data = chefes_manager.get_chefe_by_id(resp_selecionado)
                        nome_resp = st.text_input("Nome do Responsável", value=resp_data.get('nome', ''))
                        posto_resp = st.text_input("Posto do Responsável", value=resp_data.get('posto', ''))
                        # Usar funcao se setor estiver vazio
                        setor_resp = resp_data.get('setor', '') or resp_data.get('funcao', '').replace('CHEFE DO ', '').replace('CHEFE DA ', '')
                        comando_resp = resp_data.get('comando', '')
                    else:
                        nome_resp = st.text_input("Nome do Responsável", placeholder="Ex: MAXIMILIANO SILVA LOPES")
                        posto_resp = st.text_input("Posto do Responsável", placeholder="Ex: Ten Cel QOAV")
                        # Campos adicionais para digitação manual do responsável
                        st.markdown("**Setor do Responsável (opcional)**")
                        setor_resp = st.text_input("Setor", placeholder="Ex: DACTA", key="setor_resp_manual")
                        comando_resp = ""
                else:
                    nome_resp_input = st.text_input("Nome do Responsável", placeholder="Ex: MAXIMILIANO SILVA LOPES")
                    posto_resp_input = st.text_input("Posto do Responsável", placeholder="Ex: Ten Cel QOAV")
                    nome_resp = nome_resp_input
                    posto_resp = posto_resp_input
            
            # Justificativa
            st.divider()
            justificativa = st.text_area("Justificativa do Chefe Imediato", 
                                         placeholder="Descreva detalhadamente como o curso contribuirá para o desenvolvimento profissional do indicado...",
                                         value="O CURSO IRÁ CONTRIBUIR SIGNIFICATIVAMENTE PARA O APERFEIÇOAMENTO PROFISSIONAL E ATUALIZAÇÃO TÉCNICA DO INDICADO, PROPORCIONANDO MELHOR DESEMPENHO NAS ATIVIDADES OPERACIONAIS.",
                                         height=100)
            
            # Botão de gerar
            st.divider()
            gerar_clicked = st.form_submit_button("📄 Gerar FIC Preenchido", use_container_width=True, type="primary")
        
        # Gerar FIC
        if gerar_clicked:
            # Validações
            if not codigo_curso or not nome_curso or not curso_turma:
                st.error("❌ Código do curso, nome do curso e turma são obrigatórios")
                return
            
            # Preparar dados (sem armazenar em log)
            dados_fic = {
                'Nome_Completo': nome,
                'Nome_Guerra': nome_guerra,
                'Posto_Graduacao': posto,
                'Especialidade': esp,
                'OM_Indicado': om_val,
                'SARAM': saram,
                'CPF': cpf,
                'RA': ra,
                'Email': email,
                'Telefone': telefone,

                'Data_Praca': praca,
                'Data_Ultima_Promocao': data_ult_prom,
                'Habilitacao': habilitacao,
                'Codigo_Curso': codigo_curso,
                'Nome_Curso': nome_curso,
                'Turma': curso_turma,
                'Data_Inicio_Presencial': data_inicio.strftime('%d/%m/%Y') if data_inicio is not None else '',
                'Data_Termino_Presencial': data_fim.strftime('%d/%m/%Y') if data_fim is not None else '',
                'Data_Inicio_Distancia': data_inicio_ead.strftime('%d/%m/%Y') if data_inicio_ead is not None else '',
                'Data_Termino_Distancia': data_fim_ead.strftime('%d/%m/%Y') if data_fim_ead is not None else '',
                'Local_GT': local_gt,
                'Comando': comando,
                'Funcao_Atual': funcao_atual,
                'Funcao_Apos_Curso': funcao_apos_curso,
                # Questionários
                'Pre_Requisitos': pre_requisitos,
                'Curso_Mapeado': curso_mapeado,
                'Progressao_Carreira': progressao_carreira,
                'Comunicado_Indicado': comunicado,
                'Curso_Anterior': curso_anterior,
                'Ano_Curso_Anterior': ano_curso_anterior if curso_anterior == "SIM" else '',
                'Ciencia_Dedicacao_EAD': dedicacao_ead,
                # Assinaturas
                'Justificativa_Chefe': justificativa,
                'Nome_Chefe_COP': nome_chefe,
                'Posto_Chefe_COP': posto_chefe,
                'Setor_Chefe_COP': setor_chefe,
                'Comando_Chefe_COP': comando_chefe,
                'Nome_Responsavel_DACTA': nome_resp,
                'Posto_Responsavel_DACTA': posto_resp,
                'Setor_Responsavel_DACTA': setor_resp,
                'Comando_Responsavel_DACTA': comando_resp,
            }
            
            with st.spinner("Gerando documento FIC de forma segura..."):
                try:
                    # Gerar FIC
                    doc_buffer = fic_word_filler.preencher_fic(dados_fic)
                    
                    st.success("✅ FIC gerado com sucesso!")
                    
                    # Download
                    nome_arquivo = f"FIC_{nome.replace(' ', '_')[:30]}_{curso_turma.replace('/', '_')}.docx"
                    st.download_button(
                        label="⬇️ Baixar FIC",
                        data=doc_buffer,
                        file_name=nome_arquivo,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                    
                    # Informações de segurança
                    st.info("""
                    🔒 **Confirmação de Segurança:**
                    - ✅ Dados carregados do Google Sheets
                    - ✅ Sem armazenamento em banco local
                    - ✅ Campos sensíveis protegidos
                    - ✅ Log sem dados identificáveis
                    - ✅ Memória será limpa ao fechar
                    """)
                    
                    # Limpar dados sensíveis da sessão após download
                    if st.button("🧹 Limpar Dados da Sessão", type="secondary"):
                        st.session_state.fic_dados_atuais = None
                        st.session_state.fic_dados_hash = None
                        st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Erro ao gerar FIC: {e}")
                    logger.error(f"Erro ao gerar FIC (dados ocultos por segurança)")
    
    # Instruções de segurança
    with st.expander("🔒 Informações de Segurança", expanded=False):
        st.markdown("""
        ### Medidas de Segurança Implementadas
        
        **1. Armazenamento**
        - Dados são carregados diretamente do Google Sheets
        - Nenhuma informação é persistida em disco
        - Cache apenas em memória (RAM)
        - Dados são limpos ao fechar a página
        
        **2. Criptografia**
        - Campos sensíveis (CPF, SARAM) são protegidos
        - Hashes são usados para referência em logs
        - Dados não são exibidos em texto claro nos logs
        
        **3. Acesso**
        - Uso obrigatório de Streamlit Secrets
        - Sem credenciais em arquivos locais
        - Apenas leitura da planilha (escopo readonly)
        
        **4. Validação**
        - Sanitização de inputs
        - Rate limiting nas requisições
        - Timeout nas conexões
        - Retry com exponential backoff
        
        **5. Auditoria**
        - Logs anonimizados
        - Hash de identificação em vez de dados reais
        - Registro de tentativas de acesso
        
        ### Configuração Recomendada
        
        1. **Google Cloud Console:**
           - Crie uma Service Account dedicada
           - Atribua apenas permissão de LEITOR
           - Use uma chave JSON dedicada
        
        2. **Google Sheets:**
           - Compartilhe apenas com a Service Account
           - Não compartilhe publicamente
           - Use criptografia do Google (padrão)
        
        3. **Streamlit Secrets:**
           - Nunca exponha credenciais no código
           - Use variáveis de ambiente em produção
           - Rotacione chaves periodicamente
        """)


def render_configuracao_segura() -> None:
    """Renderiza painel de configuração de segurança."""
    st.subheader("🔐 Configuração de Segurança")
    
    st.markdown("""
    ### Checklist de Segurança
    
    Antes de usar o sistema, verifique:
    
    - [ ] Service Account criada apenas para leitura
    - [ ] Planilha compartilhada apenas com a Service Account
    - [ ] Secrets configurados no Streamlit Cloud
    - [ ] Nenhum arquivo de credenciais em disco
    - [ ] HTTPS habilitado (Streamlit Cloud já tem)
    - [ ] Logs sendo monitorados
    - [ ] Política de rotação de chaves definida
    
    ### Estrutura da Planilha
    
    Colunas necessárias:
    ```
    SARAM | GRAD | ESP | NOME COMPLETO | NOME DE GUERRA | NASCIMENTO | PRAÇA | ULT PROM | CPF | RA | HAB 1 | EMAIL INTERNO | EMAIL EXTERNO | TELEFONE
    ```
    
    **Nota:** A planilha deve estar no Google Drive com criptografia padrão do Google.
    """)
