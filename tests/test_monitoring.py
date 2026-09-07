"""
test_monitoring.py
-------------------
Teste que metrics_store.log() enregistre correctement une prediction,
en memoire et dans logs/predictions.csv.
Teste que le middleware/logger enregistre bien une requête (en mémoire + CSV) :
"""

import csv
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src" / "api"))

from monitoring import LOG_FILE, MetricsStore  # noqa: E402


@pytest.fixture
def fresh_store(tmp_path, monkeypatch):
    """Fournit un MetricsStore neuf, avec un fichier CSV temporaire (n'affecte pas le vrai logs/)."""
    import monitoring as monitoring_module

    temp_log_file = tmp_path / "predictions.csv"
    monkeypatch.setattr(monitoring_module, "LOG_FILE", temp_log_file)

    store = MetricsStore()
    return store, temp_log_file


def test_log_cree_une_entree_en_memoire(fresh_store):
    """Un appel a log() doit incrementer total_requests et enregistrer les infos."""
    store, _ = fresh_store

    store.log(response_time_ms=250.0, maladie="Mildiou", confidence=0.9)

    assert store.total_requests == 1
    assert store.disease_distribution["Mildiou"] == 1
    assert len(store.records) == 1
    assert store.records[0].maladie == "Mildiou"
    assert store.records[0].confidence == 0.9


def test_log_cree_le_fichier_csv(fresh_store):
    """Un appel a log() doit creer logs/predictions.csv avec les bons en-tetes et donnees."""
    store, temp_log_file = fresh_store

    store.log(response_time_ms=300.0, maladie="Tache bactérienne", confidence=0.87)

    assert temp_log_file.exists()

    with open(temp_log_file, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

    assert rows[0] == ["timestamp", "latency_ms", "disease", "confidence"]
    assert len(rows) == 2  # en-tete + 1 ligne
    assert rows[1][2] == "Tache bactérienne"
    assert rows[1][3] == "0.87"


def test_plusieurs_requetes_saccumulent(fresh_store):
    """Plusieurs appels a log() doivent tous etre enregistres, sans se remplacer."""
    store, temp_log_file = fresh_store

    store.log(response_time_ms=100.0, maladie="Saine", confidence=0.99)
    store.log(response_time_ms=200.0, maladie="Mildiou", confidence=0.85)
    store.log(response_time_ms=300.0, maladie="Mildiou", confidence=0.80)

    assert store.total_requests == 3
    assert store.disease_distribution["Mildiou"] == 2
    assert store.disease_distribution["Saine"] == 1

    with open(temp_log_file, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
    assert len(rows) == 4  # en-tete + 3 lignes