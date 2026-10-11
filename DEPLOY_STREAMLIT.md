# 🚀 Guia Rápido - Deploy no Streamlit Cloud

## ⚡ Passos para Deploy

### Passo 1: Acessar o Streamlit Cloud
- Abra: https://share.streamlit.io/
- Faça login com sua conta do GitHub

### Passo 2: Criar App
- Clique em **"New app"**
- Preencha:
  - **Repository:** `camargommc2021-star/controle_de_indicacoes`
  - **Branch:** `main`
  - **Main file:** `app.py`
  - **URL:** escolha o subdomínio desejado
- Clique em **"Deploy!"**

### Passo 3: Configurar Secrets (Opcional - Sincronização GitHub)
1. Nos **Settings** do app, acesse a aba **"Secrets"**
2. Se desejar sincronização com o GitHub, configure:
   ```toml
   GITHUB_TOKEN = "seu_token_aqui"
   GITHUB_REPO = "camargommc2021-star/controle_de_indicacoes"
   ```
3. Clique em **"Save"**

---

## 🆘 Solução de Problemas

### Erro "Module not found"
- Verifique se as dependências necessárias estão listadas em `requirements.txt`.

### Erro 404
- Verifique se o repositório é público ou se concedeu permissão ao Streamlit Cloud.
