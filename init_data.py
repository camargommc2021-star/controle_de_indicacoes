import pandas as pd
import os

if __name__ == "__main__":
    # Criar pasta data se não existir
    os.makedirs('data', exist_ok=True)

    arquivo = 'data/cursos.xlsx'
    if not os.path.exists(arquivo):
        # Criar DataFrame vazio com as colunas corretas
        colunas = [
            'Curso', 'Turma', 'Vagas', 'Autorizados pelas escalantes', 'Prioridade',
            'Recebimento do SIGAD com as vagas', 'Numero do SIGAD', 'Estado',
            'DATA_DA_CONCLUSAO', 'Numero do SIGAD  encaminhando pra chefia',
            'Prazo dado pela chefia', 'Fim da indicação da SIAT', 'Notas',
            'OM_Executora'  # NOVO CAMPO para TCA 37-1
        ]

        df = pd.DataFrame(columns=colunas)
        df.to_excel(arquivo, index=False, engine='openpyxl')

        print("Arquivo data/cursos.xlsx criado com sucesso!")
        print(f"Total de colunas: {len(colunas)}")
        print("\nColunas criadas:")
        for i, col in enumerate(colunas, 1):
            print(f"  {i}. {col}")
    else:
        print("Arquivo data/cursos.xlsx já existe. Nenhuma alteração realizada.")
