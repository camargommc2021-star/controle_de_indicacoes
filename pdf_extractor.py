import pdfplumber
import pandas as pd
from datetime import datetime
import re
from io import BytesIO

class PDFExtractor:
    def __init__(self):
        self.patterns = {
            'Curso': [
                r'Curso[\s]*[:\-]?\s*([^\n]+)',
                r'CURSO[\s]*[:\-]?\s*([^\n]+)',
                r'Nome do Curso[\s]*[:\-]?\s*([^\n]+)'
            ],
            'Data': [
                r'Data[\s]*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'Data de In[íi]cio[\s]*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'In[íi]cio[\s]*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
            ],
            'Turma': [
                r'Turma[\s]*[:\-]?\s*([^\n]+)',
                r'TURMA[\s]*[:\-]?\s*([^\n]+)',
                r'Turma/Ano[\s]*[:\-]?\s*([^\n]+)'
            ],
            'Vagas': [
                r'Vagas[\s]*[:\-]?\s*(\d+)',
                r'Quantidade de Vagas[\s]*[:\-]?\s*(\d+)',
                r'N[úu]mero de Vagas[\s]*[:\-]?\s*(\d+)'
            ],
            'SIGAD': [
                r'SIGAD[\s]*[:\-]?\s*([^\n]+)',
                r'N[úu]mero do SIGAD[\s]*[:\-]?\s*([^\n]+)',
                r'Processo SIGAD[\s]*[:\-]?\s*([^\n]+)'
            ]
        }
    
    def extrair_cursos(self, pdf_file):
        try:
            if isinstance(pdf_file, BytesIO):
                pdf_bytes = pdf_file.read()
            else:
                pdf_bytes = pdf_file.getvalue() if hasattr(pdf_file, 'getvalue') else pdf_file.read()
            
            cursos = []
            
            with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
                texto_completo = ""
                for pagina in pdf.pages:
                    texto = pagina.extract_text()
                    if texto:
                        texto_completo += texto + "\n"
                
                blocos = self._dividir_em_blocos(texto_completo)
                
                for bloco in blocos:
                    curso = self._extrair_dados_bloco(bloco)
                    if curso and curso.get('Curso'):
                        curso = self._preencher_campos_padrao(curso)
                        cursos.append(curso)
            
            return cursos
            
        except Exception as e:
            print(f"Erro ao extrair PDF: {str(e)}")
            return []
    
    def _dividir_em_blocos(self, texto):
        delimitadores = [
            r'Curso[\s]*[:\-]',
            r'\n\n+',
            r'={3,}',
            r'-{3,}',
        ]
        
        blocos = [texto]
        
        for delim in delimitadores:
            novos_blocos = []
            for bloco in blocos:
                partes = re.split(delim, bloco, flags=re.IGNORECASE)
                novos_blocos.extend([p.strip() for p in partes if p.strip()])
            blocos = novos_blocos
        
        return [b for b in blocos if len(b) > 20]
    
    def _extrair_dados_bloco(self, bloco):
        dados = {}
        
        for campo, padroes in self.patterns.items():
            for padrao in padroes:
                match = re.search(padrao, bloco, re.IGNORECASE)
                if match:
                    valor = match.group(1).strip()
                    if campo == 'Curso':
                        dados['Curso'] = valor
                    elif campo == 'Data':
                        dados['Data_Inicio'] = valor
                    elif campo == 'Turma':
                        dados['Turma'] = valor
                    elif campo == 'Vagas':
                        dados['Vagas'] = int(valor)
                    elif campo == 'SIGAD':
                        dados['Numero_SIGAD'] = valor
                    break
        
        return dados
    
    def _preencher_campos_padrao(self, curso):
        curso_completo = {
            'Curso': curso.get('Curso', ''),
            'Turma': curso.get('Turma', 'Não informada'),
            'Vagas': curso.get('Vagas', 0),
            'Autorizados pelas escalantes': '',
            'Prioridade': 'Média',
            'Recebimento do SIGAD com as vagas': curso.get('Data_Inicio', datetime.now().strftime("%d/%m/%Y")),
            'Numero do SIGAD': curso.get('Numero_SIGAD', ''),
            'Estado': 'solicitar voluntários',
            'DATA DA CONCLUSÃO': '',
            'Numero do SIGAD  encaminhando pra chefia': '',
            'Prazo dado pela chefia': '',
            'Fim da indicação da SIAT': '',
            'Notas': 'Importado via PDF'
        }
        
        return curso_completo
    
    def extrair_texto_bruto(self, pdf_file):
        try:
            if isinstance(pdf_file, BytesIO):
                pdf_bytes = pdf_file.read()
            else:
                pdf_bytes = pdf_file.getvalue() if hasattr(pdf_file, 'getvalue') else pdf_file.read()
            
            with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
                texto = ""
                for pagina in pdf.pages:
                    texto_pagina = pagina.extract_text()
                    if texto_pagina:
                        texto += texto_pagina + "\n--- PÁGINA ---\n"
                return texto
        except Exception as e:
            return f"Erro ao extrair texto: {str(e)}"

if __name__ == "__main__":
    extractor = PDFExtractor()
    print("PDF Extractor pronto para uso!")
