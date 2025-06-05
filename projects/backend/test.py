from fastapi.testclient import TestClient
from app import app  

client = TestClient(app)

def test_text_null():
    response = client.post("/predict", json={"text": None})
    assert response.status_code == 400
    assert response.json() == {"detail": "El campo 'text' no puede estar vacío o ser null."}

def test_text_empty():
    response = client.post("/predict", json={"text": ""})
    assert response.status_code == 400
    assert response.json() == {"detail": "El campo 'text' no puede estar vacío o ser null."}

def test_text_spaces():
    response = client.post("/predict", json={"text": "   "})
    assert response.status_code == 400
    assert response.json() == {"detail": "El campo 'text' no puede estar vacío o ser null."}

def test_text_valid():
    response = client.post("/predict", json={"text": "Comentario clasificado"})
    assert response.status_code == 200
    json_data = response.json()
    assert "etiqueta" in json_data
    assert "confianza" in json_data

