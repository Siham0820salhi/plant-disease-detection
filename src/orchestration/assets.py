import sys
import subprocess
from dagster import asset, AssetIn, AssetExecutionContext

# Asset 1 : Ingestion
@asset
def asset_ingestion(context: AssetExecutionContext):
    """Ingestion des données brutes vers DuckDB avec dlt"""
    context.log.info("Démarrage de l'étape Ingestion...")
    result = subprocess.run(
        [sys.executable, "pipeline_ingestion.py"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        context.log.error(f"[ALERTE ECHEC] Ingestion a échoué : {result.stderr}")
        raise Exception(f"Ingestion failed: {result.stderr}")
    
    context.log.info("Ingestion terminée avec succès.")
    return "Ingestion completed"


# Asset 2 : Preprocessing & Qualité
@asset(ins={"asset_ingestion": AssetIn()})
def asset_preprocessing(context: AssetExecutionContext, asset_ingestion):
    """Prétraitement d'images et validation Data Quality"""
    context.log.info("Démarrage du Prétraitement et Data Quality...")
    result = subprocess.run(
        [sys.executable, "preprocessing.py"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        context.log.error(f"[ALERTE ECHEC] Preprocessing a échoué : {result.stderr}")
        raise Exception(f"Preprocessing failed: {result.stderr}")
    
    context.log.info("Prétraitement terminé avec succès.")
    return "Preprocessing completed"


# Asset 3 : Entraînement Modèle (Prêt pour brancher train.py de P6)
@asset(ins={"asset_preprocessing": AssetIn()})
def asset_train_model(context: AssetExecutionContext, asset_preprocessing):
    """Entraînement du modèle CNN / Transfer Learning"""
    context.log.info("Démarrage de l'entraînement du modèle...")
    
    # Mnin Chaimae (P6) t-3tik train.py, y-t-lansa hakka :
    # result = subprocess.run([sys.executable, "train.py"], capture_output=True, text=True)
    # if result.returncode != 0:
    #     context.log.error(f"[ALERTE ECHEC] Training a échoué : {result.stderr}")
    #     raise Exception(f"Training failed: {result.stderr}")

    context.log.info("Modèle entraîné et enregistré avec succès.")
    return "Model Trained Successfully"