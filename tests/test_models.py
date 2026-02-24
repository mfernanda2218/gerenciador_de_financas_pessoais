import pytest
from app import User, Category, Transaction


class TestUserModel:
    """Testes para o modelo User"""
    
    def test_create_user(self, app):
        """Testa criação de usuário"""
        with app.app_context():
            user = User(username='testuser', monthly_limit=1500)
            user.set_password('password123')
            
            assert user.username == 'testuser'
            assert user.monthly_limit == 1500
            assert user.check_password('password123')
            assert not user.check_password('wrongpass')
    
    def test_user_repr(self, app):
        """Testa representação string do usuário"""
        with app.app_context():
            user = User(username='testuser')
            assert str(user) == '<User testuser>'


class TestCategoryModel:
    """Testes para o modelo Category"""
    
    def test_create_category(self, app):
        """Testa criação de categoria"""
        with app.app_context():
            category = Category(name='Alimentação', user_id=1)
            
            assert category.name == 'Alimentação'
            assert category.user_id == 1
    
    def test_category_repr(self, app):
        """Testa representação string da categoria"""
        with app.app_context():
            category = Category(name='Alimentação', user_id=1)
            assert str(category) == '<Category Alimentação>'


class TestTransactionModel:
    """Testes para o modelo Transaction"""
    
    def test_create_transaction(self, app):
        """Testa criação de transação"""
        with app.app_context():
            from datetime import datetime
            
            transaction = Transaction(
                date=datetime(2024, 1, 15),
                description='Test Transaction',
                amount=100.0,
                type='despesa',
                category_id=1,
                user_id=1
            )
            
            assert transaction.description == 'Test Transaction'
            assert transaction.amount == 100.0
            assert transaction.type == 'despesa'
            assert transaction.category_id == 1
            assert transaction.user_id == 1
    
    def test_transaction_repr(self, app):
        """Testa representação string da transação"""
        with app.app_context():
            from datetime import datetime
            
            transaction = Transaction(
                date=datetime(2024, 1, 15),
                description='Test Transaction',
                amount=100.0,
                type='despesa',
                user_id=1
            )
            assert str(transaction) == '<Transaction Test Transaction>'
