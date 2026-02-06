import sys
sys.path.append('.')

from data_manager import DataManager

print("Testando sistema...")
print("-" * 50)

try:
    dm = DataManager(usar_github=False)
    print("DataManager: OK")
    
    # Testar salvamento com campos vazios
    curso_vazio = {
        'Curso': 'Teste Campos Vazios',
        'Turma': '',
        'Vagas': 0,
        'Autorizados pelas escalantes': '',
        'Prioridade': '',
        'Recebimento do SIGAD com as vagas': '',
        'Numero do SIGAD': '',
        'Estado': '',
        'DATA DA CONCLUSÃO': '',
        'Numero do SIGAD  encaminhando pra chefia': '',
        'Prazo dado pela chefia': '',
        'Fim da indicação da SIAT': '',
        'Notas': ''
    }
    
    sucesso, mensagem = dm.adicionar_curso(curso_vazio)
    
    if sucesso:
        print(f"Salvamento: OK - Curso salvo com sucesso")
        df = dm.carregar_dados()
        print(f"Total de cursos: {len(df)}")
        print("-" * 50)
        print("Sistema funcionando corretamente!")
        print("Agora pode executar: streamlit run app.py")
    else:
        print(f"Erro: {mensagem}")
        
except Exception as e:
    print(f"ERRO: {str(e)}")
    import traceback
    traceback.print_exc()
