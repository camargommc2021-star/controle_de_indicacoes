#!/usr/bin/env python3
"""Teste simples do preenchimento automático"""

import streamlit as st
from managers.pessoas_manager_secure import PessoasManagerSecure

st.set_page_config(page_title="Teste FIC", layout="wide")
st.title("Teste de Preenchimento Automático FIC")

# Inicializar
if 'pm' not in st.session_state:
    st.session_state.pm = PessoasManagerSecure()
    st.session_state.dados_pessoa = None

pm = st.session_state.pm

# Listar pessoas
df = pm.listar_todos()
st.write(f"Total de pessoas: {len(df)}")

if not df.empty:
    # Selectbox
    nomes = ["-- Selecione --"] + df['Nome_Completo'].tolist()
    
    nome = st.selectbox("Escolha a pessoa:", nomes, key="select_pessoa")
    
    if nome != "-- Selecione --":
        # Botão carregar
        if st.button("CARREGAR DADOS", type="primary"):
            dados = pm.obter_dados_completos_fic(nome)
            if dados:
                st.session_state.dados_pessoa = dados
                st.rerun()
        
        # Mostrar dados se existirem
        if st.session_state.dados_pessoa:
            p = st.session_state.dados_pessoa
            
            st.success(f"Dados carregados: {p.get('Posto_Graduacao')} {p.get('Nome_Completo')}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.text_input("Posto:", value=p.get('Posto_Graduacao', ''), key="posto")
                st.text_input("Nome:", value=p.get('Nome_Completo', ''), key="nome")
                st.text_input("CPF:", value=p.get('CPF', ''), key="cpf")
                st.text_input("SARAM:", value=p.get('SARAM', ''), key="saram")
            
            with col2:
                st.text_input("Email:", value=p.get('Email', ''), key="email")
                st.text_input("Telefone:", value=p.get('Telefone', ''), key="telefone")
                st.text_input("OM:", value="CRCEA-SE", key="om")
                st.text_input("Especialidade:", value=p.get('Especialidade', ''), key="esp")
    
    if st.button("LIMPAR"):
        st.session_state.dados_pessoa = None
        st.rerun()
