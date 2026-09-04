"""
test_metrics.py
----------------
Teste que MetricsStore calcule correctement total_requests,
average_latency_ms et disease_distribution.
"""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src" / "api"))

from monitoring import MetricsStore  # noqa: E402


@pytest.fixture
def store_avec_trois_logs(tmp_path, monkeypatch):
    """MetricsStore avec 3 predictions deja enregistrees, CSV temporaire."""
    import monitoring as monitoring_module

    monkeypatch.setattr(monitoring_module, "LOG_FILE", tmp_path / "predictions.csv")

    store = MetricsStore()
    store.log(response_time_ms=300.0, maladie="Tomato_healthy", confidence=0.98)
    store.log(response_time_ms=400.0, maladie="Tomato_Early_blight", confidence=0.94)
    store.log(response_time_ms=500.0, maladie="Tomato_healthy", confidence=0.91)
    return store


def test_total_requests(store_avec_trois_logs):
    """3 logs doivent donner total_requests = 3."""
    assert store_avec_trois_logs.total_requests == 3


def test_latence_moyenne(store_avec_trois_logs):
    """La latence moyenne de [300, 400, 500] doit etre 400."""
    assert store_avec_trois_logs.average_latency_ms == pytest.approx(400.0)


def test_distribution_maladies(store_avec_trois_logs):
    """La distribution doit compter correctement chaque maladie."""
    distribution = store_avec_trois_logs.disease_distribution
    assert distribution["Tomato_healthy"] == 2
    assert distribution["Tomato_Early_blight"] == 1


def test_metrics_output_vide_sans_requete():
    """Sans aucune requete, as_metrics_output() doit renvoyer des valeurs a zero, pas planter."""
    store = MetricsStore()
    result = store.as_metrics_output()

    assert result["total_requests"] == 0
    assert result["average_latency_ms"] == 0.0
    assert result["disease_distribution"] == {}


def test_metrics_output_format(store_avec_trois_logs):
    """as_metrics_output() doit renvoyer un dict avec les bonnes cles, pret pour l'API."""
    result = store_avec_trois_logs.as_metrics_output()

    assert set(result.keys()) == {"total_requests", "average_latency_ms", "disease_distribution"}
    assert result["total_requests"] == 3
    assert result["average_latency_ms"] == pytest.approx(400.0)