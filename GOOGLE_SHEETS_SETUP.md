# 📊 Configuração Segura do Google Sheets

Guia para configurar a integração com Google Sheets na aba "Confecção de FIC" com **máxima segurança**.

## 🎯 Objetivo

A aba **Confecção de FIC** busca dados diretamente do Google Sheets com:
- ✅ Sem armazenamento local de informações sensíveis
- ✅ Criptografia de campos protegidos (CPF, SARAM)
- ✅ Logs anonimizados
- ✅ Autenticação segura via Streamlit Secrets

## ⚠️ IMPORTANTE - Leia Antes

Este sistema lida com **dados sensíveis de militares** (CPF, SARAM). Siga rigorosamente estas instruções de segurança.

---

## 🔒 Medidas de Segurança Implementadas

### 1. **Não Persistência**
- Dados carregados apenas em memória (RAM)
- Sem armazenamento em disco
- Limpo automaticamente ao fechar a página

### 2. **Criptografia**
- Campos sensíveis são protegidos
- Hashes usados para referência em logs
- Mascaramento na interface

### 3. **Acesso Seguro**
- Apenas Streamlit Secrets (nunca arquivo local)
- Service Account com permissão apenas de LEITURA
- Timeout e rate limiting

---

---

## 📋 Passo 1: Criar a Planilha

1. Acesse [Google Sheets](https://sheets.google.com)
2. Crie uma nova planilha
3. Adicione as colunas na primeira linha:

| Codigo | Nome | Posto | Especialidade | OM | SARAM | CPF | Email | Telefone |
|--------|------|-------|---------------|----|-------|-----|-------|----------|
| 001 | João Silva | 1S | TEC | CRCEA-SE | 1234567 | 12345678901 | joao@fab.mil.br | (11) 99999-9999 |
| 002 | Maria Santos | SO | ADM | CRCEA-SE | 7654321 | 98765432100 | maria@fab.mil.br | (11) 98888-8888 |

---

## 🔐 Passo 2: Configurar API do Google (Service Account)

### 2.1 Criar Projeto no Google Cloud

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Clique no seletor de projetos (topo) → **Novo Projeto**
3. Digite um nome (ex: `controle-cursos-fic`) e clique em **Criar**

### 2.2 Ativar Google Sheets API

1. No menu lateral, vá em **APIs e Serviços** → **Biblioteca**
2. Pesquise por **Google Sheets API**
3. Clique e depois em **Ativar**

### 2.3 Criar Conta de Serviço

1. Vá em **APIs e Serviços** → **Credenciais**
2. Clique em **Criar Credenciais** → **Conta de serviço**
3. Preencha:
   - **Nome da conta de serviço**: `fic-reader`
   - **Descrição**: `Leitura de dados para FIC`
4. Clique em **Criar e Continuar**
5. Em **Permissões**, pule (não necessário)
6. Clique em **Concluir**

### 2.4 Gerar Chave JSON

1. Na lista de contas de serviço, clique em **fic-reader**
2. Vá na aba **Chaves**
3. Clique em **Adicionar Chave** → **Criar nova chave**
4. Selecione **JSON** e clique em **Criar**
5. O arquivo será baixado automaticamente

---

## 🔗 Passo 3: Compartilhar Planilha

1. Abra o arquivo JSON baixado
2. Copie o email da conta de serviço (campo `client_email`)
   - Exemplo: `fic-reader@controle-cursos.iam.gserviceaccount.com`
3. No Google Sheets, clique em **Compartilhar**
4. Cole o email e dê permissão de **Leitor** (ou Editor)
5. Clique em **Enviar**

---

## 💻 Passo 4: Configurar no Sistema

### Opção A: Arquivo Local (Desenvolvimento)

1. Na pasta do projeto, crie a pasta `credentials/`
2. Copie o arquivo JSON baixado para:
   ```
   controle de cursos/
   └── credentials/
       └── google-sheets-credentials.json
   ```

### Opção B: Streamlit Cloud (Produção)

1. Acesse seu app no [Streamlit Cloud](https://share.streamlit.io)
2. Vá em **Settings** → **Secrets**
3. Adicione o conteúdo do arquivo JSON:
   ```toml
   [gcp_service_account]
   type = "service_account"
   project_id = "seu-projeto-id"
   private_key_id = "..."
   private_key = "..."
   client_email = "fic-reader@..."
   client_id = "..."
   auth_uri = "https://accounts.google.com/o/oauth2/auth"
   token_uri = "https://oauth2.googleapis.com/token"
   ```

---

## 🆔 Passo 5: Obter ID da Planilha

1. Abra sua planilha no Google Sheets
2. Olhe o URL:
   ```
   https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit#gid=0
   ```
3. O ID é a parte entre `/d/` e `/edit`:
   ```
   1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
   ```

---

## ✅ Testando

1. Execute o sistema:
   ```bash
   streamlit run app.py
   ```

2. Faça login e vá na aba **📄 Confecção de FIC**

3. Clique em **⚙️ Configuração do Google Sheets**

4. Cole o **ID da Planilha** no campo indicado

5. Digite um **código** existente na planilha

6. Clique em **Buscar**

7. Se tudo estiver correto, os dados aparecerão para edição

---

## 🔒 Segurança

- ✅ Os dados são lidos **diretamente** do Google Sheets
- ✅ **Nenhuma** informação é armazenada localmente
- ✅ O arquivo JSON de credenciais **nunca** é exposto
- ✅ Apenas **leitura** é necessária (recomendado)

---

## 🐛 Solução de Problemas

### "gspread não instalado"
```bash
pip install gspread google-auth
```

### "Credenciais não encontradas"
- Verifique se o arquivo JSON está em `credentials/google-sheets-credentials.json`
- Ou configure as secrets no Streamlit Cloud

### "Spreadsheet ID não configurado"
- Copie o ID correto da URL da planilha
- Cole no campo de configuração na aba FIC

### "Código não encontrado"
- Verifique se o código existe na coluna "Codigo"
- Verifique se a planilha está compartilhada com o email da service account

### Erro de permissão
- Certifique-se de que a planilha está compartilhada com o email da service account
- Verifique se a API do Google Sheets está ativada

---

## 📞 Suporte

Em caso de dúvidas, verifique:
1. Logs do sistema (menu lateral → Logs)
2. Permissões da planilha
3. Status da API no Google Cloud Console
