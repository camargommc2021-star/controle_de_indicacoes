"""
Script para executar todos os testes unitários do sistema.

Usage:
    python tests/run_tests.py              # Executar todos os testes
    python tests/run_tests.py -v           # Modo verboso
    python tests/run_tests.py -s           # Mostrar saída dos testes
    python tests/run_tests.py --cov        # Com cobertura
    python tests/run_tests.py test_config  # Executar testes específicos
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path


# Diretório raiz do projeto
PROJECT_ROOT = Path(__file__).parent.parent
TESTS_DIR = PROJECT_ROOT / "tests"


def run_tests(args=None):
    """Executa os testes com pytest."""
    
    # Argumentos padrão do pytest
    pytest_args = [
        "pytest",
        str(TESTS_DIR),
        "-v",  # Modo verboso
        "--tb=short",  # Traceback curto
        "--color=yes",  # Cores na saída
    ]
    
    # Adicionar argumentos extras
    if args:
        if args.verbose:
            pytest_args.append("-vv")
        
        if args.capture:
            pytest_args.append("-s")
        
        if args.coverage:
            pytest_args.extend(["--cov=.", "--cov-report=term-missing"])
        
        if args.junit:
            pytest_args.extend(["--junitxml", "tests/results.xml"])
        
        if args.test_name:
            # Executar teste específico
            test_path = TESTS_DIR / f"test_{args.test_name}.py"
            if test_path.exists():
                pytest_args[1] = str(test_path)
            else:
                print(f"❌ Arquivo de teste não encontrado: {test_path}")
                return 1
    
    # Executar pytest
    try:
        result = subprocess.run(
            pytest_args,
            cwd=PROJECT_ROOT,
            check=False,
        )
        return result.returncode
    except FileNotFoundError:
        print("❌ pytest não encontrado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest"])
        return run_tests(args)


def run_tests_unittest():
    """Executa testes usando unittest (alternativa)."""
    import unittest
    
    # Descobrir todos os testes
    loader = unittest.TestLoader()
    suite = loader.discover(str(TESTS_DIR), pattern="test_*.py")
    
    # Executar testes
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


def check_dependencies():
    """Verifica se as dependências estão instaladas."""
    required = ["pytest", "pandas", "openpyxl"]
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Dependências ausentes: {', '.join(missing)}")
        print("Instalando...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install"] + missing,
            check=True,
        )
        print("✅ Dependências instaladas!")
    
    return len(missing) == 0


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Executa a suite de testes do Sistema de Controle de Cursos"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Modo mais verboso"
    )
    parser.add_argument(
        "-s", "--capture",
        action="store_true",
        help="Mostrar saída dos prints nos testes"
    )
    parser.add_argument(
        "--cov", "--coverage",
        action="store_true",
        help="Gerar relatório de cobertura"
    )
    parser.add_argument(
        "--junit",
        action="store_true",
        help="Gerar relatório XML no formato JUnit"
    )
    parser.add_argument(
        "--unittest",
        action="store_true",
        help="Usar unittest em vez de pytest"
    )
    parser.add_argument(
        "test_name",
        nargs="?",
        help="Nome do teste específico a executar (ex: config, data_manager)"
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🧪 SUITE DE TESTES - Sistema de Controle de Cursos")
    print("=" * 70)
    print()
    
    # Verificar dependências
    if not check_dependencies():
        print("❌ Falha ao instalar dependências")
        return 1
    
    # Executar testes
    if args.unittest:
        print("Executando com unittest...")
        return run_tests_unittest()
    else:
        print("Executando com pytest...")
        return run_tests(args)


if __name__ == "__main__":
    sys.exit(main())
