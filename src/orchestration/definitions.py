from dagster import (
    Definitions,
    define_asset_job,
    ScheduleDefinition,
)
from src.orchestration.assets import (
    asset_ingestion,
    asset_preprocessing,
    asset_train_model,
)

# 1. Définition du Job pour la Démo manuelle (Tâche 4)
pipeline_job = define_asset_job(
    name="pipeline_global_plant_disease",
    selection=[asset_ingestion, asset_preprocessing, asset_train_model],
    description="Job manuel pour lancer le pipeline complet de bout en bout (Démo Soutenance)"
)

# 2. Définition du Schedule automatique : Chaque jour à 00h00 (Tâche 4)
daily_schedule = ScheduleDefinition(
    job=pipeline_job,
    cron_schedule="0 0 * * *",  # Tous les jours à minuit
    name="daily_pipeline_schedule",
    description="Exécution quotidienne à minuit pour ingérer les nouvelles photos"
)

# 3. Definitions Globales
defs = Definitions(
    assets=[asset_ingestion, asset_preprocessing, asset_train_model],
    jobs=[pipeline_job],
    schedules=[daily_schedule],
)