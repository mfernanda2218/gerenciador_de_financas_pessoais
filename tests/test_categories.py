import pytest


class TestCategories:
    """Testes para CRUD de categorias"""
    
    def test_categories_list(self, authenticated_client, sample_data):
        """Testa listagem de categorias"""
        response = authenticated_client.get('/categories')
        assert response.status_code == 200
        assert b'Alimentacao' in response.data
        assert b'Transporte' in response.data
    
    def test_add_category(self, authenticated_client):
        """Testa adição de categoria"""
        response = authenticated_client.post('/categories/add', data={
            'name': 'Saúde'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Saude' in response.data
    
    def test_add_empty_category(self, authenticated_client):
        """Testa adição de categoria vazia"""
        response = authenticated_client.post('/categories/add', data={
            'name': ''
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_add_duplicate_category(self, authenticated_client, sample_data):
        """Testa adição de categoria duplicada"""
        response = authenticated_client.post('/categories/add', data={
            'name': 'Alimentação'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Categoria ja existe' in response.data
    
    def test_edit_category(self, authenticated_client, sample_data):
        """Testa edição de categoria"""
        response = authenticated_client.post('/category/1/edit', data={
            'name': 'Alimentação Editada'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Alimentacao Editada' in response.data
    
    def test_edit_empty_category(self, authenticated_client, sample_data):
        """Testa edição de categoria com nome vazio"""
        response = authenticated_client.post('/category/1/edit', data={
            'name': ''
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_edit_duplicate_category(self, authenticated_client, sample_data):
        """Testa edição para nome duplicado"""
        response = authenticated_client.post('/category/2/edit', data={
            'name': 'Alimentação'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Ja existe uma categoria com esse nome' in response.data
    
    def test_delete_category(self, authenticated_client, sample_data):
        """Testa exclusão de categoria"""
        response = authenticated_client.post('/category/2/delete', follow_redirects=True)
        
        assert response.status_code == 200
        # Verifica que a categoria foi removida
        response = authenticated_client.get('/categories')
        assert b'Transporte' not in response.data
    
    def test_delete_category_with_transactions(self, authenticated_client, sample_data):
        """Testa exclusão de categoria com transações associadas"""
        # Categoria 1 (Alimentação) tem transação associada
        response = authenticated_client.post('/category/1/delete', follow_redirects=True)
        
        assert response.status_code == 200
        # Categoria deve ser removida e transação fica sem categoria
        response = authenticated_client.get('/categories')
        assert b'Alimentacao' not in response.data
    
    def test_edit_nonexistent_category(self, authenticated_client):
        """Testa edição de categoria inexistente"""
        response = authenticated_client.post('/category/999/edit', data={
            'name': 'Test'
        })
        assert response.status_code == 404
    
    def test_delete_nonexistent_category(self, authenticated_client):
        """Testa exclusão de categoria inexistente"""
        response = authenticated_client.post('/category/999/delete')
        assert response.status_code == 404
