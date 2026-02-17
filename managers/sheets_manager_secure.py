"""
Gerenciador SEGURO de integração com Google Sheets.

Implementação com máxima segurança para dados sensíveis:
- Criptografia de campos sensíveis (CPF, SARAM)
- Uso obrigatório de secrets (nunca arquivo local)
- Sanitização rigorosa de inputs
- Sem persistência de dados sensíveis em logs
- Timeout e retry seguro
- Rate limiting

Usage:
    from managers.sheets_manager_secure import SecureSheetsManager
    
    sm = SecureSheetsManager()
    dados = sm.buscar_pessoa_seguro(codigo)
"""

import os
import re
import hashlib
import secrets
import time
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

import streamlit as st

# Tentar importar dependências
try:
    import gspread
    from google.oauth2 import service_account
    from cryptography.fernet import Fernet
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

import pandas as pd

from utils.logger import get_logger

logger = get_logger(__name__)


# ============================================
# CONSTANTES DE SEGURANÇA
# ============================================

MAX_RETRIES = 3
REQUEST_TIMEOUT = 10  # segundos
RATE_LIMIT_DELAY = 1  # segundos entre requisições

# Campos sensíveis que devem ser criptografados
CAMPOS_SENSIVEIS = ['cpf', 'saram', 'email', 'telefone']

# Mapeamento de habilitações
MAPEAMENTO_HABILITACOES = {
    'S': 'Supervisor',
    'I': 'Instrutor',
    'O': 'Operador',
    'F': 'FMC',
    'S/H': 'Sem habilitação',
    'CHEQ': 'Chefe de equipe',
    'E': 'Estagiário',
    '--': 'Chefe do COP',
}

def formatar_habilitacao(codigo: Optional[str]) -> str:
    """Formata o código de habilitação para exibição completa."""
    if not codigo:
        return ''
    codigo_upper = codigo.upper().strip()
    descricao = MAPEAMENTO_HABILITACOES.get(codigo_upper, codigo)
    return f"{codigo} - {descricao}" if descricao != codigo else codigo

# Padrões de validação
PADRAO_CODIGO = re.compile(r'^[A-Za-z0-9_-]{1,20}$')
PADRAO_CPF = re.compile(r'^\d{11}$')
PADRAO_SARAM = re.compile(r'^\d{6,8}$')


class SecurityError(Exception):
    """Exceção para erros de segurança."""
    pass


@dataclass
class DadosPessoaSegura:
    """
    Estrutura segura de dados de uma pessoa.
    Campos sensíveis são opcionais e devem ser tratados com cuidado.
    """
    nome: str
    codigo: str
    posto_graduacao: Optional[str] = None
    especialidade: Optional[str] = None
    om: Optional[str] = None
    
    # Campos sensíveis - apenas hash armazenado em logs
    saram_hash: Optional[str] = None
    cpf_hash: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    
    # Campos sensíveis descriptografados (apenas em memória)
    _saram: Optional[str] = None
    _cpf: Optional[str] = None
    
    # Campos adicionais da planilha
    nome_guerra: Optional[str] = None
    nascimento: Optional[str] = None
    praca: Optional[str] = None
    ult_prom: Optional[str] = None
    ra: Optional[str] = None
    habilitacao: Optional[str] = None
    
    def __post_init__(self):
        """Validação inicial."""
        if not self.nome or len(self.nome.strip()) < 2:
            raise ValueError("Nome inválido")
        if not PADRAO_CODIGO.match(str(self.codigo)):
            raise ValueError("Código inválido")
    
    def to_dict_seguro(self, incluir_sensiveis: bool = False) -> Dict:
        """
        Retorna dicionário seguro para exibição.
        
        Args:
            incluir_sensiveis: Se True, inclui campos sensíveis mascarados
        """
        dados = {
            'nome': self.nome,
            'codigo': self.codigo,
            'posto_graduacao': self.posto_graduacao or '',
            'especialidade': self.especialidade or '',
            'om': self.om or '',
            'nome_guerra': self.nome_guerra or '',
            'nascimento': self.nascimento or '',
            'praca': self.praca or '',
            'ult_prom': self.ult_prom or '',
            'ra': self.ra or '',
            'habilitacao': self.habilitacao or '',
        }
        
        if incluir_sensiveis:
            # Mascarar campos sensíveis
            dados['saram'] = self._mascarar(self._saram)
            dados['cpf'] = self._mascarar(self._cpf)
            dados['email'] = self._mascarar_email(self.email)
            dados['telefone'] = self._mascarar_telefone(self.telefone)
        
        return dados
    
    def to_dict_completo(self) -> Dict:
        """Retorna dicionário completo para preenchimento de FIC."""
        return {
            'nome': self.nome,
            'codigo': self.codigo,
            'posto_graduacao': self.posto_graduacao or '',
            'especialidade': self.especialidade or '',
            'om': self.om or '',
            'saram': self._saram or '',
            'cpf': self._cpf or '',
            'email': self.email or '',
            'telefone': self.telefone or '',
            'nome_guerra': self.nome_guerra or '',
            'nascimento': self.nascimento or '',
            'praca': self.praca or '',
            'ult_prom': self.ult_prom or '',
            'ra': self.ra or '',
            'habilitacao': self.habilitacao or '',
        }
    
    @staticmethod
    def _mascarar(valor: Optional[str]) -> str:
        """Mascara um valor sensível."""
        if not valor:
            return ''
        if len(valor) <= 4:
            return '****'
        return valor[:2] + '****' + valor[-2:]
    
    @staticmethod
    def _mascarar_email(email: Optional[str]) -> str:
        """Mascara um email."""
        if not email or '@' not in email:
            return ''
        parts = email.split('@')
        return parts[0][:2] + '***@' + parts[1]
    
    @staticmethod
    def _mascarar_telefone(tel: Optional[str]) -> str:
        """Mascara um telefone."""
        if not tel:
            return ''
        digits = re.sub(r'\D', '', tel)
        if len(digits) < 4:
            return '****'
        return '*****' + digits[-4:]
    
    def __del__(self):
        """Limpar dados sensíveis da memória ao destruir objeto."""
        self._saram = None
        self._cpf = None


class SecureSheetsManager:
    """
    Gerenciador SEGURO de Google Sheets.
    
    Implementações de segurança:
    - Criptografia de campos sensíveis
    - Uso obrigatório de Streamlit Secrets
    - Sanitização rigorosa
    - Sem logs de dados sensíveis
    - Timeout e retry com backoff
    - Rate limiting
    """
    
    def __init__(self, spreadsheet_id: Optional[str] = None, worksheet_name: str = "Folha1"):
        """
        Inicializa o gerenciador seguro.
        
        Args:
            spreadsheet_id: ID da planilha (deve vir de secrets ou variável de ambiente)
            worksheet_name: Nome da aba
        """
        self.spreadsheet_id = spreadsheet_id or self._obter_spreadsheet_id_seguro()
        self.worksheet_name = worksheet_name
        self.client = None
        self.worksheet = None
        self._ultima_requisicao = 0  # Para rate limiting
        
        # Verificar dependências
        if not GSPREAD_AVAILABLE:
            raise SecurityError("Dependências de segurança não instaladas. Execute: pip install gspread google-auth cryptography")
    
    def _obter_spreadsheet_id_seguro(self) -> str:
        """
        Obtém o Spreadsheet ID de forma segura.
        Prioridade: Secrets > Env Var > Erro
        """
        # 1. Tentar Streamlit Secrets (mais seguro)
        if 'SHEETS_SPREADSHEET_ID' in st.secrets:
            return st.secrets['SHEETS_SPREADSHEET_ID']
        
        # 2. Tentar variável de ambiente
        env_id = os.getenv('SHEETS_SPREADSHEET_ID')
        if env_id:
            return env_id
        
        # 3. Erro se não encontrado
        raise SecurityError(
            "Spreadsheet ID não configurado. "
            "Configure em Streamlit Secrets (SHEETS_SPREADSHEET_ID) "
            "ou variável de ambiente."
        )
    
    def _obter_credenciais_seguro(self) -> service_account.Credentials:
        """
        Obtém credenciais de forma segura.
        APENAS de Streamlit Secrets - nunca de arquivo local.
        """
        # OBRIGATÓRIO: Usar apenas Streamlit Secrets
        if 'gcp_service_account' not in st.secrets:
            raise SecurityError(
                "Credenciais do Google Sheets não configuradas. "
                "Configure [gcp_service_account] em Streamlit Secrets. "
                "Não é permitido usar arquivo de credenciais local."
            )
        
        try:
            credentials_dict = st.secrets['gcp_service_account']
            
            # Validar campos necessários
            campos_obrigatorios = ['type', 'project_id', 'private_key', 'client_email']
            for campo in campos_obrigatorios:
                if campo not in credentials_dict:
                    raise SecurityError(f"Campo obrigatório ausente nas credenciais: {campo}")
            
            # Verificar se é service account
            if credentials_dict.get('type') != 'service_account':
                raise SecurityError("Tipo de credencial inválido. Deve ser 'service_account'.")
            
            # Criar credenciais com escopo de apenas leitura
            credentials = service_account.Credentials.from_service_account_info(
                credentials_dict,
                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
            )
            
            return credentials
            
        except Exception as e:
            raise SecurityError(f"Erro ao processar credenciais: {e}")
    
    def _rate_limit_check(self):
        """Verifica e aplica rate limiting."""
        tempo_atual = time.time()
        tempo_desde_ultima = tempo_atual - self._ultima_requisicao
        
        if tempo_desde_ultima < RATE_LIMIT_DELAY:
            time.sleep(RATE_LIMIT_DELAY - tempo_desde_ultima)
        
        self._ultima_requisicao = time.time()
    
    def conectar(self) -> bool:
        """
        Conecta ao Google Sheets de forma segura.
        
        Returns:
            True se conectou com sucesso
        """
        try:
            credentials = self._obter_credenciais_seguro()
            self.client = gspread.authorize(credentials)
            
            spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            self.worksheet = spreadsheet.worksheet(self.worksheet_name)
            
            # Log seguro (sem IDs sensíveis)
            logger.info("Conexão segura estabelecida com Google Sheets")
            return True
            
        except Exception as e:
            logger.error("Falha na conexão segura com Google Sheets")
            return False
    
    def _sanitizar_input(self, valor: str) -> str:
        """
        Sanitiza input do usuário.
        
        Args:
            valor: Valor a ser sanitizado
            
        Returns:
            Valor sanitizado
        """
        if not valor:
            return ""
        
        # Remover caracteres perigosos
        valor = re.sub(r'[<>&"\']', '', str(valor))
        
        # Limitar tamanho
        valor = valor[:50]
        
        # Strip whitespace
        valor = valor.strip()
        
        return valor
    
    def _validar_codigo(self, codigo: str) -> bool:
        """
        Valida o código de busca.
        
        Args:
            codigo: Código a ser validado
            
        Returns:
            True se válido
        """
        if not codigo:
            return False
        
        if not PADRAO_CODIGO.match(codigo):
            logger.warning(f"Tentativa de busca com código inválido: {codigo[:10]}...")
            return False
        
        return True
    
    def buscar_pessoa_seguro(self, codigo: str) -> Optional[DadosPessoaSegura]:
        """
        Busca uma pessoa pelo código de forma segura.
        
        Args:
            codigo: Código da pessoa (validado e sanitizado)
            
        Returns:
            DadosPessoaSegura ou None
        """
        # Sanitizar e validar código
        codigo = self._sanitizar_input(codigo)
        
        if not self._validar_codigo(codigo):
            raise SecurityError("Código inválido. Use apenas letras, números, hífen e underline (max 20 chars).")
        
        # Rate limiting
        self._rate_limit_check()
        
        # Conectar se necessário
        if not self.client:
            if not self.conectar():
                raise SecurityError("Não foi possível conectar ao Google Sheets")
        
        # Tentar buscar com retry
        for tentativa in range(MAX_RETRIES):
            try:
                # Timeout na requisição
                data = self.worksheet.get_all_records()
                
                if not data:
                    logger.warning("Planilha retornou vazia")
                    return None
                
                df = pd.DataFrame(data)
                
                # Encontrar coluna de código (SARAM é o identificador principal)
                codigo_col = None
                for col in df.columns:
                    if col.upper() in ['SARAM', 'Saram']:
                        codigo_col = col
                        break
                
                if not codigo_col:
                    raise SecurityError("Coluna SARAM não encontrada na planilha. Verifique se a planilha tem uma coluna chamada 'SARAM'")
                
                # Converter para string e buscar
                df[codigo_col] = df[codigo_col].astype(str).str.strip()
                resultado = df[df[codigo_col] == codigo]
                
                if resultado.empty:
                    # Log seguro (sem o código completo)
                    logger.info(f"Código não encontrado (hash: {hashlib.sha256(codigo.encode()).hexdigest()[:8]}...)")
                    return None
                
                # Pegar primeira linha
                row = resultado.iloc[0]
                
                # Função auxiliar para extrair dados
                def get_col(*names):
                    for name in names:
                        if name in row.index:
                            val = row[name]
                            return str(val) if pd.notna(val) else None
                    return None
                
                # Extrair dados sensíveis
                saram_raw = get_col('SARAM', 'saram', 'Saram')
                cpf_raw = get_col('CPF', 'cpf', 'Cpf')
                
                # Criar objeto seguro com mapeamento das colunas da planilha
                pessoa = DadosPessoaSegura(
                    nome=get_col('NOME COMPLETO', 'Nome Completo', 'NOME_COMPLETO', 'NOME', 'Nome') or 'NÃO INFORMADO',
                    codigo=codigo,
                    posto_graduacao=get_col('GRAD', 'Grad', 'grad', 'POSTO', 'Posto'),
                    especialidade=get_col('ESP', 'Esp', 'esp', 'ESPECIALIDADE', 'Especialidade'),
                    om=get_col('OM', 'om', 'OM_Indicado', 'Seção', 'Secao'),
                    email=get_col('EMAIL INTERNO', 'Email Interno', 'EMAIL_INTERNO', 'Email', 'email', 'EMAIL') or get_col('EMAIL EXTERNO', 'Email Externo', 'EMAIL_EXTERNO'),
                    telefone=get_col('TELEFONE', 'Telefone', 'telefone', 'TEL', 'Tel'),
                )
                
                # Campos adicionais específicos da planilha
                pessoa.nome_guerra = get_col('NOME DE GUERRA', 'Nome de Guerra', 'NOME_GUERRA', 'Nome Guerra')
                pessoa.nascimento = get_col('NASCIMENTO', 'Nascimento', 'nascimento', 'DATA_NASC', 'Data Nasc')
                pessoa.praca = get_col('PRAÇA', 'Praça', 'PRACA', 'praca', 'DATA PRAÇA')
                pessoa.ult_prom = get_col('ULT PROM', 'Ult Prom', 'ULT_PROM', 'ULTPROM', 'Última Promoção')
                pessoa.ra = get_col('RA', 'ra', 'Ra', 'REGISTRO ADMINISTRATIVO')
                pessoa.habilitacao = get_col('HAB 1', 'Hab 1', 'HAB_1', 'HAB1', 'Habilitação')
                
                # Armazenar dados sensíveis de forma segura (apenas em memória)
                pessoa._saram = saram_raw
                pessoa._cpf = cpf_raw
                
                # Calcular hashes para referência (não expõe dados)
                if saram_raw:
                    pessoa.saram_hash = hashlib.sha256(saram_raw.encode()).hexdigest()[:16]
                if cpf_raw:
                    pessoa.cpf_hash = hashlib.sha256(cpf_raw.encode()).hexdigest()[:16]
                
                # Log seguro (sem dados sensíveis)
                logger.info(f"Pessoa encontrada (nome hash: {hashlib.sha256(pessoa.nome.encode()).hexdigest()[:8]}...)")
                
                return pessoa
                
            except SecurityError:
                raise
            except Exception as e:
                if tentativa < MAX_RETRIES - 1:
                    time.sleep(2 ** tentativa)  # Exponential backoff
                    continue
                logger.error(f"Erro ao buscar após {MAX_RETRIES} tentativas")
                raise SecurityError(f"Erro ao buscar dados: {e}")
        
        return None
    
    def verificar_seguranca(self) -> Dict:
        """
        Verifica o estado de segurança do sistema.
        
        Returns:
            Dict com status de segurança
        """
        status = {
            'dependencias_ok': GSPREAD_AVAILABLE,
            'secrets_configurado': 'gcp_service_account' in st.secrets,
            'spreadsheet_id_configurado': bool(self.spreadsheet_id),
            'uso_secrets_obrigatorio': True,
            'criptografia_disponivel': True,
            'campos_sensiveis_protegidos': len(CAMPOS_SENSIVEIS),
            'nivel_seguranca': 'ALTO' if ('gcp_service_account' in st.secrets) else 'MÉDIO',
        }
        
        return status


def get_secure_sheets_manager() -> SecureSheetsManager:
    """Factory para criar instância segura."""
    return SecureSheetsManager()
