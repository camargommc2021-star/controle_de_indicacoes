"""
Gerenciador de Autenticação e Controle de Acesso.

Este módulo gerencia o sistema de login, autenticação de usuários,
controle de permissões e sessões.

Usage:
    from managers.auth_manager import AuthManager, NivelAcesso
    
    auth = AuthManager()
    sucesso, msg = auth.login("usuario", "senha")
    if sucesso:
        print(f"Bem-vindo, {auth.usuario_atual['nome']}")
"""

import os
import hashlib
import secrets
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from enum import Enum
from dataclasses import dataclass

from utils.logger import get_logger

logger = get_logger(__name__)


# ============================================================================
# CONSTANTES E CONFIGURAÇÕES
# ============================================================================

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
ARQUIVO_USUARIOS = DATA_DIR / "usuarios.xlsx"
ARQUIVO_SESSOES = DATA_DIR / "sessoes.xlsx"

SALT_LENGTH = 32
ITERATIONS = 100000


# ============================================================================
# ENUMS E DATACLASSES
# ============================================================================

class NivelAcesso(Enum):
    """Níveis de acesso disponíveis no sistema."""
    ADMIN = "admin"           # Acesso total (CRUD + configurações + usuários)
    EDITOR = "editor"         # CRUD cursos e pessoas, sem gerenciar usuários
    VIEWER = "viewer"         # Apenas visualização, sem edição


@dataclass
class Permissoes:
    """Define as permissões para cada nível de acesso."""
    ver_dashboard: bool = True
    ver_cursos: bool = True
    criar_curso: bool = False
    editar_curso: bool = False
    excluir_curso: bool = False
    ver_pessoas: bool = True
    criar_pessoa: bool = False
    editar_pessoa: bool = False
    excluir_pessoa: bool = False
    ver_fics: bool = True
    criar_fic: bool = False
    editar_fic: bool = False
    gerenciar_usuarios: bool = False
    fazer_backup: bool = False
    ver_logs: bool = False
    
    @classmethod
    def from_nivel(cls, nivel: NivelAcesso) -> 'Permissoes':
        """Retorna permissões baseadas no nível de acesso."""
        permissoes = {
            NivelAcesso.ADMIN: cls(
                ver_dashboard=True, ver_cursos=True, criar_curso=True,
                editar_curso=True, excluir_curso=True, ver_pessoas=True,
                criar_pessoa=True, editar_pessoa=True, excluir_pessoa=True,
                ver_fics=True, criar_fic=True, editar_fic=True,
                gerenciar_usuarios=True, fazer_backup=True, ver_logs=True
            ),
            NivelAcesso.EDITOR: cls(
                ver_dashboard=True, ver_cursos=True, criar_curso=True,
                editar_curso=True, excluir_curso=False, ver_pessoas=True,
                criar_pessoa=True, editar_pessoa=True, excluir_pessoa=False,
                ver_fics=True, criar_fic=True, editar_fic=True,
                gerenciar_usuarios=False, fazer_backup=False, ver_logs=False
            ),
            NivelAcesso.VIEWER: cls(
                ver_dashboard=True, ver_cursos=True, criar_curso=False,
                editar_curso=False, excluir_curso=False, ver_pessoas=True,
                criar_pessoa=False, editar_pessoa=False, excluir_pessoa=False,
                ver_fics=True, criar_fic=False, editar_fic=False,
                gerenciar_usuarios=False, fazer_backup=False, ver_logs=False
            )
        }
        return permissoes.get(nivel, cls())


# ============================================================================
# CLASSE PRINCIPAL
# ============================================================================

class AuthManager:
    """
    Gerenciador de autenticação e controle de acesso.
    
    Responsável por:
    - Criar e gerenciar usuários
    - Autenticar login/logout
    - Hash seguro de senhas
    - Controle de permissões
    - Registro de sessões
    
    Attributes:
        usuario_atual: Dicionário com dados do usuário logado
        autenticado: Boolean indicando se há usuário logado
        permissoes: Objeto Permissoes do usuário atual
    """
    
    def __init__(self):
        """Inicializa o gerenciador de autenticação."""
        self.usuario_atual: Optional[Dict] = None
        self.autenticado: bool = False
        self.permissoes: Permissoes = Permissoes()
        
        # Garantir diretório existe
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Criar usuário admin padrão se não existir
        self._inicializar_usuarios_padrao()
        
        logger.info("AuthManager inicializado")
    
    # ====================================================================
    # MÉTODOS PRIVADOS
    # ====================================================================
    
    def _hash_senha(self, senha: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """
        Gera hash seguro da senha usando PBKDF2.
        
        Args:
            senha: Senha em texto plano
            salt: Salt opcional (gera novo se não fornecido)
            
        Returns:
            Tupla (hash, salt)
        """
        if salt is None:
            salt = secrets.token_hex(SALT_LENGTH)
        
        # PBKDF2 com SHA-256
        hash_bytes = hashlib.pbkdf2_hmac(
            'sha256',
            senha.encode('utf-8'),
            salt.encode('utf-8'),
            ITERATIONS
        )
        hash_hex = hash_bytes.hex()
        
        return hash_hex, salt
    
    def _verificar_senha(self, senha: str, hash_armazenado: str, salt: str) -> bool:
        """
        Verifica se a senha corresponde ao hash armazenado.
        
        Args:
            senha: Senha em texto plano
            hash_armazenado: Hash armazenado no banco
            salt: Salt usado no hash
            
        Returns:
            True se a senha está correta
        """
        hash_calc, _ = self._hash_senha(senha, salt)
        return secrets.compare_digest(hash_calc, hash_armazenado)
    
    def _inicializar_usuarios_padrao(self) -> None:
        """Cria usuários padrão se o arquivo não existir."""
        if ARQUIVO_USUARIOS.exists():
            return
        
        logger.info("Criando usuários padrão...")
        
        # Criar usuário admin padrão
        admin_senha = "admin123"
        hash_senha, salt = self._hash_senha(admin_senha)
        
        usuarios_default = [
            {
                'id': 1,
                'username': 'admin',
                'nome': 'Administrador',
                'email': 'admin@crcea-se.fab.mil.br',
                'nivel_acesso': NivelAcesso.ADMIN.value,
                'hash_senha': hash_senha,
                'salt': salt,
                'ativo': True,
                'data_criacao': datetime.now(),
                'ultimo_login': None,
                'tentativas_falhas': 0,
                'bloqueado_ate': None
            },
            {
                'id': 2,
                'username': 'editor',
                'nome': 'Usuário Editor',
                'email': 'editor@crcea-se.fab.mil.br',
                'nivel_acesso': NivelAcesso.EDITOR.value,
                'hash_senha': '',  # Senha será definida no primeiro login
                'salt': '',
                'ativo': True,
                'data_criacao': datetime.now(),
                'ultimo_login': None,
                'tentativas_falhas': 0,
                'bloqueado_ate': None
            },
            {
                'id': 3,
                'username': 'viewer',
                'nome': 'Usuário Visualizador',
                'email': 'viewer@crcea-se.fab.mil.br',
                'nivel_acesso': NivelAcesso.VIEWER.value,
                'hash_senha': '',
                'salt': '',
                'ativo': True,
                'data_criacao': datetime.now(),
                'ultimo_login': None,
                'tentativas_falhas': 0,
                'bloqueado_ate': None
            }
        ]
        
        df = pd.DataFrame(usuarios_default)
        df.to_excel(ARQUIVO_USUARIOS, index=False)
        
        logger.info(f"Usuários padrão criados. Admin senha: {admin_senha}")
        logger.warning("ALTERE A SENHA PADRÃO DO ADMIN IMEDIATAMENTE!")
    
    def _carregar_usuarios(self) -> pd.DataFrame:
        """Carrega DataFrame de usuários."""
        if not ARQUIVO_USUARIOS.exists():
            return pd.DataFrame()
        
        df = pd.read_excel(ARQUIVO_USUARIOS)
        
        # Garantir tipos de dados corretos para colunas de data
        for col in ['data_criacao', 'ultimo_login', 'bloqueado_ate']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        return df
    
    def _salvar_usuarios(self, df: pd.DataFrame) -> bool:
        """Salva DataFrame de usuários."""
        try:
            df.to_excel(ARQUIVO_USUARIOS, index=False)
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar usuários: {e}")
            return False
    
    def _registrar_sessao(self, username: str, sucesso: bool, ip: str = "local") -> None:
        """Registra tentativa de login no log de sessões."""
        try:
            sessao = {
                'timestamp': datetime.now(),
                'username': username,
                'sucesso': sucesso,
                'ip': ip
            }
            
            if ARQUIVO_SESSOES.exists():
                df_sessoes = pd.read_excel(ARQUIVO_SESSOES)
                df_sessoes = pd.concat([df_sessoes, pd.DataFrame([sessao])], ignore_index=True)
            else:
                df_sessoes = pd.DataFrame([sessao])
            
            # Manter apenas últimos 1000 registros
            if len(df_sessoes) > 1000:
                df_sessoes = df_sessoes.tail(1000)
            
            df_sessoes.to_excel(ARQUIVO_SESSOES, index=False)
        except Exception as e:
            logger.error(f"Erro ao registrar sessão: {e}")
    
    # ====================================================================
    # MÉTODOS PÚBLICOS - AUTENTICAÇÃO
    # ====================================================================
    
    def login(self, username: str, senha: str) -> Tuple[bool, str]:
        """
        Realiza login do usuário.
        
        Args:
            username: Nome de usuário
            senha: Senha
            
        Returns:
            Tupla (sucesso, mensagem)
        """
        df = self._carregar_usuarios()
        
        if df.empty:
            return False, "Sistema não inicializado"
        
        # Buscar usuário
        usuario = df[df['username'] == username]
        
        if usuario.empty:
            self._registrar_sessao(username, False)
            return False, "Usuário não encontrado"
        
        user = usuario.iloc[0].to_dict()
        
        # Verificar se está ativo
        if not user.get('ativo', True):
            return False, "Usuário desativado. Contate o administrador."
        
        # Verificar bloqueio
        if user.get('bloqueado_ate'):
            bloqueio = pd.to_datetime(user['bloqueado_ate'])
            if bloqueio > datetime.now():
                return False, f"Usuário bloqueado até {bloqueio.strftime('%d/%m/%Y %H:%M')}"
        
        # Verificar senha
        hash_senha = user.get('hash_senha', '')
        salt = user.get('salt', '')
        
        if not hash_senha or not salt:
            return False, "Senha não definida. Contate o administrador."
        
        if not self._verificar_senha(senha, hash_senha, salt):
            # Incrementar tentativas falhas
            idx = usuario.index[0]
            tentativas = user.get('tentativas_falhas', 0) + 1
            df.at[idx, 'tentativas_falhas'] = tentativas
            
            # Bloquear após 5 tentativas
            if tentativas >= 5:
                df.at[idx, 'bloqueado_ate'] = datetime.now() + pd.Timedelta(minutes=30)
                df.at[idx, 'tentativas_falhas'] = 0
                self._salvar_usuarios(df)
                self._registrar_sessao(username, False)
                return False, "Muitas tentativas. Usuário bloqueado por 30 minutos."
            
            self._salvar_usuarios(df)
            self._registrar_sessao(username, False)
            return False, f"Senha incorreta. Tentativas restantes: {5 - tentativas}"
        
        # Login bem-sucedido
        idx = usuario.index[0]
        df.at[idx, 'ultimo_login'] = datetime.now()
        df.at[idx, 'tentativas_falhas'] = 0
        df.at[idx, 'bloqueado_ate'] = None
        self._salvar_usuarios(df)
        
        # Definir usuário atual
        self.usuario_atual = {
            'id': user['id'],
            'username': user['username'],
            'nome': user['nome'],
            'email': user['email'],
            'nivel_acesso': user['nivel_acesso']
        }
        self.autenticado = True
        self.permissoes = Permissoes.from_nivel(NivelAcesso(user['nivel_acesso']))
        
        self._registrar_sessao(username, True)
        logger.info(f"Login bem-sucedido: {username}")
        
        return True, f"Bem-vindo, {user['nome']}!"
    
    def logout(self) -> None:
        """Realiza logout do usuário atual."""
        if self.usuario_atual:
            logger.info(f"Logout: {self.usuario_atual['username']}")
        
        self.usuario_atual = None
        self.autenticado = False
        self.permissoes = Permissoes()
    
    # ====================================================================
    # MÉTODOS PÚBLICOS - GESTÃO DE USUÁRIOS
    # ====================================================================
    
    def criar_usuario(self, username: str, nome: str, email: str, 
                      nivel_acesso: str, senha: str) -> Tuple[bool, str]:
        """
        Cria novo usuário.
        
        Args:
            username: Nome de usuário único
            nome: Nome completo
            email: Email
            nivel_acesso: 'admin', 'editor' ou 'viewer'
            senha: Senha inicial
            
        Returns:
            Tupla (sucesso, mensagem)
        """
        # Verificar permissão
        if not self.permissoes.gerenciar_usuarios:
            return False, "Sem permissão para criar usuários"
        
        df = self._carregar_usuarios()
        
        # Verificar se username já existe
        if not df.empty and username in df['username'].values:
            return False, "Nome de usuário já existe"
        
        # Validar nível de acesso
        try:
            nivel = NivelAcesso(nivel_acesso)
        except ValueError:
            return False, "Nível de acesso inválido"
        
        # Gerar hash da senha
        hash_senha, salt = self._hash_senha(senha)
        
        # Criar novo usuário
        novo_id = 1 if df.empty else df['id'].max() + 1
        
        novo_usuario = {
            'id': novo_id,
            'username': username,
            'nome': nome,
            'email': email,
            'nivel_acesso': nivel.value,
            'hash_senha': hash_senha,
            'salt': salt,
            'ativo': True,
            'data_criacao': datetime.now(),
            'ultimo_login': None,
            'tentativas_falhas': 0,
            'bloqueado_ate': None
        }
        
        df_novo = pd.DataFrame([novo_usuario])
        df = pd.concat([df, df_novo], ignore_index=True)
        
        if self._salvar_usuarios(df):
            logger.info(f"Usuário criado: {username} ({nivel.value})")
            return True, f"Usuário '{username}' criado com sucesso"
        
        return False, "Erro ao salvar usuário"
    
    def alterar_senha(self, username: str, senha_atual: str, 
                      nova_senha: str) -> Tuple[bool, str]:
        """
        Altera senha do usuário.
        
        Args:
            username: Nome de usuário
            senha_atual: Senha atual
            nova_senha: Nova senha
            
        Returns:
            Tupla (sucesso, mensagem)
        """
        df = self._carregar_usuarios()
        usuario = df[df['username'] == username]
        
        if usuario.empty:
            return False, "Usuário não encontrado"
        
        # Verificar se é o próprio usuário ou admin
        if (self.usuario_atual and self.usuario_atual['username'] != username 
            and not self.permissoes.gerenciar_usuarios):
            return False, "Só pode alterar sua própria senha"
        
        # Verificar senha atual (se não for admin alterando)
        if self.usuario_atual and self.usuario_atual['username'] == username:
            user = usuario.iloc[0].to_dict()
            if not self._verificar_senha(senha_atual, user['hash_senha'], user['salt']):
                return False, "Senha atual incorreta"
        
        # Validar nova senha
        if len(nova_senha) < 6:
            return False, "Senha deve ter no mínimo 6 caracteres"
        
        # Gerar novo hash
        hash_senha, salt = self._hash_senha(nova_senha)
        
        idx = usuario.index[0]
        df.at[idx, 'hash_senha'] = hash_senha
        df.at[idx, 'salt'] = salt
        
        if self._salvar_usuarios(df):
            logger.info(f"Senha alterada: {username}")
            return True, "Senha alterada com sucesso"
        
        return False, "Erro ao salvar nova senha"
    
    def listar_usuarios(self) -> pd.DataFrame:
        """
        Lista todos os usuários (sem dados sensíveis).
        
        Returns:
            DataFrame com usuários
        """
        if not self.permissoes.gerenciar_usuarios:
            return pd.DataFrame()
        
        df = self._carregar_usuarios()
        
        if df.empty:
            return df
        
        # Remover colunas sensíveis
        cols_seguras = ['id', 'username', 'nome', 'email', 'nivel_acesso', 
                       'ativo', 'data_criacao', 'ultimo_login']
        return df[[col for col in cols_seguras if col in df.columns]]
    
    def desativar_usuario(self, username: str) -> Tuple[bool, str]:
        """
        Desativa um usuário.
        
        Args:
            username: Nome de usuário
            
        Returns:
            Tupla (sucesso, mensagem)
        """
        if not self.permissoes.gerenciar_usuarios:
            return False, "Sem permissão"
        
        # Não pode desativar a si mesmo
        if self.usuario_atual and self.usuario_atual['username'] == username:
            return False, "Não pode desativar seu próprio usuário"
        
        df = self._carregar_usuarios()
        usuario = df[df['username'] == username]
        
        if usuario.empty:
            return False, "Usuário não encontrado"
        
        idx = usuario.index[0]
        df.at[idx, 'ativo'] = False
        
        if self._salvar_usuarios(df):
            logger.info(f"Usuário desativado: {username}")
            return True, f"Usuário '{username}' desativado"
        
        return False, "Erro ao desativar usuário"
    
    def redefinir_senha(self, username: str, nova_senha: str) -> Tuple[bool, str]:
        """
        Redefine senha (admin only).
        
        Args:
            username: Nome de usuário
            nova_senha: Nova senha
            
        Returns:
            Tupla (sucesso, mensagem)
        """
        if not self.permissoes.gerenciar_usuarios:
            return False, "Sem permissão"
        
        df = self._carregar_usuarios()
        usuario = df[df['username'] == username]
        
        if usuario.empty:
            return False, "Usuário não encontrado"
        
        if len(nova_senha) < 6:
            return False, "Senha deve ter no mínimo 6 caracteres"
        
        hash_senha, salt = self._hash_senha(nova_senha)
        
        idx = usuario.index[0]
        df.at[idx, 'hash_senha'] = hash_senha
        df.at[idx, 'salt'] = salt
        df.at[idx, 'tentativas_falhas'] = 0
        df.at[idx, 'bloqueado_ate'] = None
        
        if self._salvar_usuarios(df):
            logger.info(f"Senha redefinida: {username}")
            return True, f"Senha de '{username}' redefinida"
        
        return False, "Erro ao redefinir senha"
    
    def editar_usuario(self, username_atual: str, novo_username: str, 
                       novo_nome: str, novo_email: str, 
                       novo_nivel: str) -> Tuple[bool, str]:
        """
        Edita dados de um usuário existente.
        
        Args:
            username_atual: Username atual do usuário
            novo_username: Novo username (pode ser igual ao atual)
            novo_nome: Novo nome completo
            novo_email: Novo email
            novo_nivel: Novo nível de acesso ('admin', 'editor' ou 'viewer')
            
        Returns:
            Tupla (sucesso, mensagem)
        """
        if not self.permissoes.gerenciar_usuarios:
            return False, "Sem permissão para editar usuários"
        
        df = self._carregar_usuarios()
        usuario = df[df['username'] == username_atual]
        
        if usuario.empty:
            return False, "Usuário não encontrado"
        
        # Verificar se o novo username já existe (e é diferente do atual)
        if novo_username != username_atual:
            if novo_username in df['username'].values:
                return False, "Novo nome de usuário já existe"
        
        # Validar nível de acesso
        try:
            nivel = NivelAcesso(novo_nivel)
        except ValueError:
            return False, "Nível de acesso inválido"
        
        idx = usuario.index[0]
        df.at[idx, 'username'] = novo_username
        df.at[idx, 'nome'] = novo_nome
        df.at[idx, 'email'] = novo_email
        df.at[idx, 'nivel_acesso'] = nivel.value
        
        if self._salvar_usuarios(df):
            logger.info(f"Usuário editado: {username_atual} -> {novo_username}")
            return True, f"Usuário '{novo_username}' atualizado com sucesso"
        
        return False, "Erro ao salvar alterações"
    
    def pode(self, permissao: str) -> bool:
        """
        Verifica se usuário tem uma permissão específica.
        
        Args:
            permissao: Nome da permissão (ex: 'criar_curso')
            
        Returns:
            True se tem permissão
        """
        if not self.autenticado:
            return False
        return getattr(self.permissoes, permissao, False)
