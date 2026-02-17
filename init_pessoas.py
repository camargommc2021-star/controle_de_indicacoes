"""
Script para inicializar o arquivo de pessoas com dados de exemplo.

Cria o arquivo data/pessoas.xlsx com militares fictícios para teste.
"""

import os
from managers.pessoas_manager import PessoasManager


def criar_dados_exemplo():
    """
    Cria o arquivo de pessoas com dados de exemplo.
    
    Returns:
        True se criou com sucesso, False caso contrário
    """
    # Verificar se o arquivo já existe
    arquivo = "data/pessoas.xlsx"
    if os.path.exists(arquivo):
        print(f"Arquivo {arquivo} já existe.")
        resposta = input("Deseja recriar com dados de exemplo? (s/n): ")
        if resposta.lower() != 's':
            print("Operação cancelada.")
            return False
    
    # Inicializar o manager
    pm = PessoasManager(arquivo)
    
    # Dados de exemplo - Militares fictícios
    militares_exemplo = [
        {
            'Nome_Completo': 'JOÃO DA SILVA SANTOS',
            'Posto_Graduacao': '1S',
            'OM_Indicado': 'CRCEA-SE',
            'CPF': '123.456.789-00',
            'SARAM': '123456-7',
            'Email': 'joao.santos@fab.mil.br',
            'Telefone': '(11) 98765-4321',
            'Funcao_Atual': 'SUPERVISOR DO CRCEA-SE',
            'Data_Ultima_Promocao': '15/03/2020',
            'Tempo_Servico': '18 ANOS e 6 MESES'
        },
        {
            'Nome_Completo': 'MARIA FERNANDA OLIVEIRA LIMA',
            'Posto_Graduacao': 'SO',
            'OM_Indicado': 'APP-SP',
            'CPF': '987.654.321-00',
            'SARAM': '765432-1',
            'Email': 'maria.lima@fab.mil.br',
            'Telefone': '(11) 91234-5678',
            'Funcao_Atual': 'AUXILIAR DO APP-SP',
            'Data_Ultima_Promocao': '10/08/2022',
            'Tempo_Servico': '12 ANOS e 3 MESES'
        },
        {
            'Nome_Completo': 'CARLOS EDUARDO PEREIRA NETO',
            'Posto_Graduacao': '2S',
            'OM_Indicado': 'GCC',
            'CPF': '456.789.123-00',
            'SARAM': '456789-0',
            'Email': 'carlos.neto@fab.mil.br',
            'Telefone': '(61) 99876-5432',
            'Funcao_Atual': 'OPERADOR DO GCC',
            'Data_Ultima_Promocao': '20/11/2021',
            'Tempo_Servico': '8 ANOS e 9 MESES'
        },
        {
            'Nome_Completo': 'ANA CAROLINA MENDES ROCHA',
            'Posto_Graduacao': '3S',
            'OM_Indicado': 'CRCEA-SE',
            'CPF': '789.123.456-00',
            'SARAM': '789123-4',
            'Email': 'ana.rocha@fab.mil.br',
            'Telefone': '(11) 96543-2187',
            'Funcao_Atual': 'AUXILIAR DE SUPERVISÃO',
            'Data_Ultima_Promocao': '05/07/2023',
            'Tempo_Servico': '5 ANOS e 2 MESES'
        },
        {
            'Nome_Completo': 'ROBERTO ALVES FERREIRA',
            'Posto_Graduacao': 'CB',
            'OM_Indicado': 'DTCEA-SP',
            'CPF': '321.654.987-00',
            'SARAM': '321654-9',
            'Email': 'roberto.ferreira@fab.mil.br',
            'Telefone': '(11) 94321-8765',
            'Funcao_Atual': 'AUXILIAR TÉCNICO',
            'Data_Ultima_Promocao': '30/09/2019',
            'Tempo_Servico': '10 ANOS e 5 MESES'
        }
    ]
    
    print("Criando arquivo de pessoas com dados de exemplo...")
    print("-" * 50)
    
    sucessos = 0
    erros = []
    
    for militar in militares_exemplo:
        sucesso, mensagem = pm.adicionar_pessoa(militar)
        if sucesso:
            print(f"[OK] {militar['Posto_Graduacao']} {militar['Nome_Completo']}")
            sucessos += 1
        else:
            print(f"[ERRO] Erro ao adicionar {militar['Nome_Completo']}: {mensagem}")
            erros.append((militar['Nome_Completo'], mensagem))
    
    print("-" * 50)
    print(f"Total: {sucessos}/{len(militares_exemplo)} militares cadastrados")
    
    if erros:
        print("\nErros encontrados:")
        for nome, erro in erros:
            print(f"  - {nome}: {erro}")
    
    return sucessos > 0


if __name__ == "__main__":
    criar_dados_exemplo()
