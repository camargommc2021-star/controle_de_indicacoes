"""
Testes unitários para o módulo managers/base_manager.py.

Testa a classe abstrata BaseManager e suas funcionalidades base.
"""

import pytest
import pandas as pd
import os
import sys
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from managers.base_manager import BaseManager


# =============================================================================
# CLASSE CONCRETA PARA TESTES
# =============================================================================

class ConcreteManager(BaseManager):
    """Implementação concreta para testar BaseManager."""
    
    def adicionar(self, dados):
        """Implementação de adicionar."""
        df = self.carregar_dados()
        df = pd.concat([df, pd.DataFrame([dados])], ignore_index=True)
        sucesso = self._salvar_dados(df)
        return sucesso, "Adicionado" if sucesso else "Erro"
    
    def atualizar(self, id_valor, dados, coluna_id='ID'):
        """Implementação de atualizar."""
        df = self.carregar_dados()
        mask = df[coluna_id] == id_valor
        if not mask.any():
            return False, "Não encontrado"
        
        for col, val in dados.items():
            if col in df.columns and col != coluna_id:
                df.loc[mask, col] = val
        
        sucesso = self._salvar_dados(df)
        return sucesso, "Atualizado" if sucesso else "Erro"


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def temp_manager():
    """Cria um ConcreteManager com diretório temporário."""
    temp_dir = tempfile.mkdtemp()
    arquivo = os.path.join(temp_dir, "test.xlsx")
    colunas = ['ID', 'Nome', 'Status', 'Valor']
    
    manager = ConcreteManager(arquivo, colunas)
    
    yield manager
    
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_data():
    """Retorna dados de exemplo."""
    return {
        'ID': '001',
        'Nome': 'Teste',
        'Status': 'Ativo',
        'Valor': 100,
    }


# =============================================================================
# TESTES DE INICIALIZAÇÃO
# =============================================================================

class TestInicializacao:
    """Testes para inicialização do BaseManager."""
    
    def test_inicializacao_cria_arquivo(self, temp_manager):
        """Testa se o arquivo é criado na inicialização."""
        assert os.path.exists(temp_manager.arquivo)
    
    def test_inicializacao_colunas(self, temp_manager):
        """Testa se as colunas são definidas corretamente."""
        assert temp_manager.colunas == ['ID', 'Nome', 'Status', 'Valor']
    
    def test_inicializacao_colunas_vazias(self):
        """Testa que colunas vazias lançam erro."""
        with pytest.raises(ValueError, match="lista de colunas não pode estar vazia"):
            ConcreteManager("test.xlsx", [])
    
    def test_inicializacao_cria_diretorio(self):
        """Testa criação automática de diretório."""
        temp_dir = tempfile.mkdtemp()
        subdir = os.path.join(temp_dir, "sub", "dir")
        arquivo = os.path.join(subdir, "test.xlsx")
        
        try:
            manager = ConcreteManager(arquivo, ['ID', 'Nome'])
            assert os.path.exists(subdir)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


# =============================================================================
# TESTES DE CARREGAMENTO DE DADOS
# =============================================================================

class TestCarregarDados:
    """Testes para carregamento de dados."""
    
    def test_carregar_dados_vazio(self, temp_manager):
        """Testa carregamento de arquivo vazio."""
        df = temp_manager.carregar_dados()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
        assert list(df.columns) == ['ID', 'Nome', 'Status', 'Valor']
    
    def test_carregar_dados_adiciona_colunas_faltantes(self, temp_manager):
        """Testa adição de colunas faltantes."""
        # Criar arquivo com colunas incompletas
        df_incompleto = pd.DataFrame({
            'ID': ['001'],
            'Nome': ['Teste'],
        })
        df_incompleto.to_excel(temp_manager.arquivo, index=False, engine='openpyxl')
        
        df = temp_manager.carregar_dados()
        
        assert 'Status' in df.columns
        assert 'Valor' in df.columns
    
    def test_carregar_dados_reordena_colunas(self, temp_manager):
        """Testa reordenação de colunas."""
        # Criar arquivo com colunas em ordem diferente
        df_desordenado = pd.DataFrame({
            'Valor': [100],
            'ID': ['001'],
            'Status': ['Ativo'],
            'Nome': ['Teste'],
        })
        df_desordenado.to_excel(temp_manager.arquivo, index=False, engine='openpyxl')
        
        df = temp_manager.carregar_dados()
        
        # Primeiras colunas devem ser as definidas
        assert list(df.columns[:4]) == ['ID', 'Nome', 'Status', 'Valor']


# =============================================================================
# TESTES DE SALVAMENTO
# =============================================================================

class TestSalvarDados:
    """Testes para salvamento de dados."""
    
    def test_salvar_dados_sucesso(self, temp_manager, sample_data):
        """Testa salvamento bem-sucedido."""
        df = pd.DataFrame([sample_data])
        
        sucesso = temp_manager._salvar_dados(df)
        
        assert sucesso is True
    
    def test_salvar_dados_adiciona_colunas_faltantes(self, temp_manager):
        """Testa adição de colunas faltantes no salvamento."""
        df_incompleto = pd.DataFrame({
            'ID': ['001'],
            'Nome': ['Teste'],
        })
        
        temp_manager._salvar_dados(df_incompleto)
        
        # Verificar se colunas foram adicionadas no arquivo
        df_carregado = pd.read_excel(temp_manager.arquivo, engine='openpyxl')
        assert 'Status' in df_carregado.columns
        assert 'Valor' in df_carregado.columns
    
    def test_salvar_dados_reordena_colunas(self, temp_manager):
        """Testa reordenação de colunas no salvamento."""
        df_desordenado = pd.DataFrame({
            'Valor': [100],
            'ID': ['001'],
            'Status': ['Ativo'],
            'Nome': ['Teste'],
        })
        
        temp_manager._salvar_dados(df_desordenado)
        
        df_carregado = pd.read_excel(temp_manager.arquivo, engine='openpyxl')
        assert list(df_carregado.columns[:4]) == ['ID', 'Nome', 'Status', 'Valor']


# =============================================================================
# TESTES DE BUSCA
# =============================================================================

class TestBuscar:
    """Testes para busca de registros."""
    
    def test_buscar_por_id_encontrado(self, temp_manager, sample_data):
        """Testa busca por ID existente."""
        temp_manager.adicionar(sample_data)
        
        registro = temp_manager.buscar_por_id('001')
        
        assert registro is not None
        assert registro['ID'] == '001'
        assert registro['Nome'] == 'Teste'
    
    def test_buscar_por_id_nao_encontrado(self, temp_manager):
        """Testa busca por ID inexistente."""
        registro = temp_manager.buscar_por_id('999')
        
        assert registro is None
    
    def test_buscar_por_id_coluna_diferente(self, temp_manager, sample_data):
        """Testa busca por coluna diferente de ID."""
        temp_manager.adicionar(sample_data)
        
        registro = temp_manager.buscar_por_id('Teste', coluna_id='Nome')
        
        assert registro is not None
        assert registro['Nome'] == 'Teste'
    
    def test_buscar_por_id_coluna_inexistente(self, temp_manager):
        """Testa busca por coluna inexistente."""
        registro = temp_manager.buscar_por_id('valor', coluna_id='ColunaInexistente')
        
        assert registro is None


# =============================================================================
# TESTES DE EXCLUSÃO
# =============================================================================

class TestExcluir:
    """Testes para exclusão de registros."""
    
    def test_excluir_por_id_sucesso(self, temp_manager, sample_data):
        """Testa exclusão bem-sucedida."""
        temp_manager.adicionar(sample_data)
        assert temp_manager.contar_registros() == 1
        
        sucesso, mensagem = temp_manager.excluir_por_id('001')
        
        assert sucesso is True
        assert temp_manager.contar_registros() == 0
    
    def test_excluir_por_id_nao_encontrado(self, temp_manager):
        """Testa exclusão de ID inexistente."""
        sucesso, mensagem = temp_manager.excluir_por_id('999')
        
        assert sucesso is False
        assert "não encontrado" in mensagem.lower()
    
    def test_excluir_preserva_outros(self, temp_manager):
        """Testa que exclusão preserva outros registros."""
        temp_manager.adicionar({'ID': '001', 'Nome': 'Primeiro'})
        temp_manager.adicionar({'ID': '002', 'Nome': 'Segundo'})
        temp_manager.adicionar({'ID': '003', 'Nome': 'Terceiro'})
        
        temp_manager.excluir_por_id('002')
        
        assert temp_manager.contar_registros() == 2
        assert temp_manager.existe_registro('001')
        assert not temp_manager.existe_registro('002')
        assert temp_manager.existe_registro('003')


# =============================================================================
# TESTES DE CONSULTAS
# =============================================================================

class TestConsultas:
    """Testes para consultas diversas."""
    
    def test_contar_registros_vazio(self, temp_manager):
        """Testa contagem com arquivo vazio."""
        assert temp_manager.contar_registros() == 0
    
    def test_contar_registros_com_dados(self, temp_manager):
        """Testa contagem com dados."""
        temp_manager.adicionar({'ID': '001', 'Nome': 'Teste 1'})
        temp_manager.adicionar({'ID': '002', 'Nome': 'Teste 2'})
        
        assert temp_manager.contar_registros() == 2
    
    def test_listar_todos_vazio(self, temp_manager):
        """Testa listagem com arquivo vazio."""
        registros = temp_manager.listar_todos()
        
        assert isinstance(registros, list)
        assert len(registros) == 0
    
    def test_listar_todos_com_dados(self, temp_manager):
        """Testa listagem com dados."""
        temp_manager.adicionar({'ID': '001', 'Nome': 'Teste'})
        
        registros = temp_manager.listar_todos()
        
        assert isinstance(registros, list)
        assert len(registros) == 1
        assert registros[0]['ID'] == '001'
    
    def test_existe_registro_true(self, temp_manager, sample_data):
        """Testa verificação de existência (existe)."""
        temp_manager.adicionar(sample_data)
        
        assert temp_manager.existe_registro('001') is True
    
    def test_existe_registro_false(self, temp_manager):
        """Testa verificação de existência (não existe)."""
        assert temp_manager.existe_registro('999') is False
    
    def test_obter_colunas_atuais(self, temp_manager, sample_data):
        """Testa obtenção de colunas."""
        temp_manager.adicionar(sample_data)
        
        colunas = temp_manager.obter_colunas_atuais()
        
        assert isinstance(colunas, list)
        assert 'ID' in colunas
        assert 'Nome' in colunas


# =============================================================================
# TESTES DE MÉTODOS ABSTRATOS
# =============================================================================

class TestMetodosAbstratos:
    """Testes para métodos abstratos."""
    
    def test_adicionar_deve_ser_implementado(self):
        """Testa que adicionar deve ser implementado."""
        # ConcreteManager implementa adicionar
        temp_dir = tempfile.mkdtemp()
        try:
            manager = ConcreteManager(os.path.join(temp_dir, "test.xlsx"), ['ID'])
            sucesso, _ = manager.adicionar({'ID': '001'})
            assert sucesso is True
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_atualizar_deve_ser_implementado(self):
        """Testa que atualizar deve ser implementado."""
        temp_dir = tempfile.mkdtemp()
        try:
            manager = ConcreteManager(os.path.join(temp_dir, "test.xlsx"), ['ID', 'Nome'])
            manager.adicionar({'ID': '001', 'Nome': 'Original'})
            
            sucesso, _ = manager.atualizar('001', {'Nome': 'Atualizado'})
            assert sucesso is True
            
            registro = manager.buscar_por_id('001')
            assert registro['Nome'] == 'Atualizado'
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


# =============================================================================
# TESTES DE TRATAMENTO DE ERROS
# =============================================================================

class TestTratamentoErros:
    """Testes para tratamento de erros."""
    
    def test_carregar_dados_arquivo_invalido(self, temp_manager):
        """Testa carregamento de arquivo inválido."""
        # Escrever conteúdo inválido no arquivo
        with open(temp_manager.arquivo, 'w') as f:
            f.write("conteúdo inválido")
        
        # Não deve lançar exceção
        df = temp_manager.carregar_dados()
        assert isinstance(df, pd.DataFrame)
    
    def test_contar_registros_erro(self, temp_manager):
        """Testa contagem quando há erro."""
        # Simular erro no arquivo
        os.remove(temp_manager.arquivo)
        
        # Deve retornar 0 em caso de erro
        assert temp_manager.contar_registros() == 0
