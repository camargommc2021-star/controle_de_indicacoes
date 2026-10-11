# 🔒 Guia de Segurança

Este documento descreve as medidas de segurança implementadas no Sistema de Controle de Cursos.

---

## 🛡️ Medidas de Segurança Implementadas

### 1. Autenticação e Senhas
- Senhas protegidas com derivação segura PBKDF2 (HMAC-SHA256) e salt individual aleatório.
- Bloqueio automático de conta após 5 tentativas consecutivas de login incorreto.
- Sessões registradas com identificador único.

### 2. Controle de Acesso Baseado em Papéis (RBAC)
- **Admin**: Acesso total (CRUD de cursos, gestão de usuários, backups).
- **Editor**: CRUD de cursos (sem acesso à gestão de usuários).
- **Viewer**: Apenas visualização.

### 3. Sanitização e Validação
- Validação estrita de entradas em formulários de cursos.
- Sanitização de strings para prevenção de injeção.

### 4. Política de Senhas
- Mínimo de 6 caracteres.
- Troca de senha pelo próprio usuário na interface.

---

**Versão:** 2.0  
**Classificação:** USO OFICIAL
