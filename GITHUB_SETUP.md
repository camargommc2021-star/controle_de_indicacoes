# 🔧 Configuração do GitHub - Persistência de Dados

Este guia explica como configurar o token do GitHub para que seus dados sejam salvos permanentemente no repositório.

## 📋 O que você precisa

1. Conta no GitHub (você já tem: `camargommc2021-star`)
2. Repositório criado: `controledeindica-es` (você já tem)
3. Token de acesso pessoal do GitHub (vamos criar agora)

## 🔑 Passo 1: Criar Token do GitHub

1. Acesse: https://github.com/settings/tokens
2. Clique em **"Generate new token (classic)"**
3. Dê um nome: `Streamlit Controle de Cursos`
4. Selecione a validade (recomendo: **No expiration** ou 1 ano)
5. Marque as seguintes permissões (scopes):
   - ✅ `repo` (acesso completo aos repositórios)
   - ✅ `read:org` (opcional, mas recomendado)

6. Clique em **"Generate token"**
7. **⚠️ COPIE O TOKEN AGORA!** (ele só aparece uma vez)
   - Formato: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

## ☁️ Passo 2: Configurar no Streamlit Cloud

1. Acesse: https://share.streamlit.io/
2. Encontre seu app: `controledeindica-es`
3. Clique nos **três pontos** (⋯) → **Settings**
4. Vá para a seção **"Secrets"**
5. Clique em **"Add a new secret"**
6. Preencha:
   - **Key**: `GITHUB_TOKEN`
   - **Value**: Cole o token que você copiou no Passo 1
7. Clique em **Save**

## 🔄 Passo 3: Reiniciar o App

1. No Streamlit Cloud, clique em **"Manage app"**
2. Clique nos **três pontos** (⋯) → **Reboot**
3. Aguarde o app reiniciar (cerca de 1 minuto)

## ✅ Verificação

Após reiniciar, você verá no sidebar:
- ✅ **"GitHub conectado"** (em verde)
- A mensagem com seu usuário GitHub
- A data do último commit

Se aparecer **"GitHub não conectado"**, verifique:
1. Se o token foi copiado corretamente (sem espaços)
2. Se as permissões `repo` estão marcadas
3. Se salvou nos Secrets do Streamlit

## 📝 Como funciona?

- **Ao cadastrar/editar/excluir**: Dados salvos automaticamente no GitHub
- **Ao abrir o app**: Dados carregados automaticamente do GitHub
- **Histórico**: Todas as alterações ficam registradas no Git (commits)
- **Backup**: Seu arquivo Excel fica seguro no repositório

## 🆘 Problemas comuns

### "Token não configurado"
- Verifique se adicionou o secret `GITHUB_TOKEN` no Streamlit Cloud
- Reinicie o app após adicionar o secret

### "Erro de autenticação"
- O token pode ter expirado (crie um novo)
- Verifique se marcou a permissão `repo`
- Certifique-se de que o repositório é público ou você tem acesso

### "Erro 404 ao salvar"
- O arquivo será criado automaticamente no primeiro salvamento
- Não se preocupe, o app funciona mesmo sem o arquivo no GitHub inicialmente

### Dados não aparecem em outro dispositivo
- Verifique se o GitHub está conectado em todos os dispositivos
- Clique em "Sincronizar do GitHub" no sidebar
- Aguarde alguns segundos para o carregamento

## 🔄 Sincronização manual

Se precisar forçar a sincronização:
1. No sidebar, clique em **"🔄 Sincronizar do GitHub"**
2. Aguarde a mensagem de confirmação
3. Os dados serão atualizados imediatamente

## 📊 Ver histórico de alterações

Você pode ver todas as alterações no GitHub:
1. Acesse: https://github.com/camargommc2021-star/controledeindica-es
2. Vá para a pasta: `data/cursos.xlsx`
3. Clique em **"History"** para ver todos os commits
4. Cada commit mostra: data, autor e mensagem da alteração

---

**💡 Dica**: Guarde o token do GitHub em um local seguro (gerenciador de senhas). Se perder, você precisará criar um novo.

**🎉 Pronto!** Seus dados agora ficam salvos permanentemente no GitHub e são acessíveis de qualquer lugar!
