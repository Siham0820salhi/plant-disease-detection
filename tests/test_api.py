from fastapi.testclient import TestClient
# كنعيطو لـ app من الكود ديال أميمة بصح
from src.api.main import app

client = TestClient(app)

def test_health_check():
    """Vérifier que l'API répond 'ok' sur /health (Tâche P2/P7)."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_predict_endpoint_validation():
    """Vérifier que /predict refuse les mauvais formats (Validation P7)."""
    # كنصيفطو ملف ماشي تصويرة (.txt)
    response = client.post(
        "/predict",
        files={"file": ("test.txt", b"not an image", "text/plain")}
    )
    # الـ API خاصو يرفض بـ 422 (Unprocessable Entity)
    assert response.status_code == 422
