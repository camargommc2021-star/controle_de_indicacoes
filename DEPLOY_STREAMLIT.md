# 🚀 Guia Rápido - Deploy no Streamlit Cloud

## ⚡ MÉTODO ULTRA RÁPIDO (2 minutos)

### Passo 1: Acessar
- Abra: https://share.streamlit.io/
- Clique em **"Sign in with GitHub"**

### Passo 2: Criar App
- Clique em **"New app"**
- Preencha:
  - **Repository:** `camargommc2021-star/controle_de_indicacoes`
  - **Branch:** `main`
  - **Main file:** `app.py`
  - **URL:** `controle-cursos-crcea` (ou escolha outro)
- Clique **"Deploy!"**

### Passo 3: Configurar Secrets (IMPORTANTE!)
1. Espere o app abrir (vai dar erro inicial, normal!)
2. Clique nos **3 pontinhos ⋮** (canto superior direito)
3. Clique em **"Settings"**
4. No menu lateral, clique em **"Secrets"**
5. Cole TODO o conteúdo do arquivo `.streamlit/secrets.toml`
6. **IMPORTANTE:** Troque `COLE_AQUI_O_ID_DA_PLANILHA` pelo ID real da sua planilha
7. Clique **"Save"**

### Passo 4: Reiniciar
- Volte para o app
- Clique nos **3 pontinhos ⋮** > **"Reboot"**

✅ Pronto! Seu app estará online!

---

## 🔧 Como encontrar o ID da planilha Google Sheets

1. Abra sua planilha no Google Sheets
2. Olhe a URL: `https://docs.google.com/spreadsheets/d/1ABC123xyz/edit`
3. O ID é a parte entre `/d/` e `/edit`
4. Copie e cole no secrets

---

## 🆘 Se der erro

### Erro "Module not found"
- Verifique se `requirements.txt` está no repositório ✅ (já está!)

### Erro de conexão com Google Sheets
- Verifique se as credenciais estão corretas no Secrets
- Verifique se o ID da planilha está correto

### Erro 404
- Verifique se o repositório é público ou se deu acesso ao Streamlit

---

## 📱 URL Final
Seu app será acessível em:
`https://controle-cursos-crcea.streamlit.app`
(Ou o nome que você escolheu no passo 2)
