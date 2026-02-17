"""
Configurações e fixtures do pytest para o sistema de testes.

Este arquivo contém fixtures compartilhadas entre todos os testes,
configurações de ambiente e utilitários de teste.
"""

import pytest
import os
import sys
import shutil
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd

# Adicionar o diretório raiz ao path para importar módulos do projeto
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# =============================================================================
# FIXTURES DE AMBIENTE
# =============================================================================

@pytest.fixture(scope="session")
def test_data_dir():
    """Retorna o diretório de dados de teste."""
    return PROJECT_ROOT / "tests" / "data"


@pytest.fixture(scope="function")
def temp_dir():
    """Cria um diretório temporário para testes isolados."""
    temp_path = tempfile.mkdtemp(prefix="test_controle_cursos_")
    yield Path(temp_path)
    # Limpar após o teste
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture(scope="function")
def clean_test_data(test_data_dir):
    """Limpa arquivos de teste antes e depois de cada teste."""
    # Limpar antes do teste
    if test_data_dir.exists():
        for file in test_data_dir.glob("*.xlsx"):
            file.unlink(missing_ok=True)
        for file in test_data_dir.glob("*.csv"):
            file.unlink(missing_ok=True)
    
    yield test_data_dir
    
    # Limpar após o teste
    if test_data_dir.exists():
        for file in test_data_dir.glob("*.xlsx"):
            file.unlink(missing_ok=True)
        for file in test_data_dir.glob("*.csv"):
            file.unlink(missing_ok=True)


# =============================================================================
# FIXTURES DE DADOS DE EXEMPLO
# =============================================================================

@pytest.fixture
def sample_curso_data():
    """Retorna dados de exemplo para um curso."""
    return {
        'Curso': 'CILE - Módulo 1',
        'Turma': '2024-001',
        'Vagas': 30,
        'Autorizados pelas escalantes': 25,
        'Prioridade': 'Alta',
        'Recebimento do SIGAD com as vagas': '15/01/2024',
        'Numero do SIGAD': '12345/2024',
        'Estado': 'solicitar voluntários',
        'DATA_DA_CONCLUSAO': '',
        'Numero do SIGAD  encaminhando pra chefia': '',
        'Prazo dado pela chefia': '20/01/2024',
        'Fim da indicação da SIAT': '25/01/2024',
        'Notas': 'Curso de informática básica',
        'OM_Executora': 'Cmdo',
    }


@pytest.fixture
def sample_curso_list():
    """Retorna uma lista de cursos de exemplo."""
    return [
        {
            'Curso': 'CILE - Módulo 1',
            'Turma': '2024-001',
            'Vagas': 30,
            'Autorizados pelas escalantes': 25,
            'Prioridade': 'Alta',
            'Estado': 'solicitar voluntários',
            'OM_Executora': 'Cmdo',
        },
        {
            'Curso': 'CILE - Módulo 2',
            'Turma': '2024-002',
            'Vagas': 20,
            'Autorizados pelas escalantes': 20,
            'Prioridade': 'Média',
            'Estado': 'fazer indicação',
            'OM_Executora': 'C Op',
        },
        {
            'Curso': 'Gestão de Projetos',
            'Turma': '2024-003',
            'Vagas': 15,
            'Autorizados pelas escalantes': 10,
            'Prioridade': 'Baixa',
            'Estado': 'Concluído',
            'OM_Executora': 'DACTA',
        },
    ]


@pytest.fixture
def sample_fic_data():
    """Retorna dados de exemplo para uma FIC."""
    return {
        'Curso': 'CILE-MOD1',
        'Turma': '2024-001',
        'Local_GT': 'Rio de Janeiro',
        'Comando': 'Cmdo',
        'Data_Inicio_Presencial': '01/02/2024',
        'Data_Termino_Presencial': '15/02/2024',
        'Data_Inicio_Distancia': '16/02/2024',
        'Data_Termino_Distancia': '28/02/2024',
        'PPD_Civil': 'Não',
        'Posto_Graduacao': 'SGT',
        'Nome_Completo': 'João da Silva',
        'OM_Indicado': 'Cmdo',
        'CPF': '529.982.247-25',
        'SARAM': '123456',
        'Email': 'joao.silva@email.com',
        'Telefone': '(21) 98765-4321',
        'Funcao_Atual': 'Assistente Administrativo',
        'Data_Ultima_Promocao': '01/01/2022',
        'Funcao_Apos_Curso': 'Analista de Sistemas',
        'Tempo_Servico': '5 anos',
        'Pre_Requisitos': 'Sim',
        'Curso_Mapeado': 'Sim',
        'Progressao_Carreira': 'Sim',
        'Comunicado_Indicado': 'Sim',
        'Outro_Impedimento': 'Não',
        'Curso_Anterior': '',
        'Ano_Curso_Anterior': '',
        'Ciencia_Dedicacao_EAD': 'Sim',
        'Justificativa_Chefe': 'Necessidade de capacitação',
        'Nome_Chefe_COP': 'Capitão Santos',
        'Posto_Chefe_COP': 'CAP',
        'Nome_Responsavel_DACTA': 'Major Oliveira',
        'Posto_Responsavel_DACTA': 'MAJ',
    }


@pytest.fixture
def sample_fic_list():
    """Retorna uma lista de FICs de exemplo."""
    return [
        {
            'Curso': 'CILE-MOD1',
            'Turma': '2024-001',
            'Posto_Graduacao': 'SGT',
            'Nome_Completo': 'João da Silva',
            'OM_Indicado': 'Cmdo',
            'CPF': '529.982.247-25',
            'SARAM': '123456',
            'Email': 'joao.silva@email.com',
            'Telefone': '(21) 98765-4321',
        },
        {
            'Curso': 'CILE-MOD2',
            'Turma': '2024-002',
            'Posto_Graduacao': '1º SGT',
            'Nome_Completo': 'Maria Oliveira',
            'OM_Indicado': 'C Op',
            'CPF': '987.654.321-00',
            'SARAM': '654321',
            'Email': 'maria.oliveira@email.com',
            'Telefone': '(21) 91234-5678',
        },
    ]


@pytest.fixture
def sample_dataframe():
    """Retorna um DataFrame de exemplo com dados de cursos."""
    data = {
        'Curso': ['Curso A', 'Curso B', 'Curso C'],
        'Turma': ['T1', 'T2', 'T3'],
        'Vagas': [30, 25, 20],
        'Prioridade': ['Alta', 'Média', 'Baixa'],
        'Estado': ['solicitar voluntários', 'fazer indicação', 'Concluído'],
        'OM_Executora': ['Cmdo', 'C Op', 'DACTA'],
    }
    return pd.DataFrame(data)


# =============================================================================
# FIXTURES DE MANAGERS (MOCKADOS)
# =============================================================================

@pytest.fixture
def mock_github_manager():
    """Retorna um mock do GitHubManager."""
    mock = MagicMock()
    mock.authenticated = True
    mock.verificar_autenticacao.return_value = (True, "Autenticado como: test_user")
    mock.commit_excel.return_value = (True, "✅ Dados salvos no GitHub")
    mock.sincronizar_para_local.return_value = (True, "✅ Dados sincronizados")
    mock.obter_arquivo_excel.return_value = (b"fake_excel_bytes", None)
    mock.obter_ultimo_commit.return_value = {
        'data': datetime.now(),
        'mensagem': 'Test commit',
        'autor': 'Test User'
    }
    return mock


@pytest.fixture
def temp_data_manager(temp_dir):
    """Cria um DataManager com diretório temporário."""
    from data_manager import DataManager
    
    # Patch para usar diretório temporário
    with patch.object(DataManager, '__init__', lambda self, usar_github=False: None):
        dm = DataManager.__new__(DataManager)
        dm.arquivo_local = str(temp_dir / "cursos.xlsx")
        dm.colunas_base = [
            'Curso', 'Turma', 'Vagas', 'Autorizados pelas escalantes', 'Prioridade',
            'Recebimento do SIGAD com as vagas', 'Numero do SIGAD', 'Estado',
            'DATA_DA_CONCLUSAO', 'Numero do SIGAD  encaminhando pra chefia',
            'Prazo dado pela chefia', 'Fim da indicação da SIAT', 'Notas',
            'OM_Executora'
        ]
        dm.colunas_om = []
        dm.colunas = dm.colunas_base.copy()
        dm.github_manager = None
        dm.ultima_mensagem = ""
        dm._criar_arquivo_se_nao_existir()
        yield dm


@pytest.fixture
def temp_fic_manager(temp_dir):
    """Cria um FICManager com diretório temporário."""
    from fic_manager import FICManager
    
    with patch.object(FICManager, '__init__', lambda self: None):
        fm = FICManager.__new__(FICManager)
        fm.arquivo_fics = str(temp_dir / "fics.xlsx")
        fm.colunas = [
            'ID', 'Data_Criacao', 'Data_Atualizacao', 'Status',
            'Curso', 'Turma', 'Local_GT', 'Comando', 
            'Data_Inicio_Presencial', 'Data_Termino_Presencial',
            'Data_Inicio_Distancia', 'Data_Termino_Distancia',
            'PPD_Civil',
            'Posto_Graduacao', 'Nome_Completo', 'OM_Indicado',
            'CPF', 'SARAM', 'Email', 'Telefone',
            'Funcao_Atual', 'Data_Ultima_Promocao',
            'Funcao_Apos_Curso', 'Tempo_Servico',
            'Pre_Requisitos',
            'Curso_Mapeado', 'Progressao_Carreira', 
            'Comunicado_Indicado', 'Outro_Impedimento',
            'Curso_Anterior', 'Ano_Curso_Anterior',
            'Ciencia_Dedicacao_EAD',
            'Justificativa_Chefe', 
            'Nome_Chefe_COP', 'Posto_Chefe_COP',
            'Nome_Responsavel_DACTA', 'Posto_Responsavel_DACTA'
        ]
        fm._criar_arquivo_se_nao_existir()
        yield fm


@pytest.fixture
def temp_backup_manager(temp_dir):
    """Cria um BackupManager com diretório temporário."""
    from backup_manager import BackupManager
    
    arquivo_dados = temp_dir / "cursos.xlsx"
    pasta_backup = temp_dir / "backups"
    
    # Criar arquivo de dados fake
    df = pd.DataFrame({'coluna': [1, 2, 3]})
    df.to_excel(arquivo_dados, index=False, engine='openpyxl')
    
    bm = BackupManager(
        arquivo_dados=str(arquivo_dados),
        pasta_backup=str(pasta_backup)
    )
    yield bm


# =============================================================================
# FIXTURES DE STREAMLIT (MOCKADAS)
# =============================================================================

@pytest.fixture
def mock_streamlit():
    """Mock para o streamlit."""
    with patch.dict('sys.modules', {'streamlit': MagicMock()}):
        import streamlit as st_mock
        st_mock.session_state = {}
        st_mock.columns.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        yield st_mock


# =============================================================================
# CONFIGURAÇÕES DO PYTEST
# =============================================================================

def pytest_configure(config):
    """Configurações adicionais do pytest."""
    config.addinivalue_line(
        "markers", "slow: marca testes que são lentos"
    )
    config.addinivalue_line(
        "markers", "integration: marca testes de integração"
    )
    config.addinivalue_line(
        "markers", "unit: marca testes unitários"
    )


def pytest_collection_modifyitems(config, items):
    """Modifica itens de teste durante a coleta."""
    for item in items:
        # Adicionar marker 'unit' se não tiver nenhum marker específico
        if not any(marker.name in ['slow', 'integration', 'unit'] for marker in item.own_markers):
            item.add_marker(pytest.mark.unit)
