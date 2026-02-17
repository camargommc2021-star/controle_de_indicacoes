"""
Testes unitários para o módulo data_manager.py.

Testa todas as operações CRUD do DataManager,
incluindo gerenciamento de cursos e integração com GitHub.
"""

import pytest
import pandas as pd
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from data_manager import DataManager


# =============================================================================
# TESTES DE CRIAÇÃO DE ARQUIVO
# =============================================================================

class TestCriarArquivo:
    """Testes para criação de arquivo de dados."""
    
    def test_criar_arquivo_se_nao_existir(self, temp_data_manager):
        """Testa criação automática do arquivo se não existir."""
        dm = temp_data_manager
        assert os.path.exists(dm.arquivo_local)
    
    def test_criar_arquivo_com_colunas_corretas(self, temp_data_manager):
        """Testa se o arquivo é criado com as colunas corretas."""
        dm = temp_data_manager
        df = dm.carregar_dados()
        
        for col in dm.colunas_base:
            assert col in df.columns, f"Coluna {col} não encontrada"
    
    def test_carregar_dados_arquivo_vazio(self, temp_data_manager):
        """Testa carregamento de arquivo vazio."""
        dm = temp_data_manager
        df = dm.carregar_dados()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
        assert len(df.columns) == len(dm.colunas)


# =============================================================================
# TESTES DE ADIÇÃO DE CURSO
# =============================================================================

class TestAdicionarCurso:
    """Testes para adição de cursos."""
    
    def test_adicionar_curso_sucesso(self, temp_data_manager, sample_curso_data):
        """Testa adição bem-sucedida de um curso."""
        dm = temp_data_manager
        
        sucesso, mensagem = dm.adicionar_curso(sample_curso_data)
        
        assert sucesso is True
        assert "sucesso" in mensagem.lower() or "cadastrado" in mensagem.lower()
    
    def test_adicionar_curso_verifica_duplicados(self, temp_data_manager, sample_curso_data):
        """Testa verificação de cursos duplicados."""
        dm = temp_data_manager
        
        # Adicionar primeiro curso
        dm.adicionar_curso(sample_curso_data)
        
        # Tentar adicionar o mesmo curso novamente
        sucesso, mensagem = dm.adicionar_curso(sample_curso_data)
        
        assert sucesso is False
        assert "já existe" in mensagem.lower() or "duplicado" in mensagem.lower()
    
    def test_adicionar_curso_adiciona_colunas_om(self, temp_data_manager):
        """Testa adição dinâmica de colunas de OM."""
        dm = temp_data_manager
        
        curso_com_om = {
            'Curso': 'Curso Teste',
            'Turma': '2024-001',
            'Vagas': 30,
            'OM_GCC': '5 vagas',
            'OM_CINDACTA_I': '3 vagas',
        }
        
        dm.adicionar_curso(curso_com_om)
        df = dm.carregar_dados()
        
        assert 'OM_GCC' in df.columns
        assert 'OM_CINDACTA_I' in df.columns
    
    def test_adicionar_curso_completa_campos_ausentes(self, temp_data_manager):
        """Testa preenchimento automático de campos ausentes."""
        dm = temp_data_manager
        
        curso_incompleto = {
            'Curso': 'Curso Teste',
            'Turma': '2024-001',
        }
        
        dm.adicionar_curso(curso_incompleto)
        df = dm.carregar_dados()
        
        assert len(df) == 1
        # Campos ausentes devem ser preenchidos com string vazia
        assert df.iloc[0]['Vagas'] == "" or df.iloc[0]['Vagas'] == 0


# =============================================================================
# TESTES DE ATUALIZAÇÃO DE CURSO
# =============================================================================

class TestAtualizarCurso:
    """Testes para atualização de cursos."""
    
    def test_atualizar_curso_sucesso(self, temp_data_manager, sample_curso_data):
        """Testa atualização bem-sucedida de um curso."""
        dm = temp_data_manager
        
        # Adicionar curso
        dm.adicionar_curso(sample_curso_data)
        
        # Atualizar curso
        dados_atualizados = {
            'Curso': 'Curso Atualizado',
            'Vagas': 50,
        }
        
        sucesso, mensagem = dm.atualizar_curso(0, dados_atualizados)
        
        assert sucesso is True
        
        # Verificar se foi atualizado
        df = dm.carregar_dados()
        assert df.iloc[0]['Curso'] == 'Curso Atualizado'
        assert df.iloc[0]['Vagas'] == 50
    
    def test_atualizar_curso_index_invalido(self, temp_data_manager):
        """Testa atualização com índice inválido."""
        dm = temp_data_manager
        
        sucesso, mensagem = dm.atualizar_curso(999, {'Curso': 'Teste'})
        
        assert sucesso is False
        assert "nao encontrado" in mensagem.lower() or "não encontrado" in mensagem.lower()
    
    def test_atualizar_curso_index_negativo(self, temp_data_manager):
        """Testa atualização com índice negativo."""
        dm = temp_data_manager
        
        sucesso, mensagem = dm.atualizar_curso(-1, {'Curso': 'Teste'})
        
        assert sucesso is False


# =============================================================================
# TESTES DE EXCLUSÃO DE CURSO
# =============================================================================

class TestExcluirCurso:
    """Testes para exclusão de cursos."""
    
    def test_excluir_curso_sucesso(self, temp_data_manager, sample_curso_data):
        """Testa exclusão bem-sucedida de um curso."""
        dm = temp_data_manager
        
        # Adicionar curso
        dm.adicionar_curso(sample_curso_data)
        assert len(dm.carregar_dados()) == 1
        
        # Excluir curso
        sucesso, mensagem = dm.excluir_curso(0)
        
        assert sucesso is True
        assert len(dm.carregar_dados()) == 0
    
    def test_excluir_curso_index_invalido(self, temp_data_manager):
        """Testa exclusão com índice inválido."""
        dm = temp_data_manager
        
        sucesso, mensagem = dm.excluir_curso(999)
        
        assert sucesso is False
        assert "nao encontrado" in mensagem.lower() or "não encontrado" in mensagem.lower()
    
    def test_excluir_todos_cursos(self, temp_data_manager, sample_curso_list):
        """Testa exclusão de todos os cursos."""
        dm = temp_data_manager
        
        # Adicionar vários cursos
        for curso in sample_curso_list:
            # Ajustar turma para evitar duplicados
            dm.adicionar_curso(curso)
        
        # Excluir todos
        sucesso, mensagem = dm.excluir_todos_cursos()
        
        assert sucesso is True
        df = dm.carregar_dados()
        assert len(df) == 0
        # Colunas devem ser preservadas
        assert 'Curso' in df.columns


# =============================================================================
# TESTES DE BUSCA DE CURSO
# =============================================================================

class TestBuscarCurso:
    """Testes para busca de cursos."""
    
    def test_buscar_curso_por_nome(self, temp_data_manager, sample_curso_list):
        """Testa busca por nome do curso."""
        dm = temp_data_manager
        
        # Adicionar cursos
        for curso in sample_curso_list:
            dm.adicionar_curso(curso.copy())
        
        # Buscar
        resultados = dm.buscar_curso("CILE")
        
        assert len(resultados) >= 2
        assert all("CILE" in str(row['Curso']) for _, row in resultados.iterrows())
    
    def test_buscar_curso_por_turma(self, temp_data_manager, sample_curso_data):
        """Testa busca por turma."""
        dm = temp_data_manager
        dm.adicionar_curso(sample_curso_data)
        
        resultados = dm.buscar_curso("2024-001")
        
        assert len(resultados) == 1
    
    def test_buscar_curso_termo_vazio(self, temp_data_manager, sample_curso_list):
        """Testa busca com termo vazio retorna todos os cursos."""
        dm = temp_data_manager
        
        for curso in sample_curso_list:
            dm.adicionar_curso(curso.copy())
        
        resultados = dm.buscar_curso("")
        
        assert len(resultados) == len(sample_curso_list)
    
    def test_buscar_curso_sem_resultados(self, temp_data_manager, sample_curso_data):
        """Testa busca sem resultados."""
        dm = temp_data_manager
        dm.adicionar_curso(sample_curso_data)
        
        resultados = dm.buscar_curso("TERMO_INEXISTENTE")
        
        assert len(resultados) == 0


# =============================================================================
# TESTES DE VERIFICAÇÃO DE DUPLICADOS
# =============================================================================

class TestVerificarDuplicados:
    """Testes para verificação de cursos duplicados."""
    
    def test_verificar_duplicados_detecta_repetidos(self, temp_data_manager, sample_curso_data):
        """Testa detecção de cursos duplicados."""
        dm = temp_data_manager
        
        # Adicionar curso
        dm.adicionar_curso(sample_curso_data)
        
        # Tentar adicionar duplicado
        sucesso, mensagem = dm.adicionar_curso(sample_curso_data)
        
        assert sucesso is False
        assert "já existe" in mensagem.lower()
    
    def test_verificar_duplicados_mesmo_curso_turma_diferente(self, temp_data_manager, sample_curso_data):
        """Testa que mesmo curso com turma diferente não é duplicado."""
        dm = temp_data_manager
        
        # Adicionar curso
        dm.adicionar_curso(sample_curso_data)
        
        # Adicionar mesmo curso com turma diferente
        curso_diferente = sample_curso_data.copy()
        curso_diferente['Turma'] = '2024-002'
        
        sucesso, _ = dm.adicionar_curso(curso_diferente)
        
        assert sucesso is True


# =============================================================================
# TESTES DE COLUNAS OM
# =============================================================================

class TestColunasOM:
    """Testes para gerenciamento de colunas de OM."""
    
    def test_adicionar_coluna_om(self, temp_data_manager):
        """Testa adição de coluna de OM."""
        dm = temp_data_manager
        
        nome_campo = dm.adicionar_coluna_om("CINDACTA I")
        
        assert nome_campo == "OM_CINDACTA_I"
        assert nome_campo in dm.colunas
    
    def test_adicionar_coluna_om_duplicada(self, temp_data_manager):
        """Testa adição de coluna OM já existente."""
        dm = temp_data_manager
        
        # Adicionar primeira vez
        nome_campo1 = dm.adicionar_coluna_om("CINDACTA I")
        colunas_antes = len(dm.colunas)
        
        # Adicionar segunda vez
        nome_campo2 = dm.adicionar_coluna_om("CINDACTA I")
        
        assert nome_campo1 == nome_campo2
        assert len(dm.colunas) == colunas_antes  # Não deve duplicar
    
    def test_get_colunas_om(self, temp_data_manager):
        """Testa obtenção de colunas de OM."""
        dm = temp_data_manager
        
        dm.adicionar_coluna_om("CINDACTA I")
        dm.adicionar_coluna_om("CINDACTA II")
        
        colunas_om = dm.get_colunas_om()
        
        assert "OM_CINDACTA_I" in colunas_om
        assert "OM_CINDACTA_II" in colunas_om
        assert "OM_Executora" not in colunas_om  # Não deve incluir OM_Executora


# =============================================================================
# TESTES DE EXPORTAÇÃO
# =============================================================================

class TestExportar:
    """Testes para exportação de dados."""
    
    def test_exportar_excel_bytes(self, temp_data_manager, sample_curso_data):
        """Testa exportação para bytes Excel."""
        dm = temp_data_manager
        dm.adicionar_curso(sample_curso_data)
        
        excel_bytes = dm.exportar_excel_bytes()
        
        assert isinstance(excel_bytes, bytes)
        assert len(excel_bytes) > 0


# =============================================================================
# TESTES DE INTEGRAÇÃO COM GITHUB (MOCKADOS)
# =============================================================================

class TestGitHubIntegration:
    """Testes para integração com GitHub (usando mocks)."""
    
    def test_verificar_status_github_desabilitado(self, temp_data_manager):
        """Testa verificação de status quando GitHub está desabilitado."""
        dm = temp_data_manager
        dm.github_manager = None
        
        autenticado, mensagem = dm.verificar_status_github()
        
        assert autenticado is False
        assert "nao habilitado" in mensagem.lower() or "não habilitado" in mensagem.lower()
    
    def test_verificar_status_github_autenticado(self, temp_data_manager, mock_github_manager):
        """Testa verificação de status quando autenticado."""
        dm = temp_data_manager
        dm.github_manager = mock_github_manager
        
        autenticado, mensagem = dm.verificar_status_github()
        
        assert autenticado is True
        mock_github_manager.verificar_autenticacao.assert_called_once()


# =============================================================================
# TESTES DE TRATAMENTO DE ERROS
# =============================================================================

class TestTratamentoErros:
    """Testes para tratamento de erros."""
    
    def test_carregar_dados_arquivo_corrompido(self, temp_data_manager):
        """Testa carregamento de arquivo corrompido."""
        dm = temp_data_manager
        
        # Criar arquivo inválido
        with open(dm.arquivo_local, 'w') as f:
            f.write("conteúdo inválido")
        
        # Não deve lançar exceção
        df = dm.carregar_dados()
        assert isinstance(df, pd.DataFrame)
