"""
Módulo da classe base para gerenciadores de dados do sistema.

Este módulo fornece a classe BaseManager que define a interface e implementação
base para todos os gerenciadores de dados que operam com arquivos Excel.

Example:
    >>> from managers.base_manager import BaseManager
    >>> class MeuManager(BaseManager):
    ...     def __init__(self):
    ...         super().__init__("data/meus_dados.xlsx", ["ID", "Nome", "Status"])
"""

from abc import ABC, abstractmethod
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple, Union
from datetime import datetime
import os

from utils.logger import get_logger


class BaseManager(ABC):
    """Classe base abstrata para gerenciadores de dados.
    
    Esta classe fornece uma estrutura padronizada para gerenciadores que
    operam com arquivos Excel, incluindo operações CRUD básicas,
    tratamento de exceções e logging de operações.
    
    Attributes:
        logger: Logger configurado para a classe filha.
        arquivo: Caminho do arquivo Excel gerenciado.
        colunas: Lista de colunas esperadas no arquivo.
    
    Example:
        >>> class CursoManager(BaseManager):
        ...     def __init__(self):
        ...         super().__init__("data/cursos.xlsx", ["ID", "Nome", "Status"])
        ...     
        ...     def adicionar(self, dados: Dict[str, Any]) -> Tuple[bool, str]:
        ...         df = self.carregar_dados()
        ...         df = pd.concat([df, pd.DataFrame([dados])], ignore_index=True)
        ...         sucesso = self._salvar_dados(df)
        ...         return sucesso, "Adicionado com sucesso" if sucesso else "Erro ao salvar"
    """
    
    def __init__(self, arquivo: str, colunas: List[str]):
        """Inicializa o gerenciador base.
        
        Args:
            arquivo: Caminho do arquivo Excel a ser gerenciado.
            colunas: Lista de nomes das colunas esperadas no arquivo.
        
        Raises:
            ValueError: Se a lista de colunas estiver vazia.
        """
        if not colunas:
            raise ValueError("A lista de colunas não pode estar vazia")
        
        self.logger = get_logger(self.__class__.__name__)
        self.arquivo = Path(arquivo)
        self.colunas = colunas.copy()
        
        self.logger.debug(
            "Inicializando %s com arquivo '%s' e %d colunas",
            self.__class__.__name__, self.arquivo, len(self.colunas)
        )
        
        self._criar_arquivo_se_nao_existir()
    
    def _criar_arquivo_se_nao_existir(self) -> None:
        """Cria o arquivo Excel se não existir.
        
        Cria o diretório pai se necessário e inicializa um arquivo Excel
        vazio com as colunas definidas.
        
        Raises:
            PermissionError: Se não houver permissão para criar o arquivo.
            OSError: Se houver erro ao criar o diretório ou arquivo.
        """
        try:
            if not self.arquivo.exists():
                self.logger.info(
                    "Arquivo '%s' não existe. Criando novo arquivo.",
                    self.arquivo
                )
                
                # Criar diretório pai se não existir
                self.arquivo.parent.mkdir(parents=True, exist_ok=True)
                
                # Criar DataFrame vazio com as colunas
                df = pd.DataFrame(columns=self.colunas)
                df.to_excel(self.arquivo, index=False, engine='openpyxl')
                
                self.logger.info(
                    "Arquivo '%s' criado com sucesso com %d colunas.",
                    self.arquivo, len(self.colunas)
                )
        except PermissionError as e:
            self.logger.error(
                "Permissão negada ao criar arquivo '%s': %s",
                self.arquivo, str(e)
            )
            raise
        except OSError as e:
            self.logger.error(
                "Erro do sistema ao criar arquivo '%s': %s",
                self.arquivo, str(e)
            )
            raise
        except Exception as e:
            self.logger.error(
                "Erro inesperado ao criar arquivo '%s': %s",
                self.arquivo, str(e), exc_info=True
            )
            raise
    
    def carregar_dados(self) -> pd.DataFrame:
        """Carrega dados do arquivo Excel.
        
        Returns:
            DataFrame com os dados do arquivo. Se o arquivo não existir
            ou houver erro na leitura, retorna um DataFrame vazio
            com as colunas definidas.
        
        Example:
            >>> df = manager.carregar_dados()
            >>> print(f"Total de registros: {len(df)}")
        """
        try:
            if not self.arquivo.exists():
                self.logger.warning(
                    "Arquivo '%s' não encontrado. Retornando DataFrame vazio.",
                    self.arquivo
                )
                return pd.DataFrame(columns=self.colunas)
            
            self.logger.debug("Carregando dados de '%s'", self.arquivo)
            df = pd.read_excel(self.arquivo, engine='openpyxl')
            
            # Garantir que todas as colunas esperadas existam
            for col in self.colunas:
                if col not in df.columns:
                    df[col] = ""
                    self.logger.debug("Coluna '%s' adicionada ao DataFrame", col)
            
            # Reordenar colunas conforme a ordem definida
            colunas_existentes = [col for col in self.colunas if col in df.columns]
            colunas_adicionais = [col for col in df.columns if col not in self.colunas]
            df = df[colunas_existentes + colunas_adicionais]
            
            self.logger.info(
                "Dados carregados com sucesso: %d registros, %d colunas",
                len(df), len(df.columns)
            )
            return df
            
        except pd.errors.EmptyDataError:
            self.logger.warning("Arquivo '%s' está vazio", self.arquivo)
            return pd.DataFrame(columns=self.colunas)
        except pd.errors.ParserError as e:
            self.logger.error(
                "Erro ao analisar arquivo '%s': %s", self.arquivo, str(e)
            )
            return pd.DataFrame(columns=self.colunas)
        except Exception as e:
            self.logger.error(
                "Erro inesperado ao carregar dados de '%s': %s",
                self.arquivo, str(e), exc_info=True
            )
            return pd.DataFrame(columns=self.colunas)
    
    def _salvar_dados(self, df: pd.DataFrame) -> bool:
        """Salva DataFrame no arquivo Excel.
        
        Args:
            df: DataFrame a ser salvo no arquivo.
        
        Returns:
            True se o salvamento for bem-sucedido, False caso contrário.
        
        Example:
            >>> df = manager.carregar_dados()
            >>> df = pd.concat([df, pd.DataFrame([novo_registro])])
            >>> if manager._salvar_dados(df):
            ...     print("Salvo com sucesso!")
        """
        try:
            self.logger.debug(
                "Salvando %d registros em '%s'", len(df), self.arquivo
            )
            
            # Criar diretório pai se não existir
            self.arquivo.parent.mkdir(parents=True, exist_ok=True)
            
            # Garantir que todas as colunas esperadas existam no DataFrame
            for col in self.colunas:
                if col not in df.columns:
                    df[col] = ""
            
            # Reordenar colunas conforme a ordem definida
            colunas_existentes = [col for col in self.colunas if col in df.columns]
            colunas_adicionais = [col for col in df.columns if col not in self.colunas]
            df_salvar = df[colunas_existentes + colunas_adicionais].copy()
            
            # Salvar no arquivo
            df_salvar.to_excel(self.arquivo, index=False, engine='openpyxl')
            
            self.logger.info(
                "Dados salvos com sucesso em '%s': %d registros, %d colunas",
                self.arquivo, len(df_salvar), len(df_salvar.columns)
            )
            return True
            
        except PermissionError as e:
            self.logger.error(
                "Permissão negada ao salvar arquivo '%s': %s",
                self.arquivo, str(e)
            )
            return False
        except OSError as e:
            self.logger.error(
                "Erro do sistema ao salvar arquivo '%s': %s",
                self.arquivo, str(e)
            )
            return False
        except Exception as e:
            self.logger.error(
                "Erro inesperado ao salvar dados em '%s': %s",
                self.arquivo, str(e), exc_info=True
            )
            return False
    
    def buscar_por_id(
        self, id_valor: str, coluna_id: str = 'ID'
    ) -> Optional[Dict[str, Any]]:
        """Busca registro por ID.
        
        Args:
            id_valor: Valor do ID a ser buscado.
            coluna_id: Nome da coluna de ID. Padrão é 'ID'.
        
        Returns:
            Dicionário com os dados do registro encontrado, ou None
            se não encontrado ou em caso de erro.
        
        Example:
            >>> registro = manager.buscar_por_id("CURSO-001")
            >>> if registro:
            ...     print(f"Encontrado: {registro['Nome']}")
        """
        try:
            self.logger.debug(
                "Buscando registro com %s='%s' em '%s'",
                coluna_id, id_valor, self.arquivo
            )
            
            df = self.carregar_dados()
            
            if coluna_id not in df.columns:
                self.logger.warning(
                    "Coluna '%s' não encontrada no arquivo '%s'",
                    coluna_id, self.arquivo
                )
                return None
            
            # Buscar registro - comparação robusta tratando strings e números
            # O Excel pode converter valores como '001' para número 1
            valores_coluna = df[coluna_id].apply(
                lambda x: str(int(x)) if pd.notna(x) and isinstance(x, (int, float)) else str(x)
            ).str.strip()
            mask = valores_coluna == str(id_valor).strip()
            resultado = df[mask]
            
            if resultado.empty:
                self.logger.debug(
                    "Registro com %s='%s' não encontrado", coluna_id, id_valor
                )
                return None
            
            # Converter primeira linha para dicionário
            registro = resultado.iloc[0].to_dict()
            self.logger.info(
                "Registro encontrado: %s='%s'", coluna_id, id_valor
            )
            return registro
            
        except Exception as e:
            self.logger.error(
                "Erro ao buscar registro com %s='%s': %s",
                coluna_id, id_valor, str(e), exc_info=True
            )
            return None
    
    def excluir_por_id(
        self, id_valor: str, coluna_id: str = 'ID'
    ) -> Tuple[bool, str]:
        """Exclui registro por ID.
        
        Args:
            id_valor: Valor do ID do registro a ser excluído.
            coluna_id: Nome da coluna de ID. Padrão é 'ID'.
        
        Returns:
            Tupla contendo:
                - bool: True se a exclusão foi bem-sucedida, False caso contrário.
                - str: Mensagem descritiva do resultado.
        
        Example:
            >>> sucesso, mensagem = manager.excluir_por_id("CURSO-001")
            >>> print(mensagem)
            "Registro excluído com sucesso!"
        """
        try:
            self.logger.debug(
                "Tentando excluir registro com %s='%s'",
                coluna_id, id_valor
            )
            
            df = self.carregar_dados()
            
            if coluna_id not in df.columns:
                mensagem = f"Coluna '{coluna_id}' não encontrada"
                self.logger.warning("%s em '%s'", mensagem, self.arquivo)
                return False, mensagem
            
            # Verificar se o registro existe - comparação robusta
            # O Excel pode converter valores como '001' para número 1
            valores_coluna = df[coluna_id].apply(
                lambda x: str(int(x)) if pd.notna(x) and isinstance(x, (int, float)) else str(x)
            ).str.strip()
            mask = valores_coluna == str(id_valor).strip()
            if not mask.any():
                mensagem = f"Registro com {coluna_id}='{id_valor}' não encontrado"
                self.logger.warning(mensagem)
                return False, mensagem
            
            # Guardar informação do registro para log
            registro_excluido = df[mask].iloc[0].to_dict()
            
            # Remover registro
            df = df[~mask].reset_index(drop=True)
            
            # Salvar alterações
            if self._salvar_dados(df):
                mensagem = f"Registro com {coluna_id}='{id_valor}' excluído com sucesso"
                self.logger.info("%s. Registro excluído: %s", mensagem, registro_excluido)
                return True, mensagem
            else:
                mensagem = "Erro ao salvar após exclusão"
                self.logger.error(mensagem)
                return False, mensagem
                
        except Exception as e:
            mensagem = f"Erro ao excluir registro: {str(e)}"
            self.logger.error(
                "Erro ao excluir registro com %s='%s': %s",
                coluna_id, id_valor, str(e), exc_info=True
            )
            return False, mensagem
    
    def contar_registros(self) -> int:
        """Retorna quantidade de registros.
        
        Returns:
            Número de registros no arquivo. Retorna 0 em caso de erro.
        
        Example:
            >>> total = manager.contar_registros()
            >>> print(f"Total: {total} registros")
        """
        try:
            df = self.carregar_dados()
            count = len(df)
            self.logger.debug(
                "Arquivo '%s' contém %d registros", self.arquivo, count
            )
            return count
        except Exception as e:
            self.logger.error(
                "Erro ao contar registros em '%s': %s",
                self.arquivo, str(e), exc_info=True
            )
            return 0
    
    def listar_todos(self) -> List[Dict[str, Any]]:
        """Retorna todos os registros como lista de dicionários.
        
        Returns:
            Lista contendo todos os registros do arquivo.
            Retorna lista vazia em caso de erro.
        
        Example:
            >>> registros = manager.listar_todos()
            >>> for reg in registros:
            ...     print(reg['Nome'])
        """
        try:
            df = self.carregar_dados()
            registros = df.to_dict('records')
            self.logger.debug(
                "Listando todos os registros: %d encontrados", len(registros)
            )
            return registros
        except Exception as e:
            self.logger.error(
                "Erro ao listar registros: %s", str(e), exc_info=True
            )
            return []
    
    def existe_registro(self, id_valor: str, coluna_id: str = 'ID') -> bool:
        """Verifica se um registro existe pelo ID.
        
        Args:
            id_valor: Valor do ID a ser verificado.
            coluna_id: Nome da coluna de ID. Padrão é 'ID'.
        
        Returns:
            True se o registro existir, False caso contrário.
        
        Example:
            >>> if manager.existe_registro("CURSO-001"):
            ...     print("Registro existe")
        """
        return self.buscar_por_id(id_valor, coluna_id) is not None
    
    def obter_colunas_atuais(self) -> List[str]:
        """Retorna a lista de colunas do arquivo atual.
        
        Returns:
            Lista com os nomes das colunas existentes no arquivo.
            Retorna lista vazia em caso de erro.
        
        Example:
            >>> colunas = manager.obter_colunas_atuais()
            >>> print(f"Colunas disponíveis: {', '.join(colunas)}")
        """
        try:
            df = self.carregar_dados()
            colunas = list(df.columns)
            self.logger.debug("Colunas atuais: %s", colunas)
            return colunas
        except Exception as e:
            self.logger.error(
                "Erro ao obter colunas: %s", str(e), exc_info=True
            )
            return []
    
    @abstractmethod
    def adicionar(self, dados: Dict[str, Any]) -> Tuple[bool, str]:
        """Adiciona um novo registro.
        
        Este método deve ser implementado pelas classes filhas
        para definir a lógica específica de adição de registros.
        
        Args:
            dados: Dicionário com os dados do novo registro.
        
        Returns:
            Tupla contendo:
                - bool: True se a adição foi bem-sucedida, False caso contrário.
                - str: Mensagem descritiva do resultado.
        """
        pass
    
    @abstractmethod
    def atualizar(
        self, id_valor: str, dados: Dict[str, Any], coluna_id: str = 'ID'
    ) -> Tuple[bool, str]:
        """Atualiza um registro existente.
        
        Este método deve ser implementado pelas classes filhas
        para definir a lógica específica de atualização de registros.
        
        Args:
            id_valor: Valor do ID do registro a ser atualizado.
            dados: Dicionário com os novos dados.
            coluna_id: Nome da coluna de ID. Padrão é 'ID'.
        
        Returns:
            Tupla contendo:
                - bool: True se a atualização foi bem-sucedida, False caso contrário.
                - str: Mensagem descritiva do resultado.
        """
        pass
