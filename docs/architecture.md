# Architecture du projet — Plant Disease Detection

## Vue d'ensemble

Le projet est un pipeline MLOps/DataOps complet de détection de maladies des
feuilles de plantes, du dataset brut jusqu'à une API de diagnostic
surveillée en production. Il est organisé en 8 modules, chacun porté par un
membre de l'équipe.

```
                         UTILISATEUR (agriculteur)
                                  │
                                  │ upload photo.jpg
                                  ▼
                          ┌───────────────┐
                          │    FastAPI    │  (P7)
                          └───────┬───────┘
                                  │
                    ┌─────────────┼──────────────┐
                    ▼             ▼              ▼
               POST /predict  GET /health   GET /metrics
                    │
                    ▼
              ┌──────────┐
              │Middleware│  (P7 + P8)
              │monitoring│
              └────┬─────┘
                    │
                    ▼
              Modèle MLflow  (P6)
                    │
                    ▼
           maladie + confiance
                    │
                    ▼
          Middleware termine
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
  MetricsStore              logs/
  (mémoire)              predictions.csv
        │                       │
        └───────────┬───────────┘
                     ▼
               GET /metrics
```

## Pipeline de données (amont de l'API)

```
Kaggle (PlantVillage)
        │
        ▼
data/raw/PlantVillage/<classe>/*.jpg     ← Ingestion (P3, dlt + DuckDB)
        │
        ▼
data/processed/{train,val,test}/         ← Prétraitement (P4)
   resize 224x224, split stratifié,
   augmentation, contrôle qualité
        │
        ▼
Entraînement du modèle (P6)
   CNN / Transfer Learning
   Tracking + Registry MLflow
        │
        ▼
Modèle chargé par l'API (P7)
   alias "production" dans MLflow
        │
        ▼
POST /predict
```

L'orchestration de bout en bout (ingestion → prétraitement → entraînement)
est gérée par **Dagster** (P5), qui déclenche chaque étape en assets liés
par des dépendances.

## Module Monitoring & Drift (périmètre P8)

C'est la partie qui observe le système **après** le déploiement du modèle,
une fois qu'il reçoit de vraies requêtes.

```
src/
├── api/
│   ├── main.py            (P7)  — endpoints + middleware de monitoring
│   ├── models.py          (P7)  — schémas Pydantic (Prediction, Health, Metrics)
│   ├── class_mapping.py   (P7)  — mapping classe brute → (plante, maladie)
│   └── monitoring.py      (P7+P8) — MetricsStore : compteurs + persistance CSV
│
└── monitoring/
    ├── __init__.py
    └── drift.py           (P8)  — détection de dérive statistique (SciPy)

data/
├── raw/            — images brutes (référence de secours pour le drift)
├── processed/
│   └── train/       — référence principale pour le drift
└── new_data/         — échantillon simulant les nouvelles photos reçues

logs/
└── predictions.csv  — historique persistant de toutes les prédictions

tests/
├── test_monitoring.py  — vérifie le logging (mémoire + CSV)
├── test_metrics.py     — vérifie les calculs de /metrics
└── test_drift.py       — vérifie la détection de drift (cas positif/négatif)

docs/
├── monitoring.md
├── metrics.md
├── drift.md
└── architecture.md   (ce fichier)
```

## Flux détaillé : une requête `/predict`

1. L'utilisateur envoie une image via `POST /predict`.
2. Le middleware `monitoring_middleware` (dans `main.py`) démarre un
   chronomètre avant de laisser passer la requête.
3. FastAPI valide le fichier (extension, taille), prétraite l'image
   (resize 224x224, normalisation ResNet50), puis appelle le modèle
   chargé depuis le MLflow Model Registry.
4. Le modèle renvoie des probabilités par classe ; la classe la plus
   probable est convertie en (plante, maladie) lisible via
   `class_mapping.py`.
5. Le résultat est stocké temporairement dans `request.state.prediction`.
6. Le middleware calcule la durée totale et appelle
   `metrics_store.log(...)`, qui :
   - incrémente les compteurs en mémoire (`MetricsStore`) ;
   - ajoute une ligne dans `logs/predictions.csv`.
7. La réponse (`plante`, `maladie`, `confidence`) est renvoyée à
   l'utilisateur.

## Flux détaillé : `GET /metrics`

Lit directement l'état courant de `MetricsStore` (en mémoire, donc
instantané) et renvoie `total_requests`, `average_latency_ms` et
`disease_distribution`. Ne lit pas le fichier CSV — le CSV sert de
sauvegarde persistante, pas de source pour cet endpoint.

## Flux détaillé : détection de drift

Le script `drift.py` est exécuté **indépendamment** de l'API (en ligne de
commande, ou potentiellement planifié via Dagster à l'avenir) :

1. Recherche un dossier de référence (`data/processed/train`, sinon
   `data/raw` en repli).
2. Calcule 4 caractéristiques (luminosité, moyennes R/G/B) sur un
   échantillon d'images de référence et un échantillon de
   `data/new_data`.
3. Compare les deux distributions par caractéristique avec un test de
   Kolmogorov-Smirnov (`scipy.stats.ks_2samp`).
4. Affiche un rapport indiquant, pour chaque caractéristique, si une
   dérive statistiquement significative est détectée (p-value < 0.05).

Ce script est volontairement découplé de l'API : il n'est pas appelé à
chaque requête (trop coûteux), mais lancé ponctuellement pour auditer la
santé des données reçues face aux données d'entraînement.

## Déploiement (vue Docker/CI-CD, périmètre P7)

```
GitHub
   │  push
   ▼
GitHub Actions (.github/workflows/ci.yml)
   │  lint (ruff) → tests (pytest) → build Docker
   ▼
docker-compose.yml
   ├── FastAPI  (expose /predict, /health, /metrics)
   ├── MLflow
   └── Dagster
```

Les tests lancés en CI incluent `tests/test_monitoring.py`,
`tests/test_metrics.py` et `tests/test_drift.py` — toute régression sur
le monitoring ou le drift est donc détectée avant le déploiement.

## Choix d'architecture notables

- **Stockage en mémoire + CSV plutôt qu'une base de données** : suffisant
  pour la taille et le rythme de requêtes attendus dans ce projet
  académique. Une base de données (ou un outil comme Prometheus) serait
  une évolution naturelle pour un déploiement à plus grande échelle.
- **Référence de drift adaptable** (`processed/train` ou `raw` en repli) :
  permet à P8 d'avancer sans être bloqué par l'avancement du pipeline de
  P3/P4, conformément à la règle anti-blocage du projet.
- **Caractéristiques de drift volontairement simples** (luminosité,
  moyennes RGB) : rapides à calculer sur de grands volumes d'images,
  suffisantes pour un signal de premier niveau. Des caractéristiques plus
  riches (histogrammes de couleur, features extraites par un CNN)
  seraient une amélioration possible.
