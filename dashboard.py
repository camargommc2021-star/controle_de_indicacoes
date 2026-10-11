import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date

from utils.validators import parse_data, calcular_metricas_prazos

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

    
    def _grafico_por_estado(self, df):
        try:
            if 'Estado' in df.columns:
                contagem = df['Estado'].value_counts().reset_index()
                contagem.columns = ['Estado', 'Quantidade']
                
                cores = {
                    'solicitar voluntários': '#FF6B6B',
                    'fazer indicação': '#FFD93D',
                    'Concluído': '#6BCF7F',
                    'ver vagas escalantes': '#4D96FF'
                }
                
                fig = px.bar(
                    contagem, 
                    x='Estado', 
                    y='Quantidade',
                    color='Estado',
                    color_discrete_map=cores,
                    title='Cursos por Estado'
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao gerar gráfico de estados: {str(e)}")
    
    def _grafico_por_prioridade(self, df):
        try:
            if 'Prioridade' in df.columns:
                contagem = df['Prioridade'].value_counts().reset_index()
                contagem.columns = ['Prioridade', 'Quantidade']
                
                cores_prioridade = {
                    'Alta': '#FF6B6B',
                    'Média': '#FFD93D',
                    'Baixa': '#6BCF7F'
                }
                
                fig = px.pie(
                    contagem,
                    values='Quantidade',
                    names='Prioridade',
                    color='Prioridade',
                    color_discrete_map=cores_prioridade,
                    title='Distribuição por Prioridade'
                )
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao gerar gráfico de prioridades: {str(e)}")
    
    def _grafico_prazos_proximos(self, df):
        try:
            if 'Fim da indicação da SIAT' in df.columns:
                df_prazos = df[df['Fim da indicação da SIAT'].notna()].copy()
                
                if not df_prazos.empty:
                    hoje = date.today()
                    
                    def calcular_dias(valor):
                        d = parse_data(valor)
                        if d is not None:
                            return (d - hoje).days
                        return None
                    
                    df_prazos['dias_restantes'] = df_prazos['Fim da indicação da SIAT'].apply(calcular_dias)
                    df_prazos = df_prazos[df_prazos['dias_restantes'].notna()]
                    
                    if not df_prazos.empty:
                        def categorizar_prazo(dias):
                            if dias < 0:
                                return "Atrasado"
                            elif dias <= 5:
                                return "0-5 dias"
                            elif dias <= 15:
                                return "6-15 dias"
                            elif dias <= 30:
                                return "16-30 dias"
                            else:
                                return "+30 dias"
                        
                        df_prazos['categoria'] = df_prazos['dias_restantes'].apply(categorizar_prazo)
                        
                        contagem = df_prazos['categoria'].value_counts().reset_index()
                        contagem.columns = ['Prazo', 'Quantidade']
                        
                        ordem = ["Atrasado", "0-5 dias", "6-15 dias", "16-30 dias", "+30 dias"]
                        contagem['Prazo'] = pd.Categorical(contagem['Prazo'], categories=ordem, ordered=True)
                        contagem = contagem.sort_values('Prazo')
                        
                        cores_prazo = {
                            'Atrasado': '#FF0000',
                            '0-5 dias': '#FFD700',
                            '6-15 dias': '#FFA500',
                            '16-30 dias': '#90EE90',
                            '+30 dias': '#008000'
                        }
                        
                        fig = px.bar(
                            contagem,
                            x='Prazo',
                            y='Quantidade',
                            color='Prazo',
                            color_discrete_map=cores_prazo,
                            title='Prazos de Indicação SIAT'
                        )
                        fig.update_layout(showlegend=False)
                        st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao gerar gráfico de prazos: {str(e)}")
    
    def _grafico_vagas_turma(self, df):
        try:
            if 'Turma' in df.columns and 'Vagas' in df.columns:
                df_copy = df.copy()
                df_copy['Vagas'] = pd.to_numeric(df_copy['Vagas'], errors='coerce').fillna(0)
                df_vagas = df_copy.groupby('Turma')['Vagas'].sum().reset_index()
                df_vagas = df_vagas.sort_values('Vagas', ascending=True).tail(10)
                
                if not df_vagas.empty:
                    fig = px.bar(
                        df_vagas,
                        x='Vagas',
                        y='Turma',
                        orientation='h',
                        title='Top 10 Turmas por Número de Vagas',
                        color='Vagas',
                        color_continuous_scale='Blues'
                    )
                    st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao gerar gráfico de vagas: {str(e)}")
    
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
