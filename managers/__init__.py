"""
Pacote de gerenciadores de dados do sistema de controle de cursos.

Este pacote contém classes gerenciadoras para operações CRUD em arquivos Excel,
fornecendo uma interface padronizada para manipulação de dados.

Classes disponíveis:
    - BaseManager: Classe base abstrata para todos os gerenciadores.

Example:
    >>> from managers import BaseManager
    >>> from managers.base_manager import BaseManager
"""

from .base_manager import BaseManager
from .auth_manager import AuthManager, NivelAcesso, Permissoes

__all__ = ['BaseManager', 'AuthManager', 'NivelAcesso', 'Permissoes']
