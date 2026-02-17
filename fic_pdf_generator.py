from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from io import BytesIO
import os

class FICPDFGenerator:
    """Gerador de PDF para Ficha de Indicação de Candidato (FIC)"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.logo_path = "assets/crcea_se_logo.png"
        
    def gerar_pdf(self, dados_fic):
        """Gera o PDF do FIC preenchido"""
        buffer = BytesIO()
        
        # Criar documento
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=1*cm,
            bottomMargin=1*cm
        )
        
        # Container para elementos
        elementos = []
        
        # Estilos personalizados
        titulo_style = ParagraphStyle(
            'Titulo',
            parent=self.styles['Heading1'],
            fontSize=10,
            alignment=TA_CENTER,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        )
        
        subtitulo_style = ParagraphStyle(
            'Subtitulo',
            parent=self.styles['Heading2'],
            fontSize=9,
            alignment=TA_CENTER,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        )
        
        texto_style = ParagraphStyle(
            'Texto',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_LEFT,
            spaceAfter=3
        )
        
        texto_centralizado_style = ParagraphStyle(
            'TextoCentralizado',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            spaceAfter=3
        )
        
        # === CABEÇALHO ===
        # Logo e título
        header_data = []
        
        # Tentar adicionar logo
        if os.path.exists(self.logo_path):
            try:
                img = Image(self.logo_path, width=2.5*cm, height=3*cm)
                header_data.append([img, '', '', ''])
            except:
                header_data.append(['', '', '', ''])
        else:
            header_data.append(['', '', '', ''])
        
        # Títulos
        titulo1 = Paragraph("CENTRO REGIONAL DE CONTROLE DO ESPAÇO AÉREO SUDESTE", titulo_style)
        titulo2 = Paragraph("ASSESSORIA DE INSTRUÇÃO E ATUALIZAÇÃO TÉCNICA", subtitulo_style)
        titulo3 = Paragraph("FICHA DE INDICAÇÃO DE CANDIDATO A CURSO", subtitulo_style)
        
        # Aviso
        aviso_texto = """ESTA FICHA DEVERÁ SER ADEQUADAMENTE PREENCHIDA E ENVIADA À DIVISÃO/SEÇÃO DO CURSO PARA APROVAÇÃO E PARA ENTRADA NA SIAT EM ATÉ 5 (CINCO) DIAS ÚTEIS ANTES DO PRAZO DE INDICAÇÃO."""
        aviso = Paragraph(aviso_texto, ParagraphStyle('Aviso', parent=texto_style, fontSize=7, alignment=TA_JUSTIFY))
        
        # === SEÇÃO 1: DADOS DO CURSO ===
        dados_curso = [
            ['CÓDIGO DO CURSO:', dados_fic.get('Curso', ''), 'TURMA:', dados_fic.get('Turma', ''),
             'LOCAL DO CURSO GT:', dados_fic.get('Local_GT', ''), 'COMANDO:', dados_fic.get('Comando', '')],
            ['DATA DE INÍCIO (Presencial):', dados_fic.get('Data_Inicio_Presencial', ''), 
             '', '', 'DATA DE TÉRMINO (Presencial):', dados_fic.get('Data_Termino_Presencial', ''), '', ''],
            ['DATA DE INÍCIO (À distância):', dados_fic.get('Data_Inicio_Distancia', ''),
             '', '', 'DATA DE TÉRMINO (À distância):', dados_fic.get('Data_Termino_Distancia', ''), '', '']
        ]
        
        # PPD para civis
        ppd = dados_fic.get('PPD_Civil', '')
        ppd_sim = '(X)' if ppd == 'SIM' else '( )'
        ppd_nao = '(X)' if ppd == 'NÃO' else '( )'
        
        # === SEÇÃO 2: DADOS PESSOAIS ===
        posto_nome = f"{dados_fic.get('Posto_Graduacao', '')} {dados_fic.get('Nome_Completo', '')}"
        dados_pessoais = [
            ['POSTO/GRAD/ESP/NOME COMPLETO (Sublinhar nome de guerra):', '', '', '', '', '', '', ''],
            [posto_nome, '', '', '', '', '', '', ''],
            ['OM DO INDICADO:', dados_fic.get('OM_Indicado', ''), 'CPF:', dados_fic.get('CPF', ''),
             'SARAM:', dados_fic.get('SARAM', ''), '', ''],
            ['E-MAIL:', dados_fic.get('Email', ''), '', '', 'TELEFONE:', dados_fic.get('Telefone', ''), '', '']
        ]
        
        # === SEÇÃO 3: DADOS FUNCIONAIS ===
        pre_req = dados_fic.get('Pre_Requisitos', '')
        pre_req_sim = '(X)' if pre_req == 'SIM' else '( )'
        pre_req_nao = '(X)' if pre_req == 'NÃO' else '( )'
        
        dados_funcionais = [
            ['FUNÇÃO ATUAL:', dados_fic.get('Funcao_Atual', ''), '', '', 
             'DATA ÚLTIMA PROMOÇÃO:', dados_fic.get('Data_Ultima_Promocao', ''), '', ''],
            ['FUNÇÃO QUE O INDICADO EXERCERÁ APÓS O CURSO/ESTÁGIO:', dados_fic.get('Funcao_Apos_Curso', ''), '', '', '', '', '', ''],
            ['TEMPO DE SERVIÇO:', dados_fic.get('Tempo_Servico', ''),
             f'POSSUI OS PRÉ-REQUISITOS PARA O CURSO? {pre_req_sim} SIM {pre_req_nao} NÃO', '', '', '', '', '']
        ]
        
        # === SEÇÃO 4: QUESTIONÁRIO ===
        q1 = '(X)' if dados_fic.get('Curso_Mapeado') == 'SIM' else '( )'
        q1_nao = '(X)' if dados_fic.get('Curso_Mapeado') == 'NÃO' else '( )'
        
        q2 = '(X)' if dados_fic.get('Progressao_Carreira') == 'SIM' else '( )'
        q2_nao = '(X)' if dados_fic.get('Progressao_Carreira') == 'NÃO' else '( )'
        
        q3 = '(X)' if dados_fic.get('Comunicado_Indicado') == 'SIM' else '( )'
        q3_nao = '(X)' if dados_fic.get('Comunicado_Indicado') == 'NÃO' else '( )'
        
        q4 = '(X)' if dados_fic.get('Outro_Impedimento') == 'SIM' else '( )'
        q4_nao = '(X)' if dados_fic.get('Outro_Impedimento') == 'NÃO' else '( )'
        
        q5 = '(X)' if dados_fic.get('Curso_Anterior') == 'SIM' else '( )'
        q5_nao = '(X)' if dados_fic.get('Curso_Anterior') == 'NÃO' else '( )'
        
        q6 = '(X)' if dados_fic.get('Ciencia_Dedicacao_EAD') == 'SIM' else '( )'
        q6_nao = '(X)' if dados_fic.get('Ciencia_Dedicacao_EAD') == 'NÃO' else '( )'
        
        ano_curso = dados_fic.get('Ano_Curso_Anterior', '')
        
        questionario = [
            [f'O CURSO SOLICITADO ESTÁ MAPEADO NO POSTO DE TRABALHO DO INDICADO? {q1} SIM {q1_nao} NÃO', '', '', '', '', '', '', ''],
            [f'O CURSO SOLICITADO FAZ PARTE DA PROGRESSÃO INDIVIDUAL DE SUA CARREIRA? {q2} SIM {q2_nao} NÃO', '', '', '', '', '', '', ''],
            [f'O INDICADO FOI COMUNICADO A RESPEITO DESTA INDICAÇÃO E CONFIRMOU NÃO ESTAR DE FÉRIAS OU NÃO TER OUTRO IMPEDIMENTO (EX. CURSO CONCOMITANTE QUE NÃO É DE CARREIRA)? {q3} SIM {q3_nao} NÃO', '', '', '', '', '', '', ''],
            [f'JÁ REALIZOU O CURSO ANTERIORMENTE? SE SIM, EM QUE ANO? {q5} SIM {q5_nao} NÃO   ANO: {ano_curso}', '', '', '', '', '', '', ''],
            [f'O CHEFE ESTÁ CIENTE QUE, PARA CURSOS EAD, O MILITAR PRECISA DE DEDICAÇÃO EXCLUSIVA DE 4H DIÁRIAS CONSECUTIVAS? {q6} SIM {q6_nao} NÃO', '', '', '', '', '', '', '']
        ]
        
        # === SEÇÃO 5: JUSTIFICATIVA ===
        justificativa = dados_fic.get('Justificativa_Chefe', '')
        
        # === ASSINATURAS ===
        data_atual = dados_fic.get('Data_Criacao', '').split()[0] if dados_fic.get('Data_Criacao') else '__/__/____'
        assinaturas = [
            [f'DATA: {data_atual}', '', ''],
            ['', dados_fic.get('Nome_Chefe_COP', ''), dados_fic.get('Nome_Responsavel_DACTA', '')],
            ['', dados_fic.get('Posto_Chefe_COP', ''), dados_fic.get('Posto_Responsavel_DACTA', '')],
            ['', 'Chefe do COP', 'Responsável DACTA']
        ]
        
        # === MONTAR TABELAS ===
        
        # Tabela de aviso
        tabela_aviso = Table([[aviso]], colWidths=[19*cm])
        tabela_aviso.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#E8F4F8')),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        # Tabela dados do curso
        tabela_curso = Table(dados_curso, colWidths=[3.5*cm, 3*cm, 2*cm, 2*cm, 3.5*cm, 2.5*cm, 1.5*cm, 1*cm])
        tabela_curso.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        
        # Tabela dados pessoais
        tabela_pessoais = Table(dados_pessoais, colWidths=[3*cm, 3*cm, 2*cm, 3*cm, 2*cm, 2*cm, 2*cm, 2*cm])
        tabela_pessoais.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        
        # Tabela dados funcionais
        tabela_funcionais = Table(dados_funcionais, colWidths=[3*cm, 4*cm, 2*cm, 4*cm, 2*cm, 2*cm, 1*cm, 1*cm])
        tabela_funcionais.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        
        # Tabela questionário
        tabela_questionario = Table(questionario, colWidths=[19*cm])
        tabela_questionario.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        # Tabela justificativa
        justificativa_texto = Paragraph(justificativa, ParagraphStyle('Justificativa', parent=texto_style, fontSize=8))
        tabela_justificativa = Table([[justificativa_texto]], colWidths=[19*cm], rowHeights=[4*cm])
        tabela_justificativa.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        # Tabela assinaturas
        tabela_assinaturas = Table(assinaturas, colWidths=[6*cm, 6.5*cm, 6.5*cm])
        tabela_assinaturas.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LINEABOVE', (1, 1), (2, 1), 1, colors.black),  # Linha de assinatura
        ]))
        
        # === MONTAR DOCUMENTO ===
        elementos.append(titulo1)
        elementos.append(titulo2)
        elementos.append(titulo3)
        elementos.append(Spacer(1, 0.3*cm))
        elementos.append(tabela_aviso)
        elementos.append(Spacer(1, 0.3*cm))
        elementos.append(Paragraph("<b>DADOS DO CURSO</b>", texto_style))
        elementos.append(tabela_curso)
        elementos.append(Spacer(1, 0.3*cm))
        elementos.append(Paragraph("<b>DADOS PESSOAIS</b>", texto_style))
        elementos.append(tabela_pessoais)
        elementos.append(Spacer(1, 0.3*cm))
        elementos.append(Paragraph("<b>DADOS FUNCIONAIS</b>", texto_style))
        elementos.append(tabela_funcionais)
        elementos.append(Spacer(1, 0.3*cm))
        elementos.append(Paragraph("<b>QUESTIONÁRIO</b>", texto_style))
        elementos.append(tabela_questionario)
        elementos.append(Spacer(1, 0.3*cm))
        elementos.append(Paragraph("<b>JUSTIFICATIVA DO CHEFE IMEDIATO</b>", texto_style))
        elementos.append(tabela_justificativa)
        elementos.append(Spacer(1, 0.5*cm))
        elementos.append(tabela_assinaturas)
        
        # Gerar PDF
        doc.build(elementos)
        
        # Retornar buffer
        buffer.seek(0)
        return buffer
    
    def gerar_pdf_bytes(self, dados_fic):
        """Retorna os bytes do PDF para download"""
        buffer = self.gerar_pdf(dados_fic)
        return buffer.getvalue()

if __name__ == "__main__":
    # Teste
    dados_teste = {
        'Curso': 'CILE-MOD I',
        'Turma': '01/2026',
        'Local_GT': 'FEAR',
        'Comando': 'DECEA',
        'Data_Inicio_Presencial': '18/05/2026',
        'Data_Termino_Presencial': '29/04/2026',
        'Posto_Graduacao': '1S',
        'Nome_Completo': 'DOUGLAS AMARAL PINTO',
        'OM_Indicado': 'CRCEA-SE',
        'CPF': '228.119.538-41',
        'SARAM': '437.947-0',
        'Email': '(19) 99719-1735',
        'Telefone': '(11) 2112-3421',
        'Funcao_Atual': 'SUPERVISOR DO APP-SP',
        'Data_Ultima_Promocao': '01/12/2022',
        'Tempo_Servico': '18 ANOS e 11 MESES',
        'Pre_Requisitos': 'SIM',
        'Curso_Mapeado': 'SIM',
        'Progressao_Carreira': 'SIM',
        'Comunicado_Indicado': 'SIM',
        'Outro_Impedimento': 'NÃO',
        'Curso_Anterior': 'NÃO',
        'Ano_Curso_Anterior': '',
        'Ciencia_Dedicacao_EAD': 'SIM',
        'Justificativa_Chefe': 'O indicado é SUPERVISOR DO APP-SP e atende os pré-requisitos conforme o PUD do curso que, além de fazer parte da progressão individual de sua carreira, será de suma importância para a elevação e manutenção dos requisitos de Segurança Operacional do APP-SP',
        'Nome_Chefe_COP': 'LEONARDO REZENDE ALVES',
        'Posto_Chefe_COP': 'MJ QOAV',
        'Nome_Responsavel_DACTA': 'NATALIA DE CASTRO GUERREIRO',
        'Posto_Responsavel_DACTA': 'C- DACTA 1301',
        'Data_Criacao': '06/02/2026 14:30'
    }
    
    generator = FICPDFGenerator()
    pdf_buffer = generator.gerar_pdf(dados_teste)
    
    # Salvar arquivo de teste
    with open('teste_fic.pdf', 'wb') as f:
        f.write(pdf_buffer.getvalue())
    
    print("PDF de teste gerado: teste_fic.pdf")
