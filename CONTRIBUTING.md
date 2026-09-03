# 🚀 Guide de Contribution - Projet Plant Disease Detection

Bienvenue ! Ce document définit les standards de collaboration pour notre équipe de 8 personnes. En tant que Scrum Master (P2), je veille au respect de ces règles.

---

## 📅 1. Organisation du Projet (Scrum)
Chaque membre de l'équipe a un rôle défini selon le plan MLOps :
- **P1 (Hassnae)** : Vision et User Stories.
- **P2 (Hiba)** : Scrum Master, Tests unitaires et Rapports.
- **P3 (Khansae)** : Ingestion (dlt/DuckDB).
- **P4 (Salma)** : Transformation et Qualité (Great Expectations).
- **P5 (Btissam)** : Orchestration avec Dagster.
- **P6 (Chaimae)** : Modèles CNN et MLflow.
- **P7 (Siham)** : FastAPI, Docker et CI/CD.
- **P8 (Oumaia)** : EDA et Monitoring.

## 🌿 2. Gestion des Branches & Git
Pour éviter les conflits, nous suivons cette structure :
- **`main`** : Code stable uniquement.
- **`dev`** : Branche principale de développement.
- **`feature/[votre-tâche]`** : Créez une branche pour chaque module (ex: `feature/api-fastapi`).

### Convention des Commits
- `feat:` (nouvelle fonctionnalité)
- `fix:` (correction)
- `docs:` (documentation)
- `test:` (tests unitaires)

## ✅ 3. Qualité & Tests (Mission de P2)
- **Pytest** : Avant chaque Pull Request, lancez `pytest` pour vérifier vos fonctions.
- **Code Review** : Aucune PR ne sera mergée sans la validation d'un autre membre de l'équipe.
- **Linting** : Utilisez `ruff` ou `flake8` pour garder un code propre.

## 🔄 4. Workflow des Pull Requests
1. Travaillez sur votre branche `feature/`.
2. Ouvrez une Pull Request (PR) vers `dev`.
3. Attendez la validation et le passage des tests CI/CD.
4. Merge vers `main` uniquement en fin de sprint.

---
*Maintenue par Hiba (Scrum Master).*
