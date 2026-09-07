import sqlite3
import shutil
from datetime import datetime

DB_PATH = "mlflow.db"
OLD_PATH = "file:///C:/Users/LI/plant-disease-detection"
NEW_PATH = "file:///C:/Users/USER/Desktop/plant-disease-detection"

# --- Sauvegarde de sécurité avant toute modification ---
backup_name = f"mlflow_backup_before_path_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
shutil.copy(DB_PATH, backup_name)
print(f"Sauvegarde créée : {backup_name}")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

targets = [
    ("runs", "artifact_uri"),
    ("logged_models", "artifact_location"),
    ("experiments", "artifact_location"),
    ("model_versions", "storage_location"),
]

total_updated = 0

for table, col in targets:
    cursor.execute(
        f'UPDATE "{table}" SET "{col}" = REPLACE("{col}", ?, ?) WHERE "{col}" LIKE ?',
        (OLD_PATH, NEW_PATH, f"%{OLD_PATH}%"),
    )
    updated = cursor.rowcount
    total_updated += updated
    print(f"{table}.{col} : {updated} lignes mises à jour")

conn.commit()

# --- Vérification finale : plus aucune trace de l'ancien chemin ---
print("\n--- Vérification ---")
remaining = 0
for table, col in targets:
    cursor.execute(f'SELECT COUNT(*) FROM "{table}" WHERE "{col}" LIKE ?', (f"%Users%LI%",))
    count = cursor.fetchone()[0]
    remaining += count
    if count > 0:
        print(f"⚠️  {table}.{col} : encore {count} lignes avec l'ancien chemin")

if remaining == 0:
    print("✅ Plus aucune trace de l'ancien chemin. Correction réussie.")
else:
    print(f"⚠️  {remaining} lignes n'ont pas été corrigées, vérifier manuellement.")

print(f"\nTotal de lignes mises à jour : {total_updated}")

conn.close()
