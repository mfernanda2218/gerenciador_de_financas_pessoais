# Testes Automatizados

Este projeto inclui uma suite completa de testes automatizados para garantir a qualidade e estabilidade da aplicação.

## 📁 Estrutura dos Testes

```
tests/
├── conftest.py          # Configuração e fixtures
├── test_models.py       # Testes dos modelos de dados
├── test_auth.py         # Testes de autenticação
├── test_transactions.py # Testes de CRUD de transações
├── test_categories.py  # Testes de CRUD de categorias
├── test_dashboard.py    # Testes do dashboard e APIs
└── test_csv.py         # Testes de importação/exportação
```

## 🛠️ Configuração

### Dependências de Teste
```bash
pip install -r requirements-test.txt
```

### Arquivos de Configuração
- `pytest.ini`: Configuração do pytest
- `requirements-test.txt`: Dependências específicas para testes

## 🚀 Executando os Testes

### Windows
```bash
run_tests.bat
```

### Linux/Mac
```bash
chmod +x run_tests.sh
./run_tests.sh
```

### Manualmente
```bash
# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Executar todos os testes
pytest tests/ -v

# Executar com cobertura
pytest tests/ --cov=app --cov-report=html

# Executar teste específico
pytest tests/test_auth.py -v
```

## 📊 Cobertura de Código

Os testes cobrem:
- ✅ Modelos de dados (User, Category, Transaction)
- ✅ Autenticação (login, registro, logout)
- ✅ CRUD de transações
- ✅ CRUD de categorias
- ✅ Dashboard e APIs
- ✅ Importação/exportação CSV
- ✅ Validação de dados
- ✅ Tratamento de erros

## 🔧 Fixtures Disponíveis

- `client`: Cliente de teste com banco temporário
- `user`: Usuário de teste
- `authenticated_client`: Cliente autenticado
- `sample_data`: Dados de teste completos

## 📈 Relatórios

Após executar os testes com cobertura:
- Relatório HTML: `htmlcov/index.html`
- Cobertura no terminal: exibida automaticamente

## 🐛 Debug de Testes

```bash
# Executar com modo debug
pytest tests/ -v -s --pdb

# Parar no primeiro erro
pytest tests/ -x

# Executar apenas testes falhados
pytest tests/ --lf
```

## 🎯 Boas Práticas

1. **Execute testes antes de commits**
2. **Mantenha cobertura > 80%**
3. **Teste casos extremos (edge cases)**
4. **Use descritivos nos nomes dos testes**
5. **Mock dependências externas quando necessário**
