"""
Testes mockados para o módulo github_manager.py.

Testa todas as operações do GitHubManager usando mocks,
para evitar dependências de rede e API externa.
"""

import pytest
import os
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock, mock_open

sys.path.insert(0, str(Path(__file__).parent.parent))


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def mock_github_env():
    """Configura variáveis de ambiente mockadas para GitHub."""
    env_vars = {
        'GITHUB_TOKEN': 'fake_token_123',
        'GITHUB_REPO': 'usuario/repo-teste',
    }
    with patch.dict(os.environ, env_vars, clear=False):
        yield env_vars


@pytest.fixture
def mock_github_class(mock_github_env):
    """Cria um mock da classe Github do PyGithub."""
    with patch('github_manager.Github') as MockGithub:
        # Configurar mock do usuário
        mock_user = MagicMock()
        mock_user.login = 'test_user'
        
        # Configurar mock do repositório
        mock_repo = MagicMock()
        mock_repo.full_name = 'usuario/repo-teste'
        
        # Configurar mock da classe Github
        mock_github_instance = MagicMock()
        mock_github_instance.get_user.return_value = mock_user
        mock_github_instance.get_repo.return_value = mock_repo
        
        MockGithub.return_value = mock_github_instance
        
        yield {
            'class': MockGithub,
            'instance': mock_github_instance,
            'user': mock_user,
            'repo': mock_repo,
        }


@pytest.fixture
def github_manager_authenticated(mock_github_class):
    """Cria um GitHubManager autenticado com mocks."""
    from github_manager import GitHubManager
    
    gm = GitHubManager()
    return gm


@pytest.fixture
def github_manager_no_auth():
    """Cria um GitHubManager sem autenticação."""
    from github_manager import GitHubManager
    
    with patch.dict(os.environ, {}, clear=True):
        with patch('github_manager.st'):
            gm = GitHubManager()
            return gm


# =============================================================================
# TESTES DE INICIALIZAÇÃO
# =============================================================================

class TestInicializacao:
    """Testes para inicialização do GitHubManager."""
    
    def test_inicializacao_com_token(self, mock_github_class):
        """Testa inicialização com token válido."""
        from github_manager import GitHubManager
        
        gm = GitHubManager()
        
        assert gm.authenticated is True
        assert gm.token == 'fake_token_123'
        assert gm.repo_name == 'usuario/repo-teste'
    
    def test_inicializacao_sem_token(self):
        """Testa inicialização sem token."""
        from github_manager import GitHubManager
        
        with patch.dict(os.environ, {}, clear=True):
            with patch('github_manager.st') as mock_st:
                mock_st.secrets.get.return_value = None
                gm = GitHubManager()
                
                assert gm.authenticated is False
    
    def test_inicializacao_erro_conexao(self):
        """Testa inicialização com erro de conexão."""
        from github_manager import GitHubManager
        
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'invalid_token'}, clear=False):
            with patch('github_manager.Github') as MockGithub:
                MockGithub.side_effect = Exception("Erro de conexão")
                
                gm = GitHubManager()
                
                assert gm.authenticated is False


# =============================================================================
# TESTES DE AUTENTICAÇÃO
# =============================================================================

class TestAutenticacao:
    """Testes para verificação de autenticação."""
    
    def test_verificar_autenticacao_sucesso(self, github_manager_authenticated, mock_github_class):
        """Testa verificação de autenticação bem-sucedida."""
        gm = github_manager_authenticated
        
        autenticado, mensagem = gm.verificar_autenticacao()
        
        assert autenticado is True
        assert 'test_user' in mensagem
    
    def test_verificar_autenticacao_falha(self):
        """Testa verificação de autenticação falha."""
        from github_manager import GitHubManager
        
        with patch.dict(os.environ, {}, clear=True):
            with patch('github_manager.st') as mock_st:
                mock_st.secrets.get.return_value = None
                gm = GitHubManager()
                
                autenticado, mensagem = gm.verificar_autenticacao()
                
                assert autenticado is False
                assert "token" in mensagem.lower()
    
    def test_verificar_autenticacao_erro_api(self, github_manager_authenticated, mock_github_class):
        """Testa erro na API durante verificação."""
        gm = github_manager_authenticated
        
        # Configurar mock para lançar exceção
        mock_github_class['instance'].get_user.side_effect = Exception("API Error")
        
        autenticado, mensagem = gm.verificar_autenticacao()
        
        assert autenticado is False
        assert "erro" in mensagem.lower()


# =============================================================================
# TESTES DE OPERAÇÕES COM ARQUIVOS
# =============================================================================

class TestObterArquivo:
    """Testes para obter arquivo do GitHub."""
    
    def test_obter_arquivo_excel_sucesso(self, github_manager_authenticated, mock_github_class):
        """Testa obtenção bem-sucedida do arquivo."""
        gm = github_manager_authenticated
        
        # Configurar mock do conteúdo
        mock_content = MagicMock()
        mock_content.content = 'ZmFrZV9leGNlbF9jb250ZW50'  # base64 de "fake_excel_content"
        mock_github_class['repo'].get_contents.return_value = mock_content
        
        content_bytes, error = gm.obter_arquivo_excel()
        
        assert error is None
        assert content_bytes == b'fake_excel_content'
    
    def test_obter_arquivo_nao_autenticado(self):
        """Testa obtenção sem autenticação."""
        from github_manager import GitHubManager
        
        with patch.dict(os.environ, {}, clear=True):
            with patch('github_manager.st') as mock_st:
                mock_st.secrets.get.return_value = None
                gm = GitHubManager()
                
                content_bytes, error = gm.obter_arquivo_excel()
                
                assert content_bytes is None
                assert "não autenticado" in error.lower()
    
    def test_obter_arquivo_nao_encontrado(self, github_manager_authenticated, mock_github_class):
        """Testa arquivo não encontrado (404)."""
        gm = github_manager_authenticated
        
        mock_github_class['repo'].get_contents.side_effect = Exception("404 Not Found")
        
        content_bytes, error = gm.obter_arquivo_excel()
        
        assert content_bytes is None
        assert "não encontrado" in error.lower()


class TestCommitArquivo:
    """Testes para commit de arquivo no GitHub."""
    
    def test_commit_arquivo_atualizar_existente(self, github_manager_authenticated, mock_github_class):
        """Testa commit atualizando arquivo existente."""
        gm = github_manager_authenticated
        
        # Configurar mock do conteúdo existente
        mock_content = MagicMock()
        mock_content.sha = 'abc123'
        mock_github_class['repo'].get_contents.return_value = mock_content
        
        file_bytes = b'conteudo_do_arquivo'
        sucesso, mensagem = gm.commit_excel(file_bytes, "Mensagem de teste")
        
        assert sucesso is True
        mock_github_class['repo'].update_file.assert_called_once()
    
    def test_commit_arquivo_criar_novo(self, github_manager_authenticated, mock_github_class):
        """Testa commit criando novo arquivo."""
        gm = github_manager_authenticated
        
        # Configurar get_contents para falhar (arquivo não existe)
        mock_github_class['repo'].get_contents.side_effect = Exception("404")
        
        file_bytes = b'conteudo_do_arquivo'
        sucesso, mensagem = gm.commit_excel(file_bytes)
        
        assert sucesso is True
        mock_github_class['repo'].create_file.assert_called_once()
    
    def test_commit_arquivo_nao_autenticado(self):
        """Testa commit sem autenticação."""
        from github_manager import GitHubManager
        
        with patch.dict(os.environ, {}, clear=True):
            with patch('github_manager.st') as mock_st:
                mock_st.secrets.get.return_value = None
                gm = GitHubManager()
                
                sucesso, mensagem = gm.commit_excel(b'teste')
                
                assert sucesso is False
                assert "token" in mensagem.lower()
    
    def test_commit_arquivo_erro(self, github_manager_authenticated, mock_github_class):
        """Testa erro durante commit."""
        gm = github_manager_authenticated
        
        mock_github_class['repo'].get_contents.side_effect = Exception("Erro inesperado")
        
        sucesso, mensagem = gm.commit_excel(b'teste')
        
        assert sucesso is False
        assert "erro" in mensagem.lower()


# =============================================================================
# TESTES DE SINCRONIZAÇÃO
# =============================================================================

class TestSincronizacao:
    """Testes para sincronização de dados."""
    
    def test_sincronizar_para_local_sucesso(self, github_manager_authenticated, mock_github_class, tmp_path):
        """Testa sincronização bem-sucedida para local."""
        gm = github_manager_authenticated
        
        # Configurar mock do conteúdo
        mock_content = MagicMock()
        mock_content.content = 'ZmFrZV9jb250ZW50'  # base64 de "fake_content"
        mock_github_class['repo'].get_contents.return_value = mock_content
        
        # Mudar para diretório temporário
        gm.arquivo_path = "data/cursos.xlsx"
        
        with patch('os.makedirs'):
            with patch('builtins.open', mock_open()):
                sucesso, mensagem = gm.sincronizar_para_local()
                
                assert sucesso is True
                assert "sincronizados" in mensagem.lower()
    
    def test_sincronizar_para_local_nao_autenticado(self):
        """Testa sincronização sem autenticação."""
        from github_manager import GitHubManager
        
        with patch.dict(os.environ, {}, clear=True):
            with patch('github_manager.st') as mock_st:
                mock_st.secrets.get.return_value = None
                gm = GitHubManager()
                
                sucesso, mensagem = gm.sincronizar_para_local()
                
                assert sucesso is False
    
    def test_sincronizar_arquivo_nao_existe_remoto(self, github_manager_authenticated, mock_github_class):
        """Testa sincronização quando arquivo não existe no GitHub."""
        gm = github_manager_authenticated
        
        mock_github_class['repo'].get_contents.return_value = (None, "não encontrado")
        
        sucesso, mensagem = gm.sincronizar_para_local()
        
        assert sucesso is True  # Não é erro, apenas arquivo ainda não existe


# =============================================================================
# TESTES DE COMMIT INFO
# =============================================================================

class TestCommitInfo:
    """Testes para informações de commit."""
    
    def test_obter_ultimo_commit_sucesso(self, github_manager_authenticated, mock_github_class):
        """Testa obtenção do último commit."""
        gm = github_manager_authenticated
        
        # Configurar mock de commits
        mock_commit = MagicMock()
        mock_commit.commit.committer.date = datetime(2024, 1, 15, 10, 30, 0)
        mock_commit.commit.message = "Atualização de teste"
        mock_commit.commit.committer.name = "Test User"
        
        mock_commits = MagicMock()
        mock_commits.totalCount = 1
        mock_commits.__getitem__ = MagicMock(return_value=mock_commit)
        mock_github_class['repo'].get_commits.return_value = mock_commits
        
        resultado = gm.obter_ultimo_commit()
        
        assert resultado is not None
        assert resultado['mensagem'] == "Atualização de teste"
        assert resultado['autor'] == "Test User"
    
    def test_obter_ultimo_commit_nenhum_commit(self, github_manager_authenticated, mock_github_class):
        """Testa quando não há commits."""
        gm = github_manager_authenticated
        
        mock_commits = MagicMock()
        mock_commits.totalCount = 0
        mock_github_class['repo'].get_commits.return_value = mock_commits
        
        resultado = gm.obter_ultimo_commit()
        
        assert resultado is None
    
    def test_obter_ultimo_commit_nao_autenticado(self):
        """Testa obtenção de commit sem autenticação."""
        from github_manager import GitHubManager
        
        with patch.dict(os.environ, {}, clear=True):
            with patch('github_manager.st') as mock_st:
                mock_st.secrets.get.return_value = None
                gm = GitHubManager()
                
                resultado = gm.obter_ultimo_commit()
                
                assert resultado is None
    
    def test_obter_ultimo_commit_erro(self, github_manager_authenticated, mock_github_class):
        """Testa erro ao obter commit."""
        gm = github_manager_authenticated
        
        mock_github_class['repo'].get_commits.side_effect = Exception("Erro")
        
        resultado = gm.obter_ultimo_commit()
        
        assert resultado is None


# =============================================================================
# TESTES DE CONFIGURAÇÃO
# =============================================================================

class TestConfiguracao:
    """Testes para configuração do GitHubManager."""
    
    def test_caminho_arquivo_padrao(self, mock_github_class):
        """Testa caminho padrão do arquivo."""
        from github_manager import GitHubManager
        
        gm = GitHubManager()
        
        assert gm.arquivo_path == "data/cursos.xlsx"
    
    def test_repo_padrao_streamlit_secrets(self):
        """Testa repo padrão de streamlit secrets."""
        from github_manager import GitHubManager
        
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'token'}, clear=True):
            with patch('github_manager.st') as mock_st:
                mock_st.secrets.get.side_effect = lambda key, default=None: {
                    'GITHUB_REPO': 'repo/streamlit',
                    'GITHUB_TOKEN': 'token_st',
                }.get(key, default)
                
                with patch('github_manager.Github'):
                    gm = GitHubManager()
                    
                    # Verifica que tentou pegar do secrets
                    mock_st.secrets.get.assert_called()
