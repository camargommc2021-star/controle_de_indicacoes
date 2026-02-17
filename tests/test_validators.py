"""
Testes unitários para o módulo utils/validators.py.

Testa todas as funções de validação de dados do sistema,
incluindo datas, documentos (CPF, SARAM), campos de cursos e FIC.
"""

import pytest
from datetime import datetime, date, timedelta

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.validators import (
    # Validação de datas
    is_valid_date,
    parse_date,
    is_future_date,
    is_past_date,
    date_range_valid,
    # Validação de documentos
    clean_cpf,
    is_valid_cpf,
    format_cpf,
    is_valid_saram,
    format_saram,
    # Validação de campos do curso
    validate_turma,
    validate_vagas,
    validate_sigad,
    validate_curso,
    # Validação de FIC
    validate_email,
    clean_phone,
    validate_phone,
    validate_fic,
    # Utilitários
    sanitize_string,
    normalize_text,
    truncate_string,
    slugify,
    validate_nota,
    validate_frequencia,
    validate_ano,
    validate_carga_horaria,
)


# =============================================================================
# TESTES DE VALIDAÇÃO DE DATAS
# =============================================================================

class TestDateValidation:
    """Testes para funções de validação de datas."""
    
    def test_is_valid_date_with_valid_dates(self):
        """Testa datas válidas no formato padrão."""
        assert is_valid_date("25/12/2023") is True
        assert is_valid_date("01/01/2024") is True
        assert is_valid_date("31/12/2023") is True
        assert is_valid_date("29/02/2024") is True  # Ano bissexto
    
    def test_is_valid_date_with_invalid_dates(self):
        """Testa datas inválidas."""
        assert is_valid_date("32/12/2023") is False  # Dia inválido
        assert is_valid_date("25/13/2023") is False  # Mês inválido
        assert is_valid_date("25/12/23") is False    # Ano incompleto
        assert is_valid_date("invalid") is False
        assert is_valid_date("") is False
        assert is_valid_date(None) is False
    
    def test_is_valid_date_with_custom_format(self):
        """Testa datas com formato personalizado."""
        assert is_valid_date("2023-12-25", "%Y-%m-%d") is True
        assert is_valid_date("12/25/2023", "%m/%d/%Y") is True
        assert is_valid_date("25-12-2023", "%d-%m-%Y") is True
    
    def test_parse_date_with_valid_dates(self):
        """Testa parsing de datas válidas."""
        result = parse_date("25/12/2023")
        assert isinstance(result, datetime)
        assert result.day == 25
        assert result.month == 12
        assert result.year == 2023
    
    def test_parse_date_with_invalid_dates(self):
        """Testa parsing de datas inválidas."""
        assert parse_date("invalid") is None
        assert parse_date("") is None
        assert parse_date(None) is None
        assert parse_date("32/12/2023") is None
    
    def test_is_future_date(self):
        """Testa verificação de datas futuras."""
        future = (date.today() + timedelta(days=30)).strftime("%d/%m/%Y")
        past = (date.today() - timedelta(days=30)).strftime("%d/%m/%Y")
        
        assert is_future_date(future) is True
        assert is_future_date(past) is False
    
    def test_is_past_date(self):
        """Testa verificação de datas passadas."""
        future = (date.today() + timedelta(days=30)).strftime("%d/%m/%Y")
        past = (date.today() - timedelta(days=30)).strftime("%d/%m/%Y")
        
        assert is_past_date(past) is True
        assert is_past_date(future) is False
    
    def test_date_range_valid(self):
        """Testa validação de intervalo de datas."""
        assert date_range_valid("01/01/2024", "31/12/2024") is True
        assert date_range_valid("01/01/2024", "01/01/2024") is True  # Mesmo dia
        assert date_range_valid("31/12/2024", "01/01/2024") is False  # Invertido
        assert date_range_valid("invalid", "31/12/2024") is False
        assert date_range_valid("01/01/2024", "invalid") is False


# =============================================================================
# TESTES DE VALIDAÇÃO DE DOCUMENTOS
# =============================================================================

class TestCPFValidation:
    """Testes para funções de validação de CPF."""
    
    def test_clean_cpf(self):
        """Testa limpeza de CPF."""
        assert clean_cpf("529.982.247-25") == "52998224725"
        assert clean_cpf("529-982-247.25") == "52998224725"
        assert clean_cpf("52998224725") == "52998224725"
        assert clean_cpf("") == ""
        assert clean_cpf(None) == ""
    
    def test_is_valid_cpf_with_valid_cpfs(self):
        """Testa CPFs válidos."""
        assert is_valid_cpf("529.982.247-25") is True
        assert is_valid_cpf("52998224725") is True
        assert is_valid_cpf("111.444.777-35") is True
    
    def test_is_valid_cpf_with_invalid_cpfs(self):
        """Testa CPFs inválidos."""
        # CPFs com dígitos iguais
        assert is_valid_cpf("111.111.111-11") is False
        assert is_valid_cpf("000.000.000-00") is False
        
        # CPFs com dígitos errados
        assert is_valid_cpf("529.982.247-26") is False
        assert is_valid_cpf("123.456.789-00") is False
        
        # CPFs mal formatados
        assert is_valid_cpf("123") is False
        assert is_valid_cpf("") is False
        assert is_valid_cpf("abc.def.ghi-jk") is False
        assert is_valid_cpf(None) is False
    
    def test_format_cpf(self):
        """Testa formatação de CPF."""
        assert format_cpf("52998224725") == "529.982.247-25"
        assert format_cpf("529.982.247-25") == "529.982.247-25"
        assert format_cpf("123") == ""  # CPF inválido
        assert format_cpf("") == ""


class TestSARAMValidation:
    """Testes para funções de validação de SARAM."""
    
    def test_is_valid_saram(self):
        """Testa validação de SARAM."""
        # Válidos
        assert is_valid_saram("123456") is True
        assert is_valid_saram("1234") is True      # Mínimo 4 dígitos
        assert is_valid_saram("12345678") is True  # Máximo 8 dígitos
        
        # Inválidos
        assert is_valid_saram("123") is False      # Menos de 4 dígitos
        assert is_valid_saram("123456789") is False  # Mais de 8 dígitos
        assert is_valid_saram("ABC123") is False   # Contém letras
        assert is_valid_saram("") is False
        assert is_valid_saram(None) is False
    
    def test_format_saram(self):
        """Testa formatação de SARAM."""
        assert format_saram("123456") == "123456"
        assert format_saram("12.34-56") == "123456"
        assert format_saram("ABC123") == "123"


# =============================================================================
# TESTES DE VALIDAÇÃO DE CAMPOS DO CURSO
# =============================================================================

class TestTurmaValidation:
    """Testes para validação de turma."""
    
    def test_validate_turma_valid(self):
        """Testa códigos de turma válidos."""
        assert validate_turma("2024-001") is True
        assert validate_turma("T1") is True
        assert validate_turma("Turma A") is True
        assert validate_turma("ABC123") is True
    
    def test_validate_turma_invalid(self):
        """Testa códigos de turma inválidos."""
        assert validate_turma("A") is False  # Muito curto
        assert validate_turma("") is False
        assert validate_turma(None) is False
        assert validate_turma("<script>") is False  # Caracteres perigosos
        assert validate_turma("DROP TABLE;") is False


class TestVagasValidation:
    """Testes para validação de vagas."""
    
    def test_validate_vagas_valid(self):
        """Testa números de vagas válidos."""
        assert validate_vagas(30) == (True, "")
        assert validate_vagas(1) == (True, "")    # Mínimo
        assert validate_vagas(999) == (True, "")  # Máximo
        assert validate_vagas("30") == (True, "")  # String numérica
    
    def test_validate_vagas_invalid(self):
        """Testa números de vagas inválidos."""
        assert validate_vagas(0) == (False, "Número de vagas deve ser maior que zero")
        assert validate_vagas(-1) == (False, "Número de vagas deve ser maior que zero")
        assert validate_vagas(1000) == (False, "Número de vagas parece excessivo (máximo: 999)")
        assert validate_vagas("abc") == (False, "Número de vagas deve ser um número inteiro válido")
        assert validate_vagas(None) == (False, "Número de vagas deve ser um número inteiro")


class TestSIGADValidation:
    """Testes para validação de SIGAD."""
    
    def test_validate_sigad_valid(self):
        """Testa números SIGAD válidos."""
        assert validate_sigad("12345/2024") is True
        assert validate_sigad("123456789") is True
        assert validate_sigad("PROC-12345-2024") is True
    
    def test_validate_sigad_invalid(self):
        """Testa números SIGAD inválidos."""
        assert validate_sigad("1234") is False  # Muito curto
        assert validate_sigad("") is False
        assert validate_sigad(None) is False
        assert validate_sigad("<script>") is False


class TestCursoValidation:
    """Testes para validação completa de curso."""
    
    def test_validate_curso_valid(self):
        """Testa dados de curso válidos."""
        data = {
            'nome': 'Curso de Teste',
            'turma': '2024-001',
            'vagas': 30,
            'data_inicio': '01/01/2024',
            'data_fim': '31/12/2024',
            'sigad': '12345/2024',
        }
        is_valid, errors = validate_curso(data)
        assert is_valid is True
        assert errors == []
    
    def test_validate_curso_invalid(self):
        """Testa dados de curso inválidos."""
        data = {
            'nome': '',  # Vazio
            'turma': 'A',  # Muito curto
            'vagas': 0,  # Inválido
            'data_inicio': 'invalid',
            'data_fim': '01/01/2024',  # Antes do início
            'sigad': '123',
        }
        is_valid, errors = validate_curso(data)
        assert is_valid is False
        assert len(errors) > 0
        assert any("Nome do curso" in e for e in errors)
        assert any("turma" in e.lower() for e in errors)
    
    def test_validate_curso_empty(self):
        """Testa validação com dados vazios."""
        is_valid, errors = validate_curso({})
        assert is_valid is False
        assert len(errors) > 0
        
        is_valid, errors = validate_curso(None)
        assert is_valid is False


# =============================================================================
# TESTES DE VALIDAÇÃO DE EMAIL E TELEFONE
# =============================================================================

class TestEmailValidation:
    """Testes para validação de e-mail."""
    
    def test_validate_email_valid(self):
        """Testa e-mails válidos."""
        assert validate_email("usuario@exemplo.com") is True
        assert validate_email("teste.teste@dominio.com.br") is True
        assert validate_email("nome+tag@email.org") is True
        assert validate_email("user123@test.io") is True
    
    def test_validate_email_invalid(self):
        """Testa e-mails inválidos."""
        assert validate_email("usuario@exemplo") is False  # Sem TLD
        assert validate_email("usuario@.com") is False
        assert validate_email("@exemplo.com") is False
        assert validate_email("usuario@") is False
        assert validate_email("usuario@@exemplo.com") is False
        assert validate_email("usuario@exemplo..com") is False
        assert validate_email("") is False
        assert validate_email(None) is False
        assert validate_email("invalido") is False


class TestPhoneValidation:
    """Testes para validação de telefone."""
    
    def test_clean_phone(self):
        """Testa limpeza de telefone."""
        assert clean_phone("(11) 98765-4321") == "11987654321"
        assert clean_phone("11 98765-4321") == "11987654321"
        assert clean_phone("+55 (11) 98765-4321") == "5511987654321"
    
    def test_validate_phone_valid(self):
        """Testa telefones válidos."""
        assert validate_phone("(11) 98765-4321") == "(11) 98765-4321"
        assert validate_phone("11987654321") == "(11) 98765-4321"
        assert validate_phone("(11) 8765-4321") == "(11) 8765-4321"  # Fixo
        assert validate_phone("1187654321") == "(11) 8765-4321"
    
    def test_validate_phone_invalid(self):
        """Testa telefones inválidos."""
        assert validate_phone("123") is None  # Muito curto
        assert validate_phone("123456789012") is None  # Muito longo
        assert validate_phone("(00) 98765-4321") is None  # DDD inválido
        assert validate_phone("") is None
        assert validate_phone(None) is None
        assert validate_phone("ABC") is None


# =============================================================================
# TESTES DE VALIDAÇÃO DE FIC
# =============================================================================

class TestFICValidation:
    """Testes para validação completa de FIC."""
    
    def test_validate_fic_valid(self):
        """Testa dados de FIC válidos."""
        data = {
            'nome': 'João da Silva',
            'cpf': '529.982.247-25',
            'saram': '123456',
            'email': 'joao@email.com',
            'telefone': '(11) 98765-4321',
            'curso': 'CILE',
            'turma': '2024-001',
            'data_inicio': '01/01/2024',
            'data_fim': '31/12/2024',
        }
        is_valid, errors = validate_fic(data)
        assert is_valid is True
        assert errors == []
    
    def test_validate_fic_invalid(self):
        """Testa dados de FIC inválidos."""
        data = {
            'nome': '',  # Obrigatório
            'cpf': '111.111.111-11',  # Inválido
            'saram': '123',  # Muito curto
            'email': 'invalido',
            'telefone': '123',
            'nota_teorica': 150,  # Fora do range
        }
        is_valid, errors = validate_fic(data)
        assert is_valid is False
        assert len(errors) > 0


# =============================================================================
# TESTES DE UTILITÁRIOS DE TEXTO
# =============================================================================

class TestSanitizeString:
    """Testes para sanitização de strings."""
    
    def test_sanitize_string_removes_dangerous_chars(self):
        """Testa remoção de caracteres perigosos."""
        assert sanitize_string("<script>alert('xss')</script>") == "scriptalert(xss)/script"
        assert sanitize_string("DROP TABLE users; --") == "DROP TABLE users"
        assert sanitize_string('"quoted"') == "quoted"
    
    def test_sanitize_string_empty(self):
        """Testa sanitização de strings vazias."""
        assert sanitize_string("") == ""
        assert sanitize_string(None) == ""


class TestNormalizeText:
    """Testes para normalização de texto."""
    
    def test_normalize_text(self):
        """Testa normalização de texto."""
        assert normalize_text("  texto ExEmPlO  ") == "TEXTO EXEMPLO"
        assert normalize_text("outro   exemplo") == "OUTRO EXEMPLO"
        assert normalize_text("  espaços  extras  ") == "ESPAÇOS EXTRAS"
    
    def test_normalize_text_empty(self):
        """Testa normalização de texto vazio."""
        assert normalize_text("") == ""
        assert normalize_text(None) == ""


class TestTruncateString:
    """Testes para truncamento de strings."""
    
    def test_truncate_string(self):
        """Testa truncamento de strings."""
        assert truncate_string("Hello World", 5) == "He..."
        assert truncate_string("Hello", 10) == "Hello"
        assert truncate_string("", 10) == ""
        assert truncate_string(None, 10) == ""


class TestSlugify:
    """Testes para criação de slugs."""
    
    def test_slugify(self):
        """Testa criação de slugs."""
        assert slugify("Título do Curso 2024!") == "titulo-do-curso-2024"
        assert slugify("  espaços  extras  ") == "espacos-extras"
        assert slugify("São Paulo") == "sao-paulo"  # Sem acentos
    
    def test_slugify_empty(self):
        """Testa slugify com texto vazio."""
        assert slugify("") == ""
        assert slugify(None) == ""


# =============================================================================
# TESTES DE VALIDAÇÃO DE NOTAS E FREQUÊNCIA
# =============================================================================

class TestNotaValidation:
    """Testes para validação de notas."""
    
    def test_validate_nota_valid(self):
        """Testa notas válidas."""
        assert validate_nota(0) == (True, "")
        assert validate_nota(100) == (True, "")
        assert validate_nota(75.5) == (True, "")
        assert validate_nota("85,5") == (True, "")  # Com vírgula
    
    def test_validate_nota_invalid(self):
        """Testa notas inválidas."""
        assert validate_nota(-1) == (False, "Nota geral deve estar entre 0 e 100")
        assert validate_nota(101) == (False, "Nota geral deve estar entre 0 e 100")
        assert validate_nota("abc") == (False, "Nota geral deve ser um número válido")


class TestFrequenciaValidation:
    """Testes para validação de frequência."""
    
    def test_validate_frequencia_valid(self):
        """Testa frequências válidas."""
        assert validate_frequencia(0) == (True, "")
        assert validate_frequencia(100) == (True, "")
        assert validate_frequencia(75) == (True, "")
    
    def test_validate_frequencia_invalid(self):
        """Testa frequências inválidas."""
        assert validate_frequencia(-1) == (False, "Frequência deve estar entre 0% e 100%")
        assert validate_frequencia(101) == (False, "Frequência deve estar entre 0% e 100%")
        assert validate_frequencia("abc") == (False, "Frequência deve ser um número válido")


class TestAnoValidation:
    """Testes para validação de ano."""
    
    def test_validate_ano_valid(self):
        """Testa anos válidos."""
        assert validate_ano(2024) == (True, "")
        assert validate_ano(1900) == (True, "")
        assert validate_ano("2025") == (True, "")
    
    def test_validate_ano_invalid(self):
        """Testa anos inválidos."""
        assert validate_ano(1899)[0] is False  # Antes de 1900
        assert validate_ano("abc") == (False, "Ano deve ser um número inteiro válido")


class TestCargaHorariaValidation:
    """Testes para validação de carga horária."""
    
    def test_validate_carga_horaria_valid(self):
        """Testa cargas horárias válidas."""
        assert validate_carga_horaria(1) == (True, "")
        assert validate_carga_horaria(2000) == (True, "")
        assert validate_carga_horaria(40) == (True, "")
    
    def test_validate_carga_horaria_invalid(self):
        """Testa cargas horárias inválidas."""
        assert validate_carga_horaria(0) == (False, "Carga horária deve ser maior que zero")
        assert validate_carga_horaria(2001) == (False, "Carga horária parece excessiva (máximo: 2000h)")
        assert validate_carga_horaria("abc") == (False, "Carga horária deve ser um número inteiro válido")
