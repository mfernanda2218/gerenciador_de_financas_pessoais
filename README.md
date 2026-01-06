# Gerenciador de Finanças (Flask + SQLite)

Sistema web para controle de finanças pessoais com autenticação, categorias personalizadas, dashboard com gráficos e CRUD completo de transações e categorias.

## Funcionalidades

### Autenticação

- **Cadastro de usuário**: `GET/POST /register`
  - Validações:
    - usuário obrigatório
    - senha com mínimo de 6 caracteres
    - confirmação de senha
    - usuário único
- **Login**: `GET/POST /login`
- **Logout**: `GET /logout`
- Rotas principais protegidas por sessão (`Flask-Login`).

### Dashboard (relatórios e gráficos)

- **Filtro por período** (mês/ano) no dashboard
- **Gastos por categoria** (somente despesas)
- **Receita x Despesa**
- **Evolução mensal (saldo)**
  - saldo = receita - despesa
- **Alerta de gasto**
  - limite mensal configurável por usuário (`monthly_limit`)
  - aparece aviso quando despesas do mês filtrado ultrapassam o limite
- **Exportação CSV** (com filtro)
  - `GET /export_csv?month=...&year=...`

### Importação CSV

- `POST /import_csv`
- Espera um CSV com colunas:
  - `date` (formato `YYYY-MM-DD`)
  - `description`
  - `amount`
  - `type` (`receita` ou `despesa`)
  - `category`
- Se a categoria ainda não existir para o usuário logado, ela é criada automaticamente.

### Categorias personalizadas (CRUD)

- **Listar**: `GET /categories`
- **Adicionar**: `POST /categories/add`
- **Renomear**: `POST /category/<id>/edit`
- **Excluir**: `POST /category/<id>/delete`
  - ao excluir uma categoria, as transações associadas ficam como **Sem categoria** (`category_id = NULL`).
- Regras:
  - categoria é **única por usuário** (`user_id + name`).

### Transações (CRUD)

- **Criar**: `GET/POST /add_transaction`
  - aceita **Sem categoria**
- **Listar + filtrar**: `GET /transactions`
  - filtros disponíveis:
    - `month` (1-12)
    - `year`
    - `type` (`receita`/`despesa`)
    - `category` (id da categoria) ou `none` (sem categoria)
    - `q` (busca na descrição)
- **Editar**: `GET/POST /transaction/<id>/edit`
- **Excluir**: `POST /transaction/<id>/delete`

## Tecnologias

- Python
- Flask
- Flask-Login
- Flask-SQLAlchemy
- Flask-Bcrypt
- SQLite
- Pandas
- Chart.js (via CDN)

## Estrutura do projeto

- `app.py`: aplicação Flask (rotas, modelos, regras)
- `templates/`: páginas HTML
- `static/`:
  - `style.css`: estilos
  - `script.js`: dashboard/gráficos e ações do dashboard
- `database.db`: banco SQLite
- `requirements.txt`: dependências

## Como executar no PC (Windows)

### 1) Pré-requisitos

- Python 3.10+ (recomendado)

### 2) Criar e ativar o ambiente virtual

Abra o **Prompt de Comando** (cmd) na pasta do projeto e execute:

```bat
python -m venv venv
venv\Scripts\activate
```

### 3) Instalar dependências

```bat
pip install -r requirements.txt
```

### 4) Executar o servidor

```bat
python app.py
```

Acesse no navegador:

- `http://127.0.0.1:5000/login`

### 5) Fluxo sugerido de uso

- Crie conta em `/register`
- Faça login
- Cadastre categorias em **Categorias** (`/categories`)
- Cadastre transações (ou importe CSV)
- Veja relatórios no dashboard
- Use **Transações** (`/transactions`) para editar/excluir

## Como executar no Notebook (Jupyter)

Você pode rodar o sistema a partir de um notebook para manter tudo no mesmo ambiente.

### Opção A (recomendada): usar o mesmo venv

1. Ative o venv no terminal:

```bat
venv\Scripts\activate
```

2. Instale Jupyter e registre o kernel:

```bat
pip install notebook ipykernel
python -m ipykernel install --user --name gerenciador_de_financas --display-name "Python (gerenciador_de_financas)"
```

3. Inicie o Jupyter:

```bat
jupyter notebook
```

4. No notebook, selecione o kernel **Python (gerenciador_de_financas)**.

5. Para subir o servidor pelo notebook, rode em uma célula:

```python
!python app.py
```

Depois acesse `http://127.0.0.1:5000/login`.

### Opção B: executar via terminal e usar notebook apenas para análise

- Suba o Flask no terminal (`python app.py`)
- Use o notebook para analisar/exportar CSVs, etc.

## Observações sobre o banco

- O banco é SQLite (`database.db`).
- O projeto possui uma rotina de ajuste de schema na inicialização para:
  - adicionar a coluna `monthly_limit` em `user` caso não exista
  - corrigir a unicidade de categoria para ser por usuário

## Rotas principais

- `/login`
- `/register`
- `/logout`
- `/` (dashboard)
- `/transactions`
- `/transaction/<id>/edit`
- `/transaction/<id>/delete`
- `/categories`
- `/categories/add`
- `/category/<id>/edit`
- `/category/<id>/delete`
- `/import_csv`
- `/export_csv`
- `/dashboard_data`
- `/set_monthly_limit`

