from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file, session, abort
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy.exc import IntegrityError
import pandas as pd
from io import StringIO, BytesIO
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'  # Mude para uma chave segura
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Modelos do Banco
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    monthly_limit = db.Column(db.Float, default=1000)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    __table_args__ = (db.UniqueConstraint('user_id', 'name', name='uq_category_user_name'),)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    description = db.Column(db.String(200))
    amount = db.Column(db.Float)
    type = db.Column(db.String(10))  # 'receita' ou 'despesa'
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    limit_monthly = db.Column(db.Float, default=0)  # Limite mensal para alerta (por categoria ou geral)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def _ensure_schema():
    db.create_all()

    cols = db.session.execute(db.text("PRAGMA table_info(user)")).fetchall()
    col_names = {c[1] for c in cols}
    if 'monthly_limit' not in col_names:
        db.session.execute(db.text("ALTER TABLE user ADD COLUMN monthly_limit FLOAT"))
        db.session.execute(db.text("UPDATE user SET monthly_limit = 1000 WHERE monthly_limit IS NULL"))
        db.session.commit()

    category_sql = db.session.execute(db.text("SELECT sql FROM sqlite_master WHERE type='table' AND name='category'"))
    category_row = category_sql.fetchone()
    if category_row and category_row[0] and 'name' in category_row[0] and 'UNIQUE' in category_row[0].upper():
        db.session.execute(db.text("PRAGMA foreign_keys=OFF"))
        db.session.execute(db.text("ALTER TABLE category RENAME TO category_old"))
        db.session.execute(
            db.text(
                "CREATE TABLE category ("
                "id INTEGER NOT NULL PRIMARY KEY, "
                "name VARCHAR(100) NOT NULL, "
                "user_id INTEGER, "
                "CONSTRAINT uq_category_user_name UNIQUE (user_id, name), "
                "FOREIGN KEY(user_id) REFERENCES user (id)"
                ")"
            )
        )
        db.session.execute(db.text("INSERT INTO category (id, name, user_id) SELECT id, name, user_id FROM category_old"))
        db.session.execute(db.text("DROP TABLE category_old"))
        db.session.execute(db.text("PRAGMA foreign_keys=ON"))
        db.session.commit()

with app.app_context():
    _ensure_schema()

# Rotas
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and bcrypt.check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('index'))
        error = 'Usuário ou senha inválidos.'
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''
        confirm = request.form.get('confirm_password') or ''

        if not username:
            error = 'Informe um usuário.'
        elif len(password) < 6:
            error = 'A senha deve ter pelo menos 6 caracteres.'
        elif password != confirm:
            error = 'As senhas não conferem.'
        elif User.query.filter_by(username=username).first():
            error = 'Esse usuário já existe.'
        else:
            hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
            user = User(username=username, password=hashed_pw, monthly_limit=1000)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('index'))

    return render_template('register.html', error=error)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/add_transaction', methods=['GET', 'POST'])
@login_required
def add_transaction():
    if request.method == 'POST':
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        raw_category = (request.form.get('category') or '').strip()
        category_id = int(raw_category) if raw_category else None
        if category_id is not None and not Category.query.filter_by(id=category_id, user_id=current_user.id).first():
            category_id = None
        trans = Transaction(date=date, description=request.form['description'], amount=float(request.form['amount']),
                            type=request.form['type'], category_id=category_id, user_id=current_user.id)
        db.session.add(trans)
        db.session.commit()
        return redirect(url_for('index'))
    categories = Category.query.filter_by(user_id=current_user.id).all()
    return render_template('add_transaction.html', categories=categories)

@app.route('/transactions')
@login_required
def transactions():
    month = (request.args.get('month') or '').strip()
    year = (request.args.get('year') or '').strip()
    trans_type = (request.args.get('type') or '').strip()
    category = (request.args.get('category') or '').strip()
    q = (request.args.get('q') or '').strip()

    query = Transaction.query.filter_by(user_id=current_user.id)

    if month:
        try:
            query = query.filter(db.extract('month', Transaction.date) == int(month))
        except ValueError:
            month = ''
    if year:
        try:
            query = query.filter(db.extract('year', Transaction.date) == int(year))
        except ValueError:
            year = ''
    if trans_type in ('receita', 'despesa'):
        query = query.filter(Transaction.type == trans_type)
    else:
        trans_type = ''

    if category == 'none':
        query = query.filter(Transaction.category_id.is_(None))
    elif category:
        try:
            cat_id = int(category)
            if Category.query.filter_by(id=cat_id, user_id=current_user.id).first():
                query = query.filter(Transaction.category_id == cat_id)
            else:
                category = ''
        except ValueError:
            category = ''

    if q:
        query = query.filter(Transaction.description.ilike(f"%{q}%"))

    transactions_list = query.order_by(Transaction.date.desc(), Transaction.id.desc()).all()
    categories_list = Category.query.filter_by(user_id=current_user.id).order_by(Category.name.asc()).all()
    category_map = {c.id: c.name for c in categories_list}

    return render_template(
        'transactions.html',
        transactions=transactions_list,
        categories=categories_list,
        category_map=category_map,
        filters={'month': month, 'year': year, 'type': trans_type, 'category': category, 'q': q},
    )

@app.route('/transaction/<int:transaction_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_transaction(transaction_id):
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()
    if not transaction:
        abort(404)

    categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.name.asc()).all()
    error = None

    if request.method == 'POST':
        try:
            date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        except ValueError:
            error = 'Data inválida.'
            return render_template('edit_transaction.html', transaction=transaction, categories=categories, error=error)

        raw_amount = (request.form.get('amount') or '').strip()
        try:
            amount = float(raw_amount)
        except ValueError:
            error = 'Valor inválido.'
            return render_template('edit_transaction.html', transaction=transaction, categories=categories, error=error)

        trans_type = request.form.get('type')
        if trans_type not in ('receita', 'despesa'):
            error = 'Tipo inválido.'
            return render_template('edit_transaction.html', transaction=transaction, categories=categories, error=error)

        raw_category = (request.form.get('category') or '').strip()
        category_id = int(raw_category) if raw_category else None
        if category_id is not None and not Category.query.filter_by(id=category_id, user_id=current_user.id).first():
            category_id = None

        transaction.date = date
        transaction.description = request.form.get('description') or ''
        transaction.amount = amount
        transaction.type = trans_type
        transaction.category_id = category_id

        db.session.commit()
        return redirect(url_for('transactions'))

    return render_template('edit_transaction.html', transaction=transaction, categories=categories, error=error)

@app.route('/transaction/<int:transaction_id>/delete', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()
    if not transaction:
        abort(404)
    db.session.delete(transaction)
    db.session.commit()
    return redirect(url_for('transactions'))

@app.route('/categories')
@login_required
def categories():
    categories_list = Category.query.filter_by(user_id=current_user.id).order_by(Category.name.asc()).all()
    counts = {
        row[0]: row[1]
        for row in db.session.query(Transaction.category_id, db.func.count(Transaction.id))
        .filter(Transaction.user_id == current_user.id)
        .group_by(Transaction.category_id)
        .all()
        if row[0] is not None
    }
    return render_template('categories.html', categories=categories_list, counts=counts, error=None)

@app.route('/categories/add', methods=['POST'])
@login_required
def add_category_page():
    name = (request.form.get('name') or '').strip()
    if not name:
        return redirect(url_for('categories'))
    cat = Category(name=name, user_id=current_user.id)
    db.session.add(cat)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        categories_list = Category.query.filter_by(user_id=current_user.id).order_by(Category.name.asc()).all()
        counts = {
            row[0]: row[1]
            for row in db.session.query(Transaction.category_id, db.func.count(Transaction.id))
            .filter(Transaction.user_id == current_user.id)
            .group_by(Transaction.category_id)
            .all()
            if row[0] is not None
        }
        return render_template('categories.html', categories=categories_list, counts=counts, error='Categoria já existe.')
    return redirect(url_for('categories'))

@app.route('/category/<int:category_id>/edit', methods=['POST'])
@login_required
def edit_category(category_id):
    cat = Category.query.filter_by(id=category_id, user_id=current_user.id).first()
    if not cat:
        abort(404)

    name = (request.form.get('name') or '').strip()
    if not name:
        return redirect(url_for('categories'))

    cat.name = name
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        categories_list = Category.query.filter_by(user_id=current_user.id).order_by(Category.name.asc()).all()
        counts = {
            row[0]: row[1]
            for row in db.session.query(Transaction.category_id, db.func.count(Transaction.id))
            .filter(Transaction.user_id == current_user.id)
            .group_by(Transaction.category_id)
            .all()
            if row[0] is not None
        }
        return render_template('categories.html', categories=categories_list, counts=counts, error='Já existe uma categoria com esse nome.')

    return redirect(url_for('categories'))

@app.route('/category/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    cat = Category.query.filter_by(id=category_id, user_id=current_user.id).first()
    if not cat:
        abort(404)

    Transaction.query.filter_by(user_id=current_user.id, category_id=category_id).update({'category_id': None})
    db.session.delete(cat)
    db.session.commit()
    return redirect(url_for('categories'))

@app.route('/import_csv', methods=['POST'])
@login_required
def import_csv():
    file = request.files['file']
    df = pd.read_csv(file)
    # Assuma colunas: date (YYYY-MM-DD), description, amount, type (receita/despesa), category
    for _, row in df.iterrows():
        cat = Category.query.filter_by(name=row['category'], user_id=current_user.id).first()
        if not cat:
            cat = Category(name=row['category'], user_id=current_user.id)
            db.session.add(cat)
            db.session.commit()
        trans = Transaction(date=datetime.strptime(row['date'], '%Y-%m-%d'), description=row['description'],
                            amount=row['amount'], type=row['type'], category_id=cat.id, user_id=current_user.id)
        db.session.add(trans)
    db.session.commit()
    return jsonify({'message': 'CSV importado com sucesso'})

@app.route('/export_csv')
@login_required
def export_csv():
    month = request.args.get('month')
    year = request.args.get('year')

    query = Transaction.query.filter_by(user_id=current_user.id)
    if month:
        try:
            month_int = int(month)
            query = query.filter(db.extract('month', Transaction.date) == month_int)
        except ValueError:
            pass
    if year:
        try:
            year_int = int(year)
            query = query.filter(db.extract('year', Transaction.date) == year_int)
        except ValueError:
            pass

    trans = query.all()
    category_map = {c.id: c.name for c in Category.query.filter_by(user_id=current_user.id).all()}
    data = [
        {
            'date': t.date,
            'description': t.description,
            'amount': t.amount,
            'type': t.type,
            'category': category_map.get(t.category_id, 'Sem Categoria'),
        }
        for t in trans
    ]
    df = pd.DataFrame(data)
    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return send_file(output, mimetype='text/csv', as_attachment=True, download_name='relatorio.csv')

@app.route('/dashboard_data')
@login_required
def dashboard_data():
    month = request.args.get('month')
    year = request.args.get('year', datetime.now().year)
    query = Transaction.query.filter_by(user_id=current_user.id)
    if month:
        try:
            query = query.filter(db.extract('month', Transaction.date) == int(month))
        except ValueError:
            pass
    if year:
        try:
            query = query.filter(db.extract('year', Transaction.date) == int(year))
        except ValueError:
            pass
    trans = query.all()

    category_map = {c.id: c.name for c in Category.query.filter_by(user_id=current_user.id).all()}
    df = pd.DataFrame(
        [
            {
                'amount': t.amount,
                'type': t.type,
                'category': category_map.get(t.category_id, 'Sem Categoria'),
                'date': t.date,
            }
            for t in trans
        ]
    )
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        df['signed_amount'] = df.apply(lambda r: r['amount'] if r['type'] == 'receita' else -r['amount'], axis=1)

    # Métricas
    gastos_por_categoria = (
        df[df['type'] == 'despesa'].groupby('category')['amount'].sum().to_dict() if not df.empty else {}
    )
    receita = float(df[df['type'] == 'receita']['amount'].sum()) if not df.empty else 0
    despesa = float(df[df['type'] == 'despesa']['amount'].sum()) if not df.empty else 0
    saldo = receita - despesa

    if not df.empty:
        evolucao = (
            df.groupby(df['date'].dt.to_period('M'))['signed_amount']
            .sum()
            .sort_index()
        )
        evolucao_mensal = {str(k): float(v) for k, v in evolucao.to_dict().items()}
    else:
        evolucao_mensal = {}

    # Alerta de gasto (limite geral por usuário)
    alerta = None
    limit_value = float(current_user.monthly_limit or 0)
    if limit_value > 0 and despesa > limit_value:
        alerta = 'Aviso: Gastos ultrapassaram o limite mensal!'

    return jsonify({
        'total_mensal': saldo,
        'total_receita': receita,
        'total_despesa': despesa,
        'gastos_por_categoria': gastos_por_categoria,
        'receita_despesa': {'receita': receita, 'despesa': despesa},
        'evolucao_mensal': evolucao_mensal,
        'alerta': alerta,
        'monthly_limit': limit_value
    })

@app.route('/set_monthly_limit', methods=['POST'])
@login_required
def set_monthly_limit():
    value = (request.form.get('monthly_limit') or '').strip()
    try:
        limit_value = float(value)
        if limit_value < 0:
            raise ValueError()
    except ValueError:
        return jsonify({'message': 'Valor inválido'}), 400

    current_user.monthly_limit = limit_value
    db.session.commit()
    return jsonify({'message': 'Limite atualizado', 'monthly_limit': float(current_user.monthly_limit or 0)})

@app.route('/add_category', methods=['POST'])
@login_required
def add_category():
    name = (request.form.get('name') or '').strip()
    if not name:
        return jsonify({'message': 'Nome inválido'}), 400
    if Category.query.filter_by(user_id=current_user.id, name=name).first():
        return jsonify({'message': 'Categoria já existe'}), 409
    cat = Category(name=name, user_id=current_user.id)
    db.session.add(cat)
    db.session.commit()
    return jsonify({'message': 'Categoria adicionada'})

if __name__ == '__main__':
    app.run(debug=True)