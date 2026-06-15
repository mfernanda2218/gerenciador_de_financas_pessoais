import pytest
import json
from datetime import datetime


class TestDashboard:
    """Testes para dashboard e API endpoints"""
    
    def test_dashboard_get(self, authenticated_client):
        """Testa acesso ao dashboard"""
        response = authenticated_client.get('/')
        assert response.status_code == 200
        assert b'Dashboard' in response.data
    
    def test_dashboard_data_empty(self, authenticated_client):
        """Testa API do dashboard sem dados"""
        response = authenticated_client.get('/dashboard_data')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['total_mensal'] == 0
        assert data['total_receita'] == 0
        assert data['total_despesa'] == 0
        assert data['gastos_por_categoria'] == {}
        assert data['evolucao_mensal'] == {}
    
    def test_dashboard_data_with_transactions(self, authenticated_client, sample_data):
        """Testa API do dashboard com dados"""
        response = authenticated_client.get('/dashboard_data')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['total_receita'] == 3000.0
        assert data['total_despesa'] == 200.0
        assert data['total_mensal'] == 2800.0
        assert 'Alimentação' in data['gastos_por_categoria']
    
    def test_dashboard_data_filtered(self, authenticated_client, sample_data):
        """Testa API do dashboard com filtros"""
        response = authenticated_client.get('/dashboard_data?month=1&year=2024')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['total_receita'] == 3000.0
        assert data['total_despesa'] == 200.0
    
    def test_dashboard_data_invalid_filter(self, authenticated_client, sample_data):
        """Testa API do dashboard com filtros inválidos"""
        response = authenticated_client.get('/dashboard_data?month=invalid')
        assert response.status_code == 200
        
        # Deve ignorar filtro inválido e retornar todos os dados
        data = json.loads(response.data)
        assert data['total_receita'] == 3000.0
    
    def test_set_monthly_limit(self, authenticated_client, sample_data):
        """Testa configuração de limite mensal"""
        response = authenticated_client.post('/set_monthly_limit', data={
            'monthly_limit': '1500.50'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['monthly_limit'] == 1500.50
    
    def test_set_monthly_limit_invalid(self, authenticated_client):
        """Testa configuração de limite mensal inválido"""
        response = authenticated_client.post('/set_monthly_limit', data={
            'monthly_limit': 'invalid'
        })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['message'] == 'Valor inválido'
    
    def test_set_monthly_limit_negative(self, authenticated_client):
        """Testa configuração de limite mensal negativo"""
        response = authenticated_client.post('/set_monthly_limit', data={
            'monthly_limit': '-100'
        })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['message'] == 'Valor inválido'
    
    def test_add_category_api(self, authenticated_client):
        """Testa API de adicionar categoria"""
        response = authenticated_client.post('/add_category', data={
            'name': 'Nova Categoria'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Categoria adicionada'
    
    def test_add_category_api_duplicate(self, authenticated_client, sample_data):
        """Testa API de adicionar categoria duplicada"""
        response = authenticated_client.post('/add_category', data={
            'name': 'Alimentação'
        })
        
        assert response.status_code == 409
        data = json.loads(response.data)
        assert data['message'] == 'Categoria já existe'
    
    def test_add_category_api_empty(self, authenticated_client):
        """Testa API de adicionar categoria vazia"""
        response = authenticated_client.post('/add_category', data={
            'name': ''
        })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['message'] == 'Nome inválido'
    
    def test_spending_alert(self, authenticated_client, sample_data):
        """Testa alerta de gasto quando ultrapassa limite"""
        # Configurar limite baixo para trigger alerta
        authenticated_client.post('/set_monthly_limit', data={
            'monthly_limit': '100'
        })
        
        response = authenticated_client.get('/dashboard_data')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['alerta'] is not None
        assert 'ultrapassaram' in data['alerta']
    
    def test_no_spending_alert(self, authenticated_client, sample_data):
        """Testa sem alerta quando não ultrapassa limite"""
        # Configurar limite alto
        authenticated_client.post('/set_monthly_limit', data={
            'monthly_limit': '5000'
        })
        
        response = authenticated_client.get('/dashboard_data')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['alerta'] is None
