import pandas as pd
import json

# Ler arquivo Excel da chefia
df = pd.read_excel('data/chefia.xlsx')

# Limpar dados - remover colunas unnamed e linhas vazias
df = df.drop(columns=[col for col in df.columns if 'Unnamed' in col], errors='ignore')
df = df.dropna(subset=['CURSO', 'NOME DO CURSO'], how='all')

# Criar estrutura do JSON
chefia_data = []
for _, row in df.iterrows():
    if pd.notna(row['CURSO']) and pd.notna(row['NOME DO CURSO']):
        chefia_data.append({
            'codigo_curso': str(row['CURSO']).strip(),
            'nome_curso': str(row['NOME DO CURSO']).strip(),
            'comando': str(row['SETOR RESPONSÁVEL']).strip() if pd.notna(row['SETOR RESPONSÁVEL']) else '',
            'setor_responsavel': str(row['SETOR RESPONSÁVEL.1']).strip() if pd.notna(row['SETOR RESPONSÁVEL.1']) else '',
            'nome_chefe': str(row['NOME']).strip() if pd.notna(row['NOME']) else '',
            'posto_chefe': str(row['POSTO']).strip() if pd.notna(row['POSTO']) else '',
            'funcao_chefe': str(row['FUNÇÃO']).strip() if pd.notna(row['FUNÇÃO']) else ''
        })

# Salvar JSON
with open('data/chefia.json', 'w', encoding='utf-8') as f:
    json.dump(chefia_data, f, ensure_ascii=False, indent=2)

print(f'JSON criado com {len(chefia_data)} registros')
print()
print('Primeiros 5 registros:')
for item in chefia_data[:5]:
    print(f"  {item['codigo_curso']}: {item['nome_curso'][:40]}...")
    print(f"    Chefe: {item['nome_chefe']} - {item['posto_chefe']}")
