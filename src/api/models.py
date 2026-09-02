"""
models.py
---------
Schémas Pydantic pour les réponses de l'API de détection de maladies.
"""

from pydantic import BaseModel, Field


class PredictionOutput(BaseModel):
    """Résultat du diagnostic renvoyé par l'endpoint /predict."""

    plante: str = Field(..., description="Nom de la plante identifiée (en français).")
    maladie: str = Field(..., description="Maladie détectée ou état de santé (en français).")
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Score de confiance de la prédiction (entre 0 et 1).",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "plante": "Tomate",
                "maladie": "Mildiou (brûlure tardive)",
                "confidence": 0.87,
            }
        }
    }


class HealthOutput(BaseModel):
    """Réponse de l'endpoint /health."""

    status: str = Field(..., description="État de l'API.")
    model_version: str = Field(..., description="Version du modèle chargé.")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "ok",
                "model_version": "dummy-v0",
            }
        }
    }
