"""
main.py
-------
Application FastAPI pour la détection de maladies des feuilles de plantes.
Endpoint principal : POST /predict — reçoit une image et renvoie un diagnostic.
"""

import io
import logging
import os
import time
from pathlib import Path
from typing import Any

import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

try:
    from api.class_mapping import CLASS_MAPPING, parse_class_name
    from api.models import HealthOutput, PredictionOutput
    from api.monitoring import metrics_store
except ImportError:
    from class_mapping import CLASS_MAPPING, parse_class_name
    from models import HealthOutput, PredictionOutput
    from monitoring import metrics_store

logging.basicConfig(level=logging.INFO)

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

ALLOWED_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 Mo
MODEL_URI: str = "models:/plant-disease-classifier@production"
MODEL_VERSION: str = "resnet50-v10-production"

# Cet ordre doit rester synchronise avec P6 : Keras le determine par le tri
# alphabetique des dossiers de classes dans data/processed/train/.
CLASS_NAMES: list[str] = sorted(CLASS_MAPPING.keys())

logger = logging.getLogger(__name__)
model: Any = None
model_loaded: bool = False

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Charge le modele MLflow au demarrage sans bloquer le lancement de l'API."""
    global model, model_loaded

    try:
        import mlflow
        from mlflow.tracking import MlflowClient

        mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))

        # Resolution manuelle en deux etapes : mlflow.pyfunc.load_model() ne
        # delegue pas correctement quand l'alias pointe vers un "Logged Model"
        # (source de la forme "models:/m-<id>"), ce qui provoque une erreur
        # "No such artifact: ''". On resout donc l'alias nous-memes, puis on
        # charge directement via le model_id resolu.
        client = MlflowClient()
        model_version = client.get_model_version_by_alias(
            "plant-disease-classifier", "production"
        )
        model = mlflow.pyfunc.load_model(model_version.source)
        model_loaded = True
        logger.info(
            "Modele MLflow charge avec succes : version=%s source=%s",
            model_version.version,
            model_version.source,
        )
    except Exception:
        model = None
        model_loaded = False
        logger.exception("Impossible de charger le modele MLflow %s", MODEL_URI)

    yield


app = FastAPI(
    title="Plant Disease Detection API",
    description=(
        "API de diagnostic de maladies des feuilles de plantes "
        "(tomate, poivron, pomme de terre) basée sur le dataset PlantVillage."
    ),
    version="0.1.0",
    lifespan=lifespan,
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


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """Prepare une image pour l'inference ResNet50."""
    from tensorflow.keras.applications.resnet50 import preprocess_input

    with Image.open(io.BytesIO(image_bytes)) as image:
        image_rgb = image.convert("RGB").resize((224, 224), Image.Resampling.LANCZOS)

    image_array = np.asarray(image_rgb, dtype=np.float32)
    image_array = preprocess_input(image_array)
    return image_array.reshape((1, 224, 224, 3))


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
    return HealthOutput(
        status="ok",
        model_version=MODEL_VERSION if model_loaded else "unavailable",
    )


@app.post("/predict", response_model=PredictionOutput, summary="Diagnostic d'une feuille de plante")
async def predict(file: UploadFile = File(..., description="Image de la feuille (.jpg, .jpeg ou .png, max 5 Mo)")) -> PredictionOutput:  # noqa: B008
    """Reçoit une image de feuille et renvoie un diagnostic (plante + maladie + confiance).

    Args:
        file: Image uploadée par l'utilisateur.

    Returns:
        PredictionOutput avec la plante, la maladie et le score de confiance.
    """
    start_time = time.perf_counter()
    content: bytes = await file.read()

    # Validation du fichier
    _validate_image_file(file, content)

    if not model_loaded or model is None:
        raise HTTPException(status_code=503, detail="Modèle non disponible")

    try:
        image_batch = preprocess_image(content)
        predictions = np.asarray(model.predict(image_batch))
        probabilities = predictions.reshape(-1)
        if probabilities.size != len(CLASS_NAMES):
            raise ValueError(
                f"Le modèle a renvoyé {probabilities.size} probabilités, "
                f"{len(CLASS_NAMES)} attendues."
            )
    except Exception as exc:
        logger.exception("Echec de l'inference du modele MLflow")
        raise HTTPException(status_code=500, detail="Échec de l'inférence du modèle") from exc

    class_index = int(np.argmax(probabilities))
    raw_class = CLASS_NAMES[class_index]
    plante, maladie = parse_class_name(raw_class)
    confidence = float(probabilities[class_index])

    response_time_ms = (time.perf_counter() - start_time) * 1000  
    metrics_store.log(response_time_ms, maladie, confidence)  

    return PredictionOutput(plante=plante, maladie=maladie, confidence=confidence)
