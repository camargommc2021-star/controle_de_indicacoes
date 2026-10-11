"""
Módulo de validação de dados para o sistema de controle de cursos.

Este módulo fornece funções para validação de datas, campos de cursos
e utilitários de sanitização de texto.
"""

import re
import unicodedata
from datetime import datetime, date
from typing import Optional, Tuple, List, Any
import pandas as pd


# ============================================================================
# PARSER E VALIDAÇÃO DE DATAS
# ============================================================================

def parse_data(valor: Any) -> Optional[date]:
    """
    Converte diversos formatos de data para datetime.date.
    Retorna None se o valor for inválido, nulo ou vazio.
    Suporta: None, NaN, '', 'nan', str 'DD/MM/AAAA', 'AAAA-MM-DD',
    'AAAA-MM-DD HH:MM:SS', datetime, date, pd.Timestamp.
    """
    if valor is None:
        return None
    
    if isinstance(valor, str):
        val_str = valor.strip()
        if not val_str or val_str.lower() in ('nan', 'none', 'nat', 'null'):
            return None
        for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%Y-%m-%dT%H:%M:%S'):
            try:
                return datetime.strptime(val_str, fmt).date()
            except ValueError:
                pass
        try:
            ts = pd.to_datetime(val_str, errors='coerce')
            if pd.notna(ts):
                return ts.date()
        except Exception:
            pass
        return None

    try:
        if pd.isna(valor):
            return None
    except Exception:
        pass

    if isinstance(valor, pd.Timestamp):
        return valor.date()
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor

    try:
        ts = pd.to_datetime(valor, errors='coerce')
        if pd.notna(ts):
            return ts.date()
    except Exception:
        pass

    return None


def curso_concluido(row: Any) -> bool:
    """
    Verifica se um curso está concluído.

    Critérios de conclusão:
    - Estado normalizado (strip, lowercase, sem acentos via unicodedata) inicia com 'conclu', OU
    - DATA_DA_CONCLUSAO é uma data válida reconhecida por parse_data.

    Args:
        row: Linha do curso (pd.Series, dict ou mapeamento com dados do curso).

    Returns:
        bool: True se o curso estiver concluído, False caso contrário.
    """
    if row is None:
        return False

    estado = None
    data_conclusao = None

    if hasattr(row, 'get'):
        estado = row.get('Estado')
        data_conclusao = row.get('DATA_DA_CONCLUSAO')
    elif hasattr(row, '__getitem__'):
        try:
            estado = row['Estado']
        except Exception:
            pass
        try:
            data_conclusao = row['DATA_DA_CONCLUSAO']
        except Exception:
            pass

    if estado is not None:
        try:
            if not pd.isna(estado):
                norm = unicodedata.normalize('NFKD', str(estado)).encode('ASCII', 'ignore').decode('utf-8').strip().lower()
                if norm.startswith('conclu'):
                    return True
        except Exception:
            pass

    if parse_data(data_conclusao) is not None:
        return True

    return False


def calcular_metricas_prazos(df: pd.DataFrame) -> dict:
    """
    Calcula métricas consolidadas de prazos para o Dashboard e a Barra Lateral.

    Cursos concluídos são desconsiderados na contagem de atrasados, urgentes
    e prazos próximos da chefia.

    Regras de prazos:
    - Atrasado: data < hoje
    - Urgente: entre 0 e 5 dias restantes
    - Chefia próximo: entre 0 e 7 dias restantes

    Args:
        df: DataFrame contendo os cursos.

    Returns:
        dict: Dicionário contendo as contagens de 'atrasados', 'urgentes' e 'chefia_proximo'.
    """
    hoje = date.today()
    atrasados = 0
    urgentes = 0
    chefia_proximo = 0

    if df is not None and not df.empty:
        tem_siat = 'Fim da indicação da SIAT' in df.columns
        tem_chefia = 'Prazo dado pela chefia' in df.columns

        for _, row in df.iterrows():
            if curso_concluido(row):
                continue

            if tem_siat:
                d = parse_data(row.get('Fim da indicação da SIAT'))
                if d is not None:
                    dias = (d - hoje).days
                    if dias < 0:
                        atrasados += 1
                    elif 0 <= dias <= 5:
                        urgentes += 1

            if tem_chefia:
                d = parse_data(row.get('Prazo dado pela chefia'))
                if d is not None:
                    dias = (d - hoje).days
                    if 0 <= dias <= 7:
                        chefia_proximo += 1

    return {
        'atrasados': atrasados,
        'urgentes': urgentes,
        'chefia_proximo': chefia_proximo
    }


def limpar_valor(valor: Any) -> str:
    """
    Retorna string vazia se o valor for None, NaN, 'nan' ou vazio.
    Caso contrário, retorna a representação em string (ou formatada) sem espaços extras.
    """
    if valor is None:
        return ""
    try:
        if pd.isna(valor):
            return ""
    except Exception:
        pass
    s = str(valor).strip()
    if s.lower() in ('nan', 'none', 'nat'):
        return ""
    return s


def is_valid_date(date_str: str, date_format: str = "%d/%m/%Y") -> bool:
    """
    Verifica se uma string representa uma data válida no formato especificado.

    Args:
        date_str: String contendo a data a ser validada.
        date_format: Formato esperado da data (padrão: "%d/%m/%Y").

    Returns:
        bool: True se a data for válida, False caso contrário.

    Examples:
        >>> is_valid_date("25/12/2023")
        True
        >>> is_valid_date("32/12/2023")
        False
        >>> is_valid_date("2023-12-25", "%Y-%m-%d")
        True
    """
    if not date_str or not isinstance(date_str, str):
        return False
    
    try:
        datetime.strptime(date_str.strip(), date_format)
        return True
    except ValueError:
        return False
    except Exception:
        return False


def parse_date(date_str: str, date_format: str = "%d/%m/%Y") -> Optional[datetime]:
    """
    Converte uma string em um objeto datetime.

    Args:
        date_str: String contendo a data a ser convertida.
        date_format: Formato esperado da data (padrão: "%d/%m/%Y").

    Returns:
        Optional[datetime]: Objeto datetime se a conversão for bem-sucedida,
            None caso contrário.

    Examples:
        >>> parse_date("25/12/2023")
        datetime(2023, 12, 25, 0, 0)
        >>> parse_date("data inválida")
        None
    """
    if not date_str or not isinstance(date_str, str):
        return None
    
    try:
        return datetime.strptime(date_str.strip(), date_format)
    except ValueError:
        return None
    except Exception:
        return None


def is_future_date(date_str: str, date_format: str = "%d/%m/%Y") -> bool:
    """
    Verifica se uma data está no futuro.

    Args:
        date_str: String contendo a data a ser verificada.
        date_format: Formato esperado da data (padrão: "%d/%m/%Y").

    Returns:
        bool: True se a data for futura, False caso contrário.

    Examples:
        >>> is_future_date("25/12/2030")
        True
        >>> is_future_date("25/12/2020")
        False
    """
    parsed_date = parse_date(date_str, date_format)
    if parsed_date is None:
        return False
    
    try:
        return parsed_date.date() > date.today()
    except Exception:
        return False


def is_past_date(date_str: str, date_format: str = "%d/%m/%Y") -> bool:
    """
    Verifica se uma data está no passado.

    Args:
        date_str: String contendo a data a ser verificada.
        date_format: Formato esperado da data (padrão: "%d/%m/%Y").

    Returns:
        bool: True se a data for passada, False caso contrário.
    """
    parsed_date = parse_date(date_str, date_format)
    if parsed_date is None:
        return False
    
    try:
        return parsed_date.date() < date.today()
    except Exception:
        return False


def date_range_valid(start_date: str, end_date: str, 
                     date_format: str = "%d/%m/%Y") -> bool:
    """
    Verifica se o intervalo de datas é válido (data inicial <= data final).

    Args:
        start_date: String com a data inicial.
        end_date: String com a data final.
        date_format: Formato das datas.

    Returns:
        bool: True se o intervalo for válido.
    """
    start = parse_date(start_date, date_format)
    end = parse_date(end_date, date_format)
    
    if start is None or end is None:
        return False
    
    return start <= end


# ============================================================================
# VALIDAÇÃO DE CAMPOS DO CURSO
# ============================================================================

def validate_turma(turma: str) -> bool:
    """
    Valida o código de uma turma.

    Args:
        turma: String contendo o código da turma.

    Returns:
        bool: True se a turma for válida, False caso contrário.
    """
    if not turma or not isinstance(turma, str):
        return False
    
    turma = turma.strip()
    
    # Turma deve ter pelo menos 2 caracteres
    if len(turma) < 2:
        return False
    
    # Turma não deve conter caracteres especiais perigosos
    if re.search(r"[<>'\"%;&]", turma):
        return False
    
    return True


def validate_vagas(vagas: Any) -> Tuple[bool, str]:
    """
    Valida o número de vagas de um curso.

    Args:
        vagas: Valor representando o número de vagas.

    Returns:
        Tuple[bool, str]: (True, "") se válido, (False, mensagem_erro) se inválido.

    Examples:
        >>> validate_vagas(30)
        (True, "")
        >>> validate_vagas(0)
        (False, "Número de vagas deve ser maior que zero")
        >>> validate_vagas("abc")
        (False, "Número de vagas deve ser um número inteiro")
    """
    try:
        # Converte para inteiro se for string numérica
        if isinstance(vagas, str):
            vagas = int(vagas.strip())
        elif isinstance(vagas, float):
            vagas = int(vagas)
        elif not isinstance(vagas, int):
            return False, "Número de vagas deve ser um número inteiro"
        
        # Verifica se é positivo
        if vagas <= 0:
            return False, "Número de vagas deve ser maior que zero"
        
        # Verifica limite máximo razoável
        if vagas > 999:
            return False, "Número de vagas parece excessivo (máximo: 999)"
        
        return True, ""
        
    except ValueError:
        return False, "Número de vagas deve ser um número inteiro válido"
    except Exception as e:
        return False, f"Erro ao validar vagas: {str(e)}"


def validate_sigad(sigad: str) -> bool:
    """
    Valida um número de processo SIGAD.

    Args:
        sigad: String contendo o número do processo SIGAD.

    Returns:
        bool: True se o SIGAD for válido, False caso contrário.
    """
    if not sigad or not isinstance(sigad, str):
        return False
    
    sigad = sigad.strip()
    
    # SIGAD deve ter pelo menos 5 caracteres
    if len(sigad) < 5:
        return False
    
    # SIGAD não deve conter caracteres especiais perigosos
    if re.search(r"[<>'\"%;&]", sigad):
        return False
    
    return True


def validate_curso(data: dict) -> Tuple[bool, List[str]]:
    """
    Valida todos os campos de um curso.

    Args:
        data: Dicionário contendo os dados do curso.

    Returns:
        Tuple[bool, List[str]]: (True, []) se válido, 
            (False, [lista de erros]) se inválido.
    """
    errors = []
    
    if not data or not isinstance(data, dict):
        return False, ["Dados do curso não fornecidos"]
    
    # Valida nome do curso
    if not data.get('nome') or not str(data.get('nome')).strip():
        errors.append("Nome do curso é obrigatório")
    
    # Valida turma
    if not validate_turma(data.get('turma', '')):
        errors.append("Código da turma é inválido")
    
    # Valida vagas
    vagas_valid, vagas_error = validate_vagas(data.get('vagas', 0))
    if not vagas_valid:
        errors.append(f"Vagas: {vagas_error}")
    
    # Valida datas se fornecidas
    if data.get('data_inicio') and not is_valid_date(str(data.get('data_inicio'))):
        errors.append("Data de início inválida")
    
    if data.get('data_fim') and not is_valid_date(str(data.get('data_fim'))):
        errors.append("Data de término inválida")
    
    # Valida intervalo de datas
    if (data.get('data_inicio') and data.get('data_fim') and
        is_valid_date(str(data.get('data_inicio'))) and 
        is_valid_date(str(data.get('data_fim')))):
        if not date_range_valid(str(data.get('data_inicio')), str(data.get('data_fim'))):
            errors.append("Data de início deve ser anterior à data de término")
    
    # Valida SIGAD se fornecido
    if data.get('sigad') and not validate_sigad(str(data.get('sigad'))):
        errors.append("Número SIGAD inválido")
    
    return len(errors) == 0, errors


# ============================================================================
# UTILITÁRIOS
# ============================================================================

def sanitize_string(text: str) -> str:
    """
    Remove caracteres especiais perigosos de uma string.

    Remove caracteres que podem ser usados para injeção de código,
    SQL injection, XSS, etc.

    Args:
        text: String a ser sanitizada.

    Returns:
        str: String sanitizada.

    Examples:
        >>> sanitize_string("<script>alert('xss')</script>")
        "scriptalert('xss')/script"
        >>> sanitize_string("DROP TABLE users; --")
        "DROP TABLE users --"
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Caracteres perigosos a serem removidos
    dangerous_chars = [
        '<', '>',  # Tags HTML
        '"',     # Aspas duplas
        ';',     # SQL statement terminator
        '--',    # SQL comment
        '/*', '*/',  # SQL block comment
        "'",     # Aspas simples
        '`',     # Backtick
        '|',     # Pipe
        '&',     # Ampersand (XSS)
        '%',     # Percent (SQL wildcards)
    ]
    
    result = text
    for char in dangerous_chars:
        result = result.replace(char, '')
    
    # Remove múltiplos espaços
    result = ' '.join(result.split())
    
    return result.strip()


def normalize_text(text: str) -> str:
    """
    Normaliza um texto convertendo para maiúsculas e removendo espaços extras.

    Args:
        text: String a ser normalizada.

    Returns:
        str: Texto normalizado em maiúsculas sem espaços extras.

    Examples:
        >>> normalize_text("  texto ExEmPlO  ")
        "TEXTO EXEMPLO"
        >>> normalize_text("outro   exemplo")
        "OUTRO EXEMPLO"
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Remove espaços no início e fim, converte múltiplos espaços em um
    text = ' '.join(text.split())
    
    # Converte para maiúsculas
    return text.strip().upper()


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Trunca uma string se exceder o tamanho máximo.

    Args:
        text: String a ser truncada.
        max_length: Tamanho máximo permitido.
        suffix: Sufixo a ser adicionado se truncado.

    Returns:
        str: String truncada se necessário.
    """
    if not text or not isinstance(text, str):
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def slugify(text: str) -> str:
    """
    Converte um texto para formato slug (URL-friendly).

    Args:
        text: String a ser convertida.

    Returns:
        str: Texto em formato slug.

    Examples:
        >>> slugify("Título do Curso 2024!")
        "titulo-do-curso-2024"
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Converte para minúsculas
    text = text.lower()
    
    # Remove acentos (simplificado)
    accents = {
        'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a', 'ä': 'a',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
        'ó': 'o', 'ò': 'o', 'õ': 'o', 'ô': 'o', 'ö': 'o',
        'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
        'ç': 'c', 'ñ': 'n', 'ý': 'y', 'ÿ': 'y',
    }
    
    for char, replacement in accents.items():
        text = text.replace(char, replacement)
    
    # Substitui espaços e caracteres não alfanuméricos por hífen
    text = re.sub(r'[^a-z0-9]+', '-', text)
    
    # Remove hífens múltiplos
    text = re.sub(r'-+', '-', text)
    
    # Remove hífens no início e fim
    return text.strip('-')


# ============================================================================
# FUNÇÕES AUXILIARES ESPECÍFICAS DO DOMÍNIO
# ============================================================================

def validate_nota(nota: Any, tipo: str = "geral") -> Tuple[bool, str]:
    """
    Valida uma nota (deve estar entre 0 e 100).

    Args:
        nota: Valor da nota a ser validada.
        tipo: Tipo da nota (para mensagem de erro).

    Returns:
        Tuple[bool, str]: (True, "") se válido, (False, mensagem_erro) se inválido.
    """
    try:
        if isinstance(nota, str):
            nota = float(nota.replace(',', '.'))
        else:
            nota = float(nota)
        
        if nota < 0 or nota > 100:
            return False, f"Nota {tipo} deve estar entre 0 e 100"
        
        return True, ""
        
    except (ValueError, TypeError):
        return False, f"Nota {tipo} deve ser um número válido"


def validate_frequencia(frequencia: Any) -> Tuple[bool, str]:
    """
    Valida uma frequência (deve estar entre 0 e 100).

    Args:
        frequencia: Valor da frequência a ser validada.

    Returns:
        Tuple[bool, str]: (True, "") se válido, (False, mensagem_erro) se inválido.
    """
    try:
        if isinstance(frequencia, str):
            freq = float(frequencia.replace(',', '.'))
        else:
            freq = float(frequencia)
        
        if freq < 0 or freq > 100:
            return False, "Frequência deve estar entre 0% e 100%"
        
        return True, ""
        
    except (ValueError, TypeError):
        return False, "Frequência deve ser um número válido"


def validate_ano(ano: Any) -> Tuple[bool, str]:
    """
    Valida um ano (deve ser um ano válido).

    Args:
        ano: Valor do ano a ser validado.

    Returns:
        Tuple[bool, str]: (True, "") se válido, (False, mensagem_erro) se inválido.
    """
    try:
        if isinstance(ano, str):
            ano = int(ano.strip())
        else:
            ano = int(ano)
        
        ano_atual = date.today().year
        
        if ano < 1900 or ano > ano_atual + 5:
            return False, f"Ano deve estar entre 1900 e {ano_atual + 5}"
        
        return True, ""
        
    except (ValueError, TypeError):
        return False, "Ano deve ser um número inteiro válido"


def validate_carga_horaria(carga: Any) -> Tuple[bool, str]:
    """
    Valida uma carga horária.

    Args:
        carga: Valor da carga horária a ser validada.

    Returns:
        Tuple[bool, str]: (True, "") se válido, (False, mensagem_erro) se inválido.
    """
    try:
        if isinstance(carga, str):
            carga = int(carga.strip())
        else:
            carga = int(carga)
        
        if carga <= 0:
            return False, "Carga horária deve ser maior que zero"
        
        if carga > 2000:
            return False, "Carga horária parece excessiva (máximo: 2000h)"
        
        return True, ""
        
    except (ValueError, TypeError):
        return False, "Carga horária deve ser um número inteiro válido"
