# 📚 Controle de Cursos

Sistema web para gestão de cursos, com persistência via Excel e deploy no Streamlit Cloud.

## 🚀 Funcionalidades

- ✅ **CRUD Completo**: Cadastrar, editar e excluir cursos
- ✅ **Dashboard Interativo**: Visualização de prazos e estatísticas
- ✅ **Alertas Visuais**: Cores automáticas nos prazos (verde/amarelo/vermelho)
- ✅ **Persistência**: Dados salvos em Excel com sincronização GitHub opcional
- ✅ **Acesso Web**: Funciona em qualquer lugar via Streamlit Cloud
- 🔐 **Sistema de Login**: Autenticação com níveis de acesso (Admin/Editor/Viewer)
- 📅 **Calendário de Prazos**: Visualização mensal/semanal dos prazos dos cursos
- 👥 **Gestão de Usuários**: Administração de usuários e permissões

## 📋 Campos do Sistema

### Campos Base:
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
14. OM_Executora

## 🎨 Sistema de Cores nos Prazos

- 🟢 **Verde**: Mais de 5 dias para o prazo
- 🟡 **Amarelo**: 5 dias ou menos (alerta)
- 🔴 **Vermelho**: Prazo vencido

## 🔐 Sistema de Login

O sistema possui autenticação com 3 níveis de acesso:

| Nível | Permissões |
|-------|-----------|
| 🔴 **Admin** | Acesso total: CRUD completo + gestão de usuários + backups |
| 🟡 **Editor** | CRUD cursos, sem gerenciar usuários |
| 🟢 **Viewer** | Apenas visualização, sem edição |

### Credenciais Padrão

```
Usuário: admin
Senha:   admin123
```

⚠️ **IMPORTANTE**: Altere a senha padrão após o primeiro login!

### Recursos de Segurança

- Senhas com hash PBKDF2 + Salt
- Bloqueio automático após 5 tentativas falhas
- Logs de auditoria de acessos
- Controle de sessão

## 📅 Calendário de Prazos

Visualização em calendário dos prazos dos cursos:

- **Modo Mensal**: Visão geral do mês com indicadores de eventos
- **Modo Semanal**: Detalhamento da semana atual
- **Navegação**: Fácil navegação entre meses
- **Categorias de Eventos**:
  - 📋 Prazo SIAT (Laranja)
  - 👔 Prazo Chefia (Azul)
  - ✅ Conclusão (Verde)
  - 📨 Recebimento SIGAD (Cinza)

## 🚀 Como Usar

### Instalação Local

```bash
# Clone o repositório
git clone https://github.com/camargommc2021-star/controledeindica-es.git
cd controledeindica-es

# Instale as dependências
pip install -r requirements.txt

# Execute localmente
streamlit run app.py
```

Acesse: http://localhost:8501

## 🔧 Configuração do GitHub (Persistência Opcional)

Para salvar dados automaticamente no GitHub:

1. Gere um token no GitHub: Settings → Developer settings → Personal access tokens
2. No Streamlit Cloud, adicione como secret: `GITHUB_TOKEN`
3. Dados serão commitados automaticamente a cada alteração

Veja o guia em: [GITHUB_SETUP.md](GITHUB_SETUP.md)

## 📦 Dependências

- streamlit >= 1.28.0
- pandas >= 2.0.0, < 3.0
- openpyxl >= 3.1.0
- plotly >= 5.15.0
- python-dateutil >= 2.8.0
- PyGithub >= 2.1.0
- requests >= 2.31.0

## 📝 Estrutura de Arquivos

```
controledeindica-es/
├── app.py                    # Aplicativo principal
├── data_manager.py           # Gerenciamento de dados dos cursos
├── github_manager.py         # Persistência no GitHub
├── dashboard.py              # Visualizações
├── backup_manager.py         # Gerenciamento de backups
├── json_import.py            # Importação JSON
├── managers/
│   ├── auth_manager.py       # Sistema de autenticação
│   └── base_manager.py       # Classe base para managers
├── components/
│   ├── calendar_view.py      # Componente de calendário
│   ├── cards.py              # Cards de UI
│   ├── forms.py              # Formulários
│   ├── tables.py             # Tabelas
│   ├── alerts.py             # Alertas/toasts
│   └── sidebar.py            # Sidebar navigation
├── data/
│   ├── cursos.xlsx           # Dados dos cursos
│   ├── usuarios.xlsx         # Usuários do sistema
│   └── sessoes.xlsx          # Logs de acesso
├── requirements.txt          # Dependências
├── README.md                 # Este arquivo
└── GITHUB_SETUP.md           # Guia de configuração do GitHub
```

---

Desenvolvido com Python e Streamlit
