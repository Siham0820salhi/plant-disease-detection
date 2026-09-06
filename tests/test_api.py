from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_predict_endpoint_validation():
    response = client.post(
        "/predict",
        files={"file": ("test.txt", b"not an image", "text/plain")}
    )
    assert response.status_code == 422

def test_predict_file_too_large():
    big_file = b"0" * (6 * 1024 * 1024) 
    response = client.post(
        "/predict",
        files={"file": ("large_image.jpg", big_file, "image/jpeg")}
    )
    assert response.status_code == 422
    assert "Fichier trop volumineux" in response.json()["detail"]
