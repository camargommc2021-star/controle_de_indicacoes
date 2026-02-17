"""
Gerenciador de Chefes - Cadastro e consulta de chefes
"""

import pandas as pd
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from utils.logger import get_logger

logger = get_logger(__name__)


class ChefesManager:
    """Gerencia o cadastro de chefes"""
    
    def __init__(self):
        self.data_dir = "data"
        self.json_file = os.path.join(self.data_dir, "chefes_cadastrados.json")
        self.excel_file = os.path.join(self.data_dir, "chefia.xlsx")
        self._ensure_data_dir()
        self.chefes = self._load_chefes()
    
    def _ensure_data_dir(self):
        """Garante que o diretório de dados existe"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def _load_chefes(self) -> List[Dict]:
        """Carrega os chefes do JSON ou cria a partir do Excel se não existir"""
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erro ao carregar chefes: {e}")
                return []
        
        # Se não existe JSON, tenta carregar do Excel
        return self._import_from_excel()
    
    def _import_from_excel(self) -> List[Dict]:
        """Importa chefes do Excel da chefia"""
        chefes = []
        if os.path.exists(self.excel_file):
            try:
                df = pd.read_excel(self.excel_file)
                df = df.drop(columns=[col for col in df.columns if 'Unnamed' in col], errors='ignore')
                
                for _, row in df.iterrows():
                    if pd.notna(row.get('NOME')) and pd.notna(row.get('CURSO')):
                        chefes.append({
                            'id': len(chefes) + 1,
                            'nome': str(row.get('NOME', '')).strip(),
                            'posto': str(row.get('POSTO', '')).strip(),
                            'funcao': str(row.get('FUNÇÃO', '')).strip(),
                            'setor': str(row.get('SETOR RESPONSÁVEL.1', '')).strip(),
                            'curso_codigo': str(row.get('CURSO', '')).strip(),
                            'curso_nome': str(row.get('NOME DO CURSO', '')).strip(),
                            'comando': str(row.get('COMANDO', '')).strip(),
                            'ativo': True,
                            'data_cadastro': datetime.now().strftime('%d/%m/%Y')
                        })
                
                # Salva no JSON
                self._save_chefes(chefes)
                logger.info(f"Importados {len(chefes)} chefes do Excel")
            except Exception as e:
                logger.error(f"Erro ao importar do Excel: {e}")
        
        return chefes
    
    def _save_chefes(self, chefes: List[Dict] = None):
        """Salva os chefes no JSON"""
        if chefes is None:
            chefes = self.chefes
        
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(chefes, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar chefes: {e}")
    
    def get_all_chefes(self, ativos_only: bool = True) -> List[Dict]:
        """Retorna todos os chefes cadastrados"""
        if ativos_only:
            return [c for c in self.chefes if c.get('ativo', True)]
        return self.chefes
    
    def get_chefe_by_id(self, chefe_id: int) -> Optional[Dict]:
        """Retorna um chefe pelo ID"""
        for chefe in self.chefes:
            if chefe.get('id') == chefe_id and chefe.get('ativo', True):
                return chefe
        return None
    
    def get_chefes_by_setor(self, setor: str) -> List[Dict]:
        """Retorna chefes por setor"""
        return [c for c in self.chefes 
                if c.get('setor', '').upper() == setor.upper() and c.get('ativo', True)]
    
    def add_chefe(self, nome: str, posto: str, funcao: str, setor: str = '', 
                  curso_codigo: str = '', curso_nome: str = '', comando: str = '') -> Dict:
        """Adiciona um novo chefe"""
        novo_id = max([c.get('id', 0) for c in self.chefes], default=0) + 1
        
        chefe = {
            'id': novo_id,
            'nome': nome.strip().upper(),
            'posto': posto.strip().upper(),
            'funcao': funcao.strip().upper(),
            'setor': setor.strip().upper(),
            'curso_codigo': curso_codigo.strip().upper(),
            'curso_nome': curso_nome.strip().upper(),
            'comando': comando.strip().upper(),
            'ativo': True,
            'data_cadastro': datetime.now().strftime('%d/%m/%Y')
        }
        
        self.chefes.append(chefe)
        self._save_chefes()
        logger.info(f"Chefe adicionado: {nome}")
        return chefe
    
    def update_chefe(self, chefe_id: int, **kwargs) -> Optional[Dict]:
        """Atualiza um chefe existente"""
        for chefe in self.chefes:
            if chefe.get('id') == chefe_id:
                for key, value in kwargs.items():
                    if key in ['nome', 'posto', 'funcao', 'setor', 'curso_codigo', 'curso_nome', 'comando']:
                        chefe[key] = str(value).strip().upper()
                chefe['data_atualizacao'] = datetime.now().strftime('%d/%m/%Y')
                self._save_chefes()
                logger.info(f"Chefe atualizado: {chefe['nome']}")
                return chefe
        return None
    
    def delete_chefe(self, chefe_id: int) -> bool:
        """Desativa um chefe (soft delete)"""
        for chefe in self.chefes:
            if chefe.get('id') == chefe_id:
                chefe['ativo'] = False
                chefe['data_desativacao'] = datetime.now().strftime('%d/%m/%Y')
                self._save_chefes()
                logger.info(f"Chefe desativado: {chefe['nome']}")
                return True
        return False
    
    def get_setores(self) -> List[str]:
        """Retorna lista de setores únicos"""
        setores = set()
        for chefe in self.chefes:
            if chefe.get('ativo', True) and chefe.get('setor'):
                setores.add(chefe['setor'])
        return sorted(list(setores))
    
    def search_chefes(self, termo: str) -> List[Dict]:
        """Busca chefes por nome, posto ou função"""
        termo = termo.upper()
        return [c for c in self.chefes 
                if c.get('ativo', True) and 
                (termo in c.get('nome', '') or 
                 termo in c.get('posto', '') or 
                 termo in c.get('funcao', ''))]


# Singleton para uso em toda a aplicação
_chefes_manager = None

def get_chefes_manager() -> ChefesManager:
    """Retorna a instância singleton do ChefesManager"""
    global _chefes_manager
    if _chefes_manager is None:
        _chefes_manager = ChefesManager()
    return _chefes_manager
