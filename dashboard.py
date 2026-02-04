import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date

class Dashboard:
    def __init__(self):
        pass
    
    def mostrar_dashboard(self, df):
        if df.empty:
            st.info("Nenhum dado disponível para o dashboard.")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            self._grafico_por_estado(df)
        
        with col2:
            self._grafico_por_prioridade(df)
        
        st.markdown("---")
        
        col3, col4 = st.columns(2)
        
        with col3:
            self._grafico_prazos_proximos(df)
        
        with col4:
            self._grafico_vagas_turma(df)
    
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
            if 'Fim indicação da SIAT' in df.columns:
                df_prazos = df[df['Fim indicação da SIAT'].notna()].copy()
                
                if not df_prazos.empty:
                    hoje = date.today()
                    
                    def calcular_dias(data_str):
                        try:
                            if isinstance(data_str, str):
                                data = datetime.strptime(data_str, "%d/%m/%Y").date()
                            else:
                                data = data_str
                            return (data - hoje).days
                        except:
                            return None
                    
                    df_prazos['dias_restantes'] = df_prazos['Fim indicação da SIAT'].apply(calcular_dias)
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
                df_vagas = df.groupby('Turma')['Vagas'].sum().reset_index()
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
            
            resumo['total_cursos'] = len(df)
            
            if 'Estado' in df.columns:
                resumo['por_estado'] = df['Estado'].value_counts().to_dict()
            
            if 'Prioridade' in df.columns:
                resumo['por_prioridade'] = df['Prioridade'].value_counts().to_dict()
            
            if 'Fim indicação da SIAT' in df.columns:
                hoje = date.today()
                atrasados = 0
                urgentes = 0
                
                for data_str in df['Fim indicação da SIAT'].dropna():
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
                
                resumo['prazos_atrasados'] = atrasados
                resumo['prazos_urgentes'] = urgentes
            
            return resumo
        except Exception as e:
            return {"erro": str(e)}

if __name__ == "__main__":
    print("Dashboard module pronto para uso!")
