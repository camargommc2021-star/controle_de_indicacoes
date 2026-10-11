import streamlit as st
import pandas as pd

from utils.validators import calcular_metricas_prazos

class Dashboard:
    def __init__(self):
        pass
    
    def mostrar_dashboard(self, df):
        if df.empty:
            st.info("Nenhum dado disponível para o dashboard.")
            return
        
        # Mostrar apenas resumo sem gráficos
        resumo = self.gerar_resumo(df)
        
        st.subheader("📊 Resumo Geral")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Cursos", resumo.get('total_cursos', 0))
        
        with col2:
            st.metric("Prazos Atrasados", resumo.get('prazos_atrasados', 0))
        
        with col3:
            st.metric("Prazos Urgentes (≤5 dias)", resumo.get('prazos_urgentes', 0))
        
        with col4:
            total_vagas = pd.to_numeric(df['Vagas'], errors='coerce').fillna(0).sum() if 'Vagas' in df.columns else 0
            st.metric("Total de Vagas", int(total_vagas))

    def gerar_resumo(self, df):
        try:
            resumo = {}
            
            # Filtrar cursos não concluídos para os alertas
            df_ativos = df[df['Estado'] != 'Concluído'].copy() if 'Estado' in df.columns else df.copy()
            
            resumo['total_cursos'] = len(df)
            resumo['total_ativos'] = len(df_ativos)
            
            if 'Estado' in df.columns:
                resumo['por_estado'] = df['Estado'].value_counts().to_dict()
            
            if 'Prioridade' in df.columns:
                resumo['por_prioridade'] = df['Prioridade'].value_counts().to_dict()
            
            # Calcular prazos compartilhados (mesma lógica de referência da sidebar)
            metricas_prazos = calcular_metricas_prazos(df)
            resumo['prazos_atrasados'] = metricas_prazos['atrasados']
            resumo['prazos_urgentes'] = metricas_prazos['urgentes']
            resumo['chefia_proximo'] = metricas_prazos['chefia_proximo']
            
            return resumo
        except Exception as e:
            return {"erro": str(e)}

if __name__ == "__main__":
    print("Dashboard module pronto para uso!")
