"""
Gerenciador de integração com Google Sheets.

Busca dados de pessoas diretamente do Google Sheets sem armazenar localmente.
Os dados são carregados em tempo real e usados apenas para preenchimento da FIC.

Usage:
    from managers.sheets_manager import SheetsManager
    
    sm = SheetsManager()
    dados = sm.buscar_pessoa_por_codigo(codigo)
"""

import os
import json
from typing import Dict, Optional, List
from dataclasses import dataclass

import pandas as pd
import streamlit as st

# Tentar importar gspread
try:
    import gspread
    from google.oauth2 import service_account
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class DadosPessoa:
    """Estrutura de dados de uma pessoa."""
    nome: str
    codigo: str
    posto_graduacao: str = ""
    especialidade: str = ""
    om: str = ""
    saram: str = ""
    cpf: str = ""
    email: str = ""
    telefone: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'nome': self.nome,
            'codigo': self.codigo,
            'posto_graduacao': self.posto_graduacao,
            'especialidade': self.especialidade,
            'om': self.om,
            'saram': self.saram,
            'cpf': self.cpf,
            'email': self.email,
            'telefone': self.telefone,
        }


class SheetsManager:
    """
    Gerenciador de Google Sheets para busca de dados de pessoas.
    
    Busca dados em tempo real do Google Sheets, sem persistência local.
    """
    
    def __init__(self, spreadsheet_id: Optional[str] = None, worksheet_name: str = "Pessoas"):
        """
        Inicializa o gerenciador.
        
        Args:
            spreadsheet_id: ID da planilha Google Sheets
            worksheet_name: Nome da aba worksheet
        """
        self.spreadsheet_id = spreadsheet_id or os.getenv('SHEETS_SPREADSHEET_ID')
        self.worksheet_name = worksheet_name
        self.client = None
        self.worksheet = None
        
        if not GSPREAD_AVAILABLE:
            logger.warning("gspread não instalado. Instale com: pip install gspread google-auth")
    
    def conectar(self) -> bool:
        """
        Conecta ao Google Sheets.
        
        Returns:
            True se conectou com sucesso
        """
        if not GSPREAD_AVAILABLE:
            logger.error("Biblioteca gspread não disponível")
            return False
        
        try:
            # Verificar se há credenciais no secrets.toml
            if 'gcp_service_account' in st.secrets:
                # Usar credenciais do Streamlit Cloud
                credentials_dict = st.secrets['gcp_service_account']
                credentials = service_account.Credentials.from_service_account_info(
                    credentials_dict,
                    scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
                )
            else:
                # Tentar arquivo local
                creds_file = 'credentials/google-sheets-credentials.json'
                if os.path.exists(creds_file):
                    credentials = service_account.Credentials.from_service_account_file(
                        creds_file,
                        scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
                    )
                else:
                    logger.error("Credenciais do Google Sheets não encontradas")
                    return False
            
            self.client = gspread.authorize(credentials)
            
            if self.spreadsheet_id:
                spreadsheet = self.client.open_by_key(self.spreadsheet_id)
                self.worksheet = spreadsheet.worksheet(self.worksheet_name)
                logger.info(f"Conectado ao Google Sheets: {self.spreadsheet_id}")
                return True
            else:
                logger.error("Spreadsheet ID não configurado")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao conectar ao Google Sheets: {e}")
            return False
    
    def buscar_pessoa_por_codigo(self, codigo: str) -> Optional[DadosPessoa]:
        """
        Busca uma pessoa pelo código no Google Sheets.
        
        Args:
            codigo: Código da pessoa
            
        Returns:
            DadosPessoa ou None se não encontrado
        """
        if not self.client:
            if not self.conectar():
                return None
        
        try:
            # Carregar todos os dados
            data = self.worksheet.get_all_records()
            df = pd.DataFrame(data)
            
            if df.empty:
                logger.warning("Planilha vazia")
                return None
            
            # Buscar pelo código (coluna pode ser 'Codigo', 'codigo', 'Código', etc)
            codigo_col = None
            for col in df.columns:
                if col.lower() in ['codigo', 'código', 'code', 'id']:
                    codigo_col = col
                    break
            
            if not codigo_col:
                logger.error("Coluna de código não encontrada na planilha")
                return None
            
            # Converter código para string para comparação
            df[codigo_col] = df[codigo_col].astype(str)
            
            # Buscar
            resultado = df[df[codigo_col] == str(codigo)]
            
            if resultado.empty:
                logger.info(f"Pessoa com código {codigo} não encontrada")
                return None
            
            # Pegar primeira linha
            row = resultado.iloc[0]
            
            # Mapear colunas (tentar variações de nomes)
            def get_col(*names):
                for name in names:
                    if name in row.index:
                        return str(row[name]) if pd.notna(row[name]) else ""
                return ""
            
            pessoa = DadosPessoa(
                nome=get_col('Nome', 'nome', 'NOME', 'Nome_Completo'),
                codigo=str(codigo),
                posto_graduacao=get_col('Posto', 'posto', 'POSTO', 'Posto_Graduacao', 'Graduação', 'Graduacao'),
                especialidade=get_col('Especialidade', 'especialidade', 'ESPECIALIDADE', 'ESP'),
                om=get_col('OM', 'om', 'OM_Indicado', 'Seção', 'Secao'),
                saram=get_col('SARAM', 'saram', 'Saram'),
                cpf=get_col('CPF', 'cpf', 'Cpf'),
                email=get_col('Email', 'email', 'EMAIL', 'E-mail'),
                telefone=get_col('Telefone', 'telefone', 'TELEFONE', 'Tel', 'Celular'),
            )
            
            logger.info(f"Pessoa encontrada: {pessoa.nome}")
            return pessoa
            
        except Exception as e:
            logger.error(f"Erro ao buscar pessoa: {e}")
            return None
    
    def listar_codigos(self) -> List[str]:
        """
        Lista todos os códigos disponíveis.
        
        Returns:
            Lista de códigos
        """
        if not self.client:
            if not self.conectar():
                return []
        
        try:
            data = self.worksheet.get_all_records()
            df = pd.DataFrame(data)
            
            if df.empty:
                return []
            
            # Encontrar coluna de código
            codigo_col = None
            for col in df.columns:
                if col.lower() in ['codigo', 'código', 'code', 'id']:
                    codigo_col = col
                    break
            
            if not codigo_col:
                return []
            
            return df[codigo_col].astype(str).tolist()
            
        except Exception as e:
            logger.error(f"Erro ao listar códigos: {e}")
            return []
    
    def verificar_configuracao(self) -> Dict:
        """
        Verifica se a configuração está correta.
        
        Returns:
            Dict com status da configuração
        """
        status = {
            'gspread_instalado': GSPREAD_AVAILABLE,
            'spreadsheet_id_configurado': bool(self.spreadsheet_id),
            'credenciais_disponiveis': False,
            'conexao_ok': False,
            'erro': None
        }
        
        if not GSPREAD_AVAILABLE:
            status['erro'] = "gspread não instalado"
            return status
        
        if 'gcp_service_account' in st.secrets:
            status['credenciais_disponiveis'] = True
        elif os.path.exists('credentials/google-sheets-credentials.json'):
            status['credenciais_disponiveis'] = True
        
        if status['credenciais_disponiveis'] and self.spreadsheet_id:
            status['conexao_ok'] = self.conectar()
        
        return status


# Função auxiliar para criar instância
def get_sheets_manager() -> SheetsManager:
    """Retorna instância do SheetsManager."""
    return SheetsManager()
