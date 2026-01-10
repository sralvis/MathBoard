import pytest
from app import app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_evaluate_success(client):
    response = client.post('/evaluate', json={'expression': '1 + 1'})
    data = json.loads(response.data)
    assert response.status_code == 200
    assert float(data['result']) == 2.0

def test_evaluate_no_expression(client):
    response = client.post('/evaluate', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == 'No expression provided'

def test_evaluate_invalid_expression(client):
    response = client.post('/evaluate', json={'expression': '1 +'})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'Invalid expression' in data['error']
