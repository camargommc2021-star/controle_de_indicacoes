import pandas as pd
import os
from datetime import datetime
from io import BytesIO
from github_manager import GitHubManager

# Configurar pandas para não usar PyArrow
pd.set_option('compute.use_numba', False)

class DataManager:
    def __init__(self, usar_github=False):
        self.arquivo_local = "data/cursos.xlsx"
        self.colunas = [
            'Curso', 'Turma', 'Vagas', 'Autorizados pelas escalantes', 'Prioridade',
            'Recebimento do SIGAD com as vagas', 'Numero do SIGAD', 'Estado',
            'DATA DA CONCLUSÃO', 'Numero do SIGAD  encaminhando pra chefia',
            'Prazo dado pela chefia', 'Fim da indicação da SIAT', 'Notas'
        ]
        
        # Verificar se deve usar GitHub (apenas se GITHUB_TOKEN estiver configurado)
        import os
        token = os.environ.get('GITHUB_TOKEN') or os.environ.get(' StreamlitSecrets ', {}).get('GITHUB_TOKEN', '')
        if not token and usar_github:
            usar_github = False
        
        self.github_manager = GitHubManager() if usar_github else None
        self.ultima_mensagem = ""
        
        # Sincronizar do GitHub ao iniciar (apenas se autenticado)
        if self.github_manager and self.github_manager.authenticated:
            sucesso, mensagem = self.github_manager.sincronizar_para_local()
            self.ultima_mensagem = mensagem
        
        self._criar_arquivo_se_nao_existir()
    
    def _criar_arquivo_se_nao_existir(self):
        if not os.path.exists(self.arquivo_local):
            os.makedirs("data", exist_ok=True)
            df = pd.DataFrame(columns=self.colunas)
            df.to_excel(self.arquivo_local, index=False, engine='openpyxl')
    
    def carregar_dados(self):
        try:
            if os.path.exists(self.arquivo_local):
                df = pd.read_excel(self.arquivo_local, engine='openpyxl')
                # Garantir que todas as colunas existam
                for col in self.colunas:
                    if col not in df.columns:
                        df[col] = ""
                return df
            else:
                return pd.DataFrame(columns=self.colunas)
        except Exception as e:
            print(f"Erro ao carregar dados: {str(e)}")
            return pd.DataFrame(columns=self.colunas)
    
    def _salvar_dados(self, df, mensagem_commit=None):
        try:
            os.makedirs("data", exist_ok=True)
            df.to_excel(self.arquivo_local, index=False, engine='openpyxl')
            
            # Commit no GitHub se estiver configurado
            if self.github_manager and self.github_manager.authenticated:
                # Ler o arquivo e converter para bytes
                with open(self.arquivo_local, 'rb') as f:
                    file_bytes = f.read()
                
                sucesso, mensagem = self.github_manager.commit_excel(file_bytes, mensagem_commit)
                self.ultima_mensagem = mensagem
                return sucesso
            
            return True
        except Exception as e:
            print(f"Erro ao salvar: {str(e)}")
            return False
    
    def adicionar_curso(self, curso_dict):
        try:
            df = self.carregar_dados()
            
            # Garantir que só campos válidos sejam adicionados
            curso_dict = {k: v for k, v in curso_dict.items() if k in self.colunas}
            
            # Preencher campos ausentes
            for col in self.colunas:
                if col not in curso_dict:
                    curso_dict[col] = ""
            
            # Criar DataFrame com uma linha
            novo_df = pd.DataFrame([curso_dict])
            
            # Concatenar
            df = pd.concat([df, novo_df], ignore_index=True)
            
            # Salvar com commit
            mensagem = f"Adicionado curso: {curso_dict.get('Curso', 'Novo curso')}"
            sucesso = self._salvar_dados(df, mensagem)
            
            if sucesso:
                msg = "✅ Curso cadastrado com sucesso!"
                if self.ultima_mensagem:
                    msg += f" ({self.ultima_mensagem})"
                return True, msg
            else:
                return False, "❌ Erro ao salvar o curso."
        except Exception as e:
            return False, f"❌ Erro ao adicionar curso: {str(e)}"
    
    def atualizar_curso(self, index, curso_dict):
        try:
            df = self.carregar_dados()
            
            if index < 0 or index >= len(df):
                return False, "❌ Curso não encontrado."
            
            # Garantir que só campos válidos sejam atualizados
            curso_dict = {k: v for k, v in curso_dict.items() if k in self.colunas}
            
            # Preencher campos ausentes
            for col in self.colunas:
                if col not in curso_dict:
                    curso_dict[col] = ""
            
            # Atualizar cada coluna
            for col, valor in curso_dict.items():
                df.at[index, col] = valor
            
            # Salvar com commit
            mensagem = f"Atualizado curso: {curso_dict.get('Curso', 'Curso')}"
            sucesso = self._salvar_dados(df, mensagem)
            
            if sucesso:
                msg = "✅ Curso atualizado com sucesso!"
                if self.ultima_mensagem:
                    msg += f" ({self.ultima_mensagem})"
                return True, msg
            else:
                return False, "❌ Erro ao atualizar o curso."
        except Exception as e:
            return False, f"❌ Erro ao atualizar curso: {str(e)}"
    
    def excluir_curso(self, index):
        try:
            df = self.carregar_dados()
            
            if index < 0 or index >= len(df):
                return False, "❌ Curso não encontrado."
            
            # Guardar nome do curso para a mensagem
            nome_curso = df.at[index, 'Curso'] if 'Curso' in df.columns else 'Curso'
            
            # Remover linha
            df = df.drop(index).reset_index(drop=True)
            
            # Salvar com commit
            mensagem = f"Excluído curso: {nome_curso}"
            sucesso = self._salvar_dados(df, mensagem)
            
            if sucesso:
                msg = "✅ Curso excluído com sucesso!"
                if self.ultima_mensagem:
                    msg += f" ({self.ultima_mensagem})"
                return True, msg
            else:
                return False, "❌ Erro ao excluir o curso."
        except Exception as e:
            return False, f"❌ Erro ao excluir curso: {str(e)}"
    
    def exportar_excel_bytes(self):
        try:
            df = self.carregar_dados()
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Cursos')
            output.seek(0)
            return output.getvalue()
        except Exception as e:
            print(f"Erro ao exportar: {str(e)}")
            return b""
    
    def buscar_curso(self, termo):
        try:
            df = self.carregar_dados()
            if termo:
                # Buscar em todas as colunas
                mask = df.astype(str).apply(lambda x: x.str.contains(termo, case=False, na=False))
                return df[mask.any(axis=1)]
            return df
        except Exception as e:
            print(f"Erro ao buscar: {str(e)}")
            return pd.DataFrame(columns=self.colunas)
    
    def verificar_status_github(self):
        """Retorna status da conexão com GitHub"""
        if not self.github_manager:
            return False, "GitHub não habilitado"
        
        autenticado, mensagem = self.github_manager.verificar_autenticacao()
        
        if autenticado:
            ultimo_commit = self.github_manager.obter_ultimo_commit()
            if ultimo_commit:
                mensagem += f" | Última atualização: {ultimo_commit['data'].strftime('%d/%m/%Y %H:%M')}"
        
        return autenticado, mensagem
