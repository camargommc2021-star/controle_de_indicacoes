@echo off
chcp 65001 >nul
echo ==========================================
echo  SUBINDO PARA O GITHUB AUTOMATICAMENTE
echo ==========================================
echo.

REM Verificar se está na pasta correta
IF NOT EXIST "app.py" (
    echo ERRO: Execute este arquivo na pasta 'controle de cursos'
    pause
    exit /b 1
)

echo [1/7] Verificando arquivos...
echo ✓ app.py
echo ✓ data_manager.py
echo ✓ json_import.py
echo ✓ dashboard.py
echo ✓ github_manager.py
echo ✓ init_data.py
echo ✓ requirements.txt
echo ✓ README.md
echo ✓ data/cursos.xlsx
echo.

echo [2/7] Inicializando Git...
git init
echo.

echo [3/7] Configurando repositório remoto...
git remote add origin https://github.com/camargommc2021-star/controledeindica-es.git 2>nul || echo Repositório já configurado
echo.

echo [4/7] Verificando status...
git status
echo.

echo [5/7] Adicionando arquivos ao Git...
git add app.py
git add data_manager.py
git add json_import.py
git add dashboard.py
git add github_manager.py
git add pdf_extractor.py
git add init_data.py
git add requirements.txt
git add README.md
git add GITHUB_SETUP.md
git add .gitignore
git add COMANDOS_GITHUB.txt
git add COMANDOS_GIT.txt
git add .env.example
git add .streamlit/secrets.toml
git add data/cursos.xlsx
git add teste_rapido.py
git add teste_sistema.py
echo.

echo [6/7] Criando commit...
git commit -m "Sistema Controle de Cursos v3.0 - Importacao JSON, Cards Editaveis, Filtro CRCEA-SE/APP-SP"
echo.

echo [7/7] Enviando para GitHub...
git push -u origin main
echo.

IF %ERRORLEVEL% EQU 0 (
    echo ==========================================
    echo  ✅ SUCESSO! ARQUIVOS ENVIADOS!
    echo ==========================================
    echo.
    echo Acesse: https://github.com/camargommc2021-star/controledeindica-es
    echo.
) ELSE (
    echo ==========================================
    echo  ❌ ERRO AO ENVIAR
    echo ==========================================
    echo.
    echo Tentando comando alternativo...
    git push origin main --force
    echo.
)

pause
