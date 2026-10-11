"""
Pacote de gerenciadores de dados do sistema de controle de cursos.

Este pacote contém classes gerenciadoras para autenticação e permissões.

Classes disponíveis:
    - AuthManager: Gerenciador de usuários, sessões e autenticação.
    - NivelAcesso: Enumeração de níveis de acesso.
    - Permissoes: Configuração de permissões por nível.
"""

from .auth_manager import AuthManager, NivelAcesso, Permissoes

__all__ = ['AuthManager', 'NivelAcesso', 'Permissoes']
