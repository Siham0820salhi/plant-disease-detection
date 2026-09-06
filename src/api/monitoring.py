"""
monitoring.py
-------------
Stockage en memoire des metriques de requetes /predict, partage avec P8
pour l'endpoint /metrics et la detection de derive. Chaque prediction est
aussi persistee dans logs/predictions.csv pour ne rien perdre en cas de
redemarrage de l'API.
"""

import csv # pour enregistrement 
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path 

# Racine du projet, calculee depuis ce fichier (src/api/monitoring.py -> remonte de 2 niveaux)
#PROJECT_ROOT = Path(__file__).resolve().parents[2] faut il ne trouve pas le fichier requirment  en remplacer par 
def _find_project_root() -> Path:
    """Cherche la racine du projet en remontant jusqu'à trouver requirements.txt.
    Fonctionne à la fois en local (src/api/monitoring.py -> racine) et dans
    Docker (structure à plat /app/monitoring.py, requirements.txt copié dans /app)."""
    current = Path(__file__).resolve().parent
    for parent in [current, *current.parents]:
        if (parent / "requirements.txt").exists():
            return parent
    return current  # repli de sécurité si jamais requirements.txt est introuvable

PROJECT_ROOT = _find_project_root()
########
LOG_FILE = PROJECT_ROOT / "logs" / "predictions.csv"
CSV_HEADERS = ["timestamp", "latency_ms", "disease", "confidence"]


def _ensure_log_file() -> None:
    """Cree le dossier logs/ et le fichier CSV avec ses en-tetes s'ils n'existent pas."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE.exists():
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)


def _append_to_csv(timestamp: str, latency_ms: float, disease: str, confidence: float) -> None:
    """Ajoute une ligne au fichier CSV. N'interrompt jamais la requete si l'ecriture echoue."""
    try:
        _ensure_log_file()
        with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, round(latency_ms, 2), disease, confidence])
    except Exception:
        # Le monitoring ne doit jamais faire planter une requete utilisateur.
        pass
######

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
        """Enregistre une prediction reussie, en memoire ET dans logs/predictions.csv."""
        timestamp = datetime.now(timezone.utc).isoformat()

        self.total_requests += 1
        self.total_response_time_ms += response_time_ms
        self.disease_distribution[maladie] += 1
        self.records.append(
            RequestRecord(
                timestamp=timestamp,
                response_time_ms=response_time_ms,
                maladie=maladie,
                confidence=confidence,
            )
        )

        _append_to_csv(timestamp, response_time_ms, maladie, confidence)

    @property
    def average_latency_ms(self) -> float:
        """Latence moyenne en millisecondes (0.0 si aucune requete)."""
        if self.total_requests == 0:
            return 0.0
        return self.total_response_time_ms / self.total_requests

    def as_metrics_output(self) -> dict:
        """Formate les métriques pour l'endpoint GET /metrics."""
        return {
            "total_requests": self.total_requests,
            "average_latency_ms": round(self.average_latency_ms, 2),
            "disease_distribution": dict(self.disease_distribution),
        }


# Instance unique, partagee par tout le module (importee telle quelle par P8).
metrics_store = MetricsStore()