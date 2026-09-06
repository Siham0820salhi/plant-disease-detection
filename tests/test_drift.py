"""
test_drift.py
-------------
Teste detect_drift() : pas de drift quand reference == current,
drift detecte quand les distributions sont tres differentes.
Teste les deux cas attendus par le prof : référence = actuel (pas de drift) et référence très différente (drift détecté) :

"""

import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src" / "monitoring"))

from drift import detect_drift, FEATURE_NAMES  # noqa: E402


def test_pas_de_drift_si_memes_distributions():
    """Reference et current identiques -> aucune feature ne doit signaler un drift."""
    np.random.seed(42)
    reference = np.random.normal(loc=120, scale=10, size=(200, 4))
    current = np.random.normal(loc=120, scale=10, size=(200, 4))

    results = detect_drift(reference, current)

    for feature in FEATURE_NAMES:
        assert results[feature]["drift_detected"] is False, (
            f"Drift detecte a tort sur {feature}"
        )


def test_drift_detecte_si_distributions_tres_differentes():
    """Reference et current tres eloignees -> toutes les features doivent signaler un drift."""
    np.random.seed(42)
    reference = np.random.normal(loc=120, scale=10, size=(200, 4))
    current = np.random.normal(loc=220, scale=10, size=(200, 4))  # decalage fort

    results = detect_drift(reference, current)

    for feature in FEATURE_NAMES:
        assert results[feature]["drift_detected"] is True, (
            f"Drift non detecte alors qu'il devrait l'etre sur {feature}"
        )


def test_resultat_contient_toutes_les_cles_attendues():
    """Chaque feature doit avoir ks_statistic, p_value, drift_detected, reference_mean, new_mean."""
    reference = np.random.normal(loc=100, scale=5, size=(50, 4))
    current = np.random.normal(loc=100, scale=5, size=(50, 4))

    results = detect_drift(reference, current)

    expected_keys = {"ks_statistic", "p_value", "drift_detected", "reference_mean", "new_mean"}
    for feature in FEATURE_NAMES:
        assert set(results[feature].keys()) == expected_keys