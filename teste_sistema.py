import sys
sys.path.append('.')

from data_manager import DataManager
from datetime import datetime

# Criar instância do DataManager
dm = DataManager(usar_github=False)

# Criar curso de teste
curso_teste = {
    'Curso': 'Curso de Teste - Python Avancado',
    'Turma': 'Turma A - 2026',
    'Vagas': 25,
    'Autorizados pelas escalantes': '10',
    'Prioridade': 'Alta',
    'Recebimento do SIGAD com as vagas': '15/01/2026',
    'Numero do SIGAD': '12345/2026',
    'Estado': 'solicitar voluntarios',
    'DATA DA CONCLUSÃO': '',
    'Numero do SIGAD  encaminhando pra chefia': '',
    'Prazo dado pela chefia': '20/02/2026',
    'Fim da indicação da SIAT': '25/02/2026',
    'Notas': 'Curso de teste criado automaticamente'
}

# Adicionar curso
sucesso, mensagem = dm.adicionar_curso(curso_teste)

if sucesso:
    print("SUCESSO!")
    print("Mensagem: Curso cadastrado com sucesso")
    print("\nDados atuais:")
    df = dm.carregar_dados()
    print(f"Total de cursos: {len(df)}")
    if len(df) > 0:
        print("\nUltimo curso adicionado:")
        print(df.iloc[-1].to_string())
else:
    print("ERRO!")
    print("Mensagem: Erro ao cadastrar")
