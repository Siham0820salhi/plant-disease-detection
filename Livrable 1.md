# 📘 Livrable 1 — Gestion Agile du projet

> **Projet : Plant Disease Detection**  
> **Méthodologie : Scrum**  

---

## 🎯 1. Présentation du projet

Le projet **Plant Disease Detection** consiste à développer une solution de détection et de classification des maladies des plantes à partir d'images.

Le projet suit une démarche **Agile Scrum**, organisée en quatre sprints. Le suivi du travail est assuré à travers **GitHub Issues, Milestones et Project Board**, afin de faciliter la répartition des tâches, la collaboration et le suivi de l'avancement.

### 🧩 Objectifs principaux

- 📥 Ingérer et préparer le dataset PlantVillage.
- 🧹 Contrôler la qualité et prétraiter les données.
- 🔄 Automatiser le pipeline Data avec Dagster.
- 🤖 Entraîner et évaluer les modèles de classification.
- 🧪 Suivre les expérimentations avec MLflow.
- 🚀 Exposer le modèle avec une API FastAPI.
- 🐳 Conteneuriser l'application avec Docker.
- 📊 Mettre en place le monitoring et les tests.

---

# 📋 2. Product Backlog

Le Product Backlog regroupe les User Stories nécessaires à la réalisation du produit.

| ID | User Story | Domaine | Sprint | Statut |
|---|---|---|---|---|
| US01 | Définir la vision du produit | Documentation / PM | Sprint 1 | ✅ Terminée |
| US02 | Définir la stratégie de données | Documentation / PM | Sprint 1 | ✅ Terminée |
| US03 | Définir et prioriser le Product Backlog | Documentation / PM | Sprint 1 | ✅ Terminée |
| US04 | Valider le produit avec des tests d'acceptation | Documentation / PM | Sprint 1 | ✅ Terminée |
| US05 | Tester le prétraitement des images | Testing / QA | Sprint 2 | ✅ Terminée |
| US06 | Tester le modèle | Testing / QA | Sprint 3 | ✅ Terminée |
| US07 | Tester l'API | Testing / QA | Sprint 4 | ✅ Terminée |
| US08 | Ingérer le dataset PlantVillage | Data Engineering | Sprint 1 | ✅ Terminée |
| US09 | Vérifier la qualité des images | Data Engineering | Sprint 1 | ✅ Terminée |
| US10 | Prétraiter les images | Data Engineering | Sprint 2 | ✅ Terminée |
| US11 | Augmenter les données d'entraînement | Data Engineering | Sprint 2 | ✅ Terminée |
| US12 | Vérifier la répartition des classes | Data Engineering | Sprint 2 | ✅ Terminée |
| US13 | Orchestrer le pipeline avec Dagster | Orchestration | Sprint 2 | ✅ Terminée |
| US14 | Entraîner le modèle de classification | ML Engineering | Sprint 3 | ✅ Terminée |
| US15 | Évaluer le modèle | ML Engineering | Sprint 3 | ✅ Terminée |
| US16 | Tracker les expériences avec MLflow | ML Engineering | Sprint 3 | ✅ Terminée |
| US17 | Exposer le modèle avec une API FastAPI | DevOps / Deployment | Sprint 3 | ✅ Terminée |
| US18 | Déployer l'application avec Docker | DevOps / Deployment | Sprint 3 | ✅ Terminée |
| US19 | Réaliser l'analyse exploratoire des données | Analytics / EDA | Sprint 1 | ✅ Terminée |
| US20 | Mettre en place le monitoring du modèle | Data Analysis / Monitoring | Sprint 4 | ✅ Terminée |
| US21 | Monitoring | Data Analysis / Monitoring | Sprint 4 | ✅ Terminée |
| US22 | Acceptance testing | Testing / QA | Sprint 4 | ✅ Terminée |
| US23 | Orchestrer le pipeline avec Dagster | Orchestration | Sprint 2 | ✅ Terminée |

> ℹ️ **Remarque :** US13 et US23 correspondent à deux Issues GitHub distinctes concernant l'orchestration avec Dagster. Elles sont conservées afin de refléter fidèlement le suivi GitHub du projet.

---

# 👤 3. User Stories

## 🟢 Sprint 1 — Cadrage, Data Strategy & Ingestion

🎯 **Objectif :** établir les bases du projet, définir la stratégie de données et mettre en place l'ingestion ainsi que l'analyse initiale du dataset.

### US01 — Définir la vision du produit
**En tant qu'équipe projet**, nous voulons définir la vision du produit afin d'identifier clairement les objectifs et les fonctionnalités attendues.

🔗 [GitHub Issue #2](https://github.com/Siham0820salhi/plant-disease-detection/issues/2)

### US02 — Définir la stratégie de données
**En tant qu'équipe Data**, nous voulons définir une stratégie de gestion des données afin d'assurer leur disponibilité et leur qualité.

🔗 [GitHub Issue #3](https://github.com/Siham0820salhi/plant-disease-detection/issues/3)

### US03 — Définir et prioriser le Product Backlog
**En tant que Product Owner**, nous voulons structurer et prioriser le Product Backlog afin d'organiser efficacement le travail.

🔗 [GitHub Issue #4](https://github.com/Siham0820salhi/plant-disease-detection/issues/4)

### US04 — Valider le produit avec des tests d'acceptation
**En tant qu'équipe projet**, nous voulons définir des critères de validation afin de vérifier que le produit répond aux besoins attendus.

🔗 [GitHub Issue #5](https://github.com/Siham0820salhi/plant-disease-detection/issues/5)

### US08 — Ingérer le dataset PlantVillage
**En tant que Data Engineer**, nous voulons automatiser l'ingestion du dataset PlantVillage afin de disposer des données nécessaires au projet.

🔗 [GitHub Issue #9](https://github.com/Siham0820salhi/plant-disease-detection/issues/9)

### US09 — Vérifier la qualité des images
**En tant que Data Engineer**, nous voulons contrôler la qualité des images afin d'identifier les données incorrectes ou inutilisables.

🔗 [GitHub Issue #10](https://github.com/Siham0820salhi/plant-disease-detection/issues/10)

### US19 — Réaliser l'analyse exploratoire des données
**En tant que Data Analyst**, nous voulons réaliser une EDA afin de mieux comprendre le dataset et d'identifier les éventuels problèmes de données.

🔗 [GitHub Issue #20](https://github.com/Siham0820salhi/plant-disease-detection/issues/20)

---

## 🟡 Sprint 2 — Transformation, Qualité & Orchestration

🎯 **Objectif :** industrialiser le traitement des données et automatiser le pipeline.

### US10 — Prétraiter les images
**En tant que Data Engineer**, nous voulons prétraiter les images afin de les rendre compatibles avec le modèle.

🔗 [GitHub Issue #11](https://github.com/Siham0820salhi/plant-disease-detection/issues/11)

### US11 — Augmenter les données d'entraînement
**En tant que Data Engineer**, nous voulons appliquer de la Data Augmentation afin d'améliorer la robustesse du modèle.

🔗 [GitHub Issue #12](https://github.com/Siham0820salhi/plant-disease-detection/issues/12)

### US12 — Vérifier la répartition des classes
**En tant que Data Engineer**, nous voulons analyser la répartition des classes afin d'identifier un éventuel déséquilibre des données.

🔗 [GitHub Issue #13](https://github.com/Siham0820salhi/plant-disease-detection/issues/13)

### US13 — Orchestrer le pipeline avec Dagster
**En tant que Data Engineer**, nous voulons orchestrer le pipeline afin d'automatiser l'exécution des différentes étapes de traitement.

🔗 [GitHub Issue #14](https://github.com/Siham0820salhi/plant-disease-detection/issues/14)

### US05 — Tester le prétraitement des images
**En tant que membre de l'équipe QA**, nous voulons tester le prétraitement afin de vérifier que les transformations appliquées sont correctes.

🔗 [GitHub Issue #6](https://github.com/Siham0820salhi/plant-disease-detection/issues/6)

### US23 — Orchestrer le pipeline avec Dagster
**En tant que Data Engineer**, nous voulons automatiser l'orchestration du pipeline avec Dagster afin de faciliter son exécution et sa maintenance.

🔗 [GitHub Issue #26](https://github.com/Siham0820salhi/plant-disease-detection/issues/26)

---

## 🔵 Sprint 3 — Modélisation & Expérimentation MLflow

🎯 **Objectif :** développer, évaluer et suivre les modèles de Machine Learning, puis préparer leur exposition.

### US14 — Entraîner le modèle de classification
**En tant que ML Engineer**, nous voulons entraîner un modèle de classification afin de détecter les maladies des plantes.

🔗 [GitHub Issue #15](https://github.com/Siham0820salhi/plant-disease-detection/issues/15)

### US15 — Évaluer le modèle
**En tant que ML Engineer**, nous voulons évaluer les performances du modèle afin de mesurer sa qualité.

🔗 [GitHub Issue #16](https://github.com/Siham0820salhi/plant-disease-detection/issues/16)

### US16 — Tracker les expériences avec MLflow
**En tant que ML Engineer**, nous voulons suivre les expériences avec MLflow afin de comparer les différentes configurations du modèle.

🔗 [GitHub Issue #17](https://github.com/Siham0820salhi/plant-disease-detection/issues/17)

### US17 — Exposer le modèle avec une API FastAPI
**En tant que développeur**, nous voulons exposer le modèle via une API FastAPI afin de permettre son utilisation par une application cliente.

🔗 [GitHub Issue #18](https://github.com/Siham0820salhi/plant-disease-detection/issues/18)

### US18 — Déployer l'application avec Docker
**En tant que DevOps Engineer**, nous voulons conteneuriser l'application avec Docker afin de faciliter son déploiement.

🔗 [GitHub Issue #19](https://github.com/Siham0820salhi/plant-disease-detection/issues/19)

### US06 — Tester le modèle
**En tant que membre de l'équipe QA**, nous voulons tester le modèle afin de vérifier son comportement et ses résultats.

🔗 [GitHub Issue #7](https://github.com/Siham0820salhi/plant-disease-detection/issues/7)

---

## 🟣 Sprint 4 — Déploiement, CI/CD & Monitoring

🎯 **Objectif :** finaliser l'exposition de la solution, automatiser les contrôles et mettre en place le suivi du modèle.

### US07 — Tester l'API
**En tant que membre de l'équipe QA**, nous voulons tester l'API afin de vérifier la validité des requêtes et des réponses.

🔗 [GitHub Issue #8](https://github.com/Siham0820salhi/plant-disease-detection/issues/8)

### US20 — Mettre en place le monitoring du modèle
**En tant que Data Analyst**, nous voulons mettre en place un système de monitoring afin de suivre le comportement du modèle.

🔗 [GitHub Issue #21](https://github.com/Siham0820salhi/plant-disease-detection/issues/21)

### US21 — Monitoring
**En tant que Data Analyst**, nous voulons compléter le monitoring afin de surveiller les performances et la qualité du système.

🔗 [GitHub Issue #24](https://github.com/Siham0820salhi/plant-disease-detection/issues/24)

### US22 — Acceptance testing
**En tant que Product Owner & Équipe projet**, nous voulons réaliser les tests d'acceptation afin de vérifier la conformité globale du produit.

🔗 [GitHub Issue #25](https://github.com/Siham0820salhi/plant-disease-detection/issues/25)

---

# 🗓️ 4. Sprint Planning

Les Sprint Plannings ont permis de définir l'objectif de chaque sprint, de sélectionner les User Stories prioritaires et de répartir les tâches entre les membres de l'équipe.

## 🟢 Sprint 1 — Cadrage, Data Strategy & Ingestion

📅 **Échéance :** 6 août 2026

### 🎯 Objectif
Mettre en place les fondations du projet DataOps.

### 📌 Travaux prévus
- Définir la vision du produit.
- Définir la stratégie de données.
- Construire et prioriser le Product Backlog.
- Ingérer le dataset PlantVillage.
- Vérifier la qualité des données.
- Réaliser l'EDA.
- Mettre en place la structure initiale du projet.

🔗 [Milestone Sprint 1](https://github.com/Siham0820salhi/plant-disease-detection/milestone/1)

**Avancement : 100 % ✅**

---

## 🟡 Sprint 2 — Transformation, Qualité & Orchestration

📅 **Échéance :** 13 août 2026

### 🎯 Objectif
Industrialiser le traitement des données et automatiser le pipeline.

### 📌 Travaux prévus
- Prétraiter les images.
- Réaliser la Data Augmentation.
- Vérifier la répartition des classes.
- Tester le prétraitement.
- Mettre en place les contrôles de qualité.
- Orchestrer le pipeline avec Dagster.

🔗 [Milestone Sprint 2](https://github.com/Siham0820salhi/plant-disease-detection/milestone/2)

**Avancement : 100 % ✅**

---

## 🔵 Sprint 3 — Modélisation & Expérimentation MLflow

📅 **Échéance :** 20 août 2026

### 🎯 Objectif
Développer et évaluer les modèles de classification et suivre les expérimentations.

### 📌 Travaux prévus
- Entraîner les modèles.
- Comparer les résultats.
- Évaluer les performances.
- Tracker les expériences avec MLflow.
- Exposer le modèle avec FastAPI.
- Conteneuriser l'application avec Docker.
- Tester le modèle.

🔗 [Milestone Sprint 3](https://github.com/Siham0820salhi/plant-disease-detection/milestone/3)

**Avancement : 100 % ✅**

---

## 🟣 Sprint 4 — Déploiement, CI/CD & Monitoring

📅 **Échéance :** 31 août 2026

### 🎯 Objectif
Finaliser le déploiement et mettre en place les mécanismes de test et de monitoring.

### 📌 Travaux prévus
- Tester l'API.
- Mettre en place le monitoring complet.
- Réaliser l'Acceptance Testing.
- Finaliser les éléments de déploiement et de CI/CD.

🔗 [Milestone Sprint 4](https://github.com/Siham0820salhi/plant-disease-detection/milestone/4)

**Avancement : 100 % ✅**

---

# 🎬 5. Sprint Reviews

Les Sprint Reviews permettent à l'équipe de présenter le travail réalisé, de vérifier l'atteinte des objectifs du sprint et d'identifier les éléments à améliorer pour la suite du projet.

## 🟢 Sprint 1 — Review

### ✅ Réalisé
- Vision du produit définie.
- Product Backlog initialisé et priorisé.
- Dataset PlantVillage intégré.
- Contrôles initiaux de qualité réalisés.
- EDA réalisée.
- Structure du projet mise en place.

### 📌 Résultat
Le sprint a permis de disposer d'une base solide pour poursuivre le traitement et l'industrialisation du pipeline.

---

## 🟡 Sprint 2 — Review

### ✅ Réalisé
- Prétraitement des images.
- Data Augmentation.
- Vérification de la répartition des classes.
- Tests du prétraitement.
- Orchestration du pipeline avec Dagster.

### 📌 Résultat
Le pipeline de préparation des données est devenu plus structuré et automatisé, permettant de préparer les données pour la phase de modélisation.

---

## 🔵 Sprint 3 — Review

### ✅ Réalisé
- Entraînement des modèles.
- Évaluation des performances.
- Suivi des expérimentations avec MLflow.
- Exposition du modèle avec FastAPI.
- Déploiement avec Docker.
- Tests du modèle.

### 📌 Résultat
Le modèle est intégré dans une chaîne plus complète allant de l'expérimentation jusqu'à l'exposition du service.

---

## 🟣 Sprint 4 — Review

### ✅ Réalisé
- Tests de l'API.
- Mise en place et complétion du monitoring complet du modèle.
- Réalisation des tests d'acceptation (Acceptance testing).
- Validation et vérification des éléments de déploiement.

### 📌 Résultat
Le sprint a permis de finaliser l'ensemble des éléments de déploiement, de contrôle et de suivi de la solution.

---

# 🔄 6. Sprint Retrospectives

Les rétrospectives ont permis à l'équipe d'identifier les points positifs, les difficultés rencontrées et les actions d'amélioration pour les sprints suivants.

## 🟢 Sprint 1 — Retrospective

### ✅ What went well
- Bonne définition des objectifs du projet.
- Répartition initiale des responsabilités.
- Mise en place de GitHub Issues et Milestones.
- Bonne progression sur l'ingestion et l'EDA.

### ⚠️ What could be improved
- Certaines tâches nécessitaient une meilleure estimation du temps.
- La documentation pouvait être mise à jour plus regularly.

### 💡 Actions d'amélioration
- Améliorer l'estimation des tâches.
- Documenter les décisions au fur et à mesure.
- Maintenir une communication régulière entre les membres.

---

## 🟡 Sprint 2 — Retrospective

### ✅ What went well
- Bonne coordination des tâches Data Engineering.
- Pipeline de traitement mieux structuré.
- Utilisation de Dagster pour automatiser les étapes.
- Les tests ont été intégrés au processus.

### ⚠️ What could be improved
- Certaines tâches dépendaient de travaux réalisés précédemment.
- Les problèmes de données pouvaient ralentir certaines étapes.

### 💡 Actions d'amélioration
- Identifier les dépendances avant le début du sprint.
- Commencer les tests plus tôt.
- Synchroniser régulièrement les travaux entre les membres.

---

## 🔵 Sprint 3 — Retrospective

### ✅ What went well
- Collaboration autour de la partie Machine Learning.
- Suivi des expérimentations avec MLflow.
- Progression vers une solution exploitable via FastAPI.
- Utilisation de Docker pour faciliter le déploiement.

### ⚠️ What could be improved
- Les tâches ML nécessitent parfois plusieurs expérimentations avant d'obtenir un résultat satisfaisant.
- La coordination entre développement, tests et déploiement pouvait être renforcée.

### 💡 Actions d'amélioration
- Prévoir suffisamment de temps pour les expérimentations.
- Tester les composants progressivement.
- Améliorer la synchronisation entre les parties ML et DevOps.

---

## 🟣 Sprint 4 — Retrospective

### ✅ What went well
- Tous les éléments de déploiement, monitoring et tests d'acceptation ont été finalisés.
- Les tests de l'API ont été réalisés avec succès.
- Le suivi du projet via GitHub a facilité la visibilité globale sur l'avancement.

### ⚠️ What could be improved
- La charge de travail de fin de projet nécessitait une forte coordination.

### 💡 Actions d'amélioration
- Anticiper plus tôt la préparation des environnements de déploiement.
- Prioriser les tâches essentielles à la livraison finale.
- Prévoir une phase finale dédiée à la validation et à la documentation.

---

# 📊 7. Synthèse de l'avancement

| Élément | Résultat |
|---|---:|
| 🏃 Nombre de sprints | 4 |
| 📋 User Stories suivies | 23 |
| ✅ User Stories terminées | 23 |
| ⏭️ User Stories skipped / non planifiées | 0 |
| 📌 Milestones | 4 |
| 🗂️ Suivi des tâches | GitHub Issues |
| 📅 Organisation | Scrum |
| 🔄 Suivi des sprints | GitHub Milestones |

---

# 👥 8. Organisation du travail

L'organisation repose sur la méthode Scrum, adaptée à une équipe de **8 membres**, chacun responsable d'un périmètre technique précis et complémentaire :

| Membre | Rôle principal | Périmètre technique |
|---|---|---|
| **Hasnae El Mir** | Product Owner | Vision produit, backlog, validation finale |
| **Hiba Ouafi** | Scrum Master | Facilitation, organisation Agile & processus |
| **Khansaa Balakrafas** | Data Engineer | Ingestion des données PlantVillage |
| **Salma Zamakhchari** | Data Engineer | Qualité et nettoyage des données |
| **Ibtissam Essadiki** | Data Engineer / Orchestration | Pipeline & Orchestration avec Dagster |
| **Chaimaa Afess** | ML Engineer | Entraînement, évaluation & MLflow |
| **Oumaima Talbi** | DevOps Engineer | Déploiement, FastAPI & Docker |
| **Siham Salhi** | Data Analyst | EDA & Monitoring du modèle |

L'équipe a utilisé une organisation collaborative basée sur :
- 📌 **GitHub Issues** pour les User Stories et les tâches.
- 🏁 **GitHub Milestones** pour représenter les Sprints.
- 📋 **GitHub Projects** pour visualiser l'avancement.
- 🔀 **Git/GitHub** pour la gestion du code.
- 🔄 **Scrum Events** : Sprint Planning, Sprint Review et Sprint Retrospective.

---

# 🔗 9. Liens utiles

- 🏠 [Repository GitHub](https://github.com/Siham0820salhi/plant-disease-detection)
- 📋 [GitHub Issues](https://github.com/Siham0820salhi/plant-disease-detection/issues)
- 🟢 [Sprint 1 — Milestone](https://github.com/Siham0820salhi/plant-disease-detection/milestone/1)
- 🟡 [Sprint 2 — Milestone](https://github.com/Siham0820salhi/plant-disease-detection/milestone/2)
- 🔵 [Sprint 3 — Milestone](https://github.com/Siham0820salhi/plant-disease-detection/milestone/3)
- 🟣 [Sprint 4 — Milestone](https://github.com/Siham0820salhi/plant-disease-detection/milestone/4)

---

> 💡 **Conclusion :**  
> L'utilisation de Scrum a permis de structurer progressivement le projet, de répartir les responsabilités entre les membres et de suivre l'avancement à travers des objectifs définis par sprint. Les réunions régulières et le suivi GitHub ont facilité la coordination et l'amélioration continue du travail.
