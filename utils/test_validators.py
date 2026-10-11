"""
Script de teste para o módulo validators.

Execute com: python utils/test_validators.py
"""

from utils.validators import (
    # Validação de datas
    is_valid_date, parse_date, is_future_date, date_range_valid,
    # Validação de campos do curso
    validate_turma, validate_vagas, validate_sigad, validate_curso,
    # Utilitários
    sanitize_string, normalize_text, slugify
)


def test_dates():
    """Testa funções de validação de datas."""
    print("=" * 50)
    print("TESTES DE VALIDAÇÃO DE DATAS")
    print("=" * 50)
    
    # Testes is_valid_date
    assert is_valid_date("25/12/2023") == True
    assert is_valid_date("32/12/2023") == False
    assert is_valid_date("2023-12-25", "%Y-%m-%d") == True
    print("[OK] is_valid_date funcionando")
    
    # Testes parse_date
    result = parse_date("25/12/2023")
    assert result is not None and result.year == 2023
    assert parse_date("invalido") is None
    print("[OK] parse_date funcionando")
    
    # Testes is_future_date (ajuste o ano conforme necessidade)
    assert is_future_date("25/12/2030") == True
    assert is_future_date("25/12/2000") == False
    print("[OK] is_future_date funcionando")
    
    # Testes date_range_valid
    assert date_range_valid("01/01/2023", "31/12/2023") == True
    assert date_range_valid("31/12/2023", "01/01/2023") == False
    print("[OK] date_range_valid funcionando")
    
    print("[PASS] Todos os testes de datas passaram!\n")


def test_curso():
    """Testa funções de validação de campos do curso."""
    print("=" * 50)
    print("TESTES DE VALIDAÇÃO DE CURSO")
    print("=" * 50)
    
    # Testes turma
    assert validate_turma("T-001") == True
    assert validate_turma("AB") == True
    assert validate_turma("A") == False  # Muito curto
    assert validate_turma("<script>") == False  # Caracteres perigosos
    print("[OK] validate_turma funcionando")
    
    # Testes vagas
    valid, msg = validate_vagas(30)
    assert valid == True and msg == ""
    valid, msg = validate_vagas(0)
    assert valid == False
    valid, msg = validate_vagas("abc")
    assert valid == False
    print("[OK] validate_vagas funcionando")
    
    # Testes SIGAD
    assert validate_sigad("12345/2023") == True
    assert validate_sigad("AB") == False  # Muito curto
    print("[OK] validate_sigad funcionando")
    
    # Teste validação completa de curso
    curso_valido = {
        'nome': 'Curso de Teste',
        'turma': 'T-001',
        'vagas': 30,
        'data_inicio': '01/01/2024',
        'data_fim': '31/01/2024',
        'sigad': '12345/2024'
    }
    valid, errors = validate_curso(curso_valido)
    assert valid == True and len(errors) == 0
    
    curso_invalido = {
        'nome': '',
        'turma': 'A',
        'vagas': 0,
        'data_inicio': '32/13/2024'
    }
    valid, errors = validate_curso(curso_invalido)
    assert valid == False and len(errors) > 0
    print("[OK] validate_curso funcionando")
    
    print("[PASS] Todos os testes de curso passaram!\n")


def test_utilities():
    """Testa funções utilitárias."""
    print("=" * 50)
    print("TESTES DE UTILITÁRIOS")
    print("=" * 50)
    
    # Testes sanitize_string
    assert sanitize_string("<script>alert(xss)</script>") == "scriptalert(xss)/script"
    assert sanitize_string("DROP TABLE users; --") == "DROP TABLE users"
    print("[OK] sanitize_string funcionando")
    
    # Testes normalize_text
    assert normalize_text("  texto ExEmPlO  ") == "TEXTO EXEMPLO"
    assert normalize_text("outro   exemplo") == "OUTRO EXEMPLO"
    print("[OK] normalize_text funcionando")
    
    # Testes slugify
    assert slugify("Título do Curso 2024!") == "titulo-do-curso-2024"
    assert slugify("  Espaços  Extras  ") == "espacos-extras"
    print("[OK] slugify funcionando")
    
    print("[PASS] Todos os testes de utilitários passaram!\n")


def main():
    """Executa todos os testes."""
    print("\n" + "=" * 50)
    print("INICIANDO TESTES DO MÓDULO VALIDATORS")
    print("=" * 50 + "\n")
    
    try:
        test_dates()
        test_curso()
        test_utilities()
        
        print("=" * 50)
        print(">>> TODOS OS TESTES PASSARAM COM SUCESSO!")
        print("=" * 50)
        
    except AssertionError as e:
        print(f"\n[FAIL] TESTE FALHOU: {e}")
        raise
    except Exception as e:
        print(f"\n[FAIL] ERRO INESPERADO: {e}")
        raise


if __name__ == "__main__":
    main()
