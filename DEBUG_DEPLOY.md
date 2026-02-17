# 🔧 Guia de Debug - Deploy no VPS

## ❌ Problema: Deploy não está funcionando

## ✅ Verificações Rápidas

### 1. Teste a conexão SSH manualmente

No seu computador local, execute:

```bash
# Teste com a chave SSH (substitua pelo caminho correto)
ssh -i ~/.ssh/sua_chave_privada seu_usuario@seu_ip_vps

# Ou se estiver usando senha
ssh seu_usuario@seu_ip_vps
```

### 2. Verifique se Docker está instalado no VPS

Conectado no VPS, execute:

```bash
docker --version
docker compose version
```

Se não estiver instalado:
```bash
# Instalar Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker
```

### 3. Verifique a rede "proxy"

```bash
docker network ls | grep proxy
```

Se não existir, crie:
```bash
docker network create proxy
```

### 4. Verifique permissões do diretório

```bash
ls -la /srv/docker/
sudo mkdir -p /srv/docker/controle-indicacoes
sudo chown -R $USER:$USER /srv/docker/controle-indicacoes
```

### 5. Teste o deploy manualmente no VPS

```bash
cd /srv/docker/controle-indicacoes

# Se não existir, clone
if [ ! -d ".git" ]; then
  git clone https://github.com/camargommc2021-star/controle_de_indicacoes.git .
fi

# Atualize
git pull origin main

# Build e rode
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d

# Veja os logs
docker compose -f docker-compose.prod.yml logs -f
```

---

## 🔍 Verificar Secrets no GitHub

Vá em: `Settings > Secrets and variables > Actions`

Certifique-se de que existem:
- ✅ `VPS_HOST` - IP ou domínio do servidor
- ✅ `VPS_USER` - Usuário SSH (ex: root, ubuntu, deploy)
- ✅ `VPS_SSH_KEY` - Chave SSH **PRIVADA** completa

### Formato correto da chave SSH:

```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACB(...resto da chave...)
-----END OPENSSH PRIVATE KEY-----
```

⚠️ **Importante:** 
- A chave deve incluir as linhas `-----BEGIN...` e `-----END...`
- Deve ter uma quebra de linha no final
- Não deve ter espaços extras no início/fim

---

## 🚀 Usando os Workflows de Debug

### Testar conexão SSH:

1. Vá em **Actions** no GitHub
2. Selecione **"Test SSH Connection"**
3. Clique em **"Run workflow"**
4. Veja os logs para identificar o erro

### Deploy com debug:

1. Vá em **Actions** no GitHub  
2. Selecione **"Deploy to VPS"**
3. Clique em **"Run workflow"**
4. Acompanhe os logs detalhados

---

## 🐛 Erros Comuns

### Erro: `permission denied (publickey)`
- A chave SSH privada está incorreta ou incompleta
- O usuário não tem a chave pública no `~/.ssh/authorized_keys` do VPS

### Erro: `docker: command not found`
- Docker não está instalado no VPS

### Erro: `network proxy not found`
- A rede Docker "proxy" não existe
- Crie com: `docker network create proxy`

### Erro: `cannot access /srv/docker/...`
- Problema de permissões
- Execute: `sudo chown -R $USER:$USER /srv/docker/`

### Erro: `docker compose` vs `docker-compose`
- Em versões antigas do Docker, use `docker-compose` (com hífen)
- Em versões novas, use `docker compose` (sem hífen)

---

## 📞 Próximos Passos

Se ainda não funcionar:

1. Execute o workflow **"Test SSH Connection"** no GitHub Actions
2. Copie os logs de erro
3. Me envie para análise
