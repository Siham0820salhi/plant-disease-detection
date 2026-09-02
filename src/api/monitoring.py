"""
monitoring.py
-------------
Stockage en memoire des metriques de requetes /predict, partage avec P8
pour l'endpoint /metrics et la detection de derive.
"""

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class RequestRecord:
    """Une entree de log pour une requete /predict traitee avec succes."""

    timestamp: str
    response_time_ms: float
    maladie: str
    confidence: float


@dataclass
class MetricsStore:
    """Compteur global en memoire, partage entre P7 (ecriture) et P8 (lecture)."""

    total_requests: int = 0
    total_response_time_ms: float = 0.0
    disease_distribution: Counter = field(default_factory=Counter)
    records: list[RequestRecord] = field(default_factory=list)

    def log(self, response_time_ms: float, maladie: str, confidence: float) -> None:
        """Enregistre une prediction reussie."""
        self.total_requests += 1
        self.total_response_time_ms += response_time_ms
        self.disease_distribution[maladie] += 1
        self.records.append(
            RequestRecord(
                timestamp=datetime.now(timezone.utc).isoformat(),
                response_time_ms=response_time_ms,
                maladie=maladie,
                confidence=confidence,
            )
        )

    @property
    def average_latency_ms(self) -> float:
        """Latence moyenne en millisecondes (0.0 si aucune requete)."""
        if self.total_requests == 0:
            return 0.0
        return self.total_response_time_ms / self.total_requests


# Instance unique, partagee par tout le module (importee telle quelle par P8).
metrics_store = MetricsStore()