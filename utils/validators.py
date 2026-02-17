"""
Módulo de validação de dados para o sistema de controle de cursos.

Este módulo fornece funções para validação de datas, documentos (CPF, SARAM),
campos de cursos, FIC e utilitários de sanitização de texto.
"""

import re
from datetime import datetime, date
from typing import Optional, Tuple, List, Any


# ============================================================================
# VALIDAÇÃO DE DATAS
# ============================================================================

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
# VALIDAÇÃO DE DOCUMENTOS
# ============================================================================

def clean_cpf(cpf: str) -> str:
    """
    Remove caracteres não numéricos do CPF.

    Args:
        cpf: String contendo o CPF.

    Returns:
        str: CPF contendo apenas números.
    """
    if not cpf:
        return ""
    return re.sub(r'\D', '', str(cpf))


def is_valid_cpf(cpf: str) -> bool:
    """
    Valida um CPF verificando seus dígitos verificadores.

    O CPF é composto por 11 dígitos numéricos, sendo os dois últimos
    dígitos verificadores calculados a partir dos 9 primeiros.

    Args:
        cpf: String contendo o CPF (com ou sem formatação).

    Returns:
        bool: True se o CPF for válido, False caso contrário.

    Examples:
        >>> is_valid_cpf("529.982.247-25")
        True
        >>> is_valid_cpf("111.111.111-11")
        False
        >>> is_valid_cpf("52998224725")
        True
    """
    cpf = clean_cpf(cpf)
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais (CPFs inválidos conhecidos)
    if cpf == cpf[0] * 11:
        return False
    
    try:
        # Cálculo do primeiro dígito verificador
        sum_1 = 0
        for i in range(9):
            sum_1 += int(cpf[i]) * (10 - i)
        remainder_1 = sum_1 % 11
        digit_1 = 0 if remainder_1 < 2 else 11 - remainder_1
        
        # Verifica o primeiro dígito
        if int(cpf[9]) != digit_1:
            return False
        
        # Cálculo do segundo dígito verificador
        sum_2 = 0
        for i in range(10):
            sum_2 += int(cpf[i]) * (11 - i)
        remainder_2 = sum_2 % 11
        digit_2 = 0 if remainder_2 < 2 else 11 - remainder_2
        
        # Verifica o segundo dígito
        return int(cpf[10]) == digit_2
        
    except (ValueError, IndexError):
        return False


def format_cpf(cpf: str) -> str:
    """
    Formata um CPF no padrão XXX.XXX.XXX-XX.

    Args:
        cpf: String contendo o CPF (com ou sem formatação).

    Returns:
        str: CPF formatado ou string vazia se inválido.

    Examples:
        >>> format_cpf("52998224725")
        "529.982.247-25"
        >>> format_cpf("529.982.247-25")
        "529.982.247-25"
    """
    cpf = clean_cpf(cpf)
    
    if len(cpf) != 11:
        return ""
    
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def is_valid_saram(saram: str) -> bool:
    """
    Valida um número SARAM (formato numérico).

    O SARAM (Serviço de Administração de Recursos Materiais) é um número
    utilizado na identificação de militares e civis da Marinha do Brasil.

    Args:
        saram: String contendo o número SARAM.

    Returns:
        bool: True se o SARAM for válido, False caso contrário.

    Examples:
        >>> is_valid_saram("123456")
        True
        >>> is_valid_saram("12345")
        True
        >>> is_valid_saram("ABC123")
        False
    """
    if not saram:
        return False
    
    saram = str(saram).strip()
    
    # SARAM deve conter apenas números
    if not saram.isdigit():
        return False
    
    # SARAM deve ter entre 4 e 8 dígitos
    if len(saram) < 4 or len(saram) > 8:
        return False
    
    return True


def format_saram(saram: str) -> str:
    """
    Formata um número SARAM removendo caracteres não numéricos.

    Args:
        saram: String contendo o número SARAM.

    Returns:
        str: SARAM contendo apenas números.
    """
    if not saram:
        return ""
    
    return re.sub(r'\D', '', str(saram))


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
# VALIDAÇÃO DE FIC (Ficha Individual de Curso)
# ============================================================================

def validate_email(email: str) -> bool:
    """
    Valida um endereço de e-mail.

    Args:
        email: String contendo o endereço de e-mail.

    Returns:
        bool: True se o e-mail for válido, False caso contrário.

    Examples:
        >>> validate_email("usuario@exemplo.com")
        True
        >>> validate_email("usuario@exemplo")
        False
        >>> validate_email("invalido")
        False
    """
    if not email or not isinstance(email, str):
        return False
    
    email = email.strip().lower()
    
    # Expressão regular para validação de e-mail
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False
    
    # Verificações adicionais
    if '..' in email or email.startswith('.') or email.endswith('.'):
        return False
    
    if '@.' in email or '.@' in email:
        return False
    
    # Verifica tamanho máximo
    if len(email) > 254:
        return False
    
    return True


def clean_phone(phone: str) -> str:
    """
    Remove caracteres não numéricos do telefone.

    Args:
        phone: String contendo o telefone.

    Returns:
        str: Telefone contendo apenas números.
    """
    if not phone:
        return ""
    return re.sub(r'\D', '', str(phone))


def validate_phone(phone: str) -> Optional[str]:
    """
    Valida e formata um número de telefone brasileiro.

    Args:
        phone: String contendo o número de telefone.

    Returns:
        Optional[str]: Telefone formatado no padrão (XX) XXXXX-XXXX ou
            (XX) XXXX-XXXX, ou None se inválido.

    Examples:
        >>> validate_phone("(11) 98765-4321")
        "(11) 98765-4321"
        >>> validate_phone("11987654321")
        "(11) 98765-4321"
        >>> validate_phone("123")
        None
    """
    if not phone:
        return None
    
    phone = clean_phone(phone)
    
    # Verifica tamanho (deve ter 10 ou 11 dígitos)
    if len(phone) < 10 or len(phone) > 11:
        return None
    
    # Verifica se DDD é válido (deve estar entre 11 e 99)
    ddd = int(phone[:2])
    if ddd < 11 or ddd > 99:
        return None
    
    # Formatação
    if len(phone) == 11:
        # Celular: (XX) XXXXX-XXXX
        return f"({phone[:2]}) {phone[2:7]}-{phone[7:]}"
    else:
        # Fixo: (XX) XXXX-XXXX
        return f"({phone[:2]}) {phone[2:6]}-{phone[6:]}"


def validate_fic(data: dict) -> Tuple[bool, List[str]]:
    """
    Valida todos os campos de uma FIC (Ficha Individual de Curso).

    Args:
        data: Dicionário contendo os dados da FIC.

    Returns:
        Tuple[bool, List[str]]: (True, []) se válido,
            (False, [lista de erros]) se inválido.
    """
    errors = []
    
    if not data or not isinstance(data, dict):
        return False, ["Dados da FIC não fornecidos"]
    
    # Valida nome do aluno
    if not data.get('nome') or not str(data.get('nome')).strip():
        errors.append("Nome do aluno é obrigatório")
    
    # Valida CPF
    if data.get('cpf') and not is_valid_cpf(str(data.get('cpf'))):
        errors.append("CPF inválido")
    
    # Valida SARAM
    if data.get('saram') and not is_valid_saram(str(data.get('saram'))):
        errors.append("SARAM inválido")
    
    # Valida e-mail
    if data.get('email') and not validate_email(str(data.get('email'))):
        errors.append("E-mail inválido")
    
    # Valida telefone
    if data.get('telefone'):
        phone_formatted = validate_phone(str(data.get('telefone')))
        if phone_formatted is None:
            errors.append("Telefone inválido")
    
    # Valida nome do curso
    if not data.get('curso') or not str(data.get('curso')).strip():
        errors.append("Nome do curso é obrigatório")
    
    # Valida turma
    if data.get('turma') and not validate_turma(str(data.get('turma'))):
        errors.append("Código da turma é inválido")
    
    # Valida datas
    if data.get('data_inicio') and not is_valid_date(str(data.get('data_inicio'))):
        errors.append("Data de início inválida")
    
    if data.get('data_fim') and not is_valid_date(str(data.get('data_fim'))):
        errors.append("Data de término inválida")
    
    # Valida notas se fornecidas
    if data.get('nota_teorica') is not None:
        try:
            nota = float(data.get('nota_teorica'))
            if nota < 0 or nota > 100:
                errors.append("Nota teórica deve estar entre 0 e 100")
        except (ValueError, TypeError):
            errors.append("Nota teórica deve ser um número")
    
    if data.get('nota_pratica') is not None:
        try:
            nota = float(data.get('nota_pratica'))
            if nota < 0 or nota > 100:
                errors.append("Nota prática deve estar entre 0 e 100")
        except (ValueError, TypeError):
            errors.append("Nota prática deve ser um número")
    
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
