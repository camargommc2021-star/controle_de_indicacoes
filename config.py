"""
Arquivo de configuração centralizado do Sistema de Controle de Cursos.

Este módulo contém todas as constantes, configurações e parâmetros do sistema,
organizados em classes para facilitar a manutenção e reuso.

Usage:
    from config import Settings, Colors, Columns, Choices, Messages
    
    # Acessar configurações
    print(Settings.APP_NAME)
    print(Colors.GREEN_PRIMARY)
    print(Columns.BASE)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple


# =============================================================================
# CONFIGURAÇÕES GERAIS DO SISTEMA
# =============================================================================

@dataclass(frozen=True)
class Settings:
    """Configurações gerais da aplicação."""
    
    # Informações do aplicativo
    APP_NAME: str = "Sistema de Controle de Cursos"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Sistema para gerenciamento de cursos"
    
    # Configurações de página Streamlit
    PAGE_TITLE: str = "Controle de Cursos"
    PAGE_ICON: str = "📚"
    PAGE_LAYOUT: str = "wide"
    
    # Configurações de dados
    DEFAULT_ENCODING: str = "utf-8"
    DATE_FORMAT: str = "%d/%m/%Y"
    DATETIME_FORMAT: str = "%d/%m/%Y %H:%M:%S"
    
    # Limites do sistema
    MAX_UPLOAD_SIZE_MB: int = 10
    MAX_ROWS_DISPLAY: int = 1000


# =============================================================================
# PALETA DE CORES DO SISTEMA
# =============================================================================

@dataclass(frozen=True)
class Colors:
    """Paleta de cores utilizada no sistema para UI e visualizações."""
    
    # Cores primárias - Verde
    GREEN_PRIMARY: str = "#2ecc71"
    GREEN_LIGHT: str = "#6BCF7F"
    GREEN_DARK: str = "#27ae60"
    
    # Cores de aviso - Amarelo/Laranja
    YELLOW_PRIMARY: str = "#f1c40f"
    YELLOW_LIGHT: str = "#FFD93D"
    YELLOW_GOLD: str = "#FFD700"
    ORANGE: str = "#FFA500"
    ORANGE_DARK: str = "#f39c12"
    
    # Cores de erro/perigo - Vermelho
    RED_PRIMARY: str = "#e74c3c"
    RED_LIGHT: str = "#FF6B6B"
    RED_BRIGHT: str = "#FF0000"
    RED_DARK: str = "#c0392b"
    
    # Cores de informação - Azul
    BLUE_PRIMARY: str = "#3498db"
    BLUE_DARK: str = "#2980b9"
    BLUE_LIGHT: str = "#4D96FF"
    BLUE_SKY: str = "#90EE90"
    
    # Cores neutras
    WHITE: str = "#FFFFFF"
    BLACK: str = "#000000"
    GRAY_LIGHT: str = "#ecf0f1"
    GRAY: str = "#95a5a6"
    GRAY_DARK: str = "#7f8c8d"
    
    # Mapeamento de cores para prioridades
    @classmethod
    def get_priority_color(cls, priority: str) -> str:
        """Retorna a cor correspondente à prioridade."""
        color_map = {
            "Alta": cls.RED_PRIMARY,
            "Média": cls.ORANGE,
            "Baixa": cls.GREEN_PRIMARY,
        }
        return color_map.get(priority, cls.GRAY)
    
    # Mapeamento de cores para estados
    @classmethod
    def get_state_color(cls, state: str) -> str:
        """Retorna a cor correspondente ao estado."""
        color_map = {
            "Concluído": cls.GREEN_PRIMARY,
            "solicitar voluntários": cls.BLUE_PRIMARY,
            "fazer indicação": cls.ORANGE,
            "ver vagas escalantes": cls.YELLOW_PRIMARY,
        }
        return color_map.get(state, cls.GRAY)


# =============================================================================
# DEFINIÇÃO DE COLUNAS
# =============================================================================

@dataclass(frozen=True)
class Columns:
    """Definição de colunas utilizadas em diferentes partes do sistema."""
    
    # Colunas base do sistema de controle de cursos
    BASE: List[str] = field(default_factory=lambda: [
        "Curso",
        "Turma",
        "Vagas",
        "Autorizados pelas escalantes",
        "Prioridade",
        "Recebimento do SIGAD com as vagas",
        "Numero do SIGAD",
        "Estado",
        "DATA_DA_CONCLUSAO",
        "Numero do SIGAD  encaminhando pra chefia",
        "Prazo dado pela chefia",
        "Fim da indicação da SIAT",
        "Notas",
        "OM_Executora",
    ])
    
    # Colunas numéricas (para tratamento especial)
    NUMERIC: List[str] = field(default_factory=lambda: [
        "Vagas",
        "Autorizados pelas escalantes",
    ])
    
    # Colunas de data (para tratamento especial)
    DATE: List[str] = field(default_factory=lambda: [
        "Recebimento do SIGAD com as vagas",
        "DATA_DA_CONCLUSAO",
        "Prazo dado pela chefia",
        "Fim da indicação da SIAT",
    ])
    
    # Colunas obrigatórias
    REQUIRED: List[str] = field(default_factory=lambda: [
        "Curso",
        "Turma",
        "Vagas",
    ])
    
    # Colunas editáveis na interface
    EDITABLE: List[str] = field(default_factory=lambda: [
        "Vagas",
        "Autorizados pelas escalantes",
        "Prioridade",
        "Estado",
        "Notas",
        "OM_Executora",
    ])


# =============================================================================
# OPÇÕES DE ENUMERAÇÃO
# =============================================================================

@dataclass(frozen=True)
class Choices:
    """Opções de seleção para campos do sistema."""
    
    # Opções de Prioridade
    PRIORITY: List[str] = field(default_factory=lambda: [
        "Alta",
        "Média",
        "Baixa",
    ])
    
    # Opções de Estado
    STATE: List[str] = field(default_factory=lambda: [
        "solicitar voluntários",
        "fazer indicação",
        "Concluído",
        "ver vagas escalantes",
    ])
    
    # OMs (Organizações Militares)
    OMS: List[str] = field(default_factory=lambda: [
        "Cmdo",
        "C Op",
        "DACTA",
        "DSUP",
        "DLog",
        "DTI",
        "Sec Geral",
    ])


# =============================================================================
# MENSAGENS DO SISTEMA
# =============================================================================

@dataclass(frozen=True)
class Messages:
    """Mensagens padrão utilizadas no sistema."""
    
    # Mensagens de sucesso
    SUCCESS_SAVE: str = "✅ Dados salvos com sucesso!"
    SUCCESS_DELETE: str = "✅ Registro excluído com sucesso!"
    SUCCESS_IMPORT: str = "✅ Dados importados com sucesso!"
    SUCCESS_BACKUP: str = "✅ Backup realizado com sucesso!"
    
    # Mensagens de erro
    ERROR_GENERIC: str = "❌ Ocorreu um erro. Tente novamente."
    ERROR_SAVE: str = "❌ Erro ao salvar dados."
    ERROR_LOAD: str = "❌ Erro ao carregar dados."
    ERROR_VALIDATION: str = "❌ Erro de validação nos dados."
    ERROR_FILE_NOT_FOUND: str = "❌ Arquivo não encontrado."
    ERROR_INVALID_FORMAT: str = "❌ Formato de arquivo inválido."
    ERROR_REQUIRED_FIELD: str = "❌ Campo obrigatório não preenchido."
    ERROR_DUPLICATE: str = "❌ Registro duplicado."
    
    # Mensagens de aviso
    WARNING_NO_DATA: str = "⚠️ Nenhum dado encontrado."
    WARNING_CONFIRM_DELETE: str = "⚠️ Tem certeza que deseja excluir?"
    WARNING_UNSAVED_CHANGES: str = "⚠️ Existem alterações não salvas."
    
    # Mensagens de informação
    INFO_LOADING: str = "⏳ Carregando..."
    INFO_PROCESSING: str = "⏳ Processando..."
    INFO_NO_RECORDS: str = "ℹ️ Nenhum registro encontrado."


# =============================================================================
# INSTÂNCIAS GLOBAIS (para importação direta)
# =============================================================================

# Instâncias das configurações para uso direto
settings = Settings()
colors = Colors()
columns = Columns()
choices = Choices()
messages = Messages()


# =============================================================================
# FUNÇÕES UTILITÁRIAS
# =============================================================================

def get_column_types() -> Dict[str, str]:
    """Retorna mapeamento de colunas para seus tipos de dados."""
    return {
        "Vagas": "int",
        "Autorizados pelas escalantes": "int",
        "Recebimento do SIGAD com as vagas": "date",
        "DATA_DA_CONCLUSAO": "date",
        "Prazo dado pela chefia": "date",
        "Fim da indicação da SIAT": "date",
    }


def get_default_values() -> Dict[str, any]:
    """Retorna valores padrão para colunas."""
    return {
        "Vagas": 0,
        "Autorizados pelas escalantes": 0,
        "Prioridade": "Média",
        "Estado": "solicitar voluntários",
        "Notas": "",
        "OM_Executora": "",
    }


def validate_config() -> Tuple[bool, List[str]]:
    """Valida se as configurações estão consistentes.
    
    Returns:
        Tuple contendo (sucesso, lista de erros)
    """
    errors = []
    
    # Verifica se todas as colunas base são únicas
    if len(columns.BASE) != len(set(columns.BASE)):
        errors.append("Colunas BASE contêm duplicatas")
    
    # Verifica se as opções de prioridade estão definidas
    if not choices.PRIORITY:
        errors.append("Opções de PRIORITY vazias")
    
    # Verifica se as opções de estado estão definidas
    if not choices.STATE:
        errors.append("Opções de STATE vazias")
    
    return len(errors) == 0, errors


# Valida as configurações ao importar o módulo
_is_valid, _errors = validate_config()
if not _is_valid:
    import warnings
    warnings.warn(f"Configurações inconsistentes: {_errors}")
