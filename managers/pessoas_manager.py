"""
Gerenciador de dados de pessoas/militares para preenchimento de FIC.

Adaptado para ler a planilha de pessoas com estrutura:
N, SARAM, GRAD, ESP, NOME COMPLETO, NOME DE GUERRA, GRAD + NDG, 
NASCIMENTO, PRAÇA, ULT PROM, CPF, RA, SEÇÃO, HAB 1, 
EMAIL INTERNO, EMAIL EXTERNO, TELEFONE
"""

import pandas as pd
import os
from typing import Optional, List, Dict, Any


class PessoasManager:
    """
    Gerenciador de dados de pessoas/militares.
    Lê dados da planilha pessoas.xlsx com estrutura específica.
    """
    
    def __init__(self, arquivo_excel: str = "data/pessoas.xlsx"):
        """
        Inicializa o gerenciador de pessoas.
        
        Args:
            arquivo_excel: Caminho para o arquivo Excel de pessoas
        """
        self.arquivo_local = arquivo_excel
        
        # Mapeamento de colunas do arquivo para nomes padronizados
        self.mapeamento_colunas = {
            'N': 'Numero',
            'SARAM': 'SARAM',
            'GRAD': 'Posto_Graduacao',
            'ESP': 'Especialidade',
            'NOME COMPLETO': 'Nome_Completo',
            'NOME DE GUERRA': 'Nome_Guerra',
            'GRAD + NDG': 'Grad_NDG',
            'NASCIMENTO\n': 'Nascimento',
            'PRA�A': 'Praca',
            'ULT PROM': 'Data_Ultima_Promocao',
            'CPF': 'CPF',
            'RA': 'RA',
            'SE��O': 'Secao',  # OM/Seção
            'HAB 1': 'Habilitacao',
            'EMAIL INTERNO': 'Email_Interno',
            'EMAIL EXTERNO': 'Email',
            'TELEFONE': 'Telefone'
        }
    
    def carregar_pessoas(self) -> pd.DataFrame:
        """
        Carrega todas as pessoas do arquivo Excel.
        
        Returns:
            DataFrame com todas as pessoas cadastradas
        """
        try:
            if os.path.exists(self.arquivo_local):
                # Ler o arquivo Excel
                df = pd.read_excel(self.arquivo_local, engine='openpyxl')
                
                # Renomear colunas para padronização
                df_renomeado = df.rename(columns=self.mapeamento_colunas)
                
                # Adicionar coluna OM_Indicado baseada na Seção
                if 'Secao' in df_renomeado.columns:
                    df_renomeado['OM_Indicado'] = df_renomeado['Secao']
                
                # Adicionar coluna Funcao_Atual vazia (não existe no arquivo original)
                df_renomeado['Funcao_Atual'] = ''
                
                # Adicionar coluna Tempo_Servico vazia
                df_renomeado['Tempo_Servico'] = ''
                
                return df_renomeado
            else:
                return pd.DataFrame()
        except Exception as e:
            print(f"Erro ao carregar pessoas: {e}")
            return pd.DataFrame()
    
    def listar_todas(self) -> pd.DataFrame:
        """
        Retorna todas as pessoas cadastradas.
        
        Returns:
            DataFrame com todas as pessoas
        """
        return self.carregar_pessoas()
    
    def buscar_por_nome(self, nome: str) -> pd.DataFrame:
        """
        Busca pessoas por nome (busca parcial, case insensitive).
        
        Args:
            nome: Termo de busca para o nome
            
        Returns:
            DataFrame com as pessoas encontradas
        """
        df = self.carregar_pessoas()
        
        if not nome or df.empty:
            return df
        
        try:
            # Busca case insensitive e parcial
            mask = df['Nome_Completo'].astype(str).str.contains(
                nome, case=False, na=False, regex=False
            )
            return df[mask]
        except Exception as e:
            print(f"Erro na busca: {e}")
            return pd.DataFrame()
    
    def buscar_pessoa_exata(self, nome: str) -> Optional[Dict[str, Any]]:
        """
        Busca uma pessoa pelo nome exato.
        
        Args:
            nome: Nome completo da pessoa
            
        Returns:
            Dicionário com os dados da pessoa ou None se não encontrada
        """
        df = self.carregar_pessoas()
        
        if not nome or df.empty:
            return None
        
        try:
            resultado = df[df['Nome_Completo'].astype(str).str.strip().str.upper() == nome.strip().upper()]
            
            if not resultado.empty:
                return resultado.iloc[0].to_dict()
            return None
        except Exception as e:
            print(f"Erro na busca exata: {e}")
            return None
    
    def buscar_por_cpf(self, cpf: str) -> Optional[Dict[str, Any]]:
        """
        Busca uma pessoa pelo CPF.
        
        Args:
            cpf: Número do CPF
            
        Returns:
            Dicionário com os dados da pessoa ou None se não encontrada
        """
        df = self.carregar_pessoas()
        
        if not cpf or df.empty:
            return None
        
        try:
            # Remover formatação do CPF para comparação
            cpf_limpo = cpf.replace('.', '').replace('-', '').strip()
            df['CPF_LIMPO'] = df['CPF'].astype(str).str.replace('.', '').str.replace('-', '').str.strip()
            
            resultado = df[df['CPF_LIMPO'] == cpf_limpo]
            
            if not resultado.empty:
                pessoa = resultado.iloc[0].to_dict()
                pessoa.pop('CPF_LIMPO', None)
                return pessoa
            return None
        except Exception as e:
            print(f"Erro na busca por CPF: {e}")
            return None
    
    def buscar_por_saram(self, saram: str) -> Optional[Dict[str, Any]]:
        """
        Busca uma pessoa pelo SARAM.
        
        Args:
            saram: Número do SARAM
            
        Returns:
            Dicionário com os dados da pessoa ou None se não encontrada
        """
        df = self.carregar_pessoas()
        
        if not saram or df.empty:
            return None
        
        try:
            resultado = df[df['SARAM'].astype(str).str.strip() == saram.strip()]
            
            if not resultado.empty:
                return resultado.iloc[0].to_dict()
            return None
        except Exception as e:
            print(f"Erro na busca por SARAM: {e}")
            return None
    
    def obter_sugestoes_nomes(self, termo: str = "", limite: int = 20) -> List[str]:
        """
        Retorna sugestões de nomes para autocomplete.
        
        Args:
            termo: Termo de busca (opcional, retorna todos se vazio)
            limite: Número máximo de sugestões
            
        Returns:
            Lista de nomes sugeridos
        """
        df = self.carregar_pessoas()
        
        if df.empty:
            return []
        
        try:
            if termo:
                # Filtrar por termo
                mask = df['Nome_Completo'].astype(str).str.contains(
                    termo, case=False, na=False, regex=False
                )
                df_filtrado = df[mask]
            else:
                df_filtrado = df
            
            # Retornar lista de nomes
            nomes = df_filtrado['Nome_Completo'].dropna().astype(str).tolist()
            return nomes[:limite]
        except Exception as e:
            print(f"Erro ao obter sugestões: {e}")
            return []
    
    def obter_nomes_formatados(self) -> List[str]:
        """
        Retorna lista de nomes formatados com posto/graduação para exibição.
        
        Returns:
            Lista de strings no formato "Posto - Nome"
        """
        df = self.carregar_pessoas()
        
        if df.empty:
            return []
        
        try:
            nomes_formatados = []
            for _, row in df.iterrows():
                nome = str(row.get('Nome_Completo', '')).strip()
                posto = str(row.get('Posto_Graduacao', '')).strip()
                
                if nome:
                    if posto:
                        nomes_formatados.append(f"{posto} {nome}")
                    else:
                        nomes_formatados.append(nome)
            
            return nomes_formatados
        except Exception as e:
            print(f"Erro ao obter nomes formatados: {e}")
            return []


if __name__ == "__main__":
    # Teste do módulo
    pm = PessoasManager()
    print("PessoasManager inicializado com sucesso!")
    df = pm.listar_todas()
    print(f"Total de pessoas: {len(df)}")
    
    if not df.empty:
        print("\n=== PRIMEIRAS 5 PESSOAS ===")
        for idx in range(min(5, len(df))):
            row = df.iloc[idx]
            print(f"{idx+1}: {row.get('Posto_Graduacao', '')} {row.get('Nome_Completo', '')}")
