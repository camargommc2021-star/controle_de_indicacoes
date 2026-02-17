"""
Gerenciador Seguro de Pessoas com Criptografia e Auditoria.

Este módulo gerencia os dados de pessoas com segurança reforçada,
incluindo criptografia de dados sensíveis (CPF e SARAM),
sanitização de entradas e logs de auditoria.
"""

import os
import re
import json
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict

import pandas as pd
from cryptography.fernet import Fernet


# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
KEY_FILE = BASE_DIR / ".key"

ARQUIVO_PESSOAS = DATA_DIR / "pessoas.xlsx"
ARQUIVO_AUDIT_LOG = LOGS_DIR / "pessoas_audit.log"

# Mapeamento de campos da planilha para FIC
MAPEAMENTO_CAMPOS = {
    "N": "Numero",
    "SARAM": "SARAM",
    "GRAD": "Posto_Graduacao",
    "ESP": "Especialidade",
    "NOME COMPLETO": "Nome_Completo",
    "NOME DE GUERRA": "Nome_Guerra",
    "NASCIMENTO\n": "Data_Nascimento",
    "PRAÇA": "Data_Praca",
    "ULT PROM": "Data_Ultima_Promocao",
    "CPF": "CPF",
    "RA": "RA",
    "SEÇÃO": "OM_Indicado",
    "HAB 1": "Habilitacao",
    "EMAIL INTERNO": "Email_Interno",
    "EMAIL EXTERNO": "Email",
    "TELEFONE": "Telefone",
}

# Campos que devem ser criptografados
CAMPOS_CRIPTOGRAFAR = ["CPF", "SARAM"]

# Padrões de validação
PADRAO_CPF = re.compile(r"^\d{11}$")
PADRAO_SARAM = re.compile(r"^\d{7}$")
PADRAO_EMAIL = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
PADRAO_CARACTERES_PERIGOSOS = re.compile(r"[<>\"'%;()&+\\]|--|/\*|\*/")


# ============================================================================
# LOGGER DE AUDITORIA
# ============================================================================

def configurar_logger_auditoria() -> logging.Logger:
    """
    Configura o logger de auditoria.
    
    Returns:
        Logger configurado para auditoria.
    """
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger("pessoas_audit")
    logger.setLevel(logging.INFO)
    
    # Evitar handlers duplicados
    if not logger.handlers:
        handler = logging.FileHandler(ARQUIVO_AUDIT_LOG, encoding="utf-8")
        handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


# Logger global de auditoria
audit_logger = configurar_logger_auditoria()


def log_operacao(operacao: str, detalhes: str, usuario: str = "sistema") -> None:
    """
    Registra uma operação no log de auditoria.
    
    Args:
        operacao: Tipo da operação (busca, acesso, etc.)
        detalhes: Detalhes da operação
        usuario: Identificador do usuário (padrão: "sistema")
    """
    mensagem = f"[{usuario}] {operacao.upper()} | {detalhes}"
    audit_logger.info(mensagem)


# ============================================================================
# GERENCIADOR DE CRIPTOGRAFIA
# ============================================================================

class CriptografiaManager:
    """
    Gerenciador de criptografia usando Fernet.
    
    Responsável por criptografar e descriptografar dados sensíveis,
    gerenciando a chave de criptografia de forma segura.
    """
    
    def __init__(self, key_file: Path = KEY_FILE):
        """
        Inicializa o gerenciador de criptografia.
        
        Args:
            key_file: Caminho para o arquivo de chave.
        """
        self.key_file = key_file
        self._cipher = None
        self._inicializar_chave()
    
    def _inicializar_chave(self) -> None:
        """Inicializa ou carrega a chave de criptografia."""
        if self.key_file.exists():
            with open(self.key_file, "rb") as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            self.key_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.key_file, "wb") as f:
                f.write(key)
            audit_logger.info(f"Nova chave de criptografia gerada: {self.key_file}")
        
        self._cipher = Fernet(key)
    
    def criptografar(self, valor: str) -> str:
        """
        Criptografa um valor string.
        
        Args:
            valor: Valor a ser criptografado.
            
        Returns:
            Valor criptografado em base64.
        """
        if not valor or pd.isna(valor):
            return ""
        valor_str = str(valor).strip()
        if not valor_str:
            return ""
        return self._cipher.encrypt(valor_str.encode()).decode()
    
    def _parece_criptografado(self, valor: str) -> bool:
        """
        Verifica se um valor parece estar criptografado (formato Fernet).
        
        Args:
            valor: Valor a verificar.
            
        Returns:
            True se parece criptografado, False caso contrário.
        """
        if not valor:
            return False
        # Tokens Fernet têm caracteres específicos e terminam com '='
        # e são bem maiores que o texto original
        return (
            isinstance(valor, str) and
            len(valor) > 50 and
            valor.startswith("gAAAA") and
            "=" in valor[-10:]
        )
    
    def descriptografar(self, valor_criptografado: str) -> str:
        """
        Descriptografa um valor. Se não parecer criptografado, retorna o valor original.
        
        Args:
            valor_criptografado: Valor criptografado em base64 ou texto plano.
            
        Returns:
            Valor original descriptografado ou o próprio valor se não estiver criptografado.
        """
        if not valor_criptografado or pd.isna(valor_criptografado):
            return ""
        
        valor_str = str(valor_criptografado).strip()
        
        # Se não parece criptografado, retorna o valor original
        if not self._parece_criptografado(valor_str):
            return valor_str
        
        try:
            return self._cipher.decrypt(valor_str.encode()).decode()
        except Exception as e:
            audit_logger.warning(f"Erro ao descriptografar valor, retornando original: {str(e)}")
            return valor_str


# Instância global do gerenciador de criptografia
_cripto_manager: Optional[CriptografiaManager] = None


def get_cripto_manager() -> CriptografiaManager:
    """
    Obtém a instância singleton do gerenciador de criptografia.
    
    Returns:
        Instância do CriptografiaManager.
    """
    global _cripto_manager
    if _cripto_manager is None:
        _cripto_manager = CriptografiaManager()
    return _cripto_manager


# ============================================================================
# VALIDAÇÕES E SANITIZAÇÃO
# ============================================================================

class ValidadorDados:
    """
    Validador de dados de pessoas.
    
    Fornece métodos para sanitização e validação de campos sensíveis.
    """
    
    @staticmethod
    def sanitizar_string(valor: str) -> str:
        """
        Sanitiza uma string removendo caracteres perigosos.
        
        Args:
            valor: String a ser sanitizada.
            
        Returns:
            String sanitizada.
        """
        if not valor or pd.isna(valor):
            return ""
        valor_str = str(valor).strip()
        # Remover caracteres perigosos
        valor_limpo = PADRAO_CARACTERES_PERIGOSOS.sub("", valor_str)
        return valor_limpo
    
    @staticmethod
    def validar_cpf(cpf: str) -> tuple[bool, str]:
        """
        Valida o formato do CPF.
        
        Args:
            cpf: CPF a ser validado (apenas números).
            
        Returns:
            Tupla (válido, mensagem).
        """
        cpf_limpo = re.sub(r"\D", "", str(cpf))
        
        if not PADRAO_CPF.match(cpf_limpo):
            return False, f"CPF deve conter 11 dígitos numéricos (recebido: {len(cpf_limpo)})"
        
        # Verificar CPFs inválidos conhecidos (todos dígitos iguais)
        if len(set(cpf_limpo)) == 1:
            return False, "CPF inválido (dígitos repetidos)"
        
        # Validação do dígito verificador
        def calcular_digito(cpf_base: str) -> int:
            soma = sum(int(cpf_base[i]) * (10 - i) for i in range(9))
            resto = soma % 11
            return 0 if resto < 2 else 11 - resto
        
        digito1 = calcular_digito(cpf_limpo[:9])
        digito2 = calcular_digito(cpf_limpo[:9] + str(digito1))
        
        if cpf_limpo[9] != str(digito1) or cpf_limpo[10] != str(digito2):
            return False, "CPF inválido (dígitos verificadores incorretos)"
        
        return True, "CPF válido"
    
    @staticmethod
    def validar_saram(saram: str) -> tuple[bool, str]:
        """
        Valida o formato do SARAM.
        
        Args:
            saram: SARAM a ser validado (apenas números).
            
        Returns:
            Tupla (válido, mensagem).
        """
        saram_limpo = re.sub(r"\D", "", str(saram))
        
        if not PADRAO_SARAM.match(saram_limpo):
            return False, f"SARAM deve conter 7 dígitos numéricos (recebido: {len(saram_limpo)})"
        
        return True, "SARAM válido"
    
    @staticmethod
    def validar_email(email: str) -> tuple[bool, str]:
        """
        Valida o formato do email.
        
        Args:
            email: Email a ser validado.
            
        Returns:
            Tupla (válido, mensagem).
        """
        if not email or pd.isna(email):
            return True, "Email vazio (opcional)"
        
        email_str = str(email).strip()
        if not email_str:
            return True, "Email vazio (opcional)"
        
        if not PADRAO_EMAIL.match(email_str):
            return False, f"Formato de email inválido: {email_str}"
        
        return True, "Email válido"


# ============================================================================
# DATA CLASS - PESSOA
# ============================================================================

@dataclass
class Pessoa:
    """
    Representa uma pessoa com todos os campos mapeados para FIC.
    
    Attributes:
        Numero: Número sequencial
        SARAM: SARAM criptografado
        Posto_Graduacao: Posto/Graduação
        Especialidade: Especialidade
        Nome_Completo: Nome completo
        Nome_Guerra: Nome de guerra
        Data_Nascimento: Data de nascimento
        Data_Praca: Data de praça
        Data_Ultima_Promocao: Data da última promoção
        CPF: CPF criptografado
        RA: RA
        OM_Indicado: OM/Seção
        Habilitacao: Habilitação
        Email_Interno: Email interno
        Email: Email externo
        Telefone: Telefone
    """
    Numero: Optional[int] = None
    SARAM: Optional[str] = None
    Posto_Graduacao: Optional[str] = None
    Especialidade: Optional[str] = None
    Nome_Completo: Optional[str] = None
    Nome_Guerra: Optional[str] = None
    Data_Nascimento: Optional[str] = None
    Data_Praca: Optional[str] = None
    Data_Ultima_Promocao: Optional[str] = None
    CPF: Optional[str] = None
    RA: Optional[str] = None
    OM_Indicado: Optional[str] = None
    Habilitacao: Optional[str] = None
    Email_Interno: Optional[str] = None
    Email: Optional[str] = None
    Telefone: Optional[str] = None
    
    def to_dict(self, descriptografar: bool = False) -> Dict[str, Any]:
        """
        Converte a pessoa para dicionário.
        
        Args:
            descriptografar: Se True, descriptografa CPF e SARAM.
            
        Returns:
            Dicionário com os dados da pessoa.
        """
        dados = asdict(self)
        
        if descriptografar:
            cripto = get_cripto_manager()
            if dados.get("CPF"):
                try:
                    dados["CPF"] = cripto.descriptografar(dados["CPF"])
                except ValueError:
                    pass  # Mantém criptografado se não conseguir descriptografar
            if dados.get("SARAM"):
                try:
                    dados["SARAM"] = cripto.descriptografar(dados["SARAM"])
                except ValueError:
                    pass
        
        return dados


# ============================================================================
# GERENCIADOR PRINCIPAL
# ============================================================================

class PessoasManagerSecure:
    """
    Gerenciador seguro de pessoas.
    
    Gerencia o carregamento, busca e manipulação de dados de pessoas
    com criptografia de dados sensíveis e auditoria completa.
    
    Attributes:
        arquivo_pessoas: Caminho para o arquivo Excel de pessoas
        df_cache: DataFrame cache dos dados carregados
        cripto_manager: Gerenciador de criptografia
        validador: Validador de dados
    """
    
    def __init__(self, arquivo_pessoas: Optional[Union[str, Path]] = None):
        """
        Inicializa o gerenciador de pessoas.
        
        Args:
            arquivo_pessoas: Caminho alternativo para o arquivo Excel.
        """
        self.arquivo_pessoas = Path(arquivo_pessoas) if arquivo_pessoas else ARQUIVO_PESSOAS
        self.df_cache: Optional[pd.DataFrame] = None
        self.cripto_manager = get_cripto_manager()
        self.validador = ValidadorDados()
        
        log_operacao("inicializacao", f"Manager iniciado com arquivo: {self.arquivo_pessoas}")
    
    def _normalizar_colunas(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normaliza os nomes das colunas do DataFrame.
        
        Args:
            df: DataFrame original.
            
        Returns:
            DataFrame com colunas normalizadas.
        """
        # Mapeamento reverso para encontrar colunas originais
        colunas_normalizadas = {}
        for col in df.columns:
            col_limpa = col.strip().upper()
            for chave, valor in MAPEAMENTO_CAMPOS.items():
                if chave.upper().strip() == col_limpa or valor.upper() == col_limpa:
                    colunas_normalizadas[col] = valor
                    break
            else:
                # Manter coluna original se não estiver no mapeamento
                colunas_normalizadas[col] = col
        
        df = df.rename(columns=colunas_normalizadas)
        return df
    
    def _aplicar_criptografia(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Criptografa os campos sensíveis no DataFrame.
        
        Args:
            df: DataFrame com dados em texto plano.
            
        Returns:
            DataFrame com campos sensíveis criptografados.
        """
        df = df.copy()
        
        for campo_fic in CAMPOS_CRIPTOGRAFAR:
            if campo_fic in df.columns:
                df[campo_fic] = df[campo_fic].apply(
                    lambda x: self.cripto_manager.criptografar(x) if pd.notna(x) else ""
                )
        
        return df
    
    def _remover_criptografia(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Descriptografa os campos sensíveis no DataFrame.
        
        Args:
            df: DataFrame com dados criptografados.
            
        Returns:
            DataFrame com campos sensíveis descriptografados.
        """
        df = df.copy()
        
        for campo_fic in CAMPOS_CRIPTOGRAFAR:
            if campo_fic in df.columns:
                df[campo_fic] = df[campo_fic].apply(
                    lambda x: self.cripto_manager.descriptografar(x) 
                    if pd.notna(x) and str(x).strip() else ""
                )
        
        return df
    
    def _sanitizar_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Sanitiza todas as strings do DataFrame.
        
        Args:
            df: DataFrame original.
            
        Returns:
            DataFrame sanitizado.
        """
        df = df.copy()
        
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].apply(
                    lambda x: self.validador.sanitizar_string(x) if pd.notna(x) else ""
                )
        
        return df
    
    def carregar_pessoas(self, usar_cache: bool = True, descriptografar: bool = True) -> pd.DataFrame:
        """
        Carrega as pessoas do arquivo Excel.
        
        Args:
            usar_cache: Se True, usa o cache se disponível.
            descriptografar: Se True, descriptografa CPF e SARAM.
            
        Returns:
            DataFrame com os dados das pessoas.
            
        Raises:
            FileNotFoundError: Se o arquivo não existir.
            ValueError: Se houver erro ao processar o arquivo.
        """
        if usar_cache and self.df_cache is not None:
            log_operacao("cache", "Usando cache de pessoas")
            return self.df_cache.copy()
        
        if not self.arquivo_pessoas.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {self.arquivo_pessoas}")
        
        try:
            log_operacao("carregamento", f"Carregando arquivo: {self.arquivo_pessoas}")
            
            # Carregar Excel
            df = pd.read_excel(self.arquivo_pessoas)
            
            # Normalizar nomes de colunas
            df = self._normalizar_colunas(df)
            
            # Sanitizar dados
            df = self._sanitizar_dataframe(df)
            
            # Descriptografar se necessário
            if descriptografar:
                df = self._remover_criptografia(df)
            
            # Cache
            self.df_cache = df.copy()
            
            log_operacao("carregamento", f"{len(df)} registros carregados com sucesso")
            
            return df
            
        except Exception as e:
            log_operacao("erro", f"Erro ao carregar pessoas: {str(e)}")
            raise ValueError(f"Erro ao carregar arquivo de pessoas: {str(e)}")
    
    def buscar_por_nome(self, nome: str, case_sensitive: bool = False, 
                        descriptografar: bool = True) -> pd.DataFrame:
        """
        Busca pessoas por nome (case insensitive).
        
        Args:
            nome: Nome ou parte do nome para busca.
            case_sensitive: Se True, busca considera maiúsculas/minúsculas.
            descriptografar: Se True, retorna CPF e SARAM descriptografados.
            
        Returns:
            DataFrame com os resultados da busca.
            
        Raises:
            ValueError: Se o nome for vazio ou inválido.
        """
        # Sanitizar entrada
        nome_busca = self.validador.sanitizar_string(nome)
        if not nome_busca:
            raise ValueError("Nome de busca não pode ser vazio")
        
        log_operacao("busca", f"Buscando por nome: '{nome_busca}' (case_sensitive={case_sensitive})")
        
        # Carregar dados
        df = self.carregar_pessoas(descriptografar=descriptografar)
        
        # Verificar colunas necessárias
        colunas_nome = ["Nome_Completo", "Nome_Guerra"]
        colunas_disponiveis = [col for col in colunas_nome if col in df.columns]
        
        if not colunas_disponiveis:
            raise ValueError("Colunas de nome não encontradas no DataFrame")
        
        # Preparar busca
        if not case_sensitive:
            nome_busca = nome_busca.lower()
            for col in colunas_disponiveis:
                df[col] = df[col].astype(str).str.lower()
        
        # Realizar busca
        mascara = pd.Series([False] * len(df))
        for col in colunas_disponiveis:
            mascara = mascara | df[col].str.contains(nome_busca, na=False, regex=False)
        
        resultados = df[mascara].copy()
        
        log_operacao("busca", f"{len(resultados)} resultados encontrados para '{nome_busca}'")
        
        return resultados
    
    def buscar_pessoa_exata(self, nome: str, descriptografar: bool = True) -> Optional[Dict[str, Any]]:
        """
        Busca uma pessoa pelo nome exato (nome completo ou nome de guerra).
        
        Args:
            nome: Nome completo ou nome de guerra.
            descriptografar: Se True, retorna CPF e SARAM descriptografados.
            
        Returns:
            Dicionário com os dados da pessoa ou None se não encontrada.
            
        Raises:
            ValueError: Se encontrar múltiplas pessoas com o mesmo nome.
        """
        # Sanitizar entrada
        nome_busca = self.validador.sanitizar_string(nome)
        if not nome_busca:
            raise ValueError("Nome de busca não pode ser vazio")
        
        log_operacao("busca_exata", f"Buscando pessoa exata: '{nome_busca}'")
        
        # Carregar dados
        df = self.carregar_pessoas(descriptografar=descriptografar)
        
        # Busca case-insensitive
        nome_busca_lower = nome_busca.lower()
        
        mascara = pd.Series([False] * len(df))
        
        if "Nome_Completo" in df.columns:
            mascara = mascara | df["Nome_Completo"].astype(str).str.lower().eq(nome_busca_lower)
        
        if "Nome_Guerra" in df.columns:
            mascara = mascara | df["Nome_Guerra"].astype(str).str.lower().eq(nome_busca_lower)
        
        resultados = df[mascara]
        
        if len(resultados) == 0:
            log_operacao("busca_exata", f"Nenhuma pessoa encontrada para: '{nome_busca}'")
            return None
        
        if len(resultados) > 1:
            log_operacao("busca_exata", f"Múltiplas pessoas encontradas para: '{nome_busca}' ({len(resultados)} resultados)")
            raise ValueError(f"Múltiplas pessoas encontradas com o nome '{nome_busca}'")
        
        pessoa_dict = resultados.iloc[0].to_dict()
        log_operacao("busca_exata", f"Pessoa encontrada: '{nome_busca}'")
        
        return pessoa_dict
    
    def obter_dados_completos_fic(self, nome: str) -> Optional[Dict[str, Any]]:
        """
        Obtém os dados completos de uma pessoa formatados para FIC.
        
        Retorna um dicionário com todos os campos mapeados para FIC,
        incluindo validações e formatações específicas.
        
        Args:
            nome: Nome completo ou nome de guerra da pessoa.
            
        Returns:
            Dicionário com todos os campos mapeados para FIC ou None.
            
        Raises:
            ValueError: Se encontrar múltiplas pessoas com o mesmo nome.
        """
        # Buscar pessoa (com descriptografia)
        pessoa = self.buscar_pessoa_exata(nome, descriptografar=True)
        
        if pessoa is None:
            return None
        
        log_operacao("fic", f"Obtendo dados FIC para: '{nome}'")
        
        # Criar objeto Pessoa
        pessoa_obj = Pessoa(**{k: v for k, v in pessoa.items() if hasattr(Pessoa, k)})
        
        # Validar dados sensíveis
        validacoes = {}
        
        if pessoa_obj.CPF:
            valido, msg = self.validador.validar_cpf(pessoa_obj.CPF)
            validacoes["CPF"] = {"valido": valido, "mensagem": msg}
        
        if pessoa_obj.SARAM:
            valido, msg = self.validador.validar_saram(pessoa_obj.SARAM)
            validacoes["SARAM"] = {"valido": valido, "mensagem": msg}
        
        # Converter para dicionário completo
        resultado = pessoa_obj.to_dict(descriptografar=False)  # Já está descriptografado
        resultado["_validacoes"] = validacoes
        resultado["_timestamp"] = datetime.now().isoformat()
        
        log_operacao("fic", f"Dados FIC gerados com sucesso para: '{nome}'")
        
        return resultado
    
    def validar_dados_pessoa(self, nome: str) -> Dict[str, Any]:
        """
        Valida os dados de uma pessoa específica.
        
        Args:
            nome: Nome completo ou nome de guerra da pessoa.
            
        Returns:
            Dicionário com os resultados das validações.
        """
        pessoa = self.buscar_pessoa_exata(nome, descriptografar=True)
        
        if pessoa is None:
            return {"erro": f"Pessoa não encontrada: {nome}"}
        
        log_operacao("validacao", f"Validando dados de: '{nome}'")
        
        resultados = {
            "pessoa": nome,
            "validacoes": {},
            "alertas": []
        }
        
        # Validar CPF
        cpf = pessoa.get("CPF", "")
        if cpf:
            valido, msg = self.validador.validar_cpf(cpf)
            resultados["validacoes"]["CPF"] = {"status": "válido" if valido else "inválido", "mensagem": msg}
            if not valido:
                resultados["alertas"].append(f"CPF inválido: {msg}")
        else:
            resultados["validacoes"]["CPF"] = {"status": "vazio", "mensagem": "CPF não informado"}
            resultados["alertas"].append("CPF não informado")
        
        # Validar SARAM
        saram = pessoa.get("SARAM", "")
        if saram:
            valido, msg = self.validador.validar_saram(saram)
            resultados["validacoes"]["SARAM"] = {"status": "válido" if valido else "inválido", "mensagem": msg}
            if not valido:
                resultados["alertas"].append(f"SARAM inválido: {msg}")
        else:
            resultados["validacoes"]["SARAM"] = {"status": "vazio", "mensagem": "SARAM não informado"}
            resultados["alertas"].append("SARAM não informado")
        
        # Validar emails
        email_interno = pessoa.get("Email_Interno", "")
        email_externo = pessoa.get("Email", "")
        
        for campo, email in [("Email_Interno", email_interno), ("Email", email_externo)]:
            if email:
                valido, msg = self.validador.validar_email(email)
                resultados["validacoes"][campo] = {"status": "válido" if valido else "inválido", "mensagem": msg}
                if not valido:
                    resultados["alertas"].append(f"{campo} inválido: {msg}")
        
        resultados["status_geral"] = "válido" if not resultados["alertas"] else "com_alertas"
        
        log_operacao("validacao", f"Validação concluída para '{nome}': {resultados['status_geral']}")
        
        return resultados
    
    def listar_todos(self, descriptografar: bool = False) -> pd.DataFrame:
        """
        Lista todas as pessoas.
        
        Args:
            descriptografar: Se True, descriptografa CPF e SARAM.
            
        Returns:
            DataFrame com todas as pessoas.
        """
        log_operacao("listagem", "Listando todas as pessoas")
        return self.carregar_pessoas(descriptografar=descriptografar)
    
    def limpar_cache(self) -> None:
        """Limpa o cache de dados carregados."""
        self.df_cache = None
        log_operacao("cache", "Cache limpo")
    
    def obter_nomes_formatados(self) -> List[str]:
        """
        Retorna lista de nomes formatados com posto/graduação para exibição.
        
        Returns:
            Lista de strings no formato "Posto Nome"
        """
        df = self.carregar_pessoas(descriptografar=False)
        
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
            
            # Ordenar alfabeticamente
            nomes_formatados.sort()
            
            log_operacao("consulta", f"Obtidos {len(nomes_formatados)} nomes formatados")
            return nomes_formatados
            
        except Exception as e:
            log_operacao("erro", f"Erro ao obter nomes formatados: {e}")
            return []
    
    def obter_sugestoes_nomes(self, termo: str = "", limite: int = 20) -> List[str]:
        """
        Retorna sugestões de nomes para autocomplete.
        
        Args:
            termo: Termo de busca (opcional, retorna todos se vazio)
            limite: Número máximo de sugestões
            
        Returns:
            Lista de nomes sugeridos
        """
        df = self.carregar_pessoas(descriptografar=False)
        
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
            
            # Formatar nomes com posto
            sugestoes = []
            for _, row in df_filtrado.head(limite).iterrows():
                nome = str(row.get('Nome_Completo', '')).strip()
                posto = str(row.get('Posto_Graduacao', '')).strip()
                
                if nome:
                    if posto:
                        sugestoes.append(f"{posto} {nome}")
                    else:
                        sugestoes.append(nome)
            
            log_operacao("consulta", f"Obtidas {len(sugestoes)} sugestoes para termo: {termo}")
            return sugestoes
            
        except Exception as e:
            log_operacao("erro", f"Erro ao obter sugestoes: {e}")
            return []


# ============================================================================
# FUNÇÕES DE CONVENIÊNCIA
# ============================================================================

def criar_manager(arquivo_pessoas: Optional[Union[str, Path]] = None) -> PessoasManagerSecure:
    """
    Cria uma instância do gerenciador de pessoas.
    
    Args:
        arquivo_pessoas: Caminho alternativo para o arquivo Excel.
        
    Returns:
        Instância do PessoasManagerSecure.
    """
    return PessoasManagerSecure(arquivo_pessoas)


def buscar_pessoa(nome: str) -> Optional[Dict[str, Any]]:
    """
    Função de conveniência para buscar uma pessoa pelo nome.
    
    Args:
        nome: Nome completo ou nome de guerra.
        
    Returns:
        Dicionário com os dados da pessoa ou None.
    """
    manager = criar_manager()
    return manager.buscar_pessoa_exata(nome)


def obter_dados_fic(nome: str) -> Optional[Dict[str, Any]]:
    """
    Função de conveniência para obter dados formatados para FIC.
    
    Args:
        nome: Nome completo ou nome de guerra.
        
    Returns:
        Dicionário com os dados formatados para FIC ou None.
    """
    manager = criar_manager()
    return manager.obter_dados_completos_fic(nome)


# ============================================================================
# EXECUÇÃO COMO SCRIPT
# ============================================================================

if __name__ == "__main__":
    # Testes básicos
    print("=" * 60)
    print("TESTE DO GERENCIADOR DE PESSOAS SEGURO")
    print("=" * 60)
    
    try:
        manager = PessoasManagerSecure()
        
        # Testar carregamento
        print("\n1. Carregando pessoas...")
        df = manager.carregar_pessoas(descriptografar=True)
        print(f"   Total de pessoas: {len(df)}")
        print(f"   Colunas: {list(df.columns)}")
        
        # Testar busca por nome
        print("\n2. Testando busca por nome...")
        resultados = manager.buscar_por_nome("MORAVIS")
        print(f"   Resultados encontrados: {len(resultados)}")
        if len(resultados) > 0:
            print(f"   Primeiro resultado: {resultados.iloc[0].get('Nome_Guerra', 'N/A')}")
        
        # Testar busca exata
        print("\n3. Testando busca exata...")
        pessoa = manager.buscar_pessoa_exata("EMANUEL LUIZ MORAVIS")
        if pessoa:
            print(f"   Pessoa encontrada: {pessoa.get('Nome_Guerra', 'N/A')}")
            print(f"   Posto: {pessoa.get('Posto_Graduacao', 'N/A')}")
        
        # Testar dados FIC
        print("\n4. Testando obter dados FIC...")
        dados_fic = manager.obter_dados_completos_fic("EMANUEL LUIZ MORAVIS")
        if dados_fic:
            print(f"   Campos FIC disponíveis: {list(dados_fic.keys())}")
            print(f"   Validações: {dados_fic.get('_validacoes', {})}")
        
        print("\n" + "=" * 60)
        print("TESTES CONCLUÍDOS COM SUCESSO!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()
