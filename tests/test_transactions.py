import pytest
from datetime import datetime


class TestTransactions:
    """Testes para CRUD de transações"""
    
    def test_add_transaction_get(self, authenticated_client):
        """Testa acesso à página de adicionar transação"""
        response = authenticated_client.get('/add_transaction')
        assert response.status_code == 200
        assert b'Adicionar transacao' in response.data
    
    def test_add_transaction_post(self, authenticated_client):
        """Testa adicionar transação via POST"""
        response = authenticated_client.post('/add_transaction', data={
            'date': '2024-01-15',
            'description': 'Test Transaction',
            'amount': '100.50',
            'type': 'despesa',
            'category': ''
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Gerenciador de Financas' in response.data
    
    def test_add_transaction_with_category(self, authenticated_client, sample_data):
        """Testa adicionar transação com categoria"""
        response = authenticated_client.post('/add_transaction', data={
            'date': '2024-01-16',
            'description': 'Supermercado',
            'amount': '200.00',
            'type': 'despesa',
            'category': '1'  # Alimentação
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_transactions_list(self, authenticated_client, sample_data):
        """Testa listagem de transações"""
        response = authenticated_client.get('/transactions')
        assert response.status_code == 200
        assert b'Supermercado' in response.data
        assert b'Salario' in response.data
    
    def test_transactions_filter_by_month(self, authenticated_client, sample_data):
        """Testa filtro de transações por mês"""
        response = authenticated_client.get('/transactions?month=1')
        assert response.status_code == 200
        assert b'Supermercado' in response.data
    
    def test_transactions_filter_by_type(self, authenticated_client, sample_data):
        """Testa filtro de transações por tipo"""
        response = authenticated_client.get('/transactions?type=despesa')
        assert response.status_code == 200
        assert b'Supermercado' in response.data
        assert b'Salario' not in response.data
    
    def test_edit_transaction_get(self, authenticated_client, sample_data):
        """Testa acesso à página de editar transação"""
        response = authenticated_client.get('/transaction/1/edit')
        assert response.status_code == 200
        assert b'Editar' in response.data
    
    def test_edit_transaction_post(self, authenticated_client, sample_data):
        """Testa edição de transação"""
        response = authenticated_client.post('/transaction/1/edit', data={
            'date': '2024-01-15',
            'description': 'Supermercado Editado',
            'amount': '250.00',
            'type': 'despesa',
            'category': ''
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Supermercado Editado' in response.data
    
    def test_edit_transaction_invalid_data(self, authenticated_client, sample_data):
        """Testa edição com dados inválidos"""
        response = authenticated_client.post('/transaction/1/edit', data={
            'date': 'invalid-date',
            'description': 'Test',
            'amount': '100',
            'type': 'despesa',
            'category': ''
        })
        
        assert response.status_code == 200
        assert b'Data invalida' in response.data
    
    def test_delete_transaction(self, authenticated_client, sample_data):
        """Testa exclusão de transação"""
        response = authenticated_client.post('/transaction/1/delete', follow_redirects=True)
        
        assert response.status_code == 200
        # Verifica que a transação foi removida
        response = authenticated_client.get('/transactions')
        assert b'Supermercado' not in response.data
    
    def test_edit_nonexistent_transaction(self, authenticated_client):
        """Testa edição de transação inexistente"""
        response = authenticated_client.get('/transaction/999/edit')
        assert response.status_code == 404
    
    def test_delete_nonexistent_transaction(self, authenticated_client):
        """Testa exclusão de transação inexistente"""
        response = authenticated_client.post('/transaction/999/delete')
        assert response.status_code == 404
