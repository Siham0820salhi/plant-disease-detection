# =============================================================================
# Dockerfile — API FastAPI "Plant Disease Detection"
# =============================================================================
# Image de base : python:3.11-slim
#   → slim = image allégée (sans les outils de build inutiles en production)
#   → 3.11 = cohérent avec le venv de dev ; TensorFlow n'est pas encore
#     compatible avec Python 3.12+
#
# Contexte de build : ./api  (défini dans docker-compose.yml)
#   → Tous les COPY ci-dessous sont relatifs au dossier api/
#   → Le requirements.txt ici est api/requirements.txt (léger, dédié à l'API)
#     et NON le requirements.txt racine (lourd : tensorflow, opencv, pandas…)
# =============================================================================

FROM python:3.11-slim

# ---------------------------------------------------------------------------
# Métadonnées de l'image
# ---------------------------------------------------------------------------
LABEL maintainer="Équipe MLOps - Détection maladies des plantes"
LABEL description="API FastAPI pour la détection de maladies des feuilles de plantes"
LABEL version="0.1.0"

# ---------------------------------------------------------------------------
# Variables d'environnement
# ---------------------------------------------------------------------------
# Empêche Python de créer des fichiers .pyc (garde l'image propre)
ENV PYTHONDONTWRITEBYTECODE=1
# Désactive le buffering stdout/stderr (logs visibles en temps réel)
ENV PYTHONUNBUFFERED=1

# ---------------------------------------------------------------------------
# Répertoire de travail
# ---------------------------------------------------------------------------
WORKDIR /app

# ---------------------------------------------------------------------------
# Installation des dépendances
# ---------------------------------------------------------------------------
# On copie d'abord UNIQUEMENT requirements.txt pour profiter du cache Docker :
# si les dépendances n'ont pas changé, cette couche est réutilisée sans
# réinstaller tout pip — même si le code source a changé.
#
# requirements.txt ici = api/requirements.txt (dépendances légères de l'API)
# Pour ajouter mlflow/tensorflow en Phase 4, modifier api/requirements.txt
# et NE PAS toucher au requirements.txt racine (réservé aux autres membres).
COPY requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------------
# Copie du code source de l'API
# ---------------------------------------------------------------------------
# Le contexte de build est ./api, donc "." ici = le dossier api/ sur l'hôte.
# On copie tout à la racine de /app/ (structure à plat) :
#   main.py, class_mapping.py, models.py → /app/*.py
#   Les imports sont donc : from class_mapping import ...
COPY . .

# ---------------------------------------------------------------------------
# Port exposé
# ---------------------------------------------------------------------------
EXPOSE 8000

# ---------------------------------------------------------------------------
# Health check Docker
# ---------------------------------------------------------------------------
# Interroge /health toutes les 30 secondes pour vérifier que l'API répond.
# --interval    : délai entre chaque vérification
# --timeout     : délai maximum pour qu'une vérification réussisse
# --start-period: délai de grâce au démarrage (chargement du modèle, etc.)
# --retries     : échecs consécutifs avant de déclarer le conteneur "unhealthy"
HEALTHCHECK --interval=30s --timeout=10s --start-period=180s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" \
    || exit 1

# ---------------------------------------------------------------------------
# Commande de démarrage
# ---------------------------------------------------------------------------
# --host 0.0.0.0 : OBLIGATOIRE pour que l'API soit accessible depuis l'extérieur
#                  du conteneur (sinon elle n'écoute que sur 127.0.0.1 interne)
# --port 8000    : cohérent avec le EXPOSE ci-dessus
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
