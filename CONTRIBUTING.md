# 🚀 Guide de Contribution - Projet Plant Disease Detection

Ce document est la référence pour tous les membres de l'équipe (P1 à P8). Il définit les standards techniques et organisationnels pour assurer la réussite de notre projet MLOps & DataOps.

---

## 1. 📅 Organisation Agile (Scrum)
En tant que **Scrum Master**, je veille au respect du cadre de travail :
- **Tableau Kanban** : Toutes les tâches doivent être répertoriées dans l'onglet "Projects" de GitHub.
- **États des tâches** : Chaque membre doit déplacer sa carte de `To Do` ➔ `In Progress` ➔ `Review` ➔ `Done`.
- **Sprints** : Le projet est divisé en 3 Sprints techniques. À la fin de chaque sprint, un compte-rendu sera archivé dans le dossier `docs/reports`.

## 2. 🌿 Gestion des Branches & Git Flow
Pour éviter tout conflit sur la branche principale :
- **`main`** : Code de production uniquement. Protection activée (pas de push direct).
- **`dev`** : Branche principale de développement.
- **`feature/[nom-de-la-tâche]`** : Créez une branche pour chaque User Story (ex: `feature/api-fastapi`, `feature/eda-analysis`).

### Format des Messages de Commit
Nous utilisons la convention **Conventional Commits** :
- `feat:` (nouvelle fonctionnalité)
- `fix:` (correction de bug)
- `docs:` (documentation)
- `test:` (ajout de tests unitaires/qualité)
- `refactor:` (nettoyage du code sans changement de logique)
- `ci:` (modifications liées à GitHub Actions ou Docker)

## 3. 🛠 Environnement de Travail
Avant de commencer à coder, assurez-vous de :
1. Cloner le repository : `git clone [URL_DU_REPO]`
2. Créer un environnement virtuel : `python -m venv venv`
3. Installer les dépendances : `pip install -r requirements.txt`

## 4. ✅ Qualité du Code & Tests
La qualité est l'affaire de tous, sous la supervision de la **Personne 2 (Hiba)** :

### Linting & Formatage
- Nous utilisons **Ruff** ou **Flake8** pour vérifier la conformité du code Python (PEP8).
- Vérifiez votre code avant chaque commit.

### Tests Unitaires (Pytest)
- Aucun code ne sera accepté sans test associé.
- Emplacement : Tous les tests doivent être dans le dossier `/tests`.
- Commande à lancer : `pytest`

### Qualité des Données (Great Expectations)
- Les pipelines de données (P3 et P4) doivent intégrer des checks de qualité pour éviter les données corrompues.

## 5. 🔄 Workflow de Validation (Pull Requests)
1. Ouvrez une **Pull Request (PR)** dès que votre branche est prête.
2. Décrivez brièvement vos changements.
3. **Revue de code** : Au moins un autre membre de l'équipe doit relire et approuver le code.
4. **Validation finale** : Le Scrum Master valide le merge après s'être assuré que les tests CI/CD (GitHub Actions) sont au vert.

---
*Maintenu par Hiba (Scrum Master).*
