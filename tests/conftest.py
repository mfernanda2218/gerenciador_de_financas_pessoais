import pytest
import tempfile
import os
from datetime import datetime
from app import app, db, User, Category, Transaction


@pytest.fixture
def client():
    """Cria um cliente de teste com banco de dados temporário"""
    db_fd, db_path = tempfile.mkstemp()
    
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def user():
    """Cria um usuário de teste"""
    user = User(username='testuser', monthly_limit=1000)
    user.set_password('testpass123')
    return user


@pytest.fixture
def authenticated_client(client, user):
    """Cria um cliente autenticado"""
    with app.app_context():
        db.session.add(user)
        db.session.commit()
        
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
    
    return client


@pytest.fixture
def sample_data(app):
    """Cria dados de teste (usuário, categorias, transações)"""
    with app.app_context():
        # Usuário
        user = User(username='testuser', monthly_limit=1000)
        user.set_password('testpass123')
        db.session.add(user)
        
        # Categorias
        cat1 = Category(name='Alimentação', user_id=1)
        cat2 = Category(name='Transporte', user_id=1)
        db.session.add(cat1)
        db.session.add(cat2)
        
        # Transações
        trans1 = Transaction(
            date=datetime(2024, 1, 15),
            description='Supermercado',
            amount=200.0,
            type='despesa',
            category_id=1,
            user_id=1
        )
        trans2 = Transaction(
            date=datetime(2024, 1, 20),
            description='Salário',
            amount=3000.0,
            type='receita',
            category_id=None,
            user_id=1
        )
        db.session.add(trans1)
        db.session.add(trans2)
        
        db.session.commit()
        
        return {
            'user': user,
            'categories': [cat1, cat2],
            'transactions': [trans1, trans2]
        }
