"""
Arquivo de configuração centralizado do Sistema de Controle de Cursos.

Este módulo contém todas as constantes, configurações e parâmetros do sistema,
organizados em classes para facilitar a manutenção e reuso.

Usage:
    from config import Settings, Colors, Columns, FICFields, Messages
    
    # Acessar configurações
    print(Settings.APP_NAME)
    print(Colors.GREEN_PRIMARY)
    print(Columns.BASE)
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Tuple
import os


# =============================================================================
# CONFIGURAÇÕES GERAIS DO SISTEMA
# =============================================================================

@dataclass(frozen=True)
class Settings:
    """Configurações gerais da aplicação."""
    
    # Informações do aplicativo
    APP_NAME: str = "Sistema de Controle de Cursos"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Sistema para gerenciamento de cursos e indicações"
    
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
    
    # Configurações de exportação
    EXPORT_DECIMAL_SEPARATOR: str = ","
    EXPORT_ENCODING: str = "utf-8-sig"


# =============================================================================
# CONFIGURAÇÕES DE CAMINHOS
# =============================================================================

@dataclass(frozen=True)
class Paths:
    """Caminhos de diretórios e arquivos do sistema."""
    
    # Diretório base do projeto
    BASE_DIR: Path = field(default_factory=lambda: Path(__file__).parent)
    
    # Subdiretórios
    DATA_DIR: Path = field(default_factory=lambda: Path(__file__).parent / "data")
    ASSETS_DIR: Path = field(default_factory=lambda: Path(__file__).parent / "assets")
    BACKUPS_DIR: Path = field(default_factory=lambda: Path(__file__).parent / "backups")
    STREAMLIT_DIR: Path = field(default_factory=lambda: Path(__file__).parent / ".streamlit")
    
    # Arquivos de dados
    CURSOS_FILE: Path = field(default_factory=lambda: Path(__file__).parent / "data" / "cursos.csv")
    HISTORICO_FILE: Path = field(default_factory=lambda: Path(__file__).parent / "data" / "historico.csv")
    FIC_FILE: Path = field(default_factory=lambda: Path(__file__).parent / "data" / "fic.csv")
    
    # Templates
    FIC_TEMPLATE_DOCX: Path = field(default_factory=lambda: Path(__file__).parent / "assets" / "FIC_layout.docx")
    
    def ensure_dirs(self) -> None:
        """Cria os diretórios necessários se não existirem."""
        for path in [self.DATA_DIR, self.ASSETS_DIR, self.BACKUPS_DIR]:
            path.mkdir(parents=True, exist_ok=True)


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
# CAMPOS DO FIC (FICHA DE INDICAÇÃO DE CANDIDATO)
# =============================================================================

@dataclass(frozen=True)
class FICFields:
    """Campos do FIC (Ficha de Indicação de Candidato)."""
    
    # Campos de controle
    CONTROL: List[str] = field(default_factory=lambda: [
        "ID",
        "Data_Criacao",
        "Data_Atualizacao",
        "Status",
    ])
    
    # Campos do curso
    COURSE: List[str] = field(default_factory=lambda: [
        "Curso",
        "Turma",
        "Local_GT",
        "Comando",
    ])
    
    # Campos de datas
    DATES: List[str] = field(default_factory=lambda: [
        "Data_Inicio_Presencial",
        "Data_Termino_Presencial",
        "Data_Inicio_Distancia",
        "Data_Termino_Distancia",
    ])
    
    # Campos do indicado
    CANDIDATE: List[str] = field(default_factory=lambda: [
        "Posto_Graduacao",
        "Nome_Completo",
        "OM_Indicado",
        "CPF",
        "SARAM",
        "Email",
        "Telefone",
    ])
    
    # Campos profissionais
    PROFESSIONAL: List[str] = field(default_factory=lambda: [
        "Funcao_Atual",
        "Data_Ultima_Promocao",
        "Funcao_Apos_Curso",
        "Tempo_Servico",
        "Pre_Requisitos",
    ])
    
    # Campos de cursos anteriores
    PREVIOUS_COURSES: List[str] = field(default_factory=lambda: [
        "Curso_Mapeado",
        "Progressao_Carreira",
        "Comunicado_Indicado",
        "Outro_Impedimento",
        "Curso_Anterior",
        "Ano_Curso_Anterior",
    ])
    
    # Campos de declarações
    DECLARATIONS: List[str] = field(default_factory=lambda: [
        "Ciencia_Dedicacao_EAD",
    ])
    
    # Campos de chefia
    SUPERVISOR: List[str] = field(default_factory=lambda: [
        "Justificativa_Chefe",
        "Nome_Chefe_COP",
        "Posto_Chefe_COP",
    ])
    
    # Campos DACTA
    DACTA: List[str] = field(default_factory=lambda: [
        "Nome_Responsavel_DACTA",
        "Posto_Responsavel_DACTA",
    ])
    
    # Campo especial
    PPD_CIVIL: str = "PPD_Civil"
    
    # Todas as colunas do FIC
    ALL: List[str] = field(default_factory=lambda: [
        "ID",
        "Data_Criacao",
        "Data_Atualizacao",
        "Status",
        "Curso",
        "Turma",
        "Local_GT",
        "Comando",
        "Data_Inicio_Presencial",
        "Data_Termino_Presencial",
        "Data_Inicio_Distancia",
        "Data_Termino_Distancia",
        "PPD_Civil",
        "Posto_Graduacao",
        "Nome_Completo",
        "OM_Indicado",
        "CPF",
        "SARAM",
        "Email",
        "Telefone",
        "Funcao_Atual",
        "Data_Ultima_Promocao",
        "Funcao_Apos_Curso",
        "Tempo_Servico",
        "Pre_Requisitos",
        "Curso_Mapeado",
        "Progressao_Carreira",
        "Comunicado_Indicado",
        "Outro_Impedimento",
        "Curso_Anterior",
        "Ano_Curso_Anterior",
        "Ciencia_Dedicacao_EAD",
        "Justificativa_Chefe",
        "Nome_Chefe_COP",
        "Posto_Chefe_COP",
        "Nome_Responsavel_DACTA",
        "Posto_Responsavel_DACTA",
    ])
    
    # Campos obrigatórios do FIC
    REQUIRED: List[str] = field(default_factory=lambda: [
        "Curso",
        "Turma",
        "Nome_Completo",
        "Posto_Graduacao",
        "OM_Indicado",
        "CPF",
        "SARAM",
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
    
    # Status do FIC
    FIC_STATUS: List[str] = field(default_factory=lambda: [
        "Rascunho",
        "Pendente",
        "Aprovado",
        "Reprovado",
        "Concluído",
        "Cancelado",
    ])
    
    # Postos e Graduações
    RANKS: List[str] = field(default_factory=lambda: [
        "CEL",
        "TC",
        "MAJ",
        "CAP",
        "1º TEN",
        "2º TEN",
        "ASP",
        "ST",
        "1º SGT",
        "2º SGT",
        "3º SGT",
        "CB",
        "SD",
        "CIVIL",
    ])
    
    # OMs (Organizações Militares) - exemplo, pode ser expandido
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
# CONFIGURAÇÕES DE LOGGING
# =============================================================================

@dataclass(frozen=True)
class LoggingConfig:
    """Configurações de logging do sistema."""
    
    # Nível de log padrão
    LEVEL: str = "INFO"
    
    # Formatos de log
    FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    
    # Arquivo de log
    LOG_FILE: Path = field(default_factory=lambda: Path(__file__).parent / "logs" / "app.log")
    MAX_BYTES: int = 5_242_880  # 5 MB
    BACKUP_COUNT: int = 3
    
    # Níveis disponíveis
    LEVELS: Dict[str, int] = field(default_factory=lambda: {
        "DEBUG": 10,
        "INFO": 20,
        "WARNING": 30,
        "ERROR": 40,
        "CRITICAL": 50,
    })


# =============================================================================
# MENSAGENS DO SISTEMA
# =============================================================================

@dataclass(frozen=True)
class Messages:
    """Mensagens padrão utilizadas no sistema."""
    
    # Mensagens de sucesso
    SUCCESS_SAVE: str = "✅ Dados salvos com sucesso!"
    SUCCESS_DELETE: str = "✅ Registro excluído com sucesso!"
    SUCCESS_EXPORT: str = "✅ Arquivo exportado com sucesso!"
    SUCCESS_IMPORT: str = "✅ Dados importados com sucesso!"
    SUCCESS_BACKUP: str = "✅ Backup realizado com sucesso!"
    SUCCESS_FIC_GENERATED: str = "✅ FIC gerado com sucesso!"
    
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
    
    # Mensagens específicas de FIC
    FIC_INVALID_CPF: str = "❌ CPF inválido."
    FIC_INVALID_EMAIL: str = "❌ E-mail inválido."
    FIC_COURSE_NOT_FOUND: str = "❌ Curso não encontrado."


# =============================================================================
# CONFIGURAÇÕES DE EXPORTAÇÃO
# =============================================================================

@dataclass(frozen=True)
class ExportConfig:
    """Configurações para exportação de dados."""
    
    # Configurações CSV
    CSV_SEPARATOR: str = ";"
    CSV_DECIMAL: str = ","
    CSV_ENCODING: str = "utf-8-sig"
    
    # Configurações Excel
    EXCEL_ENGINE: str = "openpyxl"
    EXCEL_SHEET_NAME: str = "Dados"
    
    # Configurações PDF
    PDF_PAGE_SIZE: str = "A4"
    PDF_ORIENTATION: str = "portrait"
    PDF_MARGIN_TOP: float = 2.0
    PDF_MARGIN_BOTTOM: float = 2.0
    PDF_MARGIN_LEFT: float = 2.0
    PDF_MARGIN_RIGHT: float = 2.0
    
    # Configurações Word (FIC)
    DOCX_FONT_NAME: str = "Arial"
    DOCX_FONT_SIZE: int = 11


# =============================================================================
# INSTÂNCIAS GLOBAIS (para importação direta)
# =============================================================================

# Instâncias das configurações para uso direto
settings = Settings()
paths = Paths()
colors = Colors()
columns = Columns()
fic_fields = FICFields()
choices = Choices()
logging_config = LoggingConfig()
messages = Messages()
export_config = ExportConfig()


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
        "Data_Inicio_Presencial": "date",
        "Data_Termino_Presencial": "date",
        "Data_Inicio_Distancia": "date",
        "Data_Termino_Distancia": "date",
        "Data_Criacao": "datetime",
        "Data_Atualizacao": "datetime",
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
    
    # Verifica se todas as colunas FIC são únicas
    if len(fic_fields.ALL) != len(set(fic_fields.ALL)):
        errors.append("Colunas FIC contêm duplicatas")
    
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
