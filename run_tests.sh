#!/bin/bash

# Script para executar testes automatizados

echo "🧪 Executando testes automatizados do Gerenciador de Finanças"
echo "=================================================="

# Verificar se ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "❌ Ambiente virtual não encontrado. Execute 'python -m venv venv' primeiro."
    exit 1
fi

# Ativar ambiente virtual
echo "📦 Ativando ambiente virtual..."
source venv/Scripts/activate 2>/dev/null || source venv/bin/activate

# Instalar dependências de teste
echo "📥 Instalando dependências de teste..."
pip install -r requirements.txt
pip install -r requirements-test.txt

# Executar testes
echo "🚀 Executando testes..."
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
pytest tests/ -v --tb=short --cov=app --cov-report=html --cov-report=term-missing

echo ""
echo "✅ Testes concluídos!"
echo "📊 Relatório de cobertura gerado em htmlcov/index.html"
