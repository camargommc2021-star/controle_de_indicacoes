@echo off
chcp 65001 >nul
echo ==========================================
echo  ATUALIZACAO SISTEMA CONTROLE DE CURSOS
echo  Versao 2.0 - Login e Calendario
echo ==========================================
echo.

REM Fazer backup do app.py original
echo [1/4] Fazendo backup do app.py original...
if exist app.py (
    copy app.py app_backup_v1.py /Y
    echo      Backup criado: app_backup_v1.py
) else (
    echo      app.py nao encontrado, pulando backup...
)
echo.

REM Copiar nova versao
echo [2/4] Aplicando nova versao...
copy app_v2.py app.py /Y
echo      app.py atualizado para v2.0
echo.

REM Verificar estrutura de dados
echo [3/4] Verificando estrutura de dados...
if not exist data\usuarios.xlsx (
    echo      Arquivo de usuarios sera criado automaticamente no primeiro login.
) else (
    echo      Arquivo de usuarios ja existe.
)
echo.

REM Instalar dependencias se necessario
echo [4/4] Verificando dependencias...
pip show cryptography >nul 2>&1
if errorlevel 1 (
    echo      Instalando dependencia: cryptography...
    pip install cryptography -q
) else (
    echo      Dependencias OK.
)
echo.

echo ==========================================
echo  ATUALIZACAO CONCLUIDA!
echo ==========================================
echo.
echo NOVIDADES v2.0:
echo   - Sistema de Login com niveis de acesso
echo   - Visualizacao em Calendario dos prazos
echo   - Controle de permissoes por funcionalidade
echo.
echo CREDENCIAIS PADRAO:
echo   Usuario: admin
echo   Senha:   admin123
echo.
echo IMPORTANTE:
echo   - Altere a senha padrao apos o primeiro login
echo   - O arquivo de usuarios esta em: data\usuarios.xlsx
echo   - Logs de acesso em: data\sessoes.xlsx
echo.
echo Para iniciar: streamlit run app.py
echo.
pause
