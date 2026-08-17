# 🌿 Plant Disease Detection — Détection des maladies des feuilles de plantes

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-En%20développement-yellow.svg)]()
[![MLflow](https://img.shields.io/badge/Tracking-MLflow-0194E2.svg)]()
[![Dagster](https://img.shields.io/badge/Orchestration-Dagster-6f42c1.svg)]()

Projet intégrateur du module **MLOps & DataOps**. Système complet de classification d'images permettant de détecter automatiquement les maladies des feuilles de plantes à partir d'une simple photo, du dataset brut jusqu'au déploiement en production.

---

## 📌 Sommaire

- [Contexte et objectifs](#-contexte-et-objectifs)
- [Dataset](#-dataset)
- [Architecture du projet](#-architecture-du-projet)
- [Structure du dépôt](#-structure-du-dépôt)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [Stack technique](#-stack-technique)
- [Organisation Agile](#-organisation-agile)
- [Équipe](#-équipe)
- [Roadmap / Sprints](#-roadmap--sprints)
- [Licence](#-licence)

---

## 🎯 Contexte et objectifs

Les maladies des cultures représentent une cause majeure de pertes agricoles à travers le monde. Une détection précoce et fiable permet aux agriculteurs et agronomes d'agir rapidement (traitement ciblé, isolement des plants) et de limiter la propagation.

Ce projet met en œuvre une chaîne **MLOps & DataOps complète** — de l'ingestion des données brutes jusqu'au modèle déployé et monitoré en production — permettant à un utilisateur d'envoyer une photo de feuille et de recevoir en retour :
- la plante concernée,
- la maladie détectée (ou l'état sain),
- un score de confiance.

**Utilisateurs cibles :** agriculteurs, agronomes, coopératives agricoles, applications mobiles de diagnostic agricole.

---

## 📊 Dataset

- **Nom :** [PlantVillage Dataset](https://www.kaggle.com/datasets/emmarex/plantdisease) (Kaggle, auteur : emmarex)
- **Contenu :** 20 638 images de feuilles, réparties en **15 classes**
- **Plantes couvertes :** Tomate, Poivron, Pomme de terre
- **Résolution :** images uniformisées en 256×256 px
- **Taille :** ~326 MB

| Statistique | Valeur |
|---|---|
| Nombre total d'images | 20 638 |
| Nombre de classes | 15 |
| Classe la plus représentée | `Tomato__Tomato_YellowLeaf__Curl_Virus` (3208 images) |
| Classe la moins représentée | `Potato___healthy` (152 images) |
| Ratio de déséquilibre | 21,1x |
| Répartition saine / malade | 15,6% / 84,4% |

📎 L'analyse exploratoire complète (EDA) est disponible dans [`notebook/eda_plantvillage_complet.ipynb`](notebook/eda_plantvillage_complet.ipynb), avec les graphiques et exports dans [`docs/`](docs/).

> ⚠️ Le dataset n'est **pas versionné** dans ce dépôt (trop volumineux). Voir la section [Installation](#-installation) pour le télécharger.

---

## 🏗 Architecture du projet

```
Kaggle → Ingestion (dlt/DuckDB) → Prétraitement & qualité → Orchestration (Dagster)
   → Entraînement (MLflow) → Modèle enregistré → API FastAPI (Docker)
   → Utilisateur (upload photo) → Prédiction + logs → Monitoring & détection de dérive
```

*(Schéma détaillé disponible dans `docs/architecture.png`)*

Le pipeline est piloté par une **orchestration Dagster** qui enchaîne automatiquement : ingestion → prétraitement → entraînement, avec gestion des dépendances et des échecs.

---

## 📂 Structure du dépôt

```
plant-disease-detection/
├── data/
│   ├── raw/              # Images brutes (non versionné, à télécharger)
│   └── processed/        # Images prétraitées (non versionné)
├── src/
│   ├── ingestion/         # Téléchargement + chargement des données (dlt, DuckDB)
│   ├── preprocessing/     # Nettoyage, resize, augmentation, qualité
│   ├── training/           # Entraînement du modèle + tracking MLflow
│   └── api/                 # API FastAPI (endpoints /predict, /health)
├── notebook/                # Notebooks d'exploration (EDA, expérimentation ML)
├── docker/                  # Dockerfile, docker-compose.yml
├── tests/                    # Tests unitaires (pytest)
├── .github/workflows/        # Pipelines CI/CD (GitHub Actions)
├── docs/                      # Documentation, schémas, graphiques, rapports EDA
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

### Prérequis
- Python 3.11+
- Un compte [Kaggle](https://www.kaggle.com/) avec une clé API (`kaggle.json`)
- Docker (pour le déploiement, Sprint 4)

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

### Lancer l'orchestration Dagster *(à venir — Sprint 2/3)*

```bash
dagster dev
```
→ interface disponible sur `http://localhost:3000`

### Lancer le suivi MLflow *(à venir — Sprint 3)*

```bash
mlflow ui
```
→ interface disponible sur `http://localhost:5000`

### Lancer l'API en local *(à venir — Sprint 4)*

```bash
uvicorn src.api.main:app --reload
```

Exemple de requête de prédiction :

```bash
curl -X POST "http://localhost:8000/predict" \
  -F "file=@chemin/vers/une_feuille.jpg"
```

Réponse attendue :
```json
{
  "plante": "Tomate",
  "maladie": "Mildiou (Late blight)",
  "confidence": 0.95
}
```

Vérifier l'état du service :
```bash
curl http://localhost:8000/health
```

### Lancer avec Docker *(à venir — Sprint 4)*

```bash
docker-compose up --build
```

---

## 🛠 Stack technique

| Domaine | Outils |
|---|---|
| Langage | Python 3.11 |
| Ingestion des données | dlt, DuckDB, Kaggle API |
| Transformation & qualité | Pillow, OpenCV, Albumentations, Great Expectations, pytest |
| Orchestration | Dagster |
| Machine Learning | TensorFlow/Keras ou PyTorch, scikit-learn |
| Tracking & Registry | MLflow |
| API & déploiement | FastAPI, Uvicorn, Pydantic, Docker, Docker Compose |
| CI/CD | GitHub Actions, ruff |
| Monitoring | Evidently AI, scipy, middleware FastAPI |
| Gestion de projet | GitHub Projects (Kanban), GitHub Issues |

---

## 🤝 Organisation Agile

Le projet est mené sur **1 mois**, en **4 sprints** :

| Sprint | Contenu |
|---|---|
| Sprint 1 | Cadrage, Data Strategy, organisation Agile, pipeline d'ingestion |
| Sprint 2 | Transformation, qualité des données, tests, orchestration |
| Sprint 3 | Machine Learning, expérimentation, reproductibilité (MLflow) |
| Sprint 4 | FastAPI, Docker, CI/CD, déploiement, monitoring, observabilité |

Voir les règles de contribution dans [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## 👥 Équipe

| Rôle | Membre | Responsabilités |
|---|---|---|
| Product Owner | *Hasnae EL MIR* | Vision, User Stories, backlog |
| Scrum Master | *Hiba OUAFI* | Agile, tests pytest |
| Data Engineer — Ingestion | *khansaa balakrafas* | dlt, DuckDB |
| Data Engineer — Qualité | *salma zamakhchari* | Prétraitement, qualité des données |
| Orchestration | *Ibtissam ESSADIKI* | Dagster |
| ML Engineer | *chaimaa AFESS* | Modèle CNN, MLflow |
| Déploiement | *Oumaima TALBI* | FastAPI, Docker, CI/CD |
| Data Analyst | *Siham SALHI* | EDA, Monitoring, Documentation |

---

## 🗺 Roadmap / Sprints

- [x] Sprint 1 — Cadrage et EDA
- [ ] Sprint 2 — Transformation, qualité, orchestration
- [ ] Sprint 3 — Entraînement du modèle et MLflow
- [ ] Sprint 4 — API, Docker, CI/CD, monitoring

---

## 📄 Licence

Projet académique réalisé dans le cadre du module MLOps & DataOps. *(Licence à préciser si besoin — MIT recommandée pour un projet open source.)*
