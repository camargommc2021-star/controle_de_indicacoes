"""
Testes unitários para o módulo backup_manager.py.

Testa todas as operações do BackupManager,
 incluindo criação, restauração e listagem de backups.
"""

import pytest
import os
import sys
import shutil
import tempfile
import time
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from backup_manager import BackupManager


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def temp_backup_setup():
    """Cria estrutura temporária para testes de backup."""
    temp_dir = tempfile.mkdtemp()
    
    arquivo_dados = Path(temp_dir) / "data" / "cursos.xlsx"
    pasta_backup = Path(temp_dir) / "backups"
    
    # Criar estrutura
    arquivo_dados.parent.mkdir(exist_ok=True)
    pasta_backup.mkdir(exist_ok=True)
    
    # Criar arquivo de dados
    import pandas as pd
    df = pd.DataFrame({
        'Curso': ['Teste 1', 'Teste 2'],
        'Vagas': [30, 25],
    })
    df.to_excel(arquivo_dados, index=False, engine='openpyxl')
    
    yield {
        'arquivo_dados': str(arquivo_dados),
        'pasta_backup': str(pasta_backup),
        'temp_dir': temp_dir,
    }
    
    # Limpar
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def backup_manager(temp_backup_setup):
    """Cria um BackupManager configurado."""
    bm = BackupManager(
        arquivo_dados=temp_backup_setup['arquivo_dados'],
        pasta_backup=temp_backup_setup['pasta_backup'],
    )
    return bm


# =============================================================================
# TESTES DE INICIALIZAÇÃO
# =============================================================================

class TestInicializacao:
    """Testes para inicialização do BackupManager."""
    
    def test_inicializacao_cria_pasta_backup(self, temp_backup_setup):
        """Testa criação da pasta de backup."""
        # Remover pasta de backup para testar criação
        shutil.rmtree(temp_backup_setup['pasta_backup'])
        
        bm = BackupManager(
            arquivo_dados=temp_backup_setup['arquivo_dados'],
            pasta_backup=temp_backup_setup['pasta_backup'],
        )
        
        assert os.path.exists(temp_backup_setup['pasta_backup'])
    
    def test_inicializacao_caminhos_padrao(self):
        """Testa caminhos padrão."""
        bm = BackupManager()
        
        assert bm.arquivo_dados == "data/cursos.xlsx"
        assert bm.pasta_backup == "backups"
        assert bm.max_backups == 30


# =============================================================================
# TESTES DE CRIAÇÃO DE BACKUP
# =============================================================================

class TestCriarBackup:
    """Testes para criação de backups."""
    
    def test_criar_backup_sucesso(self, backup_manager, temp_backup_setup):
        """Testa criação bem-sucedida de backup."""
        sucesso, mensagem = backup_manager.criar_backup()
        
        assert sucesso is True
        assert "Backup criado" in mensagem
        
        # Verificar que o arquivo foi criado
        backups = os.listdir(temp_backup_setup['pasta_backup'])
        assert len(backups) == 1
        assert backups[0].startswith("cursos_")
        assert backups[0].endswith(".xlsx")
    
    def test_criar_backup_arquivo_inexistente(self, temp_backup_setup):
        """Testa criação quando arquivo de dados não existe."""
        bm = BackupManager(
            arquivo_dados="/caminho/inexistente/cursos.xlsx",
            pasta_backup=temp_backup_setup['pasta_backup'],
        )
        
        sucesso, mensagem = bm.criar_backup()
        
        assert sucesso is False
        assert "não encontrado" in mensagem.lower()
    
    def test_criar_backup_multiplos(self, backup_manager, temp_backup_setup):
        """Testa criação de múltiplos backups."""
        # Criar vários backups
        for i in range(5):
            time.sleep(0.01)  # Pequena pausa para timestamps diferentes
            sucesso, _ = backup_manager.criar_backup()
            assert sucesso is True
        
        backups = os.listdir(temp_backup_setup['pasta_backup'])
        assert len(backups) == 5
    
    def test_criar_backup_nome_unico(self, backup_manager, temp_backup_setup):
        """Testa que cada backup tem nome único."""
        # Criar dois backups rapidamente
        backup_manager.criar_backup()
        time.sleep(0.01)
        backup_manager.criar_backup()
        
        backups = os.listdir(temp_backup_setup['pasta_backup'])
        assert len(backups) == 2
        assert backups[0] != backups[1]


# =============================================================================
# TESTES DE LIMPEZA DE BACKUPS
# =============================================================================

class TestLimparBackups:
    """Testes para limpeza de backups antigos."""
    
    def test_limpar_backups_antigos(self, backup_manager, temp_backup_setup):
        """Testa limpeza de backups antigos."""
        # Reduzir limite para teste
        backup_manager.max_backups = 3
        
        # Criar mais backups que o limite
        for i in range(5):
            time.sleep(0.01)
            backup_manager.criar_backup()
        
        backups = os.listdir(temp_backup_setup['pasta_backup'])
        assert len(backups) == 3  # Deve manter apenas 3
    
    def test_limpar_backups_mantem_recentes(self, backup_manager, temp_backup_setup):
        """Testa que os backups mais recentes são mantidos."""
        backup_manager.max_backups = 2
        
        # Criar 3 backups
        for i in range(3):
            time.sleep(0.01)
            backup_manager.criar_backup()
        
        # Listar backups ordenados por data
        backups = backup_manager.listar_backups()
        
        assert len(backups) == 2
        # Os mais recentes devem estar primeiro
        assert backups[0]['data'] >= backups[1]['data']


# =============================================================================
# TESTES DE LISTAGEM
# =============================================================================

class TestListarBackups:
    """Testes para listagem de backups."""
    
    def test_listar_backups_vazio(self, backup_manager):
        """Testa listagem quando não há backups."""
        backups = backup_manager.listar_backups()
        
        assert backups == []
    
    def test_listar_backups_com_dados(self, backup_manager, temp_backup_setup):
        """Testa listagem com backups existentes."""
        # Criar backup
        backup_manager.criar_backup()
        
        backups = backup_manager.listar_backups()
        
        assert len(backups) == 1
        assert 'nome' in backups[0]
        assert 'caminho' in backups[0]
        assert 'data' in backups[0]
        assert 'tamanho' in backups[0]
    
    def test_listar_backups_ordenado(self, backup_manager, temp_backup_setup):
        """Testa que backups são listados do mais recente para o mais antigo."""
        # Criar backups com intervalo
        for i in range(3):
            time.sleep(0.01)
            backup_manager.criar_backup()
        
        backups = backup_manager.listar_backups()
        
        # Verificar ordenação (mais recente primeiro)
        for i in range(len(backups) - 1):
            assert backups[i]['data'] >= backups[i + 1]['data']


# =============================================================================
# TESTES DE RESTAURAÇÃO
# =============================================================================

class TestRestaurarBackup:
    """Testes para restauração de backups."""
    
    def test_restaurar_backup_sucesso(self, backup_manager, temp_backup_setup):
        """Testa restauração bem-sucedida."""
        # Criar backup
        backup_manager.criar_backup()
        
        # Modificar arquivo original
        import pandas as pd
        df_modificado = pd.DataFrame({'Nova': [1, 2, 3]})
        df_modificado.to_excel(temp_backup_setup['arquivo_dados'], index=False, engine='openpyxl')
        
        # Restaurar backup
        backups = backup_manager.listar_backups()
        sucesso, mensagem = backup_manager.restaurar_backup(backups[0]['caminho'])
        
        assert sucesso is True
        assert "sucesso" in mensagem.lower()
        
        # Verificar que foi restaurado
        df_restaurado = pd.read_excel(temp_backup_setup['arquivo_dados'], engine='openpyxl')
        assert 'Curso' in df_restaurado.columns
    
    def test_restaurar_backup_inexistente(self, backup_manager):
        """Testa restauração de backup inexistente."""
        sucesso, mensagem = backup_manager.restaurar_backup("/caminho/inexistente.xlsx")
        
        assert sucesso is False
        assert "não encontrado" in mensagem.lower()
    
    def test_restaurar_cria_backup_atual(self, backup_manager, temp_backup_setup):
        """Testa que restauração cria backup do arquivo atual."""
        # Criar primeiro backup
        backup_manager.criar_backup()
        time.sleep(0.01)
        
        # Restaurar
        backups = backup_manager.listar_backups()
        backup_manager.restaurar_backup(backups[0]['caminho'])
        
        # Deve ter criado backup do arquivo atual antes de restaurar
        backups_apos = backup_manager.listar_backups()
        assert len(backups_apos) >= 2


# =============================================================================
# TESTES DE BACKUP AUTOMÁTICO
# =============================================================================

class TestBackupAutomatico:
    """Testes para verificação de backup automático."""
    
    def test_backup_automatico_necessario_sem_backups(self, backup_manager):
        """Testa que é necessário quando não há backups."""
        necessario = backup_manager.backup_automatico_necessario()
        
        assert necessario is True
    
    def test_backup_automatico_necessario_backups_antigos(self, backup_manager):
        """Testa que é necessário quando último backup é de outro dia."""
        # Criar backup
        backup_manager.criar_backup()
        
        # Simular que último backup foi ontem
        backups = backup_manager.listar_backups()
        ontem = datetime.now() - timedelta(days=2)
        
        # Modificar data do arquivo
        os.utime(backups[0]['caminho'], (ontem.timestamp(), ontem.timestamp()))
        
        necessario = backup_manager.backup_automatico_necessario()
        
        assert necessario is True
    
    def test_backup_automatico_nao_necessario(self, backup_manager):
        """Testa que não é necessário quando já tem backup hoje."""
        # Criar backup
        backup_manager.criar_backup()
        
        necessario = backup_manager.backup_automatico_necessario()
        
        assert necessario is False


# =============================================================================
# TESTES DE ERROS
# =============================================================================

class TestErros:
    """Testes para tratamento de erros."""
    
    def test_criar_backup_erro_permissao(self, backup_manager, temp_backup_setup):
        """Testa erro de permissão ao criar backup."""
        # Tornar pasta de backup somente leitura (simulação)
        with patch('shutil.copy2') as mock_copy:
            mock_copy.side_effect = PermissionError("Permissão negada")
            
            sucesso, mensagem = backup_manager.criar_backup()
            
            assert sucesso is False
            assert "erro" in mensagem.lower()
    
    def test_listar_backups_erro(self, backup_manager, temp_backup_setup):
        """Testa erro ao listar backups."""
        # Criar arquivo não-xlsx na pasta de backup
        with open(os.path.join(temp_backup_setup['pasta_backup'], "readme.txt"), 'w') as f:
            f.write("test")
        
        # Não deve incluir arquivo não-xlsx
        backups = backup_manager.listar_backups()
        assert len(backups) == 0
