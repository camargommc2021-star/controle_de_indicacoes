# 📚 Controle de Indicações 2026

Sistema web para gestão de cursos e indicações, com persistência via Excel e deploy no Streamlit Cloud.

## 🚀 Funcionalidades

- ✅ **CRUD Completo**: Cadastrar, editar e excluir cursos
- ✅ **Importação de PDF**: Extrai cursos automaticamente de arquivos PDF
- ✅ **Dashboard Interativo**: Visualização de prazos e estatísticas
- ✅ **Alertas Visuais**: Cores automáticas nos prazos (verde/amarelo/vermelho)
- ✅ **Persistência**: Dados salvos em Excel no GitHub
- ✅ **Acesso Web**: Funciona em qualquer lugar via Streamlit Cloud

## 📋 Campos do Sistema

1. Curso
2. Turma
3. Vagas
4. Autorizados pelas escalantes
5. Prioridade (Alta/Média/Baixa)
6. Recebimento do SIGAD com as vagas
7. Número do SIGAD
8. Estado (solicitar voluntários/fazer indicação/Concluído/ver vagas escalantes)
9. DATA DA CONCLUSÃO (auto preenchida)
10. Número do SIGAD encaminhando pra chefia
11. Prazo dado pela chefia
12. Fim da indicação da SIAT
13. Notas

## 🎨 Sistema de Cores nos Prazos

- 🟢 **Verde**: Mais de 5 dias para o prazo
- 🟡 **Amarelo**: 5 dias ou menos (alerta)
- 🔴 **Vermelho**: Prazo vencido

## 🚀 Como Usar

### 1. Instalação Local (Desenvolvimento)

```bash
# Clone o repositório
git clone https://github.com/camargommc2021-star/controledeindica-es.git
cd controledeindica-es

# Instale as dependências
pip install -r requirements.txt

# Execute localmente
streamlit run app.py
```

### 2. Deploy no Streamlit Cloud

1. Faça push deste código para o repositório GitHub
2. Acesse [Streamlit Cloud](https://streamlit.io/cloud)
3. Conecte seu repositório GitHub
4. Deploy automático!

## 📄 Importação de PDF

O sistema extrai automaticamente cursos de PDFs com formato:
```
Curso: Nome do Curso
Data: 15/01/2026
Turma: Turma A
SIGAD: 12345/2026
...
```

## 🔧 Configuração do GitHub (Persistência)

Para salvar dados automaticamente no GitHub:

1. Gere um token no GitHub: Settings → Developer settings → Personal access tokens
2. No Streamlit Cloud, adicione como secret: `GITHUB_TOKEN`
3. Dados serão commitados automaticamente a cada alteração

**📖 Veja o guia completo em:** [GITHUB_SETUP.md](GITHUB_SETUP.md)

## 📦 Dependências

- streamlit >= 1.28.0
- pandas >= 2.0.0
- openpyxl >= 3.1.0
- pdfplumber >= 0.9.0
- plotly >= 5.15.0
- python-dateutil >= 2.8.0
- PyGithub >= 2.1.0
- requests >= 2.31.0

## 📝 Estrutura de Arquivos

```
controledeindica-es/
├── app.py                 # Aplicativo principal
├── data_manager.py        # Gerenciamento de dados
├── github_manager.py      # Persistência no GitHub
├── pdf_extractor.py       # Extração de PDFs
├── dashboard.py          # Visualizações
├── requirements.txt      # Dependências
├── README.md            # Este arquivo
├── GITHUB_SETUP.md      # Guia de configuração do GitHub
└── data/
    └── cursos.xlsx       # Arquivo de dados (sincronizado com GitHub)
```

## 🆘 Suporte

Em caso de problemas:
1. Verifique se o arquivo `data/cursos.xlsx` existe
2. Confira as permissões de escrita na pasta `data/`
3. Verifique os logs do Streamlit Cloud

## 📅 Atualizações

- **v1.0**: Sistema inicial com todas as funcionalidades básicas
- **v1.1**: Persistência automática no GitHub via API
- Próximas: Melhorias na extração de PDF

---

Desenvolvido com ❤️ usando Python e Streamlit
