from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health():
    resp = client.get('/health')
    assert resp.status_code == 200
    assert resp.json() == {'status': 'ok'}

def test_pdf_generation():
    data = {
        'county': 'Harris',
        'petitioner_full_name': 'Jane Doe',
        'respondent_full_name': 'John Doe'
    }
    resp = client.post('/pdf', json=data)
    assert resp.status_code == 200
    assert resp.headers['content-type'] == 'application/zip'
