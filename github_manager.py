import os
import base64
from datetime import datetime
from github import Github
from github import Auth
import streamlit as st

class GitHubManager:
    def __init__(self):
        self.token = os.environ.get('GITHUB_TOKEN') or st.secrets.get('GITHUB_TOKEN', '')
        self.repo_name = os.environ.get('GITHUB_REPO') or st.secrets.get('GITHUB_REPO', 'camargommc2021-star/controledeindica-es')
        self.arquivo_path = "data/cursos.xlsx"
        
        if self.token:
            try:
                auth = Auth.Token(self.token)
                self.github = Github(auth=auth)
                self.repo = self.github.get_repo(self.repo_name)
                self.authenticated = True
            except Exception as e:
                print(f"Erro ao conectar ao GitHub: {e}")
                self.authenticated = False
        else:
            self.authenticated = False
    
    def verificar_autenticacao(self):
        if not self.authenticated:
            return False, "Token do GitHub não configurado. Configure a variável GITHUB_TOKEN."
        try:
            user = self.github.get_user()
            user.login
            return True, f"Autenticado como: {user.login}"
        except Exception as e:
            return False, f"Erro de autenticação: {str(e)}"
    
    def obter_arquivo_excel(self):
        """Busca o arquivo Excel do repositório GitHub"""
        if not self.authenticated:
            return None, "Não autenticado"
        
        try:
            contents = self.repo.get_contents(self.arquivo_path)
            content_bytes = base64.b64decode(contents.content)
            return content_bytes, None
        except Exception as e:
            if "404" in str(e):
                return None, "Arquivo não encontrado no GitHub (será criado automaticamente)"
            return None, f"Erro ao obter arquivo: {str(e)}"
    
    def commit_excel(self, file_bytes, message=None):
        """Faz commit do arquivo Excel no GitHub"""
        if not self.authenticated:
            return False, "Token do GitHub não configurado"
        
        try:
            if not message:
                message = f"Atualização automática - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            
            try:
                contents = self.repo.get_contents(self.arquivo_path)
                self.repo.update_file(
                    path=self.arquivo_path,
                    message=message,
                    content=file_bytes,
                    sha=contents.sha
                )
                return True, f"✅ Dados salvos no GitHub ({datetime.now().strftime('%H:%M')})"
            except:
                self.repo.create_file(
                    path=self.arquivo_path,
                    message=message,
                    content=file_bytes
                )
                return True, f"✅ Arquivo criado no GitHub ({datetime.now().strftime('%H:%M')})"
                
        except Exception as e:
            return False, f"❌ Erro ao salvar no GitHub: {str(e)}"
    
    def sincronizar_para_local(self):
        """Sincroniza arquivo do GitHub para pasta local"""
        if not self.authenticated:
            return False, "Não autenticado"
        
        try:
            content_bytes, error = self.obter_arquivo_excel()
            if error and "não encontrado" not in error:
                return False, error
            
            if content_bytes:
                os.makedirs("data", exist_ok=True)
                with open(self.arquivo_path, 'wb') as f:
                    f.write(content_bytes)
                return True, "✅ Dados sincronizados do GitHub"
            else:
                return True, "ℹ️ Usando dados locais (arquivo ainda não existe no GitHub)"
                
        except Exception as e:
            return False, f"Erro na sincronização: {str(e)}"
    
    def obter_ultimo_commit(self):
        """Retorna informações do último commit"""
        if not self.authenticated:
            return None
        
        try:
            commits = self.repo.get_commits(path=self.arquivo_path)
            if commits.totalCount > 0:
                last_commit = commits[0]
                return {
                    'data': last_commit.commit.committer.date,
                    'mensagem': last_commit.commit.message,
                    'autor': last_commit.commit.committer.name
                }
            return None
        except:
            return None

if __name__ == "__main__":
    print("GitHub Manager pronto para uso!")
