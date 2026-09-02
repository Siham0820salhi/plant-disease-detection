"""
test_predict.py
---------------
Tests pytest pour l'endpoint POST /predict de l'API Plant Disease Detection.
"""

import io

import pytest
from PIL import Image
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_fake_image_bytes(color: tuple[int, int, int] = (255, 0, 0), size: tuple[int, int] = (100, 100)) -> bytes:
    """Génère une image JPEG factice en mémoire.

    Args:
        color: Couleur RGB de l'image (défaut : rouge).
        size: Dimensions (largeur, hauteur) en pixels.

    Returns:
        Contenu binaire d'une image JPEG.
    """
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf.read()


# ---------------------------------------------------------------------------
# Tests — cas nominal
# ---------------------------------------------------------------------------


def test_predict_returns_200_with_valid_image() -> None:
    """POST /predict avec une image JPEG valide doit retourner HTTP 200."""
    image_bytes = _make_fake_image_bytes()
    response = client.post(
        "/predict",
        files={"file": ("test_leaf.jpg", image_bytes, "image/jpeg")},
    )
    assert response.status_code == 200


def test_predict_response_contains_required_keys() -> None:
    """La réponse de /predict doit contenir les clés 'plante', 'maladie' et 'confidence'."""
    image_bytes = _make_fake_image_bytes()
    response = client.post(
        "/predict",
        files={"file": ("test_leaf.jpg", image_bytes, "image/jpeg")},
    )
    data = response.json()
    assert "plante" in data
    assert "maladie" in data
    assert "confidence" in data


def test_predict_confidence_in_valid_range() -> None:
    """Le score de confiance renvoyé doit être compris entre 0.0 et 1.0."""
    image_bytes = _make_fake_image_bytes()
    response = client.post(
        "/predict",
        files={"file": ("test_leaf.jpg", image_bytes, "image/jpeg")},
    )
    data = response.json()
    assert 0.0 <= data["confidence"] <= 1.0


def test_predict_accepts_png_image() -> None:
    """POST /predict doit aussi accepter les images au format PNG."""
    img = Image.new("RGB", (80, 80), color=(0, 128, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    response = client.post(
        "/predict",
        files={"file": ("feuille.png", buf.read(), "image/png")},
    )
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Tests — cas d'erreur
# ---------------------------------------------------------------------------


def test_predict_rejects_non_image_file() -> None:
    """POST /predict avec un fichier .txt doit retourner HTTP 422."""
    fake_text = b"Ceci n'est pas une image."
    response = client.post(
        "/predict",
        files={"file": ("document.txt", fake_text, "text/plain")},
    )
    assert response.status_code == 422


def test_predict_rejects_file_too_large() -> None:
    """POST /predict avec un fichier dépassant 5 Mo doit retourner HTTP 422."""
    # Génère un contenu dépassant 5 Mo avec une extension valide
    oversized_content = b"A" * (5 * 1024 * 1024 + 1)
    response = client.post(
        "/predict",
        files={"file": ("big_image.jpg", oversized_content, "image/jpeg")},
    )
    assert response.status_code == 422


def test_predict_error_detail_non_image() -> None:
    """Le message d'erreur pour un fichier non-image doit mentionner le format."""
    fake_text = b"data"
    response = client.post(
        "/predict",
        files={"file": ("rapport.pdf", fake_text, "application/pdf")},
    )
    assert response.status_code == 422
    detail = response.json().get("detail", "")
    assert ".pdf" in detail or "supporté" in detail or "Extensions" in detail
