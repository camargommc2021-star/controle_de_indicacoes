import pandas as pd
import streamlit as st
from datetime import datetime, date
import os
from data_manager import DataManager
from pdf_extractor import PDFExtractor
from dashboard import Dashboard

st.set_page_config(
    page_title="Controle de Indicações 2026",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
    }
    .st-emotion-cache-1y4p8pa {
        max-width: 100%;
    }
    .verde {
        background-color: #90EE90;
        padding: 5px;
        border-radius: 3px;
    }
    .amarelo {
        background-color: #FFD700;
        padding: 5px;
        border-radius: 3px;
    }
    .vermelho {
        background-color: #FF6B6B;
        padding: 5px;
        border-radius: 3px;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()

if 'dashboard' not in st.session_state:
    st.session_state.dashboard = Dashboard()

if 'pdf_extractor' not in st.session_state:
    st.session_state.pdf_extractor = PDFExtractor()

def get_cor_prazo(data_str):
    if not data_str or pd.isna(data_str):
        return ""
    try:
        if isinstance(data_str, str):
            data_siat = datetime.strptime(data_str, "%d/%m/%Y").date()
        else:
            data_siat = data_str
        hoje = date.today()
        dias_restantes = (data_siat - hoje).days
        
        if dias_restantes < 0:
            return "vermelho"
        elif dias_restantes <= 5:
            return "amarelo"
        else:
            return "verde"
    except:
        return ""

def formatar_data_para_excel(data):
    if pd.isna(data) or data is None:
        return ""
    if isinstance(data, datetime):
        return data.strftime("%d/%m/%Y")
    if isinstance(data, date):
        return data.strftime("%d/%m/%Y")
    if isinstance(data, str):
        return data
    return str(data)

st.title("📚 Controle de Indicações 2026")

menu = st.sidebar.radio(
    "Menu",
    ["📊 Dashboard", "📋 Lista de Cursos", "➕ Novo Curso", "✏️ Editar Curso", "📄 Importar PDF"]
)

if menu == "📊 Dashboard":
    st.header("Dashboard de Prazos")
    
    df = st.session_state.data_manager.carregar_dados()
    
    if not df.empty:
        st.session_state.dashboard.mostrar_dashboard(df)
        
        st.subheader("Resumo por Estado")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            count = len(df[df['Estado'] == 'solicitar voluntários'])
            st.metric("Solicitar Voluntários", count)
        
        with col2:
            count = len(df[df['Estado'] == 'fazer indicação'])
            st.metric("Fazer Indicação", count)
        
        with col3:
            count = len(df[df['Estado'] == 'Concluído'])
            st.metric("Concluídos", count)
        
        with col4:
            count = len(df[df['Estado'] == 'ver vagas escalantes'])
            st.metric("Ver Vagas Escalantes", count)
        
        st.subheader("Alertas de Prazos")
        hoje = date.today()
        
        df_vencendo = df[df['Fim indicação SIAT'].notna()].copy()
        if not df_vencendo.empty:
            df_vencendo['dias_restantes'] = df_vencendo['Fim indicação SIAT'].apply(
                lambda x: (datetime.strptime(x, "%d/%m/%Y").date() - hoje).days 
                if isinstance(x, str) else 0
            )
            
            urgente = df_vencendo[df_vencendo['dias_restantes'] <= 5]
            atrasado = df_vencendo[df_vencendo['dias_restantes'] < 0]
            
            if not atrasado.empty:
                st.error(f"⚠️ {len(atrasado)} curso(s) com prazo ATRASADO!")
                st.dataframe(atrasado[['Curso', 'Turma', 'Fim indicação SIAT', 'Estado']], use_container_width=True)
            
            if not urgente.empty:
                st.warning(f"⚡ {len(urgente)} curso(s) com prazo em menos de 5 dias!")
                st.dataframe(urgente[['Curso', 'Turma', 'Fim indicação SIAT', 'Estado']], use_container_width=True)
    else:
        st.info("Nenhum curso cadastrado. Adicione cursos pelo menu 'Novo Curso' ou importe via PDF.")

elif menu == "📋 Lista de Cursos":
    st.header("Lista de Cursos")
    
    df = st.session_state.data_manager.carregar_dados()
    
    if not df.empty:
        col1, col2 = st.columns([3, 1])
        with col1:
            filtro_estado = st.multiselect(
                "Filtrar por Estado",
                options=df['Estado'].unique() if 'Estado' in df.columns else [],
                default=[]
            )
        with col2:
            filtro_prioridade = st.multiselect(
                "Filtrar por Prioridade",
                options=df['Prioridade'].unique() if 'Prioridade' in df.columns else [],
                default=[]
            )
        
        df_filtrado = df.copy()
        if filtro_estado:
            df_filtrado = df_filtrado[df_filtrado['Estado'].isin(filtro_estado)]
        if filtro_prioridade:
            df_filtrado = df_filtrado[df_filtrado['Prioridade'].isin(filtro_prioridade)]
        
        def colorir_prazo(val):
            cor = get_cor_prazo(val)
            if cor == "vermelho":
                return 'background-color: #FF6B6B; color: white'
            elif cor == "amarelo":
                return 'background-color: #FFD700'
            elif cor == "verde":
                return 'background-color: #90EE90'
            return ''
        
        st.dataframe(
            df_filtrado.style.applymap(colorir_prazo, subset=['Fim indicação SIAT']),
            use_container_width=True,
            hide_index=True
        )
        
        st.download_button(
            label="📥 Exportar para Excel",
            data=st.session_state.data_manager.exportar_excel_bytes(),
            file_name=f"cursos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("Nenhum curso cadastrado.")

elif menu == "➕ Novo Curso":
    st.header("Cadastrar Novo Curso")
    
    with st.form("novo_curso"):
        col1, col2 = st.columns(2)
        
        with col1:
            curso = st.text_input("Curso", placeholder="Nome do curso")
            turma = st.text_input("Turma", placeholder="Identificação da turma")
            vagas = st.number_input("Vagas", min_value=0, step=1, value=0)
            autorizados = st.text_input("Autorizados pelas escalantes", placeholder="Número ou nome")
            prioridade = st.selectbox("Prioridade", ["", "Alta", "Média", "Baixa"])
            recebimento_sigad = st.date_input("Recebimento do SIGAD com as vagas", value=None)
            num_sigad = st.text_input("Número do SIGAD", placeholder="Número do documento")
        
        with col2:
            estado = st.selectbox("Estado", ["", "solicitar voluntários", "fazer indicação", "Concluído", "ver vagas escalantes"])
            data_conclusao = st.date_input("DATA DA CONCLUSÃO", value=None, disabled=(estado != "Concluído"))
            num_sigad_chefia = st.text_input("Número do SIGAD encaminhando pra chefia", placeholder="Número do documento")
            prazo_chefia = st.date_input("Prazo dado pela chefia", value=None)
            fim_siat = st.date_input("Fim da indicação da SIAT", value=None)
            notas = st.text_area("Notas", placeholder="Observações adicionais")
        
        submitted = st.form_submit_button("💾 Salvar Curso")
        
        if submitted:
            # Todos os campos são opcionais - converter datas apenas se preenchidas
            if estado == "Concluído":
                data_conclusao_str = datetime.now().strftime("%d/%m/%Y")
            else:
                data_conclusao_str = ""
            
            # Converter datas para string apenas se preenchidas
            recebimento_str = recebimento_sigad.strftime("%d/%m/%Y") if recebimento_sigad else ""
            prazo_str = prazo_chefia.strftime("%d/%m/%Y") if prazo_chefia else ""
            fim_siat_str = fim_siat.strftime("%d/%m/%Y") if fim_siat else ""
            
            novo_curso = {
                'Curso': curso if curso else "",
                'Turma': turma if turma else "",
                'Vagas': int(vagas) if vagas else 0,
                'Autorizados pelas escalantes': autorizados if autorizados else "",
                'Prioridade': prioridade if prioridade else "",
                'Recebimento do SIGAD com as vagas': recebimento_str,
                'Numero do SIGAD': num_sigad if num_sigad else "",
                'Estado': estado if estado else "",
                'DATA DA CONCLUSÃO': data_conclusao_str,
                'Numero do SIGAD  encaminhando pra chefia': num_sigad_chefia if num_sigad_chefia else "",
                'Prazo dado pela chefia': prazo_str,
                'Fim da indicação da SIAT': fim_siat_str,
                'Notas': notas if notas else ""
            }
            
            sucesso, mensagem = st.session_state.data_manager.adicionar_curso(novo_curso)
            if sucesso:
                st.success(mensagem)
            else:
                st.error(mensagem)

elif menu == "✏️ Editar Curso":
    st.header("Editar Curso")
    
    df = st.session_state.data_manager.carregar_dados()
    
    if not df.empty:
        curso_selecionado = st.selectbox(
            "Selecione o curso para editar",
            options=df.index,
            format_func=lambda x: f"{df.loc[x, 'Curso']} - {df.loc[x, 'Turma']} ({df.loc[x, 'Estado']})"
        )
        
        if curso_selecionado is not None:
            curso_atual = df.loc[curso_selecionado]
            
            with st.form("editar_curso"):
                col1, col2 = st.columns(2)
                
                with col1:
                    curso = st.text_input("Curso", value=curso_atual.get('Curso', ''))
                    turma = st.text_input("Turma", value=curso_atual.get('Turma', ''))
                    vagas = st.number_input("Vagas", min_value=0, step=1, value=int(curso_atual.get('Vagas', 0) or 0))
                    autorizados = st.text_input("Autorizados pelas escalantes", value=curso_atual.get('Autorizados pelas escalantes', ''))
                    
                    prioridade_atual = curso_atual.get('Prioridade', '')
                    prioridade_index = 0
                    if prioridade_atual in ["Alta", "Média", "Baixa"]:
                        prioridade_index = ["Alta", "Média", "Baixa"].index(prioridade_atual) + 1
                    prioridade = st.selectbox("Prioridade", ["", "Alta", "Média", "Baixa"], 
                                            index=prioridade_index)
                    
                    try:
                        data_str = curso_atual.get('Recebimento do SIGAD com as vagas', '')
                        if data_str and data_str != "":
                            recebimento_sigad = datetime.strptime(data_str, "%d/%m/%Y").date()
                        else:
                            recebimento_sigad = None
                    except:
                        recebimento_sigad = None
                    recebimento_sigad = st.date_input("Recebimento do SIGAD com as vagas", value=recebimento_sigad)
                    
                    num_sigad = st.text_input("Número do SIGAD", value=curso_atual.get('Numero do SIGAD', ''))
                
                with col2:
                    estado_atual = curso_atual.get('Estado', '')
                    estados_lista = ["", "solicitar voluntários", "fazer indicação", "Concluído", "ver vagas escalantes"]
                    estado_index = 0
                    if estado_atual in estados_lista:
                        estado_index = estados_lista.index(estado_atual)
                    estado = st.selectbox("Estado", estados_lista, index=estado_index)
                    
                    data_conclusao_str = curso_atual.get('DATA DA CONCLUSÃO', '')
                    if estado == "Concluído" and (not data_conclusao_str or data_conclusao_str == ""):
                        data_conclusao_str = datetime.now().strftime("%d/%m/%Y")
                    
                    st.text_input("DATA DA CONCLUSÃO (auto)", value=data_conclusao_str, disabled=True)
                    
                    num_sigad_chefia = st.text_input("Número do SIGAD encaminhando pra chefia", 
                                                    value=curso_atual.get('Numero do SIGAD  encaminhando pra chefia', ''))
                    
                    try:
                        data_str = curso_atual.get('Prazo dado pela chefia', '')
                        if data_str and data_str != "":
                            prazo_chefia = datetime.strptime(data_str, "%d/%m/%Y").date()
                        else:
                            prazo_chefia = None
                    except:
                        prazo_chefia = None
                    prazo_chefia = st.date_input("Prazo dado pela chefia", value=prazo_chefia)
                    
                    try:
                        data_str = curso_atual.get('Fim da indicação da SIAT', '')
                        if data_str and data_str != "":
                            fim_siat = datetime.strptime(data_str, "%d/%m/%Y").date()
                        else:
                            fim_siat = None
                    except:
                        fim_siat = None
                    fim_siat = st.date_input("Fim da indicação da SIAT", value=fim_siat)
                    
                    notas = st.text_area("Notas", value=str(curso_atual.get('Notas', '')))
                
                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button("💾 Atualizar Curso")
                with col2:
                    excluir = st.form_submit_button("🗑️ Excluir Curso")
                
                if submitted:
                    # Todos os campos são opcionais - converter datas apenas se preenchidas
                    recebimento_str = recebimento_sigad.strftime("%d/%m/%Y") if recebimento_sigad else ""
                    prazo_str = prazo_chefia.strftime("%d/%m/%Y") if prazo_chefia else ""
                    fim_siat_str = fim_siat.strftime("%d/%m/%Y") if fim_siat else ""
                    
                    curso_atualizado = {
                        'Curso': curso if curso else "",
                        'Turma': turma if turma else "",
                        'Vagas': int(vagas) if vagas else 0,
                        'Autorizados pelas escalantes': autorizados if autorizados else "",
                        'Prioridade': prioridade if prioridade else "",
                        'Recebimento do SIGAD com as vagas': recebimento_str,
                        'Numero do SIGAD': num_sigad if num_sigad else "",
                        'Estado': estado if estado else "",
                        'DATA DA CONCLUSÃO': data_conclusao_str if estado == "Concluído" else "",
                        'Numero do SIGAD  encaminhando pra chefia': num_sigad_chefia if num_sigad_chefia else "",
                        'Prazo dado pela chefia': prazo_str,
                        'Fim da indicação da SIAT': fim_siat_str,
                        'Notas': notas if notas else ""
                    }
                    
                    sucesso, mensagem = st.session_state.data_manager.atualizar_curso(curso_selecionado, curso_atualizado)
                    if sucesso:
                        st.success(mensagem)
                    else:
                        st.error(mensagem)
                
                if excluir:
                    sucesso, mensagem = st.session_state.data_manager.excluir_curso(curso_selecionado)
                    if sucesso:
                        st.success(mensagem)
                        st.rerun()
                    else:
                        st.error(mensagem)
    else:
        st.info("Nenhum curso cadastrado para editar.")

elif menu == "📄 Importar PDF":
    st.header("Importar Cursos de PDF")
    
    st.markdown("""
    ### Como funciona:
    1. Faça upload do arquivo PDF
    2. O sistema extrairá automaticamente cursos e datas
    3. Revise os dados extraídos
    4. Clique em "Importar" para adicionar ao sistema
    
    **O sistema procura por padrões como:**
    - Curso: [nome do curso]
    - Data: [data]
    - Turma: [identificação]
    """)
    
    uploaded_file = st.file_uploader("Escolha o arquivo PDF", type=['pdf'])
    
    if uploaded_file is not None:
        with st.spinner("Extraindo dados do PDF..."):
            cursos_extraidos = st.session_state.pdf_extractor.extrair_cursos(uploaded_file)
        
        if cursos_extraidos:
            st.success(f"✅ {len(cursos_extraidos)} curso(s) encontrado(s)!")
            
            st.subheader("Dados extraídos:")
            df_extraido = pd.DataFrame(cursos_extraidos)
            st.dataframe(df_extraido, use_container_width=True)
            
            if st.button("✅ Importar Todos os Cursos"):
                sucessos = 0
                for curso in cursos_extraidos:
                    sucesso, _ = st.session_state.data_manager.adicionar_curso(curso)
                    if sucesso:
                        sucessos += 1
                
                st.success(f"✅ {sucessos} de {len(cursos_extraidos)} cursos importados com sucesso!")
        else:
            st.warning("⚠️ Nenhum curso encontrado no PDF. Verifique se o formato está correto.")
            
            st.info("""
            **Dica:** O PDF deve conter texto no formato:
            ```
            Curso: Nome do Curso
            Data: 15/01/2026
            Turma: Turma A
            ...
            ```
            """)

st.sidebar.markdown("---")

# Status do GitHub
try:
    autenticado, mensagem_status = st.session_state.data_manager.verificar_status_github()
    
    if autenticado:
        st.sidebar.success("✅ GitHub conectado")
        st.sidebar.caption(f"💾 {mensagem_status}")
        
        # Botão de sincronização manual
        if st.sidebar.button("🔄 Sincronizar do GitHub"):
            with st.spinner("Sincronizando..."):
                sucesso, mensagem = st.session_state.data_manager.github_manager.sincronizar_para_local()
                if sucesso:
                    st.sidebar.success(mensagem)
                    st.rerun()
                else:
                    st.sidebar.error(mensagem)
    else:
        st.sidebar.warning("⚠️ GitHub não conectado")
        st.sidebar.caption(f"❌ {mensagem_status}")
        st.sidebar.info("Configure GITHUB_TOKEN nos secrets do Streamlit")
        
except Exception as e:
    st.sidebar.error("❌ Erro ao verificar GitHub")

st.sidebar.markdown("---")
st.sidebar.info("💡 Dados salvos automaticamente no GitHub")
st.sidebar.markdown("📅 Última atualização: " + datetime.now().strftime("%d/%m/%Y %H:%M"))
