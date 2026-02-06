import pdfplumber
import pandas as pd
from datetime import datetime
import re
from io import BytesIO

class PDFExtractor:
    def __init__(self):
        # Padroes para formato generico
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
                
                # Tentar primeiro o formato especifico TCA 37-1
                cursos_tca = self._extrair_formato_tca(texto_completo)
                if cursos_tca:
                    cursos.extend(cursos_tca)
                else:
                    # Fallback para formato generico
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
    
    def _extrair_formato_tca(self, texto):
        """Extrai cursos no formato TCA 37-1 (DECEA)"""
        cursos = []
        
        # Padrao para identificar inicio de curso: CODIGO - TU XX ou CODIGO - TURMA XX
        padrao_curso = r'^([A-Z]{2,}\d{2,})\s*-\s*(?:TU|TURMA)\s*(\d+)'
        
        # Dividir o texto em blocos de cursos
        linhas = texto.split('\n')
        blocos = []
        bloco_atual = []
        
        for linha in linhas:
            linha = linha.strip()
            if not linha:
                continue
            
            # Verifica se eh inicio de novo curso
            match = re.match(padrao_curso, linha, re.IGNORECASE)
            if match and bloco_atual:
                # Salva bloco anterior
                blocos.append('\n'.join(bloco_atual))
                bloco_atual = []
            
            bloco_atual.append(linha)
        
        # Adiciona ultimo bloco
        if bloco_atual:
            blocos.append('\n'.join(bloco_atual))
        
        # Processar cada bloco
        for bloco in blocos:
            curso = self._processar_bloco_tca(bloco)
            if curso:
                cursos.append(curso)
        
        return cursos if cursos else None
    
    def _processar_bloco_tca(self, bloco):
        """Processa um bloco de curso no formato TCA"""
        curso = {}
        
        # 1. Extrair Codigo e Turma
        match = re.match(r'^([A-Z]{2,}\d{2,})\s*-\s*(?:TU|TURMA)\s*(\d+)', bloco, re.IGNORECASE)
        if match:
            curso['Curso'] = match.group(1)
            curso['Turma'] = f"TU {match.group(2)}"
        else:
            return None
        
        # 2. Extrair Data de Indicacao (Fim da indicacao da SIAT)
        match = re.search(r'Indica[çc][ãa]o:\s*(\d{2}[/-]\d{2}[/-]\d{4})', bloco, re.IGNORECASE)
        if match:
            curso['Fim da indicação da SIAT'] = match.group(1)
        
        # 3. Extrair OM Executora
        match = re.search(r'OM\s*executora:\s*([A-Z]+)', bloco, re.IGNORECASE)
        if match:
            curso['OM_Executora'] = match.group(1)
        
        # 4. Extrair Modalidade, Local, Inicio, Termino
        # Padrao: PRESENCIAL ICEA 22/06/2026 26/06/2026
        match = re.search(r'(PRESENCIAL|EAD|DISTANCIA)\s+([A-Z]+)\s+(\d{2}[/-]\d{2}[/-]\d{4})\s+(\d{2}[/-]\d{2}[/-]\d{4})', bloco, re.IGNORECASE)
        if match:
            modalidade = match.group(1)
            local = match.group(2)
            data_inicio = match.group(3)
            data_termino = match.group(4)
            curso['Notas'] = f"Modalidade: {modalidade}, Local: {local}, Inicio: {data_inicio}, Termino: {data_termino}"
        
        # 5. Extrair tabela de vagas por OM
        # Procurar por "Organização Vagas" ou "OM Vagas" ou similar
        vagas_om = {}
        
        # Padroes para linhas de vagas: "1 GCC 2" ou "CINDACTA I 3" ou "PAME-RJ 3"
        # Procura numeros seguidos de texto e numero no final
        padrao_vagas = r'(?:^|\n)(?:\d+\s+)?([A-Z][A-Z0-9\-]+(?:\s+[IV]+)?)\s+(\d+)(?:$|\n)'
        matches = re.findall(padrao_vagas, bloco, re.MULTILINE)
        
        for match in matches:
            nome_om = match[0].strip()
            qtd_vagas = match[1]
            # Normalizar nome do campo
            nome_campo = f"OM_{nome_om.replace(' ', '_').replace('-', '_').upper()}"
            vagas_om[nome_campo] = qtd_vagas
        
        # Se nao encontrou com padrao acima, tenta outro: cada linha com OM e numero
        if not vagas_om:
            linhas = bloco.split('\n')
            capturar_vagas = False
            for linha in linhas:
                # Detecta inicio da tabela de vagas
                if 'organiza' in linha.lower() or 'vagas' in linha.lower():
                    capturar_vagas = True
                    continue
                
                if capturar_vagas:
                    # Procura padrao: TEXTO NUMERO
                    match = re.match(r'(?:\d+\s+)?([A-Z][A-Z\s\-]+(?:\s+[IV]+)?)\s+(\d+)$', linha.strip())
                    if match:
                        nome_om = match.group(1).strip()
                        qtd_vagas = match.group(2)
                        nome_campo = f"OM_{nome_om.replace(' ', '_').replace('-', '_').upper()}"
                        vagas_om[nome_campo] = qtd_vagas
        
        # Adicionar vagas por OM ao curso
        curso.update(vagas_om)
        
        # Preencher campos padrao
        curso = self._preencher_campos_padrao(curso)
        
        return curso
    
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
            'Turma': curso.get('Turma', ''),
            'Vagas': '',  # Deixar vazio - usar campos por OM
            'Autorizados pelas escalantes': '',
            'Prioridade': '',
            'Recebimento do SIGAD com as vagas': '',
            'Numero do SIGAD': '',
            'Estado': '',
            'DATA DA CONCLUSÃO': '',
            'Numero do SIGAD  encaminhando pra chefia': '',
            'Prazo dado pela chefia': '',
            'Fim da indicação da SIAT': curso.get('Fim da indicação da SIAT', ''),
            'OM_Executora': curso.get('OM_Executora', ''),
            'Notas': curso.get('Notas', 'Importado via PDF TCA 37-1')
        }
        
        # Adicionar campos de OM dinamicos
        for key, value in curso.items():
            if key.startswith('OM_') and key != 'OM_Executora':
                curso_completo[key] = value
        
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
                        texto += texto_pagina + "\n--- PAGINA ---\n"
                return texto
        except Exception as e:
            return f"Erro ao extrair texto: {str(e)}"

if __name__ == "__main__":
    extractor = PDFExtractor()
    print("PDF Extractor atualizado para TCA 37-1!")
