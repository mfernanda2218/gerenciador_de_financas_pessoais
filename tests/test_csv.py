import pytest
import io
import csv
from datetime import datetime


class TestCSV:
    """Testes para importação/exportação CSV"""
    
    def test_export_csv_empty(self, authenticated_client):
        """Testa exportação CSV sem dados"""
        response = authenticated_client.get('/export_csv')
        assert response.status_code == 200
        assert response.content_type == 'text/csv'
        
        # Verificar cabeçalho do CSV
        csv_data = response.data.decode('utf-8')
        assert 'date,description,amount,type,category' in csv_data
    
    def test_export_csv_with_data(self, authenticated_client, sample_data):
        """Testa exportação CSV com dados"""
        response = authenticated_client.get('/export_csv')
        assert response.status_code == 200
        
        csv_data = response.data.decode('utf-8')
        assert 'Supermercado' in csv_data
        assert 'Salario' in csv_data
        assert '200.0' in csv_data
        assert '3000.0' in csv_data
    
    def test_export_csv_filtered(self, authenticated_client, sample_data):
        """Testa exportação CSV com filtros"""
        response = authenticated_client.get('/export_csv?month=1&year=2024')
        assert response.status_code == 200
        
        csv_data = response.data.decode('utf-8')
        assert 'Supermercado' in csv_data
        assert 'Salario' in csv_data
    
    def test_export_csv_filter_by_type(self, authenticated_client, sample_data):
        """Testa exportação CSV filtrado por tipo"""
        response = authenticated_client.get('/export_csv?type=despesa')
        assert response.status_code == 200
        
        csv_data = response.data.decode('utf-8')
        assert 'Supermercado' in csv_data
        assert 'Salario' not in csv_data
    
    def test_import_csv_success(self, authenticated_client):
        """Testa importação CSV bem-sucedida"""
        # Criar CSV em memória
        csv_content = """date,description,amount,type,category
2024-01-15,Test Import,100.50,despesa,Test Category
2024-01-20,Test Income,500.00,receita,"""
        
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        csv_file.name = 'test.csv'
        
        response = authenticated_client.post('/import_csv', data={
            'file': (csv_file, 'test.csv')
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'CSV importado com sucesso'
    
    def test_import_csv_with_existing_category(self, authenticated_client, sample_data):
        """Testa importação CSV com categoria existente"""
        csv_content = """date,description,amount,type,category
2024-01-25,Test Import,50.00,despesa,Alimentação"""
        
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        csv_file.name = 'test.csv'
        
        response = authenticated_client.post('/import_csv', data={
            'file': (csv_file, 'test.csv')
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'CSV importado com sucesso'
    
    def test_import_csv_creates_new_category(self, authenticated_client):
        """Testa importação CSV cria nova categoria"""
        csv_content = """date,description,amount,type,category
2024-01-15,Test Import,100.50,despesa,Nova Categoria"""
        
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        csv_file.name = 'test.csv'
        
        response = authenticated_client.post('/import_csv', data={
            'file': (csv_file, 'test.csv')
        })
        
        assert response.status_code == 200
        
        # Verificar que categoria foi criada
        response = authenticated_client.get('/categories')
        assert 'Nova Categoria' in response.data.decode('utf-8')
    
    def test_import_csv_invalid_format(self, authenticated_client):
        """Testa importação CSV com formato inválido"""
        csv_content = """invalid,csv,format
test,data"""
        
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        csv_file.name = 'invalid.csv'
        
        response = authenticated_client.post('/import_csv', data={
            'file': (csv_file, 'invalid.csv')
        })
        
        # Deve retornar erro 500 devido ao formato inválido
        assert response.status_code == 500
    
    def test_import_csv_missing_file(self, authenticated_client):
        """Testa importação CSV sem arquivo"""
        response = authenticated_client.post('/import_csv', data={})
        
        assert response.status_code == 400
    
    def test_export_csv_attachment(self, authenticated_client, sample_data):
        """Testa exportação CSV como attachment"""
        response = authenticated_client.get('/export_csv')
        assert response.status_code == 200
        
        # Verificar headers de download
        content_disposition = response.headers.get('Content-Disposition')
        assert 'attachment' in content_disposition
        assert 'relatorio.csv' in content_disposition
