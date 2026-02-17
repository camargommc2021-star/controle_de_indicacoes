import pandas as pd
import os
from datetime import datetime
from io import BytesIO

class FICManager:
    """Gerenciador de Fichas de Indicação de Candidato (FIC)"""
    
    def __init__(self):
        self.arquivo_fics = "data/fics.xlsx"
        self.colunas = [
            'ID', 'Data_Criacao', 'Data_Atualizacao', 'Status',
            # Dados do Curso
            'Curso', 'Turma', 'Local_GT', 'Comando', 
            'Data_Inicio_Presencial', 'Data_Termino_Presencial',
            'Data_Inicio_Distancia', 'Data_Termino_Distancia',
            'PPD_Civil',
            # Dados Pessoais
            'Posto_Graduacao', 'Nome_Completo', 'OM_Indicado',
            'CPF', 'SARAM', 'Email', 'Telefone',
            # Dados Funcionais
            'Funcao_Atual', 'Data_Ultima_Promocao',
            'Funcao_Apos_Curso', 'Tempo_Servico',
            'Pre_Requisitos',
            # Questionário
            'Curso_Mapeado', 'Progressao_Carreira', 
            'Comunicado_Indicado', 'Outro_Impedimento',
            'Curso_Anterior', 'Ano_Curso_Anterior',
            'Ciencia_Dedicacao_EAD',
            # Justificativa e Assinaturas
            'Justificativa_Chefe', 
            'Nome_Chefe_COP', 'Posto_Chefe_COP',
            'Nome_Responsavel_DACTA', 'Posto_Responsavel_DACTA'
        ]
        self._criar_arquivo_se_nao_existir()
    
    def _criar_arquivo_se_nao_existir(self):
        """Cria o arquivo Excel se não existir"""
        if not os.path.exists(self.arquivo_fics):
            os.makedirs('data', exist_ok=True)
            df = pd.DataFrame(columns=self.colunas)
            df.to_excel(self.arquivo_fics, index=False, engine='openpyxl')
    
    def gerar_id_fic(self, curso, nome, graduacao):
        """Gera ID único para o FIC no formato: CURSO-NOME-GRADUACAO"""
        # Limpar e formatar
        curso_limpo = curso.strip().upper().replace(' ', '-').replace('/', '-')
        nome_limpo = nome.strip().upper().replace(' ', '-')
        grad_limpo = graduacao.strip().upper().replace(' ', '-')
        
        # Formato: CILE-MOD1-SGT-DOUGLAS-AMARAL-PINTO
        id_fic = f"{curso_limpo}-{grad_limpo}-{nome_limpo}"
        
        # Remover caracteres especiais
        import re
        id_fic = re.sub(r'[^A-Z0-9\-]', '', id_fic)
        
        return id_fic
    
    def carregar_fics(self):
        """Carrega todos os FICs do Excel"""
        try:
            df = pd.read_excel(self.arquivo_fics, engine='openpyxl')
            # Garantir que todas as colunas existam
            for col in self.colunas:
                if col not in df.columns:
                    df[col] = ''
            return df
        except Exception as e:
            print(f"Erro ao carregar FICs: {e}")
            return pd.DataFrame(columns=self.colunas)
    
    def salvar_fic(self, dados_fic):
        """Salva um novo FIC"""
        try:
            df = self.carregar_fics()
            
            # Gerar ID
            id_fic = self.gerar_id_fic(
                dados_fic.get('Curso', ''),
                dados_fic.get('Nome_Completo', ''),
                dados_fic.get('Posto_Graduacao', '')
            )
            
            # Verificar se ID já existe
            if id_fic in df['ID'].values:
                return False, f"FIC com ID '{id_fic}' já existe!"
            
            # Adicionar metadados
            dados_fic['ID'] = id_fic
            dados_fic['Data_Criacao'] = datetime.now().strftime('%d/%m/%Y %H:%M')
            dados_fic['Data_Atualizacao'] = datetime.now().strftime('%d/%m/%Y %H:%M')
            
            # Adicionar ao DataFrame
            nova_linha = pd.DataFrame([dados_fic])
            df = pd.concat([df, nova_linha], ignore_index=True)
            
            # Salvar
            df.to_excel(self.arquivo_fics, index=False, engine='openpyxl')
            
            return True, id_fic
        except Exception as e:
            return False, f"Erro ao salvar FIC: {str(e)}"
    
    def atualizar_fic(self, id_fic, dados_fic):
        """Atualiza um FIC existente"""
        try:
            df = self.carregar_fics()
            
            # Encontrar o índice
            mask = df['ID'] == id_fic
            if not mask.any():
                return False, f"FIC '{id_fic}' não encontrado!"
            
            # Atualizar dados
            for coluna, valor in dados_fic.items():
                if coluna in df.columns and coluna not in ['ID', 'Data_Criacao']:
                    df.loc[mask, coluna] = valor
            
            # Atualizar data
            df.loc[mask, 'Data_Atualizacao'] = datetime.now().strftime('%d/%m/%Y %H:%M')
            
            # Salvar
            df.to_excel(self.arquivo_fics, index=False, engine='openpyxl')
            
            return True, f"FIC '{id_fic}' atualizado com sucesso!"
        except Exception as e:
            return False, f"Erro ao atualizar FIC: {str(e)}"
    
    def excluir_fic(self, id_fic):
        """Exclui um FIC"""
        try:
            df = self.carregar_fics()
            
            # Verificar se existe
            if id_fic not in df['ID'].values:
                return False, f"FIC '{id_fic}' não encontrado!"
            
            # Remover
            df = df[df['ID'] != id_fic]
            
            # Salvar
            df.to_excel(self.arquivo_fics, index=False, engine='openpyxl')
            
            return True, f"FIC '{id_fic}' excluído com sucesso!"
        except Exception as e:
            return False, f"Erro ao excluir FIC: {str(e)}"
    
    def buscar_fic(self, id_fic):
        """Busca um FIC específico pelo ID"""
        df = self.carregar_fics()
        fic = df[df['ID'] == id_fic]
        if len(fic) > 0:
            return fic.iloc[0].to_dict()
        return None
    
    def filtrar_fics(self, curso=None, nome=None, status=None):
        """Filtra FICs por critérios"""
        df = self.carregar_fics()
        
        if curso:
            df = df[df['Curso'].str.contains(curso, case=False, na=False)]
        if nome:
            df = df[df['Nome_Completo'].str.contains(nome, case=False, na=False)]
        if status:
            df = df[df['Status'] == status]
        
        return df

if __name__ == "__main__":
    # Teste
    fm = FICManager()
    print("FICManager inicializado com sucesso!")
    print(f"Total de FICs: {len(fm.carregar_fics())}")
