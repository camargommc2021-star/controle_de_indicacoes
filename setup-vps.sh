#!/bin/bash
# =============================================================================
# SCRIPT DE CONFIGURAÇÃO DO VPS - Controle de Cursos
# =============================================================================
# Execute este script no seu VPS para inicializar o ambiente
# =============================================================================

set -e

PROJECT_DIR="/srv/docker/controle-indicacoes"
SECRETS_FILE="$PROJECT_DIR/.streamlit/secrets.toml"

echo "🚀 Configurando ambiente no VPS..."
echo ""

# Criar diretório se não existir
sudo mkdir -p "$PROJECT_DIR/.streamlit"

if [ -f "$SECRETS_FILE" ]; then
    sudo chmod 600 "$SECRETS_FILE"
fi

echo "🔄 Reiniciando container..."
cd "$PROJECT_DIR"
sudo docker compose -f docker-compose.prod.yml restart

echo ""
echo "✅ Configuração completa!"
