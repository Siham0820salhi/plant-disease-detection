import sqlite3

conn = sqlite3.connect('mlflow.db')
cursor = conn.cursor()

checks = [
    ("runs", "artifact_uri"),
    ("logged_models", "artifact_location"),
    ("experiments", "artifact_location"),
    ("model_versions", "storage_location"),
]

for table, col in checks:
    cursor.execute(f'SELECT "{col}" FROM "{table}" WHERE "{col}" LIKE "%Users%LI%" LIMIT 1')
    row = cursor.fetchone()
    print(f"--- {table}.{col} ---")
    print(repr(row[0]) if row else "(aucun exemple trouvé)")
    print()

conn.close()
