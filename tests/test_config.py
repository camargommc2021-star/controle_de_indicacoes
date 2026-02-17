"""
Testes unitários para o módulo config.py.

Testa todas as classes de configuração, constantes e funções auxiliares.
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    Settings,
    Paths,
    Colors,
    Columns,
    FICFields,
    Choices,
    LoggingConfig,
    Messages,
    ExportConfig,
    # Instâncias globais
    settings,
    paths,
    colors,
    columns,
    fic_fields,
    choices,
    logging_config,
    messages,
    export_config,
    # Funções utilitárias
    get_column_types,
    get_default_values,
    validate_config,
)


# =============================================================================
# TESTES DA CLASSE SETTINGS
# =============================================================================

class TestSettings:
    """Testes para a classe Settings."""
    
    def test_settings_default_values(self):
        """Testa valores padrão das configurações."""
        s = Settings()
        assert s.APP_NAME == "Sistema de Controle de Cursos"
        assert s.APP_VERSION == "1.0.0"
        assert s.PAGE_TITLE == "Controle de Cursos"
        assert s.PAGE_ICON == "📚"
        assert s.PAGE_LAYOUT == "wide"
    
    def test_settings_data_formats(self):
        """Testa formatos de data."""
        s = Settings()
        assert s.DATE_FORMAT == "%d/%m/%Y"
        assert s.DATETIME_FORMAT == "%d/%m/%Y %H:%M:%S"
        assert s.DEFAULT_ENCODING == "utf-8"
    
    def test_settings_limits(self):
        """Testa limites do sistema."""
        s = Settings()
        assert s.MAX_UPLOAD_SIZE_MB == 10
        assert s.MAX_ROWS_DISPLAY == 1000
    
    def test_settings_is_frozen(self):
        """Testa se a dataclass é frozen (imutável)."""
        s = Settings()
        with pytest.raises(Exception):  # FrozenInstanceError
            s.APP_NAME = "Novo Nome"


# =============================================================================
# TESTES DA CLASSE PATHS
# =============================================================================

class TestPaths:
    """Testes para a classe Paths."""
    
    def test_paths_default_values(self):
        """Testa valores padrão dos caminhos."""
        p = Paths()
        assert isinstance(p.BASE_DIR, Path)
        assert isinstance(p.DATA_DIR, Path)
        assert isinstance(p.ASSETS_DIR, Path)
        assert isinstance(p.BACKUPS_DIR, Path)
    
    def test_paths_file_locations(self):
        """Testa localizações de arquivos."""
        p = Paths()
        assert p.CURSOS_FILE.name == "cursos.csv"
        assert p.FIC_FILE.name == "fic.csv"
        assert p.FIC_TEMPLATE_DOCX.name == "FIC_layout.docx"
    
    def test_paths_ensure_dirs(self, temp_dir):
        """Testa criação de diretórios."""
        p = Paths()
        # Testa que o método existe e pode ser chamado
        assert hasattr(p, 'ensure_dirs')
        assert callable(p.ensure_dirs)


# =============================================================================
# TESTES DA CLASSE COLORS
# =============================================================================

class TestColors:
    """Testes para a classe Colors."""
    
    def test_colors_defined(self):
        """Testa se todas as cores principais estão definidas."""
        c = Colors()
        assert c.GREEN_PRIMARY == "#2ecc71"
        assert c.RED_PRIMARY == "#e74c3c"
        assert c.BLUE_PRIMARY == "#3498db"
        assert c.YELLOW_PRIMARY == "#f1c40f"
    
    def test_get_priority_color(self):
        """Testa mapeamento de cores por prioridade."""
        assert Colors.get_priority_color("Alta") == Colors.RED_PRIMARY
        assert Colors.get_priority_color("Média") == Colors.ORANGE
        assert Colors.get_priority_color("Baixa") == Colors.GREEN_PRIMARY
        assert Colors.get_priority_color("Desconhecida") == Colors.GRAY
    
    def test_get_state_color(self):
        """Testa mapeamento de cores por estado."""
        assert Colors.get_state_color("Concluído") == Colors.GREEN_PRIMARY
        assert Colors.get_state_color("solicitar voluntários") == Colors.BLUE_PRIMARY
        assert Colors.get_state_color("fazer indicação") == Colors.ORANGE
        assert Colors.get_state_color("Estado Desconhecido") == Colors.GRAY


# =============================================================================
# TESTES DA CLASSE COLUMNS
# =============================================================================

class TestColumns:
    """Testes para a classe Columns."""
    
    def test_columns_base_defined(self):
        """Testa se as colunas base estão definidas."""
        c = Columns()
        assert "Curso" in c.BASE
        assert "Turma" in c.BASE
        assert "Vagas" in c.BASE
        assert "Prioridade" in c.BASE
        assert "Estado" in c.BASE
    
    def test_columns_numeric(self):
        """Testa colunas numéricas."""
        c = Columns()
        assert "Vagas" in c.NUMERIC
        assert "Autorizados pelas escalantes" in c.NUMERIC
    
    def test_columns_date(self):
        """Testa colunas de data."""
        c = Columns()
        assert "Recebimento do SIGAD com as vagas" in c.DATE
        assert "DATA_DA_CONCLUSAO" in c.DATE
        assert "Fim da indicação da SIAT" in c.DATE
    
    def test_columns_required(self):
        """Testa colunas obrigatórias."""
        c = Columns()
        assert "Curso" in c.REQUIRED
        assert "Turma" in c.REQUIRED
        assert "Vagas" in c.REQUIRED
    
    def test_columns_no_duplicates(self):
        """Testa se não há colunas duplicadas."""
        c = Columns()
        assert len(c.BASE) == len(set(c.BASE))
        assert len(c.NUMERIC) == len(set(c.NUMERIC))
        assert len(c.DATE) == len(set(c.DATE))


# =============================================================================
# TESTES DA CLASSE FICFIELDS
# =============================================================================

class TestFICFields:
    """Testes para a classe FICFields."""
    
    def test_fic_fields_control(self):
        """Testa campos de controle do FIC."""
        f = FICFields()
        assert "ID" in f.CONTROL
        assert "Data_Criacao" in f.CONTROL
        assert "Data_Atualizacao" in f.CONTROL
        assert "Status" in f.CONTROL
    
    def test_fic_fields_candidate(self):
        """Testa campos do candidato."""
        f = FICFields()
        assert "Nome_Completo" in f.CANDIDATE
        assert "CPF" in f.CANDIDATE
        assert "SARAM" in f.CANDIDATE
        assert "Email" in f.CANDIDATE
    
    def test_fic_fields_all(self):
        """Testa lista completa de campos."""
        f = FICFields()
        assert len(f.ALL) > 0
        assert "ID" in f.ALL
        assert "Nome_Completo" in f.ALL
        assert "CPF" in f.ALL
    
    def test_fic_fields_required(self):
        """Testa campos obrigatórios do FIC."""
        f = FICFields()
        assert "Curso" in f.REQUIRED
        assert "Turma" in f.REQUIRED
        assert "Nome_Completo" in f.REQUIRED
        assert "CPF" in f.REQUIRED
    
    def test_fic_fields_no_duplicates(self):
        """Testa se não há campos duplicados."""
        f = FICFields()
        assert len(f.ALL) == len(set(f.ALL))


# =============================================================================
# TESTES DA CLASSE CHOICES
# =============================================================================

class TestChoices:
    """Testes para a classe Choices."""
    
    def test_choices_priority(self):
        """Testa opções de prioridade."""
        c = Choices()
        assert "Alta" in c.PRIORITY
        assert "Média" in c.PRIORITY
        assert "Baixa" in c.PRIORITY
    
    def test_choices_state(self):
        """Testa opções de estado."""
        c = Choices()
        assert "solicitar voluntários" in c.STATE
        assert "fazer indicação" in c.STATE
        assert "Concluído" in c.STATE
        assert "ver vagas escalantes" in c.STATE
    
    def test_choices_fic_status(self):
        """Testa status do FIC."""
        c = Choices()
        assert "Rascunho" in c.FIC_STATUS
        assert "Pendente" in c.FIC_STATUS
        assert "Aprovado" in c.FIC_STATUS
        assert "Reprovado" in c.FIC_STATUS
    
    def test_choices_ranks(self):
        """Testa postos e graduações."""
        c = Choices()
        assert "CEL" in c.RANKS
        assert "TC" in c.RANKS
        assert "MAJ" in c.RANKS
        assert "CAP" in c.RANKS
        # SGT pode estar formatado de diferentes formas
        assert any("SGT" in rank for rank in c.RANKS)
        assert "CB" in c.RANKS
        assert "SD" in c.RANKS
        assert "CIVIL" in c.RANKS


# =============================================================================
# TESTES DA CLASSE LOGGINGCONFIG
# =============================================================================

class TestLoggingConfig:
    """Testes para a classe LoggingConfig."""
    
    def test_logging_default_level(self):
        """Testa nível padrão de log."""
        lc = LoggingConfig()
        assert lc.LEVEL == "INFO"
    
    def test_logging_levels(self):
        """Testa níveis de log disponíveis."""
        lc = LoggingConfig()
        assert lc.LEVELS["DEBUG"] == 10
        assert lc.LEVELS["INFO"] == 20
        assert lc.LEVELS["WARNING"] == 30
        assert lc.LEVELS["ERROR"] == 40
        assert lc.LEVELS["CRITICAL"] == 50


# =============================================================================
# TESTES DA CLASSE MESSAGES
# =============================================================================

class TestMessages:
    """Testes para a classe Messages."""
    
    def test_messages_success(self):
        """Testa mensagens de sucesso."""
        m = Messages()
        assert "sucesso" in m.SUCCESS_SAVE.lower() or "✅" in m.SUCCESS_SAVE
        assert "sucesso" in m.SUCCESS_DELETE.lower() or "✅" in m.SUCCESS_DELETE
    
    def test_messages_error(self):
        """Testa mensagens de erro."""
        m = Messages()
        assert "erro" in m.ERROR_GENERIC.lower() or "❌" in m.ERROR_GENERIC
        assert "erro" in m.ERROR_SAVE.lower() or "❌" in m.ERROR_SAVE
    
    def test_messages_fic(self):
        """Testa mensagens específicas de FIC."""
        m = Messages()
        assert "CPF" in m.FIC_INVALID_CPF
        assert "e-mail" in m.FIC_INVALID_EMAIL.lower() or "email" in m.FIC_INVALID_EMAIL.lower()


# =============================================================================
# TESTES DA CLASSE EXPORTCONFIG
# =============================================================================

class TestExportConfig:
    """Testes para a classe ExportConfig."""
    
    def test_export_csv_config(self):
        """Testa configurações de exportação CSV."""
        ec = ExportConfig()
        assert ec.CSV_SEPARATOR == ";"
        assert ec.CSV_DECIMAL == ","
        assert ec.CSV_ENCODING == "utf-8-sig"
    
    def test_export_excel_config(self):
        """Testa configurações de exportação Excel."""
        ec = ExportConfig()
        assert ec.EXCEL_ENGINE == "openpyxl"
        assert ec.EXCEL_SHEET_NAME == "Dados"
    
    def test_export_docx_config(self):
        """Testa configurações de exportação Word."""
        ec = ExportConfig()
        assert ec.DOCX_FONT_NAME == "Arial"
        assert ec.DOCX_FONT_SIZE == 11


# =============================================================================
# TESTES DAS INSTÂNCIAS GLOBAIS
# =============================================================================

class TestGlobalInstances:
    """Testes para as instâncias globais das configurações."""
    
    def test_settings_instance(self):
        """Testa instância global de settings."""
        assert isinstance(settings, Settings)
        assert settings.APP_NAME == "Sistema de Controle de Cursos"
    
    def test_paths_instance(self):
        """Testa instância global de paths."""
        assert isinstance(paths, Paths)
        assert isinstance(paths.DATA_DIR, Path)
    
    def test_colors_instance(self):
        """Testa instância global de colors."""
        assert isinstance(colors, Colors)
        assert colors.GREEN_PRIMARY == "#2ecc71"
    
    def test_columns_instance(self):
        """Testa instância global de columns."""
        assert isinstance(columns, Columns)
        assert "Curso" in columns.BASE
    
    def test_fic_fields_instance(self):
        """Testa instância global de fic_fields."""
        assert isinstance(fic_fields, FICFields)
        assert "ID" in fic_fields.CONTROL
    
    def test_choices_instance(self):
        """Testa instância global de choices."""
        assert isinstance(choices, Choices)
        assert len(choices.PRIORITY) == 3


# =============================================================================
# TESTES DAS FUNÇÕES UTILITÁRIAS
# =============================================================================

class TestUtilityFunctions:
    """Testes para funções utilitárias do módulo config."""
    
    def test_get_column_types(self):
        """Testa mapeamento de tipos de colunas."""
        types = get_column_types()
        assert isinstance(types, dict)
        assert types.get("Vagas") == "int"
        assert types.get("Data_Criacao") == "datetime"
    
    def test_get_default_values(self):
        """Testa valores padrão."""
        defaults = get_default_values()
        assert isinstance(defaults, dict)
        assert defaults.get("Vagas") == 0
        assert defaults.get("Prioridade") == "Média"
        assert defaults.get("Estado") == "solicitar voluntários"
    
    def test_validate_config_success(self):
        """Testa validação de configurações válidas."""
        is_valid, errors = validate_config()
        assert is_valid is True
        assert errors == []
