# 📚 Controle de Indicações 2026

Sistema web para gestão de cursos e indicações, com persistência via Excel e deploy no Streamlit Cloud.

## 🚀 Funcionalidades

- ✅ **CRUD Completo**: Cadastrar, editar e excluir cursos
- ✅ **Dashboard Interativo**: Visualização de prazos e estatísticas
- ✅ **Alertas Visuais**: Cores automáticas nos prazos (verde/amarelo/vermelho)
- ✅ **Persistência**: Dados salvos em Excel no GitHub
- ✅ **Acesso Web**: Funciona em qualquer lugar via Streamlit Cloud
- 🔐 **Sistema de Login** (v2.0): Autenticação com níveis de acesso
- 📅 **Calendário de Prazos** (v2.0): Visualização mensal/semanal dos prazos
- 👥 **Gestão de Usuários** (v2.0): Administração de usuários e permissões

## 📋 Campos do Sistema

### Campos Base (14 campos):
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
14. **OM_Executora** (NOVO - para TCA 37-1)


## 🎨 Sistema de Cores nos Prazos

- 🟢 **Verde**: Mais de 5 dias para o prazo
- 🟡 **Amarelo**: 5 dias ou menos (alerta)
- 🔴 **Vermelho**: Prazo vencido

## 🔐 Sistema de Login (v2.0)

O sistema possui autenticação com 3 níveis de acesso:

| Nível | Permissões |
|-------|-----------|
| 🔴 **Admin** | Acesso total: CRUD completo + gestão de usuários + backups |
| 🟡 **Editor** | CRUD cursos e pessoas, sem gerenciar usuários |
| 🟢 **Viewer** | Apenas visualização, sem edição |

### Credenciais Padrão

```
Usuário: admin
Senha:   admin123
```

⚠️ **IMPORTANTE**: Altere a senha padrão após o primeiro login!

### Recursos de Segurança

- Senhas criptografadas com PBKDF2 + Salt
- Bloqueio automático após 5 tentativas falhas
- Logs de auditoria de acessos
- Controle de sessão

## 📅 Calendário de Prazos (v2.0)

Visualização em calendário dos prazos:

- **Modo Mensal**: Visão geral do mês com indicadores de eventos
- **Modo Semanal**: Detalhamento da semana atual
- **Navegação**: Fácil navegação entre meses
- **Categorias de Eventos**:
  - 📋 Prazo SIAT (Laranja)
  - 👔 Prazo Chefia (Azul)
  - ✅ Conclusão (Verde)
  - 📄 FIC (Roxo)
  - 📨 Recebimento SIGAD (Cinza)

## 🚀 Como Usar

### Opção 1: Deploy no Streamlit Cloud (Recomendado)

1. **Faça upload do código para o GitHub:**
   ```bash
   git add .
   git commit -m "Sistema Controle de Cursos v1.0 - Campos opcionais"
   git push origin main
   ```

2. **Configure o GitHub Token:**
   - Veja o guia completo em: [GITHUB_SETUP.md](GITHUB_SETUP.md)
   - Crie um token em: https://github.com/settings/tokens
   - Adicione no Streamlit Cloud: Settings → Secrets → GITHUB_TOKEN

3. **Acesse seu app:**
   - URL: https://share.streamlit.io/camargommc2021-star/controledeindica-es

### Opção 2: Instalação Local (Testes)

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
- plotly >= 5.15.0
- python-dateutil >= 2.8.0
- PyGithub >= 2.1.0
- requests >= 2.31.0
- cryptography >= 41.0.0  # Criptografia de senhas e dados sensíveis
- gspread >= 5.10.0       # Integração Google Sheets
- google-auth >= 2.22.0   # Autenticação Google

## 📝 Estrutura de Arquivos

```
controledeindica-es/
├── app.py                    # Aplicativo principal
├── app_v2.py                 # Versão 2.0 com login e calendário
├── data_manager.py           # Gerenciamento de dados
├── github_manager.py         # Persistência no GitHub
├── dashboard.py              # Visualizações
├── managers/
│   ├── auth_manager.py       # Sistema de autenticação (v2.0)
│   ├── base_manager.py       # Classe base para managers
│   ├── pessoas_manager.py    # Gestão de pessoas
│   └── pessoas_manager_secure.py  # Gestão segura com criptografia
├── components/
│   ├── calendar_view.py      # Componente de calendário (v2.0)
│   ├── cards.py              # Cards de UI
│   ├── forms.py              # Formulários
│   ├── tables.py             # Tabelas
│   ├── alerts.py             # Alertas/toasts
│   └── sidebar.py            # Sidebar navigation
├── data/
│   ├── cursos.xlsx           # Dados dos cursos
│   ├── pessoas.xlsx          # Dados das pessoas (v2.0)
│   ├── fics.xlsx             # Dados dos FICs
│   ├── usuarios.xlsx         # Usuários do sistema (v2.0)
│   └── sessoes.xlsx          # Logs de acesso (v2.0)
├── requirements.txt          # Dependências
├── README.md                 # Este arquivo
├── GITHUB_SETUP.md           # Guia de configuração do GitHub
└── atualizar_v2.bat          # Script de atualização para v2.0
```

## 🆘 Suporte

Em caso de problemas:
1. Verifique se o arquivo `data/cursos.xlsx` existe
2. Confira as permissões de escrita na pasta `data/`
3. Verifique os logs do Streamlit Cloud

## 📅 Atualizações

- **v1.0**: Sistema inicial com todas as funcionalidades básicas
- **v1.1**: Persistência automática no GitHub via API
- **v2.0** (Atual): 
  - 🔐 Sistema de Login com níveis de acesso (Admin/Editor/Viewer)
  - 📅 Visualização em Calendário dos prazos
  - 👥 Gestão de Usuários para administradores
  - 🔒 Criptografia de senhas com PBKDF2
  - 📝 Logs de auditoria de acessos

---

Desenvolvido com ❤️ usando Python e Streamlit
