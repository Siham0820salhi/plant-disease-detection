# 📦 Module Orchestration - Dagster (Personne 5 : BTISSAM ESSADIKI)

## 🎯 Rôle et Objectifs (Livrable L5)
Ce module assure l'orchestration de bout en bout du pipeline MLOps & DataOps pour le projet de détection des maladies des plantes (PlantVillage).

---

## 🛠️ Architecture du Pipeline Dagster
Le pipeline est structuré sous forme de **Software-Defined Assets (SDA)** avec des dépendances strictes :

1. **`asset_ingestion`** (P3 - Khansae) : Ingestion des images brutes vers DuckDB avec `dlt`.
2. **`asset_preprocessing`** (P4 - Salma) : Data quality, redimensionnement et split stratifié (Train/Val/Test).
3. **`asset_train_model`** (P6 - Chaimae) : Entraînement des modèles CNN / Transfer Learning et tracking MLflow.

---

## ⚙️ Fonctionnalités Implémentées

- **Data Lineage & Dépendances :** Gestion des dépendances entre assets avec `AssetIn()`. Si une étape échoue, les étapes suivantes sont bloquées.
- **Job Manuel (`pipeline_global_plant_disease`) :** Job pour exécuter l'ensemble du pipeline à la demande (idéal pour la soutenance).
- **Schedule Automatique (`daily_pipeline_schedule`) :** Cron `0 0 * * *` (tous les jours à minuit) pour simuler l'ingestion quotidienne de nouvelles données agricoles.
- **Logging & Alertes :** Intégration de `AssetExecutionContext` pour émettre des logs informatifs (`context.log.info`) et des alertes en cas d'échec (`context.log.error`).
- **Configuration Docker :** `pyproject.toml` configuré à la racine pour un démarrage automatique dans les conteneurs Docker (`module_name = "src.orchestration.definitions"`).

---

## 🚀 Comment lancer Dagster localement

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Démarrer le serveur Dagster
dagster dev

# 3. Accéder à l'interface web
# Ouvrir le navigateur sur : http://localhost:3000