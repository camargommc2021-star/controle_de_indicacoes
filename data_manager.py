import pandas as pd
import os


class DataManager:
    def __init__(self, arquivo_local=None):
        self.arquivo_local = arquivo_local or "data/cursos.xlsx"
        
        # Campos base fixos
        self.colunas_base = [
            'Curso', 'Turma', 'Vagas', 'Autorizados pelas escalantes', 'Prioridade',
            'Recebimento do SIGAD com as vagas', 'Numero do SIGAD', 'Estado',
            'DATA_DA_CONCLUSAO', 'Numero do SIGAD  encaminhando pra chefia',
            'Prazo dado pela chefia', 'Fim da indicação da SIAT', 'Notas',
            'OM_Executora'  # NOVO CAMPO
        ]
        
        # Campos dinamicos para OMs (inicialmente vazios, serao criados conforme necessario)
        self.colunas_om = []  # Sera preenchido dinamicamente: OM_GCC, OM_CINDACTA_I, etc.
        
        self.colunas = self.colunas_base.copy()
        
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
            pasta = os.path.dirname(self.arquivo_local)
            if pasta:
                os.makedirs(pasta, exist_ok=True)
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
    
    def _salvar_dados(self, df):
        try:
            pasta = os.path.dirname(self.arquivo_local)
            if pasta:
                os.makedirs(pasta, exist_ok=True)
            
            # Garantir que todas as colunas existam no DataFrame
            for col in self.colunas:
                if col not in df.columns:
                    df[col] = ""
            
            # Reordenar colunas conforme a ordem definida
            colunas_existentes = [col for col in self.colunas if col in df.columns]
            df = df[colunas_existentes]
            
            df.to_excel(self.arquivo_local, index=False, engine='openpyxl')
            return True
        except Exception as e:
            print(f"Erro ao salvar: {str(e)}")
            return False
    
    def adicionar_curso(self, curso_dict, permitir_duplicado=False):
        try:
            df = self.carregar_dados()
            
            # Verificar duplicados (mesmo curso e turma)
            if not permitir_duplicado and 'Curso' in curso_dict and 'Turma' in curso_dict:
                curso_nome = str(curso_dict.get('Curso', '')).strip()
                turma_nome = str(curso_dict.get('Turma', '')).strip()
                
                if curso_nome and turma_nome:
                    # Buscar curso+turma existente
                    duplicado = df[
                        (df['Curso'].astype(str).str.strip() == curso_nome) &
                        (df['Turma'].astype(str).str.strip() == turma_nome)
                    ]
                    
                    if not duplicado.empty:
                        return False, f"AVISO: Já existe o curso {curso_nome} - {turma_nome}. Para cadastrar mesmo assim, marque “Salvar mesmo se já existir curso com o mesmo nome e turma” e salve de novo."
            
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
            
            # Salvar
            sucesso = self._salvar_dados(df)
            
            if sucesso:
                return True, "Curso cadastrado com sucesso!"
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
            
            # Salvar
            sucesso = self._salvar_dados(df)
            
            if sucesso:
                return True, "Curso atualizado com sucesso!"
            else:
                return False, "Erro ao atualizar o curso."
        except Exception as e:
            return False, f"Erro ao atualizar curso: {str(e)}"
    
    def excluir_curso(self, index):
        try:
            df = self.carregar_dados()
            
            if index < 0 or index >= len(df):
                return False, "Curso nao encontrado."
            
            # Remover linha
            df = df.drop(index).reset_index(drop=True)
            
            # Salvar
            sucesso = self._salvar_dados(df)
            
            if sucesso:
                return True, "Curso excluido com sucesso!"
            else:
                return False, "Erro ao excluir o curso."
        except Exception as e:
            return False, f"Erro ao excluir curso: {str(e)}"
    
    def excluir_todos_cursos(self):
        """Excluir todos os cursos do sistema"""
        try:
            # Criar DataFrame vazio com as colunas
            df = pd.DataFrame(columns=self.colunas)
            
            # Salvar
            sucesso = self._salvar_dados(df)
            
            if sucesso:
                return True, "Todos os cursos foram excluidos com sucesso!"
            else:
                return False, "Erro ao excluir os cursos."
        except Exception as e:
            return False, f"Erro ao excluir todos os cursos: {str(e)}"
    
    def buscar_curso(self, termo):
        try:
            df = self.carregar_dados()
            if termo:
                # Buscar em todas as colunas
                mask = df.astype(str).apply(lambda x: x.str.contains(termo, regex=False, case=False, na=False))
                return df[mask.any(axis=1)]
            return df
        except Exception as e:
            print(f"Erro ao buscar: {str(e)}")
            return pd.DataFrame(columns=self.colunas)
    
    def get_colunas_om(self):
        """Retorna lista de colunas de OM existentes"""
        return self.colunas_om
