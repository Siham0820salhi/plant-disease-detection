"""
conftest.py
-----------
Fixtures pytest partagées : simule un modele MLflow charge en memoire,
pour ne pas dependre d'un vrai serveur MLflow pendant les tests.
"""

import numpy as np
import pytest

import api.main as main_module


class _FakeModel:
    """Modele factice : renvoie toujours la classe d'indice 0 avec confiance 1.0."""

    def predict(self, batch: np.ndarray) -> np.ndarray:
        n_classes = len(main_module.CLASS_NAMES)
        probs = np.zeros((1, n_classes), dtype=np.float32)
        probs[0, 0] = 1.0
        return probs


@pytest.fixture(autouse=True)
def fake_model_loaded(monkeypatch: pytest.MonkeyPatch):
    """Simule un modele charge avec succes pour tous les tests par defaut.

    Les tests qui veulent tester le cas 'modele non disponible' peuvent
    surcharger ce comportement localement (voir test_health.py).
    """
    monkeypatch.setattr(main_module, "model", _FakeModel())
    monkeypatch.setattr(main_module, "model_loaded", True)
    yield