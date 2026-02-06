import pandas as pd
import os
from datetime import datetime
from io import BytesIO
from github_manager import GitHubManager

# Configurar pandas para nao usar PyArrow
pd.set_option('compute.use_numba', False)

class DataManager:
    def __init__(self, usar_github=False):
        self.arquivo_local = "data/cursos.xlsx"
        
        # Campos base fixos
        self.colunas_base = [
            'Curso', 'Turma', 'Vagas', 'Autorizados pelas escalantes', 'Prioridade',
            'Recebimento do SIGAD com as vagas', 'Numero do SIGAD', 'Estado',
            'DATA DA CONCLUSÃO', 'Numero do SIGAD  encaminhando pra chefia',
            'Prazo dado pela chefia', 'Fim da indicação da SIAT', 'Notas',
            'OM_Executora'  # NOVO CAMPO
        ]
        
        # Campos dinamicos para OMs (inicialmente vazios, serao criados conforme necessario)
        self.colunas_om = []  # Sera preenchido dinamicamente: OM_GCC, OM_CINDACTA_I, etc.
        
        self.colunas = self.colunas_base.copy()
        
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
        self._atualizar_colunas_do_existente()
    
    def _atualizar_colunas_do_existente(self):
        """Atualiza a lista de colunas baseadas no arquivo Excel existente"""
        try:
            if os.path.exists(self.arquivo_local):
                df = pd.read_excel(self.arquivo_local, engine='openpyxl')
                # Detectar colunas de OM (comecam com OM_)
                colunas_existentes = list(df.columns)
                self.colunas_om = [col for col in colunas_existentes if col.startswith('OM_') and col != 'OM_Executora']
                # Atualizar lista completa
                self.colunas = self.colunas_base + self.colunas_om
        except Exception as e:
            print(f"Erro ao atualizar colunas: {e}")
    
    def _criar_arquivo_se_nao_existir(self):
        if not os.path.exists(self.arquivo_local):
            os.makedirs("data", exist_ok=True)
            df = pd.DataFrame(columns=self.colunas)
            df.to_excel(self.arquivo_local, index=False, engine='openpyxl')
    
    def adicionar_coluna_om(self, nome_om):
        """Adiciona uma nova coluna de OM dinamicamente"""
        # Normalizar nome da OM para o campo
        nome_campo = f"OM_{nome_om.replace(' ', '_').replace('-', '_').upper()}"
        
        if nome_campo not in self.colunas:
            self.colunas_om.append(nome_campo)
            self.colunas.append(nome_campo)
            
            # Atualizar arquivo Excel existente
            try:
                df = self.carregar_dados()
                if nome_campo not in df.columns:
                    df[nome_campo] = ""
                    df.to_excel(self.arquivo_local, index=False, engine='openpyxl')
            except Exception as e:
                print(f"Erro ao adicionar coluna {nome_campo}: {e}")
        
        return nome_campo
    
    def carregar_dados(self):
        try:
            if os.path.exists(self.arquivo_local):
                df = pd.read_excel(self.arquivo_local, engine='openpyxl')
                # Atualizar colunas baseadas no arquivo
                self.colunas = list(df.columns)
                self.colunas_om = [col for col in self.colunas if col.startswith('OM_') and col != 'OM_Executora']
                
                # Garantir que todas as colunas base existam
                for col in self.colunas_base:
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
            
            # Garantir que todas as colunas existam no DataFrame
            for col in self.colunas:
                if col not in df.columns:
                    df[col] = ""
            
            # Reordenar colunas conforme a ordem definida
            colunas_existentes = [col for col in self.colunas if col in df.columns]
            df = df[colunas_existentes]
            
            df.to_excel(self.arquivo_local, index=False, engine='openpyxl')
            
            # Commit no GitHub se estiver configurado
            if self.github_manager and self.github_manager.authenticated:
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
            
            # Verificar duplicados (mesmo curso e turma)
            if 'Curso' in curso_dict and 'Turma' in curso_dict:
                curso_nome = str(curso_dict.get('Curso', '')).strip()
                turma_nome = str(curso_dict.get('Turma', '')).strip()
                
                if curso_nome and turma_nome:
                    # Buscar curso+turma existente
                    duplicado = df[
                        (df['Curso'].astype(str).str.strip() == curso_nome) &
                        (df['Turma'].astype(str).str.strip() == turma_nome)
                    ]
                    
                    if not duplicado.empty:
                        return False, f"AVISO: Já existe um curso '{curso_nome} - {turma_nome}' cadastrado. Deseja mesmo adicionar?"
            
            # Verificar se ha campos de OM novos no curso_dict
            for key in curso_dict.keys():
                if key.startswith('OM_') and key not in self.colunas:
                    self.adicionar_coluna_om(key.replace('OM_', ''))
            
            # Recarregar dados apos possivel atualizacao de colunas
            df = self.carregar_dados()
            
            # Garantir que so campos validos sejam adicionados
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
                msg = "Curso cadastrado com sucesso!"
                if self.ultima_mensagem:
                    msg += f" ({self.ultima_mensagem})"
                return True, msg
            else:
                return False, "Erro ao salvar o curso."
        except Exception as e:
            return False, f"Erro ao adicionar curso: {str(e)}"
    
    def atualizar_curso(self, index, curso_dict):
        try:
            df = self.carregar_dados()
            
            if index < 0 or index >= len(df):
                return False, "Curso nao encontrado."
            
            # Verificar se ha campos de OM novos
            for key in curso_dict.keys():
                if key.startswith('OM_') and key not in self.colunas:
                    self.adicionar_coluna_om(key.replace('OM_', ''))
            
            # Recarregar dados
            df = self.carregar_dados()
            
            # Garantir que so campos validos sejam atualizados
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
                msg = "Curso atualizado com sucesso!"
                if self.ultima_mensagem:
                    msg += f" ({self.ultima_mensagem})"
                return True, msg
            else:
                return False, "Erro ao atualizar o curso."
        except Exception as e:
            return False, f"Erro ao atualizar curso: {str(e)}"
    
    def excluir_curso(self, index):
        try:
            df = self.carregar_dados()
            
            if index < 0 or index >= len(df):
                return False, "Curso nao encontrado."
            
            # Guardar nome do curso para a mensagem
            nome_curso = df.at[index, 'Curso'] if 'Curso' in df.columns else 'Curso'
            
            # Remover linha
            df = df.drop(index).reset_index(drop=True)
            
            # Salvar com commit
            mensagem = f"Excluido curso: {nome_curso}"
            sucesso = self._salvar_dados(df, mensagem)
            
            if sucesso:
                msg = "Curso excluido com sucesso!"
                if self.ultima_mensagem:
                    msg += f" ({self.ultima_mensagem})"
                return True, msg
            else:
                return False, "Erro ao excluir o curso."
        except Exception as e:
            return False, f"Erro ao excluir curso: {str(e)}"
    
    def excluir_todos_cursos(self):
        """Excluir todos os cursos do sistema"""
        try:
            # Criar DataFrame vazio com as colunas
            df = pd.DataFrame(columns=self.colunas)
            
            # Salvar com commit
            mensagem = "Excluidos todos os cursos"
            sucesso = self._salvar_dados(df, mensagem)
            
            if sucesso:
                msg = "Todos os cursos foram excluidos com sucesso!"
                if self.ultima_mensagem:
                    msg += f" ({self.ultima_mensagem})"
                return True, msg
            else:
                return False, "Erro ao excluir os cursos."
        except Exception as e:
            return False, f"Erro ao excluir todos os cursos: {str(e)}"
    
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
        """Retorna status da conexao com GitHub"""
        if not self.github_manager:
            return False, "GitHub nao habilitado"
        
        autenticado, mensagem = self.github_manager.verificar_autenticacao()
        
        if autenticado:
            ultimo_commit = self.github_manager.obter_ultimo_commit()
            if ultimo_commit:
                mensagem += f" | Ultima atualizacao: {ultimo_commit['data'].strftime('%d/%m/%Y %H:%M')}"
        
        return autenticado, mensagem
    
    def get_colunas_om(self):
        """Retorna lista de colunas de OM existentes"""
        return self.colunas_om

import streamlit as st
