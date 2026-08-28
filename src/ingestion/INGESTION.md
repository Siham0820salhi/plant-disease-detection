# Module Ingestion — Personne 3 (Khansae)

## Objectif
Ce module télécharge le dataset PlantVillage (Kaggle), l'organise dans `data/raw/`,
génère un catalogue de métadonnées (chemin, plante, maladie, split) et le charge
dans une base DuckDB via dlt.

## Structure des données

data/raw/
├── Pepper__bell___Bacterial_spot/
├── Pepper__bell___healthy/
├── Potato___Early_blight/
├── ... (15 classes au total)

Dataset source : https://www.kaggle.com/datasets/emmarex/plantdisease
15 classes (Pepper, Potato, Tomato), 20 639 images au total.

## Comment lancer l'ingestion

### 1. Configurer l'authentification Kaggle
Créer un token API sur kaggle.com/settings/api, puis définir la variable d'environnement :
```powershell
$env:KAGGLE_API_TOKEN = "votre_token"
```

### 2. Télécharger et organiser le dataset (à faire une seule fois)
```powershell
kaggle datasets download -d emmarex/plantdisease
Expand-Archive -Path plantdisease.zip -DestinationPath data_temp
mkdir data\raw -Force
Move-Item -Path "data_temp\PlantVillage\PlantVillage\*" -Destination "data\raw"
```

### 3. Lancer le chargement complet dans DuckDB
```powershell
python pipeline_ingestion.py complet
```

### 4. Ou simuler un chargement incrémental (nouvelles photos par lots)
```powershell
python pipeline_ingestion.py incremental
```

## Où sont stockées les données
- Images brutes : `data/raw/<Plante>___<Maladie>/*.JPG`
- Métadonnées : base DuckDB `plantvillage_ingestion.duckdb`
  - Schéma `raw`, table `images_metadata` (chargement complet)
  - Schéma `raw`, table `images_metadata_incremental` (simulation incrémentale)
- Colonnes : `chemin_image`, `plante`, `maladie`, `split` (train/val/test)

## Vérifier les données
```powershell
python verifier_donnees.py
```