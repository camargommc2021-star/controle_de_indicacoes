import json
import re
from datetime import datetime

class JSONImporter:
    """Classe para importar cursos via arquivo JSON"""
    
    def __init__(self):
        self.campos_obrigatorios = ['Curso', 'Turma', 'Fim da indicação da SIAT']
        self.erros = []
        self.cursos_validos = []
        self.cursos_invalidos = []
        
        # Mapeamento de campos do novo formato para o formato interno
        self.mapeamento_campos = {
            'NOME DO CURSO - TU': 'Curso',
            'Indicação': 'Fim da indicação da SIAT',
            'OM executora': 'OM_Executora',
            'Modalidade': 'Modalidade',
            'Local': 'Local',
            'Início': 'Data_Inicio',
            'Término': 'Data_Termino',
            'Organização': 'OM_Organizacao',
            'Vagas': 'Vagas'
        }
    
    def carregar_json(self, arquivo_bytes):
        """Carrega e faz o parse do arquivo JSON"""
        try:
            conteudo = arquivo_bytes.decode('utf-8')
            dados = json.loads(conteudo)
            return dados, None
        except json.JSONDecodeError as e:
            return None, f"Erro no formato JSON: {str(e)}"
        except Exception as e:
            return None, f"Erro ao ler arquivo: {str(e)}"
    
    def normalizar_curso(self, curso_original):
        """Normaliza um curso do novo formato para o formato interno"""
        curso_normalizado = {}
        
        for campo_original, valor in curso_original.items():
            # Verificar se existe mapeamento para este campo
            if campo_original in self.mapeamento_campos:
                campo_interno = self.mapeamento_campos[campo_original]
                curso_normalizado[campo_interno] = valor
            else:
                # Manter o campo original se não houver mapeamento
                curso_normalizado[campo_original] = valor
        
        # Extrair turma do nome do curso se presente (formato: "AAC001 - TU 01")
        if 'Curso' in curso_normalizado and 'Turma' not in curso_normalizado:
            nome_completo = str(curso_normalizado['Curso'])
            if ' - TU ' in nome_completo:
                partes = nome_completo.split(' - TU ')
                curso_normalizado['Curso'] = partes[0].strip()
                curso_normalizado['Turma'] = f"TU {partes[1].strip()}"
            elif ' - ' in nome_completo:
                partes = nome_completo.split(' - ')
                curso_normalizado['Curso'] = partes[0].strip()
                curso_normalizado['Turma'] = partes[1].strip() if len(partes) > 1 else "01"
        
        # Se há uma organização, criar campo de OM com vagas
        if 'OM_Organizacao' in curso_normalizado and 'Vagas' in curso_normalizado:
            nome_om = str(curso_normalizado['OM_Organizacao']).replace(' ', '_').replace('-', '_').upper()
            campo_om = f"OM_{nome_om}"
            curso_normalizado[campo_om] = curso_normalizado.get('Vagas', 0)
        
        return curso_normalizado
    
    def validar_json(self, dados):
        """Valida a estrutura do JSON e retorna cursos válidos e inválidos"""
        self.cursos_validos = []
        self.cursos_invalidos = []
        self.erros = []
        
        # Detectar formato do JSON
        # Se for lista direta, usar como está
        if isinstance(dados, list):
            cursos = dados
        # Se for objeto com chave 'cursos', usar essa lista
        elif isinstance(dados, dict) and 'cursos' in dados:
            cursos = dados['cursos']
        else:
            self.erros.append("JSON deve ser uma lista ou conter a chave 'cursos'")
            return [], []
        
        if not isinstance(cursos, list):
            self.erros.append("Dados de cursos devem ser uma lista")
            return [], []
        
        # Validar cada curso
        for i, curso in enumerate(cursos):
            if not isinstance(curso, dict):
                self.cursos_invalidos.append({
                    'index': i,
                    'curso': curso,
                    'erro': 'Curso não é um objeto válido'
                })
                continue
            
            # Normalizar campos antes de validar
            curso_normalizado = self.normalizar_curso(curso)
            
            eh_valido, mensagem = self.validar_curso(curso_normalizado)
            
            if eh_valido:
                self.cursos_validos.append(curso_normalizado)
            else:
                self.cursos_invalidos.append({
                    'index': i,
                    'curso': curso_normalizado.get('Curso', 'Sem nome'),
                    'erro': mensagem
                })
        
        return self.cursos_validos, self.cursos_invalidos
    
    def validar_curso(self, curso):
        """Valida um curso individual"""
        # Verificar campos obrigatórios
        for campo in self.campos_obrigatorios:
            if campo not in curso or not str(curso[campo]).strip():
                return False, f"Campo obrigatório '{campo}' está vazio ou ausente"
        
        # Validar formato da data
        data_siat = str(curso.get('Fim da indicação da SIAT', ''))
        if not self.validar_data(data_siat):
            return False, f"Data 'Fim da indicação da SIAT' inválida: {data_siat}. Use formato DD/MM/AAAA"
        
        # Verificar se tem pelo menos uma OM com vaga
        tem_om_com_vaga = False
        for key, value in curso.items():
            if key.startswith('OM_') and key != 'OM_Executora':
                try:
                    vaga = int(value)
                    if vaga > 0:
                        tem_om_com_vaga = True
                        break
                except:
                    pass
        
        if not tem_om_com_vaga:
            return False, "Curso deve ter pelo menos uma OM com vaga > 0"
        
        return True, "Válido"
    
    def validar_data(self, data_str):
        """Valida formato de data DD/MM/AAAA"""
        if not data_str:
            return False
        
        padrao = r'^\d{2}/\d{2}/\d{4}$'
        if not re.match(padrao, str(data_str)):
            return False
        
        try:
            datetime.strptime(str(data_str), '%d/%m/%Y')
            return True
        except ValueError:
            return False
    
    def preparar_curso_para_importacao(self, curso):
        """Prepara o curso para importação, normalizando campos"""
        curso_preparado = {}
        
        # Campos base
        campos_base = [
            'Curso', 'Turma', 'Vagas', 'Autorizados pelas escalantes', 'Prioridade',
            'Recebimento do SIGAD com as vagas', 'Numero do SIGAD', 'Estado',
            'DATA DA CONCLUSÃO', 'Numero do SIGAD  encaminhando pra chefia',
            'Prazo dado pela chefia', 'Fim da indicação da SIAT', 'Notas',
            'OM_Executora'
        ]
        
        # Preencher campos base
        for campo in campos_base:
            if campo in curso:
                curso_preparado[campo] = str(curso[campo])
            else:
                curso_preparado[campo] = ""
        
        # Preencher campos de OM
        for key, value in curso.items():
            if key.startswith('OM_'):
                curso_preparado[key] = str(value)
        
        return curso_preparado
    
    def importar_cursos(self, cursos, data_manager):
        """Importa cursos válidos para o sistema"""
        importados = 0
        erros = []
        
        for curso in cursos:
            try:
                curso_preparado = self.preparar_curso_para_importacao(curso)
                sucesso, mensagem = data_manager.adicionar_curso(curso_preparado)
                
                if sucesso:
                    importados += 1
                else:
                    erros.append(f"Erro ao importar {curso.get('Curso', 'desconhecido')}: {mensagem}")
            except Exception as e:
                erros.append(f"Erro ao importar {curso.get('Curso', 'desconhecido')}: {str(e)}")
        
        return importados, erros
    
    def get_resumo_validacao(self):
        """Retorna resumo da validação"""
        total = len(self.cursos_validos) + len(self.cursos_invalidos)
        return {
            'total': total,
            'validos': len(self.cursos_validos),
            'invalidos': len(self.cursos_invalidos),
            'erros': self.erros
        }


if __name__ == "__main__":
    importer = JSONImporter()
    print("JSON Importer pronto para uso!")
