#!/bin/bash
# =============================================================================
# SCRIPT DE CONFIGURAÇÃO DO VPS - Controle de Cursos
# =============================================================================
# Execute este script no seu VPS para configurar o secrets.toml
# =============================================================================

set -e

PROJECT_DIR="/srv/docker/controle-indicacoes"
SECRETS_FILE="$PROJECT_DIR/.streamlit/secrets.toml"

echo "🚀 Configurando Secrets no VPS..."
echo ""

# Criar diretório se não existir
sudo mkdir -p "$PROJECT_DIR/.streamlit"

# Criar arquivo secrets.toml
echo "📝 Criando arquivo secrets.toml..."
sudo tee "$SECRETS_FILE" > /dev/null << 'EOF'
[gcp_service_account]
type = "service_account"
project_id = "controle-cursos-fic"
private_key_id = "c3ea595b7701cb64ff9cd82138efc329965c1ab8"
private_key = """-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDNq62kIlQkQ9xC
VmqJjboNU5GqoEBEg/FcXVd4LUARNQSQIPLjJaKAN7yEG7qMF+xqLgGouwPyOU8N
BMnr4vMUCbvd2ujsW0l1LlQ/XMYUH8rV+gyT/5Yx0sx8Q0L1mfy/7BasBeZIrlW6
w0Xr708M2YFfK53ow69SPFYsdLfOH098ytZgX1eAbS8G72sJklmb/zrW07cSagSt
wQdA8On3yVYjmtX2EjG1gqNqeXShZxFCxnWc+pWEq8BhP/3wCPTwifqBFmAwHmxP
g49CjnstQpJjZA3AMkJNm7pLlephSWPXwf8jFcVg+Tvx0GFF1ORdZ7OmsnWaXXoi
NKluSTqnAgMBAAECggEAE24uM+z4VQrCMtQ2MXOdyaeFAgEswSxT751z54si291N
5o3uVG5YSVO6sCJsf9K8x5U8G+Q7LbWjVcAHkYz52QFIad/GFJpVOMhdNjU+E2Wj
hI6ghJTnbCKVpgG2wDxBiCI2TB8sj95EhCXxo6YSqkycL9EPlI90L0k6/O0z9jmM
gbdxEv2kV7I05tuTq//mhdLtG6TT4ERBMPYFDPxOSM+CaOct1bY2BpbS+ZF5ZSC1
9G9Vip+8wO8ne51zcgYa3mtITIxixDqCVb+qUluht5nxgGcKcibhcAAG7M8oOpU3
7YLBh1tsqH2dhmpyC7ujyUpC4WWQqJNwoNwvEju2VQKBgQD68Nh3BkZy2lnVKAg3
+d9TmZBAJkXQyE+947Kgy7vD2hkqThbk/E0WpWcvMvU7d23cKeNLjHLPEYv1SuDw
nFTjaC0hgvTisbkT6Lazt/wralnXtyrlvKBZMMDCyLicX7+ESJsVRiHC7J0mgNeC
yUMhWlq6I+OhGUQQ9K+DWNgt7QKBgQDR0S85Jmza6w+gMwZFQDePdVbF/XEUcxJ2
s5iaJDGvbLCtz94r27q9DE89CzHR+nDSJdZzeli06VbPFj//egz4D9m/d8lodswc
VZmQTzhGfXCCLa3Suk9rwOarz8Q55sTAQAGYodl8HyHYiS6Z4nDT/N4J61CTIPvs
B1gKwb5YYwKBgBnWirNWthJFYVKNWKtK0y/sc+nnBvFEbtGCjHX6BE9aOZUdjUXu
pJFcXo+Bk7aXyXwN5BV3VKr1h4+uMhMURblUlLEKpuRgoEnogEdo/lIKFU4c0hHt
piUI3BAyUq/nO/UG9NDv87H6YwP/6DDTQFJC12yrHVkNHPESALBpiXjRAoGBAKkB
G02ocuQ/lP2QPAvJ9zb56CRgyhYTvpqYfWIjp1XLceD/X9DqE9e1M5pTCxU86mWL
jtrDgPJwRblXDcPGVu31Lor4fOZFUpG8LY69EPJOljJ1gt8LrW95GRTprQCKro7A
v8hnDhzZotSdY0kWyZUnyN4qimOInQN4wuUfPChLAoGBAIJEzlR53khT29KtbMN+
xSu9FCczbp5hVfuNEPlwfDVL0YG9af7W9Siwp6CaMLUlMvQ5/dvqJBA5ck/lJHn/
m1A3wBVcIXn//SvtG/FsqxZsWebInf3xgrvPaQ3PHa96nlPsAVYWkqEokLxAJOmL
pag3Roy0DfShKLVBhdzyGpvk
-----END PRIVATE KEY-----
"""
client_email = "fic-reader@controle-cursos-fic.iam.gserviceaccount.com"
client_id = "111598801735957865924"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/fic-reader%40controle-cursos-fic.iam.gserviceaccount.com"

SHEETS_SPREADSHEET_ID = "1SNVMZ4furWWpG9PWVwhTtTvEjtWkfsCFRE61IfxMVaw"
EOF

# Ajustar permissões
sudo chmod 600 "$SECRETS_FILE"

echo "✅ Secrets configurado com sucesso!"
echo ""
echo "📍 Local: $SECRETS_FILE"
echo ""
echo "🔄 Reiniciando container..."
cd "$PROJECT_DIR"
sudo docker compose -f docker-compose.prod.yml restart

echo ""
echo "✅ Configuração completa!"
echo ""
echo "📝 Próximos passos:"
echo "   1. Verifique se a planilha foi compartilhada com:"
echo "      fic-reader@controle-cursos-fic.iam.gserviceaccount.com"
echo "   2. Acesse o site e teste a aba 'Confecção de FIC'"
echo ""
