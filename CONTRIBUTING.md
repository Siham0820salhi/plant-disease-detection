# 🚀 Guide de Contribution - Projet Plant Disease Detection

Bienvenue ! Ce document définit les standards de collaboration et les règles techniques pour assurer la réussite de notre projet MLOps & DataOps. 🎯

---

## 👥 1. L'Équipe et la Stack Technique 🛠️

Chaque membre est responsable d'un maillon de la chaîne MLOps. Voici notre organisation :

| Rôle | Membre | Stack & Responsabilités |
| :--- | :--- | :--- |
| **Product Owner** | **Hasnae EL MIR** | Vision, User Stories, Product Backlog. |
| **Scrum Master** | **Hiba OUAFI** | Agilité (Kanban), Organisation des Sprints, **Tests unitaires (Pytest)**. |
| **Data Engineer (Ingestion)** | **Khansaa BALAKRAFAS** | **dlt, DuckDB**, Kaggle API, Ingestion des données. |
| **Data Engineer (Qualité)** | **Salma ZAMAKHCHARI** | Prétraitement (OpenCV/Pillow), **Great Expectations**. |
| **Orchestration** | **Ibtissam ESSADIKI** | Automatisation des pipelines avec **Dagster**. |
| **ML Engineer** | **Chaimaa AFESS** | Entraînement CNN, Tracking & Registry avec **MLflow**. |
| **Déploiement** | **Oumaima TALBI** | **FastAPI**, Docker, Docker Compose, CI/CD. |
| **Data Analyst** | **Siham SALHI** | EDA, Monitoring (**Evidently AI**), Documentation. |

---

## 🌿 2. Gestion du Code & Git Flow
Pour garantir la stabilité du projet, nous suivons ces règles :
- **Branches** : Protection de `main` 🔒. Toute modification passe par une branche `feature/[nom-tâche]` vers `dev`.
- **Commits** : Nous suivons la convention *Conventional Commits* :
  - `feat:` ✨ (nouvelle fonctionnalité)
  - `fix:` 🐛 (correction de bug)
  - `docs:` 📝 (documentation)
  - `test:` ✅ (tests unitaires/qualité)
  - `ci:` ⚙️ (Docker, GitHub Actions)

## 🧪 3. Qualité et Tests (Mission Hiba)
La qualité n'est pas une option. Avant toute Pull Request :
1. **Linting** : Vérifiez votre code avec **Ruff**.
2. **Tests** : Lancez `pytest` pour valider vos fonctions.
3. **Data Quality** : Vérifiez vos données avec **Great Expectations** (pour P3/P4).

## 🔄 4. Workflow de Validation
- **Pull Request (PR)** : Obligatoire pour fusionner dans `dev` ou `main`.
- **Revue de code** : Chaque PR doit être relue par un autre membre.
- **Validation Finale** : Le Scrum Master valide le merge après succès des tests CI/CD.

## 📅 5. Agilité et Suivi
Nous utilisons l'onglet **Projects** de GitHub pour le suivi Kanban. 
- Déplacez vos tickets de `To Do` ➔ `In Progress` ➔ `Done`.
- Chaque Sprint fait l'objet d'un rapport dans le dossier `docs/reports`.

---
*✍️ Document maintenu par **Hiba OUAFI** (Scrum Master).*
