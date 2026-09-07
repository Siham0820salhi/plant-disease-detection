# 🌿 Plant Disease Detection — Détection des maladies des feuilles de plantes

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-En%20développement-yellow.svg)]()
[![MLflow](https://img.shields.io/badge/Tracking-MLflow-0194E2.svg)]()
[![Dagster](https://img.shields.io/badge/Orchestration-Dagster-6f42c1.svg)]()
[![Tests](https://img.shields.io/badge/Tests-pytest-0A9EDC.svg)]()

Projet intégrateur du module **MLOps & DataOps**. Système complet de classification d'images permettant de détecter automatiquement les maladies des feuilles de plantes à partir d'une simple photo, du dataset brut jusqu'au déploiement en production, avec surveillance continue (monitoring + détection de dérive).

---

## 📌 Sommaire

- [Contexte et objectifs](#-contexte-et-objectifs)
- [Dataset](#-dataset)
- [Architecture du projet](#-architecture-du-projet)
- [Structure du dépôt](#-structure-du-dépôt)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [API — Référence des endpoints](#-api--référence-des-endpoints)
- [Monitoring et détection de dérive](#-monitoring-et-détection-de-dérive)
- [Tests](#-tests)
- [Stack technique](#-stack-technique)
- [Organisation Agile](#-organisation-agile)
- [Équipe](#-équipe)
- [Roadmap / Sprints](#-roadmap--sprints)
- [Problèmes connus et pistes d'amélioration](#-problèmes-connus-et-pistes-damélioration)
- [Licence](#-licence)

---

## 🎯 Contexte et objectifs

Les maladies des cultures représentent une cause majeure de pertes agricoles à travers le monde. Une détection précoce et fiable permet aux agriculteurs et agronomes d'agir rapidement (traitement ciblé, isolement des plants) et de limiter la propagation.

Ce projet met en œuvre une chaîne **MLOps & DataOps complète** — de l'ingestion des données brutes jusqu'au modèle déployé et **surveillé en production** — permettant à un utilisateur d'envoyer une photo de feuille et de recevoir en retour :
- la plante concernée,
- la maladie détectée (ou l'état sain),
- un score de confiance.

**Utilisateurs cibles :** agriculteurs, agronomes, coopératives agricoles, applications mobiles de diagnostic agricole.

---

## 📊 Dataset

- **Nom :** [PlantVillage Dataset](https://www.kaggle.com/datasets/emmarex/plantdisease) (Kaggle, auteur : emmarex)
- **Contenu :** 20 638 images de feuilles, réparties en **15 classes**
- **Plantes couvertes :** Tomate, Poivron, Pomme de terre
- **Résolution d'origine :** variable, redimensionnée à 224×224 px lors du prétraitement
- **Taille brute :** ~326 MB

| Statistique | Valeur |
|---|---|
| Nombre total d'images | 20 638 |
| Nombre de classes | 15 |
| Classe la plus représentée | `Tomato__Tomato_YellowLeaf__Curl_Virus` (3208 images) |
| Classe la moins représentée | `Potato___healthy` (152 images) |
| Ratio de déséquilibre | 21,1x |
| Répartition saine / malade | 15,6 % / 84,4 % |

**Split après prétraitement (stratifié par classe) :**

| Ensemble | Images | Pourcentage |
|---|---|---|
| Train | 14 446 | 70 % |
| Validation | 3 096 | 15 % |
| Test | 3 096 | 15 % |

📎 L'analyse exploratoire complète (EDA) est disponible dans [`notebook/eda_plantvillage_complet.ipynb`](notebook/eda_plantvillage_complet.ipynb), avec les graphiques et exports dans [`docs/`](docs/) et [`reports/eda/`](reports/eda/).

> ⚠️ Le dataset n'est **pas versionné** dans ce dépôt (trop volumineux). Voir la section [Installation](#-installation) pour le télécharger.
>
> ⚠️ Après extraction du zip Kaggle, les images se retrouvent dans un sous-dossier `PlantVillage/` (ex. `data/raw/PlantVillage/Tomato_healthy/`). Le pipeline de prétraitement en tient compte — vérifier ce chemin en cas d'erreur `FileNotFoundError`.

---

## 🏗 Architecture du projet

```
Kaggle
   │
   ▼
Ingestion (dlt / DuckDB)                          — P3
   │
   ▼
Prétraitement & qualité (resize, split, GX)       — P4
   │
   ▼
Orchestration (Dagster)                            — P5
   │
   ▼
Entraînement + tracking (MLflow)                    — P6
   │
   ▼
API FastAPI (Docker)                                 — P7
   │  POST /predict, GET /health, GET /metrics
   ▼
Middleware de monitoring                             — P7 + P8
   │
   ├──► logs/predictions.csv (persistance)
   └──► MetricsStore (mémoire, pour /metrics)
   │
   ▼
Détection de dérive (drift)                          — P8
   comparaison data/processed/train vs data/new_data
```

📎 Schéma détaillé et description module par module dans [`docs/architecture.md`](docs/architecture.md).

Le pipeline est piloté par une **orchestration Dagster** qui enchaîne automatiquement : ingestion → prétraitement → entraînement, avec gestion des dépendances et des échecs.

---

## 📂 Structure du dépôt

```
plant-disease-detection/
├── data/
│   ├── raw/                  # Images brutes (non versionné, à télécharger)
│   │   └── PlantVillage/<classe>/*.jpg
│   ├── processed/            # Images prétraitées : train / val / test (non versionné)
│   └── new_data/             # Échantillon simulant de nouvelles photos (pour le drift)
│
├── src/
│   ├── ingestion/             # Téléchargement + chargement des données (dlt, DuckDB)
│   ├── preprocessing/         # Nettoyage, resize, split, augmentation, qualité (Great Expectations)
│   ├── training/               # Entraînement du modèle + tracking MLflow
│   ├── orchestration/          # Assets et schedules Dagster
│   ├── api/                     # API FastAPI
│   │   ├── main.py               # Endpoints /predict, /health, /metrics + middleware
│   │   ├── models.py             # Schémas Pydantic (Prediction, Health, Metrics)
│   │   ├── class_mapping.py      # Mapping classe brute → (plante, maladie) en français
│   │   └── monitoring.py         # MetricsStore : compteurs + persistance CSV
│   └── monitoring/               # Détection de dérive (indépendante de l'API)
│       └── drift.py
│
├── notebook/                     # Notebooks d'exploration (EDA, expérimentation ML)
├── docker/                        # Dockerfile, docker-compose.yml
├── logs/
│   └── predictions.csv            # Historique persistant des prédictions (généré à l'usage)
│
├── reports/
│   ├── eda/                        # Graphiques et exports de l'EDA
│   └── monitoring/                 # Rapports de dérive (ex. Evidently, si généré)
│
├── tests/                           # Tests unitaires (pytest)
│   ├── test_monitoring.py
│   ├── test_metrics.py
│   └── test_drift.py
│
├── .github/workflows/                # Pipelines CI/CD (GitHub Actions)
├── docs/                              # Documentation, schémas, rapports
│   ├── monitoring.md
│   ├── metrics.md
│   ├── drift.md
│   └── architecture.md
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

### Prérequis
- Python 3.11+
- Un compte [Kaggle](https://www.kaggle.com/) avec une clé API (`kaggle.json`)
- Docker (pour le déploiement complet)
- *(Windows uniquement)* Microsoft C++ Build Tools si certaines dépendances (ex. `albumentations`) nécessitent une compilation locale

### 1. Cloner le dépôt

```bash
git clone https://github.com/Siham0820salhi/plant-disease-detection.git
cd plant-disease-detection
```

### 2. Créer l'environnement virtuel

```bash
python -m venv .venv
# Windows
.venv\Scripts\Activate.ps1
# Linux / macOS
source .venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

> Si l'installation groupée échoue à cause d'un package nécessitant une compilation (ex. `stringzilla` sous Windows), installer les packages un par un pour isoler le problème, ou utiliser `pip install --only-binary=:all: <package>`.

### 4. Télécharger le dataset

```bash
kaggle datasets download -d emmarex/plantdisease
```

Décompresser le contenu dans `data/raw/`, de sorte à obtenir la structure `data/raw/PlantVillage/<classe>/<images>`.

---

## 🚀 Utilisation

### Lancer l'EDA

```bash
cd notebook
jupyter notebook eda_plantvillage_complet.ipynb
```

### Lancer le pipeline de prétraitement

```bash
python src/preprocessing/preprocessing.py
python src/preprocessing/augmentation.py
python src/preprocessing/detecter_doublons.py
python -m pytest src/preprocessing/tests/test_qualite_donnees.py -v
python src/preprocessing/validation_gx.py
python src/preprocessing/rapport/rapport_qualite.py
```

Génère `data/processed/{train,val,test}` ainsi que les rapports de qualité dans `reports/`.

### Lancer l'orchestration Dagster

```bash
dagster dev
```
→ interface disponible sur `http://localhost:3000`

### Lancer le suivi MLflow

```bash
mlflow ui
```
→ interface disponible sur `http://localhost:5000`

### Lancer l'API en local

Depuis la racine du projet :

```bash
python -m uvicorn main:app --reload --app-dir src/api
```

L'API est disponible sur `http://127.0.0.1:8000`, avec documentation interactive (Swagger) sur `http://127.0.0.1:8000/docs`.

> ⚠️ Nécessite `python-multipart` pour l'upload de fichiers (`pip install python-multipart`), ainsi que `mlflow` et `tensorflow` pour le chargement et l'inférence du modèle. Sans ces packages, `/health` et `/metrics` fonctionnent normalement, mais `/predict` renverra une erreur 503 (modèle indisponible).

### Lancer avec Docker

```bash
docker-compose up --build
```

---

## 🔌 API — Référence des endpoints

### `GET /health`
Vérifie l'état de l'API et la version du modèle chargé.

```bash
curl.exe http://127.0.0.1:8000/health
```
```json
{"status": "ok", "model_version": "resnet50-v10-production"}
```

### `POST /predict`
Reçoit une image de feuille (`.jpg`, `.jpeg`, `.png`, 5 Mo max) et renvoie un diagnostic.

```bash
curl.exe -X POST "http://127.0.0.1:8000/predict" -F "file=@chemin/vers/une_feuille.jpg"
```
```json
{
  "plante": "Tomate",
  "maladie": "Mildiou (brûlure tardive)",
  "confidence": 0.95
}
```

### `GET /metrics`
Statistiques d'utilisation de l'API, calculées à partir des prédictions déjà traitées.

```bash
curl.exe http://127.0.0.1:8000/metrics
```
```json
{
  "total_requests": 42,
  "average_latency_ms": 336.9,
  "disease_distribution": {
    "Mildiou (brûlure tardive)": 12,
    "Saine (aucune maladie détectée)": 25
  }
}
```

📎 Détails complets : [`docs/metrics.md`](docs/metrics.md)

---

## 📈 Monitoring et détection de dérive

Chaque prédiction traitée par `/predict` est automatiquement :
- comptabilisée en mémoire (pour `/metrics`) ;
- persistée dans `logs/predictions.csv` (timestamp, latence, maladie, confiance), pour ne rien perdre en cas de redémarrage de l'API.

Un script indépendant compare périodiquement les nouvelles images reçues (`data/new_data/`) aux données d'entraînement (`data/processed/train/`), sur la luminosité et les couleurs dominantes, à l'aide d'un test statistique de Kolmogorov-Smirnov :

```bash
python -m src.monitoring.drift
```

```
=== Rapport de derive (drift) ===
luminosite      | p-value=0.7978 | ref_mean=113.66 | new_mean=114.92 | ✅ OK
rouge_moyen     | p-value=0.6898 | ref_mean=116.54 | new_mean=116.95 | ✅ OK
vert_moyen      | p-value=0.4042 | ref_mean=120.37 | new_mean=121.77 | ✅ OK
bleu_moyen      | p-value=0.9265 | ref_mean=104.08 | new_mean=106.04 | ✅ OK
```

📎 Détails complets, méthode et interprétation : [`docs/monitoring.md`](docs/monitoring.md) et [`docs/drift.md`](docs/drift.md)

---

## 🧪 Tests

```bash
python -m pytest tests/ -v
```

Couverture actuelle : **11 tests**, tous liés au monitoring et au drift.

| Fichier | Vérifie |
|---|---|
| `test_monitoring.py` | Le logging en mémoire et l'écriture correcte dans `logs/predictions.csv` |
| `test_metrics.py` | Les calculs de `/metrics` (total, latence moyenne, distribution) |
| `test_drift.py` | La détection de dérive dans les deux cas (identique → OK, très différent → drift détecté) |

D'autres suites de tests (prétraitement, qualité des données, API) sont à la charge des modules correspondants — voir [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## 🛠 Stack technique

| Domaine | Outils |
|---|---|
| Langage | Python 3.11 |
| Ingestion des données | dlt, DuckDB, Kaggle API |
| Transformation & qualité | Pillow, OpenCV, Albumentations, Great Expectations, pytest, scikit-learn |
| Orchestration | Dagster |
| Machine Learning | TensorFlow/Keras (ResNet50, transfer learning) |
| Tracking & Registry | MLflow |
| API & déploiement | FastAPI, Uvicorn, Pydantic, python-multipart, Docker, Docker Compose |
| CI/CD | GitHub Actions, ruff |
| Monitoring & drift | scipy (test de Kolmogorov-Smirnov), CSV, *(Evidently AI en option)* |
| Gestion de projet | GitHub Projects (Kanban), GitHub Issues |

---

## 🤝 Organisation Agile

Le projet est mené sur **1 mois**, en **4 sprints** :

| Sprint | Contenu |
|---|---|
| Sprint 1 | Cadrage, Data Strategy, organisation Agile, pipeline d'ingestion, EDA |
| Sprint 2 | Transformation, qualité des données, tests, orchestration |
| Sprint 3 | Machine Learning, expérimentation, reproductibilité (MLflow) |
| Sprint 4 | FastAPI, Docker, CI/CD, déploiement, monitoring, détection de dérive |

Voir les règles de contribution dans [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## 👥 Équipe

| Rôle | Membre | Responsabilités |
|---|---|---|
| Product Owner | *Hasnae EL MIR* | Vision, User Stories, backlog |
| Scrum Master | *Hiba OUAFI* | Agile, tests pytest |
| Data Engineer — Ingestion | *Khansaa Balakrafas* | dlt, DuckDB |
| Data Engineer — Qualité | *Salma Zamakhchari* | Prétraitement, qualité des données |
| Orchestration | *Ibtissam Essadiki* | Dagster |
| ML Engineer | *Chaimaa Afess* | Modèle CNN, MLflow |
| Déploiement | *Oumaima Talbi* | FastAPI, Docker, CI/CD |
| Data Analyst | *Siham Salhi* | EDA, Monitoring, Drift, Documentation |

---

## 🗺 Roadmap / Sprints

- [x] Sprint 1 — Cadrage et EDA
- [x] Ingestion des données (dlt / DuckDB)
- [x] Prétraitement (resize, split stratifié) — `data/processed/{train,val,test}`
- [x] Middleware de monitoring + endpoint `/metrics`
- [x] Persistance des logs (`logs/predictions.csv`)
- [x] Détection de dérive (drift) avec test statistique
- [x] Tests unitaires monitoring / metrics / drift
- [x] Documentation (`monitoring.md`, `metrics.md`, `drift.md`, `architecture.md`)
- [ ] Augmentation des données (albumentations — bloqué par un problème de compilation Windows, en cours de résolution)
- [ ] Entraînement du modèle et enregistrement MLflow (Model Registry, alias production)
- [ ] Chargement du modèle en production (`mlflow`, `tensorflow` à installer)
- [ ] Dockerisation complète et CI/CD
- [ ] Rapport de dérive Evidently (optionnel)
- [ ] Rapport final et slides de soutenance

---

## ⚠️ Problèmes connus et pistes d'amélioration

- **`albumentations` ne s'installe pas sous Windows sans Build Tools** (dépendance `stringzilla` nécessitant une compilation C++). Solutions : installer les Microsoft C++ Build Tools, ou utiliser `pip install --only-binary=:all: albumentations`.
- **`mlflow` et `tensorflow` ne sont pas encore installés** sur tous les postes de développement — `/predict` renvoie une erreur 503 tant que le modèle n'est pas chargé, mais `/health` et `/metrics` restent fonctionnels.
- **Le drift est actuellement testé avec un échantillon issu de la même distribution** (`data/processed/train`) faute de vraies photos d'utilisateurs — un signal de "pas de drift" est donc attendu tant qu'aucune dérive réelle n'est simulée ou observée.
- **Amélioration future possible** : génération automatique d'un rapport HTML de dérive avec Evidently, et rechargement de l'historique en mémoire depuis `logs/predictions.csv` au démarrage de l'API (actuellement, seule la persistance disque survit à un redémarrage).

---

## 📄 Licence

Projet académique réalisé dans le cadre du module MLOps & DataOps. *(Licence à préciser si besoin — MIT recommandée pour un projet open source.)*
