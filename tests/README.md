# Suite de Testes - Sistema de Controle de Cursos

Esta pasta contém a suite completa de testes unitários para o projeto.

## 📁 Estrutura

```
tests/
├── __init__.py              # Pacote de testes
├── conftest.py              # Configurações e fixtures do pytest
├── pytest.ini               # Configurações do pytest
├── run_tests.py             # Script para executar testes
├── README.md                # Este arquivo
├── data/                    # Diretório para arquivos temporários
│   └── __init__.py
├── test_validators.py       # Testes para utils/validators.py
├── test_config.py           # Testes para config.py
├── test_data_manager.py     # Testes para data_manager.py
├── test_fic_manager.py      # Testes para fic_manager.py
├── test_base_manager.py     # Testes para managers/base_manager.py
├── test_github_manager.py   # Testes mockados para github_manager.py
├── test_dashboard.py        # Testes para dashboard.py
└── test_backup_manager.py   # Testes para backup_manager.py
```

## 🚀 Executando os Testes

### Todos os testes
```bash
pytest tests/
```

### Usando o script
```bash
python tests/run_tests.py
```

### Teste específico
```bash
pytest tests/test_config.py
```

### Com cobertura
```bash
pytest tests/ --cov=. --cov-report=term-missing
```

### Modo verboso
```bash
pytest tests/ -vv
```

### Mostrar saída dos prints
```bash
pytest tests/ -s
```

## 📝 Categorias de Testes

### Testes Unitários (`test_*.py`)
Testam unidades individuais do código:
- **Validators**: Validação de dados (CPF, datas, e-mails, etc.)
- **Config**: Constantes e configurações
- **DataManager**: Operações CRUD de cursos
- **FICManager**: Operações CRUD de FICs
- **BaseManager**: Funcionalidades base dos managers
- **GitHubManager**: Integração com GitHub (mockada)
- **Dashboard**: Geração de resumos e métricas
- **BackupManager**: Criação e restauração de backups

## 🛠️ Fixtures Principais (`conftest.py`)

### Fixtures de Ambiente
- `temp_dir`: Diretório temporário isolado
- `clean_test_data`: Limpa arquivos de teste automaticamente

### Fixtures de Dados
- `sample_curso_data`: Dados de exemplo para um curso
- `sample_curso_list`: Lista de cursos de exemplo
- `sample_fic_data`: Dados de exemplo para uma FIC
- `sample_fic_list`: Lista de FICs de exemplo
- `sample_dataframe`: DataFrame de exemplo

### Fixtures de Managers
- `temp_data_manager`: DataManager com diretório temporário
- `temp_fic_manager`: FICManager com diretório temporário
- `temp_backup_manager`: BackupManager com diretório temporário
- `mock_github_manager`: Mock do GitHubManager

## 🔍 Boas Práticas

1. **Isolamento**: Cada teste é isolado e não depende de outros
2. **Independência**: Testes não dependem de recursos externos (usam mocks)
3. **Limpeza**: Arquivos temporários são criados em `tests/data/` e limpos automaticamente
4. **Mocking**: APIs externas (GitHub) são sempre mockadas

## 📊 Cobertura

Para gerar relatório de cobertura:
```bash
pytest tests/ --cov=. --cov-report=html
```

O relatório HTML será gerado em `htmlcov/index.html`.

## 🐛 Debug

Para debugar um teste específico:
```bash
pytest tests/test_data_manager.py::TestAdicionarCurso::test_adicionar_curso_sucesso -v --pdb
```

## 📝 Adicionando Novos Testes

1. Crie o arquivo `tests/test_novo_modulo.py`
2. Importe o módulo a ser testado
3. Crie uma classe de teste por funcionalidade
4. Use fixtures do `conftest.py` quando disponíveis
5. Execute os testes para verificar

Exemplo:
```python
# tests/test_novo_modulo.py
import pytest
from novo_modulo import minha_funcao

class TestMinhaFuncao:
    def test_comportamento_esperado(self):
        resultado = minha_funcao("entrada")
        assert resultado == "esperado"
    
    def test_com_fixture(self, sample_curso_data):
        resultado = minha_funcao(sample_curso_data)
        assert resultado is not None
```
