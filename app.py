import streamlit as st
import pandas as pd
from datetime import datetime, date
from data_manager import DataManager
from json_import import JSONImporter
from dashboard import Dashboard
from backup_manager import BackupManager

# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================
st.set_page_config(
    page_title="Controle de Cursos",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS TEMA CLARO PROFISSIONAL
# ============================================
st.markdown("""
<style>
    /* Fundo claro */
    .stApp {
        background: #f8f9fa;
        color: #333333;
    }
    
    /* Texto geral */
    .stApp, .stMarkdown, p, h1, h2, h3, h4, h5, h6 {
        color: #333333 !important;
    }
    
    label, .stTextInput label, .stSelectbox label, .stDateInput label, .stTextArea label {
        color: #555555 !important;
        font-weight: 500;
    }
    
    /* Título */
    h1 {
        color: #2c3e50 !important;
        font-weight: 700;
    }
    
    /* Cards claros */
    div[data-testid="stMetric"] {
        background: #ffffff !important;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stDateInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: #ffffff !important;
        color: #333333 !important;
        border: 1px solid #d0d0d0 !important;
        border-radius: 5px;
    }
    
    /* Selectbox dropdown */
    .stSelectbox > div > div {
        background: #ffffff !important;
    }
    
    /* Botões */
    .stButton > button {
        background: #3498db !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 5px;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background: #2980b9 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(52, 152, 219, 0.4);
    }
    
    /* Botão deletar */
    .stButton > button[kind="secondary"] {
        background: #e74c3c !important;
    }
    
    /* Abas */
    .stTabs [data-baseweb="tab-list"] {
        background: #e9ecef;
        border-radius: 10px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #555555 !important;
        background: transparent;
    }
    
    .stTabs [aria-selected="true"] {
        background: #3498db !important;
        color: #ffffff !important;
        border-radius: 5px;
    }
    
    /* Mensagens de alerta */
    .stAlert {
        border-radius: 10px;
    }
    
    /* Expander */
    .stExpander {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    
    /* Erro */
    div[data-testid="stAlert"][data-kind="error"] {
        background: rgba(231, 76, 60, 0.2) !important;
        color: #e74c3c !important;
        border-left-color: #e74c3c !important;
    }
    
    /* Sucesso */
    div[data-testid="stAlert"][data-kind="success"] {
        background: rgba(46, 204, 113, 0.2) !important;
        color: #2ecc71 !important;
        border-left-color: #2ecc71 !important;
    }
    
    /* Aviso */
    div[data-testid="stAlert"][data-kind="warning"] {
        background: rgba(241, 196, 15, 0.2) !important;
        color: #f1c40f !important;
        border-left-color: #f1c40f !important;
    }
    
    /* Info */
    div[data-testid="stAlert"][data-kind="info"] {
        background: rgba(52, 152, 219, 0.2) !important;
        color: #3498db !important;
        border-left-color: #3498db !important;
    }
    
    /* DataFrame */
    .stDataFrame {
        background: rgba(30, 30, 50, 0.9) !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(30, 30, 50, 0.9) !important;
        color: #ffffff !important;
        border-radius: 5px;
    }
    
    .streamlit-expanderContent {
        background: rgba(20, 20, 35, 0.8) !important;
        border-radius: 5px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Sidebar */
    .css-1d391kg, .css-12oz5g7 {
        background: rgba(15, 15, 26, 0.95) !important;
    }
    
    /* File uploader */
    .stFileUploader > div > div {
        background: rgba(255, 255, 255, 0.1) !important;
        color: #ffffff !important;
        border: 2px dashed rgba(255, 255, 255, 0.3) !important;
    }
    
    /* Cards de curso */
    .curso-card {
        background: rgba(30, 30, 50, 0.9);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid;
    }
    
    /* Seções de estado */
    .secao-estado {
        background: rgba(30, 30, 50, 0.7);
        border-radius: 10px;
        padding: 15px;
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# INICIALIZAÇÃO DO SESSION_STATE
# ============================================
def init_session_state():
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    if 'json_importer' not in st.session_state:
        st.session_state.json_importer = JSONImporter()
    if 'dashboard' not in st.session_state:
        st.session_state.dashboard = Dashboard()
    if 'backup_manager' not in st.session_state:
        st.session_state.backup_manager = BackupManager()

init_session_state()

# ============================================
# FUNÇÃO DE COR DO PRAZO
# ============================================
def get_cor_prazo(data_str):
    """
    Retorna a cor baseada nos dias restantes:
    - Vermelho: < 0 dias
    - Amarelo: 0-5 dias
    - Azul: 6-10 dias
    - Verde: > 10 dias
    """
    try:
        if not data_str:
            return "#95a5a6"  # Cinza para data vazia
        
        # Tentar converter a data
        if isinstance(data_str, str):
            data = datetime.strptime(data_str, "%d/%m/%Y").date()
        else:
            data = data_str
        
        hoje = date.today()
        dias_restantes = (data - hoje).days
        
        if dias_restantes < 0:
            return "#e74c3c"  # Vermelho - Atrasado
        elif dias_restantes <= 5:
            return "#f1c40f"  # Amarelo - Urgente
        elif dias_restantes <= 10:
            return "#3498db"  # Azul - Próximo
        else:
            return "#2ecc71"  # Verde - Tranquilo
    except:
        return "#95a5a6"  # Cinza para erro

def get_status_prazo(data_str):
    """Retorna o texto de status baseado nos dias restantes"""
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

# ============================================
# HEADER
# ============================================
st.title("📚 Controle de Cursos")
st.markdown("---")

# ============================================
# ABAS
# ============================================
tab_dashboard, tab_lista, tab_novo, tab_editar, tab_importar, tab_backup = st.tabs([
    "📊 Dashboard",
    "📋 Lista de Cursos",
    "➕ Novo Curso",
    "✏️ Editar Curso",
    "📥 Importar JSON",
    "💾 Backup"
])

# ============================================
# ABA 1: DASHBOARD
# ============================================
with tab_dashboard:
    st.header("📊 Dashboard")
    
    df = st.session_state.data_manager.carregar_dados()
    
    if df.empty:
        st.info("📋 Nenhum curso cadastrado ainda. Use a aba 'Novo Curso' para adicionar.")
    else:
        st.session_state.dashboard.mostrar_dashboard(df)
        
        # Resumo por estado
        st.subheader("📈 Cursos por Estado")
        if 'Estado' in df.columns:
            col1, col2, col3, col4 = st.columns(4)
            
            estados = df['Estado'].value_counts().to_dict()
            
            with col1:
                st.metric("📝 Solicitar Voluntários", estados.get('solicitar voluntários', 0))
            with col2:
                st.metric("👥 Fazer Indicação", estados.get('fazer indicação', 0))
            with col3:
                st.metric("👀 Ver Vagas Escalantes", estados.get('ver vagas escalantes', 0))
            with col4:
                st.metric("✅ Concluídos", estados.get('Concluído', 0))

# ============================================
# ABA 2: LISTA DE CURSOS
# ============================================
with tab_lista:
    st.header("📋 Lista de Cursos")
    
    # Filtro de busca
    termo_busca = st.text_input("🔍 Buscar curso", placeholder="Digite para buscar...")
    
    df = st.session_state.data_manager.carregar_dados()
    
    if termo_busca:
        df = st.session_state.data_manager.buscar_curso(termo_busca)
    
    if df.empty:
        st.info("📋 Nenhum curso encontrado.")
    else:
        # Organizar por estado
        estados_ordenados = ['solicitar voluntários', 'fazer indicação', 'ver vagas escalantes', 'Concluído', 'Sem estado']
        cores_estado = {
            'solicitar voluntários': '#e74c3c',
            'fazer indicação': '#f1c40f',
            'ver vagas escalantes': '#3498db',
            'Concluído': '#2ecc71',
            'Sem estado': '#95a5a6'
        }
        
        # Verificar se existe coluna Estado
        if 'Estado' not in df.columns:
            df['Estado'] = 'Sem estado'
        
        # Preencher estados vazios/NaN
        df['Estado'] = df['Estado'].fillna('Sem estado')
        df['Estado'] = df['Estado'].replace('', 'Sem estado')
        
        for estado in estados_ordenados:
            df_estado = df[df['Estado'] == estado]
            
            if not df_estado.empty:
                cor = cores_estado.get(estado, '#95a5a6')
                
                with st.expander(f"{estado.upper()} ({len(df_estado)} cursos)", expanded=True):
                    st.markdown(f"""
                    <div style="border-left: 4px solid {cor}; padding-left: 10px; margin-bottom: 10px;">
                        <h4 style="color: {cor};">{estado}</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for idx, row in df_estado.iterrows():
                        curso_nome = row.get('Curso', 'Sem nome')
                        turma = row.get('Turma', 'N/A')
                        vagas = row.get('Vagas', 0)
                        data_siat = row.get('Fim da indicação da SIAT', '')
                        
                        cor_prazo = get_cor_prazo(data_siat)
                        status_prazo = get_status_prazo(data_siat)
                        
                        col1, col2, col3, col4 = st.columns([3, 1, 2, 1])
                        
                        with col1:
                            st.write(f"**{curso_nome}**")
                            st.caption(f"Turma: {turma}")
                        
                        with col2:
                            st.write(f"👥 {vagas} vagas")
                        
                        with col3:
                            st.markdown(f"<span style='color: {cor_prazo};'>⏰ {status_prazo}</span>", 
                                      unsafe_allow_html=True)
                        
                        with col4:
                            if st.button("🗑️", key=f"del_{idx}"):
                                sucesso, msg = st.session_state.data_manager.excluir_curso(idx)
                                if sucesso:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                        
                        st.markdown("---")

# ============================================
# ABA 3: NOVO CURSO
# ============================================
with tab_novo:
    st.header("➕ Novo Curso")
    
    with st.form("form_novo_curso"):
        col1, col2 = st.columns(2)
        
        with col1:
            curso = st.text_input("Nome do Curso *", placeholder="Ex: AAC001")
            turma = st.text_input("Turma *", placeholder="Ex: TU 01")
            vagas = st.number_input("Vagas", min_value=0, value=0)
            estado = st.selectbox("Estado", 
                                 ['solicitar voluntários', 'fazer indicação', 'ver vagas escalantes', 'Concluído'])
            prioridade = st.selectbox("Prioridade", ['Alta', 'Média', 'Baixa'])
        
        with col2:
            data_siat = st.text_input("Fim da indicação SIAT * (DD/MM/AAAA)", 
                                     placeholder="Ex: 15/12/2024")
            num_sigad = st.text_input("Número do SIGAD")
            om_executora = st.text_input("OM Executora")
            notas = st.text_area("Notas")
        
        # Campo simples de vagas por OM (apenas texto livre)
        st.markdown("---")
        vagas_om = st.text_area("Vagas por OM (opcional)", 
                                placeholder="Ex: CRCEA-SE: 3 vagas\nAPP-SP: 2 vagas\nGCC: 1 vaga",
                                help="Informe as vagas por organização militar")
        
        submitted = st.form_submit_button("💾 Salvar Curso")
        
        if submitted:
            if not curso or not turma or not data_siat:
                st.error("⚠️ Preencha todos os campos obrigatórios (*)")
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
                
                # Adicionar vagas por OM no campo Notas se informado
                if vagas_om:
                    novo_curso['Notas'] = f"{notas}\n\nVagas por OM:\n{vagas_om}" if notas else f"Vagas por OM:\n{vagas_om}"
                
                # Salvar
                sucesso, msg = st.session_state.data_manager.adicionar_curso(novo_curso)
                if sucesso:
                    st.success(f"✅ {msg}")
                    st.session_state.backup_manager.criar_backup()
                else:
                    if "AVISO" in msg:
                        st.warning(f"⚠️ {msg}")
                    else:
                        st.error(f"❌ {msg}")

# ============================================
# ABA 4: EDITAR CURSO
# ============================================
with tab_editar:
    st.header("✏️ Editar Curso")
    
    df = st.session_state.data_manager.carregar_dados()
    
    if df.empty:
        st.info("📋 Nenhum curso cadastrado para editar.")
    else:
        # Lista de cursos para seleção
        opcoes = [f"{row['Curso']} - {row['Turma']}" for _, row in df.iterrows()]
        
        curso_selecionado = st.selectbox("Selecione o curso", opcoes)
        
        if curso_selecionado:
            # Encontrar índice do curso
            idx_curso = opcoes.index(curso_selecionado)
            curso_atual = df.iloc[idx_curso]
            
            with st.form("form_editar_curso"):
                col1, col2 = st.columns(2)
                
                with col1:
                    curso = st.text_input("Nome do Curso", value=curso_atual.get('Curso', ''))
                    turma = st.text_input("Turma", value=curso_atual.get('Turma', ''))
                    vagas = st.number_input("Vagas", min_value=0, 
                                           value=int(curso_atual.get('Vagas', 0)) if pd.notna(curso_atual.get('Vagas', 0)) else 0)
                    estado = st.selectbox("Estado", 
                                         ['solicitar voluntários', 'fazer indicação', 'ver vagas escalantes', 'Concluído'],
                                         index=['solicitar voluntários', 'fazer indicação', 'ver vagas escalantes', 'Concluído'].index(curso_atual.get('Estado', 'solicitar voluntários')) if curso_atual.get('Estado') in ['solicitar voluntários', 'fazer indicação', 'ver vagas escalantes', 'Concluído'] else 0)
                    prioridade = st.selectbox("Prioridade", ['Alta', 'Média', 'Baixa'],
                                             index=['Alta', 'Média', 'Baixa'].index(curso_atual.get('Prioridade', 'Média')) if curso_atual.get('Prioridade') in ['Alta', 'Média', 'Baixa'] else 1)
                
                with col2:
                    data_siat = st.text_input("Fim da indicação SIAT (DD/MM/AAAA)", 
                                             value=str(curso_atual.get('Fim da indicação da SIAT', '')))
                    num_sigad = st.text_input("Número do SIGAD", 
                                             value=str(curso_atual.get('Numero do SIGAD', '')))
                    om_executora = st.text_input("OM Executora", 
                                                value=str(curso_atual.get('OM_Executora', '')))
                    notas = st.text_area("Notas", 
                                        value=str(curso_atual.get('Notas', '')))
                
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
                        'Notas': notas
                    }
                    
                    # Manter valores de OM existentes
                    for col in df.columns:
                        if col.startswith('OM_') and col != 'OM_Executora':
                            curso_atualizado[col] = curso_atual.get(col, '')
                    
                    # Atualizar
                    sucesso, msg = st.session_state.data_manager.atualizar_curso(idx_curso, curso_atualizado)
                    if sucesso:
                        st.success(f"✅ {msg}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

# ============================================
# ABA 5: IMPORTAR JSON
# ============================================
with tab_importar:
    st.header("📥 Importar JSON")
    
    arquivo_json = st.file_uploader("Selecione o arquivo JSON", type=['json'])
    
    if arquivo_json is not None:
        # Carregar e validar JSON
        dados, erro = st.session_state.json_importer.carregar_json(arquivo_json.getvalue())
        
        if erro:
            st.error(f"❌ {erro}")
        else:
            # Validar estrutura
            cursos_validos, cursos_invalidos = st.session_state.json_importer.validar_json(dados)
            
            resumo = st.session_state.json_importer.get_resumo_validacao()
            
            # Mostrar resumo
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total", resumo['total'])
            with col2:
                st.metric("✅ Válidos", resumo['validos'])
            with col3:
                st.metric("❌ Inválidos", resumo['invalidos'])
            
            # Mostrar cursos válidos
            if cursos_validos:
                st.subheader("✅ Cursos Válidos")
                for curso in cursos_validos:
                    st.write(f"- {curso.get('Curso', 'Sem nome')} - {curso.get('Turma', 'N/A')}")
            
            # Mostrar cursos inválidos
            if cursos_invalidos:
                st.subheader("❌ Cursos Inválidos")
                for item in cursos_invalidos:
                    st.error(f"{item['curso']}: {item['erro']}")
            
            # Botão de importação
            if cursos_validos and st.button("📥 Importar Cursos Válidos"):
                importados, erros = st.session_state.json_importer.importar_cursos(
                    cursos_validos, st.session_state.data_manager
                )
                
                if importados > 0:
                    st.success(f"✅ {importados} curso(s) importado(s) com sucesso!")
                    # Criar backup após importação
                    st.session_state.backup_manager.criar_backup()
                    st.rerun()
                
                if erros:
                    for erro in erros:
                        st.error(f"❌ {erro}")

# ============================================
# ABA 6: BACKUP
# ============================================
with tab_backup:
    st.header("💾 Gerenciamento de Backups")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📦 Criar Backup")
        if st.button("💾 Criar Backup Agora"):
            sucesso, msg = st.session_state.backup_manager.criar_backup()
            if sucesso:
                st.success(f"✅ {msg}")
            else:
                st.error(f"❌ {msg}")
    
    with col2:
        st.subheader("📥 Exportar Excel")
        excel_bytes = st.session_state.data_manager.exportar_excel_bytes()
        if excel_bytes:
            st.download_button(
                label="📥 Baixar Excel",
                data=excel_bytes,
                file_name=f"cursos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    # Lista de backups existentes
    st.subheader("📋 Backups Disponíveis")
    backups = st.session_state.backup_manager.listar_backups()
    
    if not backups:
        st.info("Nenhum backup criado ainda.")
    else:
        for backup in backups:
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.write(f"📦 {backup['nome']}")
            
            with col2:
                st.caption(f"{backup['data'].strftime('%d/%m/%Y %H:%M')} - {backup['tamanho'] / 1024:.1f} KB")
            
            with col3:
                if st.button("↩️ Restaurar", key=f"restore_{backup['nome']}"):
                    sucesso, msg = st.session_state.backup_manager.restaurar_backup(backup['caminho'])
                    if sucesso:
                        st.success(f"✅ {msg}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.title("📚 Controle de Cursos")
    st.markdown("---")
    
    # Status GitHub
    autenticado, msg_github = st.session_state.data_manager.verificar_status_github()
    if autenticado:
        st.success(f"🟢 GitHub: {msg_github}")
    else:
        st.warning(f"🟡 GitHub: {msg_github}")
    
    st.markdown("---")
    
    # Resumo rápido
    df = st.session_state.data_manager.carregar_dados()
    st.metric("Total de Cursos", len(df))
    
    if 'Fim da indicação da SIAT' in df.columns:
        hoje = date.today()
        atrasados = 0
        urgentes = 0
        
        for data_str in df['Fim da indicação da SIAT'].dropna():
            try:
                if isinstance(data_str, str):
                    data = datetime.strptime(data_str, "%d/%m/%Y").date()
                else:
                    data = data_str
                dias = (data - hoje).days
                if dias < 0:
                    atrasados += 1
                elif dias <= 5:
                    urgentes += 1
            except:
                pass
        
        if atrasados > 0:
            st.error(f"⛔ {atrasados} prazo(s) atrasado(s)")
        if urgentes > 0:
            st.warning(f"⚠️ {urgentes} prazo(s) urgente(s)")
    
    st.markdown("---")
    st.caption("Desenvolvido para controle de cursos militares")
