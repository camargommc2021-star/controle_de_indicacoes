"""
Aba de Cadastro de Chefes
"""

import streamlit as st
import pandas as pd
from managers.chefes_manager import get_chefes_manager
from utils.logger import get_logger

logger = get_logger(__name__)


def render_chefes_tab():
    """Renderiza a aba de cadastro de chefes"""
    st.header("👔 Cadastro de Chefes")
    
    manager = get_chefes_manager()
    
    # Tabs internas
    tab_lista, tab_cadastro, tab_importar = st.tabs(["📋 Lista de Chefes", "➕ Novo Chefe", "📥 Importar do Excel"])
    
    with tab_lista:
        render_lista_chefes(manager)
    
    with tab_cadastro:
        render_form_chefe(manager)
    
    with tab_importar:
        render_importar_excel(manager)


def render_lista_chefes(manager):
    """Renderiza a lista de chefes cadastrados"""
    st.subheader("Chefes Cadastrados")
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        setores = ['Todos'] + manager.get_setores()
        setor_filtro = st.selectbox("Filtrar por Setor", setores)
    with col2:
        busca = st.text_input("Buscar por nome, posto ou função", placeholder="Digite para buscar...")
    
    # Buscar chefes
    if busca:
        chefes = manager.search_chefes(busca)
    elif setor_filtro != 'Todos':
        chefes = manager.get_chefes_by_setor(setor_filtro)
    else:
        chefes = manager.get_all_chefes()
    
    if not chefes:
        st.info("Nenhum chefe cadastrado. Use a aba 'Novo Chefe' para adicionar.")
        return
    
    # Exibir em dataframe
    df_data = []
    for chefe in chefes:
        df_data.append({
            'ID': chefe['id'],
            'Nome': chefe['nome'],
            'Posto': chefe['posto'],
            'Função': chefe['funcao'],
            'Setor': chefe.get('setor', ''),
            'Curso': chefe.get('curso_codigo', ''),
        })
    
    df = pd.DataFrame(df_data)
    
    # Seleção para edição/exclusão
    col_id, col_acoes = st.columns([3, 1])
    
    with col_id:
        selected = st.selectbox(
            "Selecione um chefe para editar/excluir:",
            options=[c['id'] for c in chefes],
            format_func=lambda x: next(f"{c['nome']} ({c['posto']})" for c in chefes if c['id'] == x)
        )
    
    with col_acoes:
        st.write("")
        st.write("")
        if st.button("🗑️ Excluir", type="secondary"):
            if manager.delete_chefe(selected):
                st.success("Chefe removido!")
                st.rerun()
    
    # Mostrar detalhes do selecionado
    if selected:
        chefe = manager.get_chefe_by_id(selected)
        if chefe:
            with st.expander("📄 Detalhes do Chefe", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Nome:** {chefe['nome']}")
                    st.write(f"**Posto:** {chefe['posto']}")
                    st.write(f"**Função:** {chefe['funcao']}")
                with col2:
                    st.write(f"**Setor:** {chefe.get('setor', 'N/A')}")
                    st.write(f"**Curso:** {chefe.get('curso_codigo', 'N/A')}")
                    st.write(f"**Comando:** {chefe.get('comando', 'N/A')}")
    
    # Tabela
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Exportar
    st.download_button(
        label="📥 Exportar para Excel",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name="chefes_cadastrados.csv",
        mime="text/csv"
    )


def render_form_chefe(manager, chefe_edit=None):
    """Renderiza o formulário de cadastro/edição de chefe"""
    st.subheader("Cadastrar Novo Chefe")
    
    with st.form("form_chefe"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome Completo *", placeholder="Ex: LEONARDO REZENDE ALVES")
            posto = st.selectbox("Posto/Graduação *", [
                "Maj Av", "Ten Cel Av", "Cel Av", "Gen Brig Av",
                "Maj QOAV", "Ten Cel QOAV", "Cel QOAV",
                "Maj QOECTA", "Ten Cel QOECTA",
                "1S", "2S", "3S", "Cb", "Sd",
                "Civ", "Cv DACTA"
            ])
            funcao = st.selectbox("Função *", [
                "Chefe do COP", "Chefe da DA", "Chefe da DO", "Chefe da DT",
                "Chefe da SIPACEA", "Chefe da SIAT", "Chefe da CSD",
                "Chefe da CST", "Chefe da AVSEC"
            ])
        
        with col2:
            setor = st.text_input("Setor/Seção", placeholder="Ex: COP, DA, DO, DT...")
            curso_codigo = st.text_input("Código do Curso (se aplicável)", placeholder="Ex: CTP001")
            curso_nome = st.text_input("Nome do Curso (se aplicável)", placeholder="Ex: CAPACITAÇÃO PARA INSTRUTORES")
            comando = st.selectbox("Comando", ["DECEA", "DIRENS", "COMGAP", "SEFA", "CENIPA", ""])
        
        submitted = st.form_submit_button("💾 Salvar Chefe", type="primary")
        
        if submitted:
            if not nome or not posto or not funcao:
                st.error("Por favor, preencha os campos obrigatórios (*)")
            else:
                chefe = manager.add_chefe(
                    nome=nome,
                    posto=posto,
                    funcao=funcao,
                    setor=setor,
                    curso_codigo=curso_codigo,
                    curso_nome=curso_nome,
                    comando=comando
                )
                st.success(f"Chefe {chefe['nome']} cadastrado com sucesso!")
                st.rerun()


def render_importar_excel(manager):
    """Renderiza a opção de importar do Excel"""
    st.subheader("Importar do Excel da Chefia")
    
    st.info("""
    Esta opção importa os dados do arquivo `data/chefia.xlsx` para o sistema.
    
    O arquivo deve conter as colunas:
    - CURSO: Código do curso
    - NOME DO CURSO: Nome completo do curso
    - COMANDO: Comando responsável
    - SETOR RESPONSÁVEL: Setor/Seção
    - NOME: Nome do chefe
    - POSTO: Posto/Graduação
    - FUNÇÃO: Função do chefe
    """)
    
    if st.button("🔄 Importar do Excel", type="primary"):
        with st.spinner("Importando..."):
            chefes = manager._import_from_excel()
            st.success(f"Importados {len(chefes)} chefes com sucesso!")
            st.rerun()
