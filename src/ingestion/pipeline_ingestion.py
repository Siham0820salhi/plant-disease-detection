import os
import sys
import dlt

RAW_DATA_DIR = "data/raw"


def parse_plante_maladie(nom_dossier):
    """Extrait le nom de la plante et de la maladie à partir du nom du dossier."""
    if "___" in nom_dossier:
        plante, maladie = nom_dossier.split("___", 1)
    else:
        parts = nom_dossier.split("_", 1)
        plante = parts[0]
        maladie = parts[1].lstrip("_") if len(parts) > 1 else "unknown"
    return plante, maladie


def generer_metadonnees(raw_dir=RAW_DATA_DIR):
    """Parcourt data/raw et génère la liste des métadonnées de chaque image."""
    metadonnees = []

    for nom_dossier in os.listdir(raw_dir):
        chemin_dossier = os.path.join(raw_dir, nom_dossier)

        if not os.path.isdir(chemin_dossier):
            continue

        plante, maladie = parse_plante_maladie(nom_dossier)

        for nom_image in os.listdir(chemin_dossier):
            if not nom_image.lower().endswith((".jpg", ".jpeg", ".png")):
                continue

            chemin_image = os.path.join(chemin_dossier, nom_image)

            metadonnees.append({
                "chemin_image": chemin_image,
                "plante": plante,
                "maladie": maladie,
            })

    return metadonnees


def charger_dans_duckdb(metadonnees):
    """Charge toutes les métadonnées d'un coup dans DuckDB."""
    pipeline = dlt.pipeline(
        pipeline_name="plantvillage_ingestion",
        destination="duckdb",
        dataset_name="raw",
    )
    info = pipeline.run(
        metadonnees,
        table_name="images_metadata",
        write_disposition="replace",
    )
    print(info)


def generer_lots(metadonnees, taille_lot=1000):
    """Découpe la liste en petits paquets de taille_lot images."""
    lots = []
    for i in range(0, len(metadonnees), taille_lot):
        lots.append(metadonnees[i:i + taille_lot])
    return lots


def charger_incrementalement(lots):
    """Charge les lots un par un, comme si les photos arrivaient progressivement."""
    pipeline = dlt.pipeline(
        pipeline_name="plantvillage_ingestion",
        destination="duckdb",
        dataset_name="raw",
    )
    for numero_lot, lot in enumerate(lots, start=1):
        print(f"Chargement du lot {numero_lot}/{len(lots)} ({len(lot)} images)...")
        pipeline.run(
            lot,
            table_name="images_metadata_incremental",
            write_disposition="append",
        )


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "complet"

    meta = generer_metadonnees()
    print(f"Nombre total d'images trouvées : {len(meta)}")

    if mode == "complet":
        charger_dans_duckdb(meta)
        print("Chargement complet terminé !")

    elif mode == "incremental":
        lots = generer_lots(meta, taille_lot=1000)
        print(f"{len(lots)} lots générés.")
        charger_incrementalement(lots)
        print("Chargement incrémental terminé !")
