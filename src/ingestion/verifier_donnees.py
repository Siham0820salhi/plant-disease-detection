import duckdb

conn = duckdb.connect("plantvillage_ingestion.duckdb")

print("=== Nombre total de lignes (table principale) ===")
print(conn.sql("SELECT COUNT(*) AS total FROM raw.images_metadata").df())

print("\n=== Répartition par plante et maladie ===")
print(conn.sql("""
    SELECT plante, maladie, COUNT(*) AS nb_images
    FROM raw.images_metadata
    GROUP BY plante, maladie
    ORDER BY nb_images DESC
""").df())

print("\n=== Table incrémentale (simulation nouvelles données) ===")
print(conn.sql("SELECT COUNT(*) AS total FROM raw.images_metadata_incremental").df())

conn.close()
