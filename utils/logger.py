"""
Módulo de logging profissional para o projeto.

Fornece configuração centralizada de logging com:
- Rotação de arquivos
- Saída para arquivo e console
- Formato padronizado
- Configuração via variáveis de ambiente

Exemplo de uso:
    from utils.logger import get_logger
    
    logger = get_logger(__name__)
    logger.info("Mensagem informativa")
    logger.error("Erro ocorrido", exc_info=True)
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


# ============================================================================
# CONFIGURAÇÕES PADRÃO
# ============================================================================

DEFAULT_LOG_DIR = "logs"
DEFAULT_LOG_FILE = "app.log"
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_MAX_BYTES = 5 * 1024 * 1024  # 5 MB
DEFAULT_BACKUP_COUNT = 5
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ============================================================================
# MAPEAMENTO DE NÍVEIS DE LOG
# ============================================================================

LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

# ============================================================================
# CACHE DE LOGGERS CONFIGURADOS
# ============================================================================

_loggers: dict[str, logging.Logger] = {}


def _get_env_or_default(var_name: str, default_value: str) -> str:
    """
    Obtém valor de variável de ambiente ou retorna valor padrão.
    
    Args:
        var_name: Nome da variável de ambiente
        default_value: Valor padrão se variável não estiver definida
        
    Returns:
        Valor da variável de ambiente ou valor padrão
    """
    return os.getenv(var_name, default_value)


def _ensure_log_directory(log_dir: str) -> Path:
    """
    Garante que o diretório de logs exista.
    
    Args:
        log_dir: Caminho do diretório de logs
        
    Returns:
        Path do diretório de logs
    """
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    return log_path


def _get_log_level() -> int:
    """
    Obtém o nível de log das variáveis de ambiente ou valor padrão.
    
    Returns:
        Nível de log como constante do módulo logging
    """
    level_name = _get_env_or_default("LOG_LEVEL", DEFAULT_LOG_LEVEL).upper()
    return LOG_LEVELS.get(level_name, logging.INFO)


def _create_formatter() -> logging.Formatter:
    """
    Cria o formatador padronizado para os logs.
    
    Returns:
        Instância de logging.Formatter configurada
    """
    log_format = _get_env_or_default("LOG_FORMAT", DEFAULT_LOG_FORMAT)
    date_format = _get_env_or_default("LOG_DATE_FORMAT", DEFAULT_DATE_FORMAT)
    return logging.Formatter(log_format, datefmt=date_format)


def _create_file_handler(log_dir: str, log_file: str) -> logging.handlers.RotatingFileHandler:
    """
    Cria handler para escrita em arquivo com rotação.
    
    Args:
        log_dir: Diretório dos arquivos de log
        log_file: Nome do arquivo de log
        
    Returns:
        Handler configurado para arquivo rotativo
    """
    log_path = _ensure_log_directory(log_dir)
    log_file_path = log_path / log_file
    
    max_bytes = int(_get_env_or_default("LOG_MAX_BYTES", str(DEFAULT_MAX_BYTES)))
    backup_count = int(_get_env_or_default("LOG_BACKUP_COUNT", str(DEFAULT_BACKUP_COUNT)))
    
    handler = logging.handlers.RotatingFileHandler(
        filename=log_file_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8"
    )
    handler.setFormatter(_create_formatter())
    handler.setLevel(_get_log_level())
    
    return handler


def _create_console_handler() -> logging.StreamHandler:
    """
    Cria handler para saída no console.
    
    Returns:
        Handler configurado para console
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_create_formatter())
    handler.setLevel(_get_log_level())
    return handler


def _configure_logger(logger: logging.Logger) -> None:
    """
    Configura um logger com handlers de arquivo e console.
    
    Args:
        logger: Instância do logger a ser configurado
    """
    # Evita duplicação de handlers
    if logger.handlers:
        return
    
    log_dir = _get_env_or_default("LOG_DIR", DEFAULT_LOG_DIR)
    log_file = _get_env_or_default("LOG_FILE", DEFAULT_LOG_FILE)
    
    # Configura nível do logger
    logger.setLevel(_get_log_level())
    
    # Adiciona handler de arquivo
    file_handler = _create_file_handler(log_dir, log_file)
    logger.addHandler(file_handler)
    
    # Adiciona handler de console (exceto se desabilitado)
    if _get_env_or_default("LOG_CONSOLE", "true").lower() != "false":
        console_handler = _create_console_handler()
        logger.addHandler(console_handler)
    
    # Evita propagação para o logger raiz (evita duplicação de mensagens)
    logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """
    Obtém um logger configurado com o nome especificado.
    
    Retorna um logger do módulo logging já configurado com:
    - Saída para arquivo (logs/app.log) com rotação
    - Saída para console
    - Formato padronizado
    - Nível configurável via variável de ambiente LOG_LEVEL
    
    Args:
        name: Nome do logger (recomendado usar __name__)
        
    Returns:
        Logger configurado e pronto para uso
        
    Example:
        >>> from utils.logger import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Aplicação iniciada")
        >>> logger.debug("Valor de x: %s", x)
        >>> try:
        ...     resultado = 1 / 0
        ... except ZeroDivisionError:
        ...     logger.error("Erro de divisão", exc_info=True)
    """
    if name not in _loggers:
        logger = logging.getLogger(name)
        _configure_logger(logger)
        _loggers[name] = logger
    
    return _loggers[name]


def configure_root_logger() -> logging.Logger:
    """
    Configura e retorna o logger raiz da aplicação.
    
    Útil para configurar logging em aplicações que usam
    bibliotecas de terceiros que logam no logger raiz.
    
    Returns:
        Logger raiz configurado
    """
    root_logger = logging.getLogger()
    
    # Limpa handlers existentes
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    log_dir = _get_env_or_default("LOG_DIR", DEFAULT_LOG_DIR)
    log_file = _get_env_or_default("LOG_FILE", "root.log")
    
    root_logger.setLevel(_get_log_level())
    root_logger.addHandler(_create_file_handler(log_dir, log_file))
    root_logger.addHandler(_create_console_handler())
    
    return root_logger


def get_logger_with_context(name: str, **context) -> logging.LoggerAdapter:
    """
    Obtém um logger com contexto adicional para todas as mensagens.
    
    Args:
        name: Nome do logger
        **context: Dicionário de contexto a ser incluído em todas as mensagens
        
    Returns:
        LoggerAdapter com contexto
        
    Example:
        >>> logger = get_logger_with_context("meu_modulo", user_id=123, request_id="abc")
        >>> logger.info("Processando requisição")
        # Saída: 2024-01-15 10:30:00 - meu_modulo - INFO - [user_id:123, request_id:abc] Processando requisição
    """
    logger = get_logger(name)
    
    class ContextAdapter(logging.LoggerAdapter):
        def process(self, msg, kwargs):
            context_str = ", ".join(f"{k}:{v}" for k, v in self.extra.items())
            return f"[{context_str}] {msg}", kwargs
    
    return ContextAdapter(logger, context)


# ============================================================================
# FUNÇÕES UTILITÁRIAS
# ============================================================================

def set_log_level(level: str) -> None:
    """
    Altera o nível de log em tempo de execução.
    
    Args:
        level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    level_value = LOG_LEVELS.get(level.upper(), logging.INFO)
    
    for logger in _loggers.values():
        logger.setLevel(level_value)
        for handler in logger.handlers:
            handler.setLevel(level_value)


def get_log_file_path() -> Optional[Path]:
    """
    Retorna o caminho do arquivo de log principal.
    
    Returns:
        Path do arquivo de log ou None se não configurado
    """
    log_dir = _get_env_or_default("LOG_DIR", DEFAULT_LOG_DIR)
    log_file = _get_env_or_default("LOG_FILE", DEFAULT_LOG_FILE)
    return Path(log_dir) / log_file


def clear_loggers() -> None:
    """
    Limpa o cache de loggers configurados.
    
    Útil para testes ou quando é necessário reconfigurar todos os loggers.
    """
    global _loggers
    _loggers.clear()
