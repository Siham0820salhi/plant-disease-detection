"""
main.py
-------
Application FastAPI pour la détection de maladies des feuilles de plantes.
Endpoint principal : POST /predict — reçoit une image et renvoie un diagnostic.
"""

import random
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from class_mapping import CLASS_MAPPING, parse_class_name
from models import HealthOutput, PredictionOutput

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

ALLOWED_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 Mo

MODEL_VERSION: str = "dummy-v0"

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Plant Disease Detection API",
    description=(
        "API de diagnostic de maladies des feuilles de plantes "
        "(tomate, poivron, pomme de terre) basée sur le dataset PlantVillage."
    ),
    version="0.1.0",
)

# Configuration CORS permissive pour le développement
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _validate_image_file(file: UploadFile, content: bytes) -> None:
    """Valide l'extension et la taille du fichier uploadé.

    Args:
        file: Fichier FastAPI UploadFile.
        content: Contenu binaire déjà lu du fichier.

    Raises:
        HTTPException 422: Si l'extension ou la taille n'est pas valide.
    """
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Format de fichier non supporté : '{suffix}'. "
                f"Extensions acceptées : {', '.join(sorted(ALLOWED_EXTENSIONS))}."
            ),
        )

    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Fichier trop volumineux ({len(content) / 1024 / 1024:.2f} Mo). "
                "La taille maximale autorisée est de 5 Mo."
            ),
        )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/health", response_model=HealthOutput, summary="Vérification de l'état de l'API")
async def health_check() -> HealthOutput:
    """Renvoie l'état de l'API et la version du modèle chargé."""
    return HealthOutput(status="ok", model_version=MODEL_VERSION)


@app.post("/predict", response_model=PredictionOutput, summary="Diagnostic d'une feuille de plante")
async def predict(file: UploadFile = File(..., description="Image de la feuille (.jpg, .jpeg ou .png, max 5 Mo)")) -> PredictionOutput:
    """Reçoit une image de feuille et renvoie un diagnostic (plante + maladie + confiance).

    Args:
        file: Image uploadée par l'utilisateur.

    Returns:
        PredictionOutput avec la plante, la maladie et le score de confiance.
    """
    content: bytes = await file.read()

    # Validation du fichier
    _validate_image_file(file, content)

    # TODO: remplacer par le vrai modèle MLflow (fourni par P6)
    raw_class: str = random.choice(list(CLASS_MAPPING.keys()))
    plante, maladie = parse_class_name(raw_class)
    confidence: float = round(random.uniform(0.6, 0.99), 4)

    return PredictionOutput(plante=plante, maladie=maladie, confidence=confidence)
