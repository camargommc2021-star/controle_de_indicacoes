import os
import shutil
from datetime import datetime
import glob


class BackupManager:
    """Gerenciador de backups automáticos"""
    
    def __init__(self, arquivo_dados="data/cursos.xlsx", pasta_backup="backups"):
        self.arquivo_dados = arquivo_dados
        self.pasta_backup = pasta_backup
        self.max_backups = 30  # Manter últimos 30 backups
        
        # Criar pasta de backup se não existir
        os.makedirs(self.pasta_backup, exist_ok=True)
    
    def criar_backup(self):
        """Cria um backup do arquivo de dados"""
        try:
            if not os.path.exists(self.arquivo_dados):
                return False, "Arquivo de dados não encontrado"
            
            # Nome do backup com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_backup = f"cursos_{timestamp}.xlsx"
            caminho_backup = os.path.join(self.pasta_backup, nome_backup)
            
            # Copiar arquivo
            shutil.copy2(self.arquivo_dados, caminho_backup)
            
            # Limpar backups antigos
            self._limpar_backups_antigos()
            
            return True, f"Backup criado: {nome_backup}"
        except Exception as e:
            return False, f"Erro ao criar backup: {str(e)}"
    
    def _limpar_backups_antigos(self):
        """Remove backups antigos mantendo apenas os últimos N"""
        try:
            # Listar todos os backups
            backups = glob.glob(os.path.join(self.pasta_backup, "cursos_*.xlsx"))
            
            # Ordenar por data de modificação (mais recentes primeiro)
            backups.sort(key=os.path.getmtime, reverse=True)
            
            # Remover backups excedentes
            for backup in backups[self.max_backups:]:
                os.remove(backup)
        except Exception as e:
            print(f"Erro ao limpar backups antigos: {str(e)}")
    
    def listar_backups(self):
        """Lista todos os backups disponíveis"""
        try:
            backups = glob.glob(os.path.join(self.pasta_backup, "cursos_*.xlsx"))
            backups.sort(key=os.path.getmtime, reverse=True)
            
            resultado = []
            for backup in backups:
                nome = os.path.basename(backup)
                data_mod = datetime.fromtimestamp(os.path.getmtime(backup))
                tamanho = os.path.getsize(backup)
                
                resultado.append({
                    'nome': nome,
                    'caminho': backup,
                    'data': data_mod,
                    'tamanho': tamanho
                })
            
            return resultado
        except Exception as e:
            print(f"Erro ao listar backups: {str(e)}")
            return []
    
    def restaurar_backup(self, caminho_backup):
        """Restaura um backup específico"""
        try:
            if not os.path.exists(caminho_backup):
                return False, "Backup não encontrado"
            
            # Criar backup do arquivo atual antes de restaurar
            self.criar_backup()
            
            # Restaurar backup
            shutil.copy2(caminho_backup, self.arquivo_dados)
            
            return True, "Backup restaurado com sucesso!"
        except Exception as e:
            return False, f"Erro ao restaurar backup: {str(e)}"
    
    def backup_automatico_necessario(self):
        """Verifica se é necessário fazer backup automático (1x por dia)"""
        try:
            backups = self.listar_backups()
            if not backups:
                return True
            
            # Verificar data do último backup
            ultimo_backup = backups[0]
            data_ultimo = ultimo_backup['data'].date()
            hoje = datetime.now().date()
            
            return data_ultimo < hoje
        except:
            return True


if __name__ == "__main__":
    manager = BackupManager()
    sucesso, msg = manager.criar_backup()
    print(msg)
