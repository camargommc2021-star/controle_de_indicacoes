# 🔒 Guia de Segurança

Este documento descreve as medidas de segurança implementadas para proteger dados sensíveis de militares.

---

## 🛡️ Resumo de Segurança

O sistema implementa **múltiplas camadas de proteção** para garantir que dados sensíveis (CPF, SARAM, etc.) nunca sejam comprometidos.

### Camadas de Proteção

1. **Não Persistência**
   - Dados carregados apenas em memória (RAM)
   - Sem armazenamento em disco local
   - Cache temporário com expiração

2. **Criptografia**
   - Campos sensíveis criptografados em trânsito
   - Hashes para referência em logs
   - Sem exposição em texto claro

3. **Controle de Acesso**
   - Autenticação obrigatória
   - Níveis de permissão (Admin/Editor/Viewer)
   - Logs de auditoria

4. **Comunicação Segura**
   - Apenas HTTPS
   - Timeout nas requisições
   - Rate limiting

---

## 📋 Checklist de Segurança para Deploy

### Antes de colocar em produção:

- [ ] **Credenciais Google Cloud**
  - [ ] Service Account criada apenas para LEITURA
  - [ ] Chave JSON não está em arquivo local
  - [ ] Configurada em Streamlit Secrets
  - [ ] Email da Service Account anotado

- [ ] **Google Sheets**
  - [ ] Planilha criada com estrutura correta
  - [ ] Compartilhada APENAS com a Service Account
  - [ ] Sem acesso público
  - [ ] Backup configurado (opcional)

- [ ] **Streamlit Secrets** (`/.streamlit/secrets.toml`)
  ```toml
  [gcp_service_account]
  type = "service_account"
  project_id = "seu-projeto-id"
  private_key_id = "..."
  private_key = "-----BEGIN PRIVATE KEY-----\n..."
  client_email = "sua-conta@projeto.iam.gserviceaccount.com"
  client_id = "..."
  auth_uri = "https://accounts.google.com/o/oauth2/auth"
  token_uri = "https://oauth2.googleapis.com/token"
  
  SHEETS_SPREADSHEET_ID = "id-da-planilha"
  ```

- [ ] **Ambiente**
  - [ ] HTTPS obrigatório
  - [ ] Sem DEBUG mode em produção
  - [ ] Logs sendo monitorados
  - [ ] Política de senhas forte ativada

---

## 🔐 Detalhes Técnicos de Segurança

### 1. Gestão de Credenciais

```python
# ✅ CORRETO - Usar Streamlit Secrets
credentials = st.secrets['gcp_service_account']

# ❌ ERRADO - Arquivo local
with open('credentials.json') as f:  # NUNCA FAÇA ISSO
    credentials = json.load(f)
```

### 2. Logs Seguros

```python
# ✅ CORRETO - Hash em vez de dados reais
logger.info(f"Usuário encontrado: hash={cpf_hash[:8]}...")

# ❌ ERRADO - Nunca logue dados sensíveis
logger.info(f"CPF: {cpf}")  # NUNCA FAÇA ISSO
```

### 3. Mascaramento de Dados

| Dado Real | Exibição | Uso |
|-----------|----------|-----|
| 12345678901 | 12****901 | Interface |
| 4379470 | 43****70 | Interface |
| email@fab.mil.br | em***@fab.mil.br | Logs |
| (11) 99999-9999 | *****9999 | Interface |

### 4. Ciclo de Vida dos Dados

```
┌─────────────────────────────────────────────────────────────┐
│  1. Usuário digita código                                   │
│     └─> Validado e sanitizado                              │
│                                                             │
│  2. Busca no Google Sheets                                  │
│     └─> Conexão HTTPS apenas                               │
│     └─> Timeout 10s                                        │
│     └─> Rate limited                                       │
│                                                             │
│  3. Dados em memória (RAM)                                  │
│     └─> Objeto DadosPessoaSegura                           │
│     └─> Campos sensíveis em atributos privados             │
│     └─> Duração: sessão apenas                             │
│                                                             │
│  4. Exibição                                                │
│     └─> Mascaramento padrão                                │
│     └─> Revelar completo apenas com clique                 │
│                                                             │
│  5. Geração FIC                                             │
│     └─> Template Word preenchido                           │
│     └─> Download direto                                    │
│                                                             │
│  6. Limpeza                                                 │
│     └─> __del__() limpa memória                           │
│     └─> Session state limpo                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚨 Procedimentos de Incidente

### Se suspeitar de vazamento:

1. **Imediato**
   ```bash
   # Revogar acesso
   # Google Cloud Console > IAM > Service Accounts > Desativar
   ```

2. **Auditoria**
   - Verificar logs de acesso
   - Identificar IPs/horários suspeitos
   - Verificar downloads de FIC

3. **Correção**
   - Gerar nova Service Account
   - Atualizar secrets
   - Notificar gestores de segurança

---

## 📊 Comparação de Segurança

| Aspecto | Versão Antiga | Versão Segura (Atual) |
|---------|---------------|----------------------|
| Armazenamento CPF/SARAM | Excel local criptografado | Google Sheets + memória apenas |
| Persistência | Sim (arquivos Excel) | Não (apenas RAM) |
| Logs | Com dados sensíveis | Hashes apenas |
| Acesso credenciais | Arquivo local | Streamlit Secrets apenas |
| Transmissão | HTTP possível | HTTPS obrigatório |
| Timeout | Não | 10 segundos |
| Rate limiting | Não | 1 req/segundo |

---

## 📝 Política de Senhas

Para usuários do sistema:

- Mínimo 8 caracteres
- Pelo menos 1 letra maiúscula
- Pelo menos 1 número
- Pelo menos 1 caractere especial
- Troca a cada 90 dias
- Sem reutilização das últimas 5 senhas

---

## 🔄 Rotação de Chaves

Recomenda-se rotacionar chaves periodicamente:

- **Service Account Key**: A cada 6 meses
- **Senhas de usuários**: A cada 3 meses
- **Streamlit Secrets**: Revisão mensal

---

## 📞 Contatos de Segurança

Em caso de vulnerabilidade:

1. **Não divulgue publicamente**
2. Documente o problema
3. Contate o administrador do sistema
4. Aguarde correção antes de divulgar

---

## ✅ Validação de Segurança

Para verificar se o sistema está seguro, acesse a aba **Confecção de FIC** e verifique:

- O banner verde "Modo Seguro Ativado" aparece
- O status mostra "Nível: 🟢 ALTO"
- Os campos sensíveis aparecem mascarados
- Os logs não mostram dados em texto claro

Se algum desses itens falhar, **não use o sistema** e contate o administrador.

---

**Última atualização:** 10/02/2026  
**Versão:** 2.0-SECURE  
**Classificação:** USO OFICIAL
