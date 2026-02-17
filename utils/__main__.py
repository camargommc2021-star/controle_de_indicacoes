"""
Script de demonstração do módulo de logging.

Execute com: python -m utils
"""

from utils.logger import get_logger


def main():
    """Demonstra as funcionalidades do logger."""
    # Obtém o logger
    logger = get_logger(__name__)
    
    print("=" * 60)
    print("DEMONSTRAÇÃO DO MÓDULO DE LOGGING")
    print("=" * 60)
    print()
    
    # Exemplos de diferentes níveis de log
    logger.debug("Esta é uma mensagem de DEBUG - visível apenas se LOG_LEVEL=DEBUG")
    logger.info("Aplicação iniciada com sucesso")
    logger.warning("Este é um aviso - verifique a configuração")
    logger.error("Ocorreu um erro durante o processamento")
    logger.critical("Erro CRÍTICO - aplicação precisa ser reiniciada")
    
    print()
    print("-" * 60)
    print("Log com informações de exceção:")
    print("-" * 60)
    
    try:
        resultado = 1 / 0
    except ZeroDivisionError:
        logger.error("Erro ao dividir por zero", exc_info=True)
    
    print()
    print("-" * 60)
    print("Log formatado com variáveis:")
    print("-" * 60)
    
    usuario = "João Silva"
    acao = "login"
    tempo = 0.045
    logger.info("Usuário '%s' realizou %s em %.3f segundos", usuario, acao, tempo)
    
    print()
    print("=" * 60)
    print("Logs salvos em: logs/app.log")
    print("=" * 60)


if __name__ == "__main__":
    main()
