"""
Testes unitários para o módulo validators.

Executar com:
    python -m unittest utils.test_validators -v
"""

import unittest
from datetime import datetime, date, timedelta
import pandas as pd

from utils.validators import (
    # Validação de datas
    is_valid_date, parse_date, parse_data, is_future_date, date_range_valid,
    # Validação de campos do curso
    validate_turma, validate_vagas, validate_sigad, validate_curso,
    # Conclusão e métricas
    curso_concluido, calcular_metricas_prazos,
    # Utilitários
    sanitize_string, normalize_text, slugify
)


class TestValidators(unittest.TestCase):
    """Casos de teste para funções de validação e utilitários."""

    def test_dates(self):
        """Testa funções de validação de datas."""
        # Testes is_valid_date
        self.assertTrue(is_valid_date("25/12/2023"))
        self.assertFalse(is_valid_date("32/12/2023"))
        self.assertTrue(is_valid_date("2023-12-25", "%Y-%m-%d"))

        # Testes parse_date
        result = parse_date("25/12/2023")
        self.assertIsNotNone(result)
        self.assertEqual(result.year, 2023)
        self.assertIsNone(parse_date("invalido"))

        # Testes parse_data
        self.assertEqual(parse_data('05/10/2026'), date(2026, 10, 5))
        self.assertEqual(parse_data('2026-10-05'), date(2026, 10, 5))
        self.assertEqual(parse_data(pd.Timestamp('2026-10-05')), date(2026, 10, 5))
        self.assertEqual(parse_data(datetime(2026, 10, 5)), date(2026, 10, 5))
        self.assertEqual(parse_data(date(2026, 10, 5)), date(2026, 10, 5))
        self.assertIsNone(parse_data(None))
        self.assertIsNone(parse_data(float('nan')))
        self.assertIsNone(parse_data('nan'))
        self.assertIsNone(parse_data(''))
        self.assertIsNone(parse_data(pd.NaT))

        # Testes is_future_date
        self.assertTrue(is_future_date("25/12/2030"))
        self.assertFalse(is_future_date("25/12/2000"))

        # Testes date_range_valid
        self.assertTrue(date_range_valid("01/01/2023", "31/12/2023"))
        self.assertFalse(date_range_valid("31/12/2023", "01/01/2023"))

    def test_curso(self):
        """Testa funções de validação de campos do curso."""
        # Testes turma
        self.assertTrue(validate_turma("T-001"))
        self.assertTrue(validate_turma("AB"))
        self.assertFalse(validate_turma("A"))  # Muito curto
        self.assertFalse(validate_turma("<script>"))  # Caracteres perigosos

        # Testes vagas
        valid, msg = validate_vagas(30)
        self.assertTrue(valid)
        self.assertEqual(msg, "")
        valid, msg = validate_vagas(0)
        self.assertFalse(valid)
        valid, msg = validate_vagas("abc")
        self.assertFalse(valid)

        # Testes SIGAD
        self.assertTrue(validate_sigad("12345/2023"))
        self.assertFalse(validate_sigad("AB"))  # Muito curto

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
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)

        curso_invalido = {
            'nome': '',
            'turma': 'A',
            'vagas': 0,
            'data_inicio': '32/13/2024'
        }
        valid, errors = validate_curso(curso_invalido)
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)

    def test_utilities(self):
        """Testa funções utilitárias."""
        # Testes sanitize_string
        self.assertEqual(sanitize_string("<script>alert(xss)</script>"), "scriptalert(xss)/script")
        self.assertEqual(sanitize_string("DROP TABLE users; --"), "DROP TABLE users")

        # Testes normalize_text
        self.assertEqual(normalize_text("  texto ExEmPlO  "), "TEXTO EXEMPLO")
        self.assertEqual(normalize_text("outro   exemplo"), "OUTRO EXEMPLO")

        # Testes slugify
        self.assertEqual(slugify("Título do Curso 2024!"), "titulo-do-curso-2024")
        self.assertEqual(slugify("  Espaços  Extras  "), "espacos-extras")

    def test_conclusao_e_metricas(self):
        """Testa detecção de curso concluído e cálculo de métricas de prazos."""
        # Testes curso_concluido
        self.assertTrue(curso_concluido({'Estado': 'Concluído'}))
        self.assertTrue(curso_concluido({'Estado': 'concluido'}))
        self.assertTrue(curso_concluido({'Estado': 'CONCLUÍDO'}))
        self.assertTrue(curso_concluido({'Estado': '  Concluída  '}))
        self.assertTrue(curso_concluido({'Estado': 'solicitar voluntários', 'DATA_DA_CONCLUSAO': '01/01/2026'}))
        self.assertFalse(curso_concluido({'Estado': 'solicitar voluntários', 'DATA_DA_CONCLUSAO': ''}))
        self.assertFalse(curso_concluido({'Estado': 'solicitar voluntários', 'DATA_DA_CONCLUSAO': None}))
        self.assertFalse(curso_concluido(None))

        # Testes calcular_metricas_prazos
        hoje = date.today()
        passado = (hoje - timedelta(days=10)).strftime('%d/%m/%Y')
        urgente = (hoje + timedelta(days=2)).strftime('%d/%m/%Y')
        chefia = (hoje + timedelta(days=3)).strftime('%d/%m/%Y')

        df_teste = pd.DataFrame([
            {'Curso': 'C1', 'Fim da indicação da SIAT': passado, 'Prazo dado pela chefia': None, 'Estado': 'solicitar voluntários'},
            {'Curso': 'C2', 'Fim da indicação da SIAT': passado, 'Prazo dado pela chefia': None, 'Estado': 'Concluído'},
            {'Curso': 'C3', 'Fim da indicação da SIAT': urgente, 'Prazo dado pela chefia': chefia, 'Estado': 'fazer indicação'},
            {'Curso': 'C4', 'Fim da indicação da SIAT': urgente, 'Prazo dado pela chefia': chefia, 'Estado': 'fazer indicação', 'DATA_DA_CONCLUSAO': '01/01/2026'},
        ])

        metricas = calcular_metricas_prazos(df_teste)
        self.assertEqual(metricas['atrasados'], 1)
        self.assertEqual(metricas['urgentes'], 1)
        self.assertEqual(metricas['chefia_proximo'], 1)


if __name__ == "__main__":
    unittest.main()
