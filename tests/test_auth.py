import pytest
from flask import url_for


class TestAuth:
    """Testes para rotas de autenticação"""
    
    def test_register_get(self, client):
        """Testa acesso à página de registro"""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'Cadastrar' in response.data
    
    def test_register_success(self, client):
        """Testa registro bem-sucedido"""
        response = client.post('/register', data={
            'username': 'newuser',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert 'Gerenciador de Finanças' in response.data.decode('utf-8')
    
    def test_register_password_mismatch(self, client):
        """Testa registro com senhas diferentes"""
        response = client.post('/register', data={
            'username': 'newuser',
            'password': 'password123',
            'confirm_password': 'different'
        })
        
        assert response.status_code == 200
        assert 'As senhas não conferem' in response.data.decode('utf-8')
    
    def test_register_short_password(self, client):
        """Testa registro com senha curta"""
        response = client.post('/register', data={
            'username': 'newuser',
            'password': '123',
            'confirm_password': '123'
        })
        
        assert response.status_code == 200
        assert b'A senha deve ter pelo menos 6 caracteres' in response.data
    
    def test_register_duplicate_username(self, client, user):
        """Testa registro com usuário duplicado"""
        with client.application.app_context():
            from app import db
            db.session.add(user)
            db.session.commit()
        
        response = client.post('/register', data={
            'username': 'testuser',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        
        assert response.status_code == 200
        assert 'Esse usuário já existe' in response.data.decode('utf-8')
    
    def test_login_get(self, client):
        """Testa acesso à página de login"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Login' in response.data
    
    def test_login_success(self, client, user):
        """Testa login bem-sucedido"""
        with client.application.app_context():
            from app import db
            db.session.add(user)
            db.session.commit()
        
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert 'Gerenciador de Finanças' in response.data.decode('utf-8')
    
    def test_login_invalid_credentials(self, client, user):
        """Testa login com credenciais inválidas"""
        with client.application.app_context():
            from app import db
            db.session.add(user)
            db.session.commit()
        
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpass'
        })
        
        assert response.status_code == 200
        assert 'Usuário ou senha inválidos' in response.data.decode('utf-8')
    
    def test_logout(self, authenticated_client):
        """Testa logout"""
        response = authenticated_client.get('/logout', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Login' in response.data
    
    def test_protected_route_without_login(self, client):
        """Testa acesso a rota protegida sem login"""
        response = client.get('/')
        assert response.status_code == 302  # Redirect to login
        
        response = client.get('/add_transaction')
        assert response.status_code == 302  # Redirect to login
