@echo off
REM Script para executar testes automatizados no Windows

echo 🧪 Executando testes automatizados do Gerenciador de Finanças
echo ==================================================

REM Verificar se ambiente virtual existe
if not exist "venv" (
    echo ❌ Ambiente virtual não encontrado. Execute 'python -m venv venv' primeiro.
    pause
    exit /b 1
)

REM Ativar ambiente virtual
echo 📦 Ativando ambiente virtual...
call venv\Scripts\activate

REM Instalar dependências de teste
echo 📥 Instalando dependências de teste...
pip install -r requirements.txt
pip install -r requirements-test.txt

REM Executar testes
echo 🚀 Executando testes...
set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
pytest tests/ -v --tb=short --cov=app --cov-report=html --cov-report=term-missing

echo.
echo ✅ Testes concluídos!
echo 📊 Relatório de cobertura gerado em htmlcov\index.html
pause
