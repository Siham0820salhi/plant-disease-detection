import os
import shutil
import numpy as np
import pandas as pd

from PIL import Image
from sklearn.model_selection import train_test_split


# ============================================================
# 1. PARAMÈTRES
# ============================================================

RAW_DATA_DIR = "data/raw"
PROCESSED_DATA_DIR = "data/processed"

TARGET_SIZE = (224, 224)
RANDOM_STATE = 42


# ============================================================
# 2. PRÉTRAITEMENT D'UNE IMAGE
# ============================================================

def preprocess_image(image_path, target_size=TARGET_SIZE):
    """
    Ouvre une image, la convertit en RGB,
    la redimensionne en 224x224
    et normalise les pixels entre 0 et 1.
    """

    image = Image.open(image_path)

    # Conversion RGB
    image = image.convert("RGB")

    # Redimensionnement
    image = image.resize(target_size)

    # Conversion NumPy
    image_array = np.array(image)

    # Normalisation [0,1]
    image_array = image_array / 255.0

    return image_array


# ============================================================
# 3. CRÉATION DE L'INVENTAIRE
# ============================================================

def creer_inventaire(raw_dir=RAW_DATA_DIR):

    donnees = []

    for classe in os.listdir(raw_dir):

        chemin_classe = os.path.join(raw_dir, classe)

        if not os.path.isdir(chemin_classe):
            continue

        for nom_image in os.listdir(chemin_classe):

            if nom_image.lower().endswith(
                (".jpg", ".jpeg", ".png")
            ):

                chemin_image = os.path.join(
                    chemin_classe,
                    nom_image
                )

                donnees.append({
                    "chemin_image": chemin_image,
                    "classe": classe,
                    "nom_image": nom_image
                })

    return pd.DataFrame(donnees)


# ============================================================
# 4. SPLIT STRATIFIÉ 70 / 15 / 15
# ============================================================

def creer_split_stratifie(df):

    # 70 % train + 30 % temporaire
    train_df, temp_df = train_test_split(
        df,
        test_size=0.30,
        stratify=df["classe"],
        random_state=RANDOM_STATE
    )

    # 15 % validation + 15 % test
    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,
        stratify=temp_df["classe"],
        random_state=RANDOM_STATE
    )

    return train_df, val_df, test_df


# ============================================================
# 5. CRÉER LES DOSSIERS TRAIN / VAL / TEST
# ============================================================

def creer_dossiers_split():

    for split in ["train", "val", "test"]:

        chemin = os.path.join(
            PROCESSED_DATA_DIR,
            split
        )

        os.makedirs(
            chemin,
            exist_ok=True
        )


# ============================================================
# 6. PRÉPARER ET SAUVEGARDER LES IMAGES
# ============================================================

def sauvegarder_split(df, nom_split):

    print(f"\nPréparation du dossier {nom_split}...")

    for _, row in df.iterrows():

        chemin_source = row["chemin_image"]
        classe = row["classe"]
        nom_image = row["nom_image"]

        # Créer le dossier de la classe
        dossier_classe = os.path.join(
            PROCESSED_DATA_DIR,
            nom_split,
            classe
        )

        os.makedirs(
            dossier_classe,
            exist_ok=True
        )

        chemin_destination = os.path.join(
            dossier_classe,
            nom_image
        )

        try:

            # Ouvrir l'image
            with Image.open(chemin_source) as image:

                # Convertir RGB
                image = image.convert("RGB")

                # Redimensionner
                image = image.resize(TARGET_SIZE)

                # Sauvegarder
                image.save(chemin_destination)

        except Exception as e:

            print(
                f"Erreur avec {chemin_source} : {e}"
            )

    print(
        f"{nom_split} terminé : {len(df)} images"
    )


# ============================================================
# 7. AFFICHER LA RÉPARTITION
# ============================================================

def afficher_repartition(train_df, val_df, test_df):

    total = (
        len(train_df)
        + len(val_df)
        + len(test_df)
    )

    print("\n================================")
    print("RÉPARTITION DES DONNÉES")
    print("================================")

    print(
        f"TRAIN      : {len(train_df)} images"
    )

    print(
        f"VALIDATION : {len(val_df)} images"
    )

    print(
        f"TEST       : {len(test_df)} images"
    )

    print(f"\nTOTAL : {total}")

    print("\nPourcentages :")

    print(
        f"Train      : {len(train_df)/total*100:.2f}%"
    )

    print(
        f"Validation : {len(val_df)/total*100:.2f}%"
    )

    print(
        f"Test       : {len(test_df)/total*100:.2f}%"
    )


# ============================================================
# 8. VÉRIFIER LES CLASSES
# ============================================================

def verifier_classes(train_df, val_df, test_df):

    print("\n================================")
    print("VÉRIFICATION DES CLASSES")
    print("================================")

    print(
        "Classes TRAIN :",
        train_df["classe"].nunique()
    )

    print(
        "Classes VALIDATION :",
        val_df["classe"].nunique()
    )

    print(
        "Classes TEST :",
        test_df["classe"].nunique()
    )


# ============================================================
# 9. PROGRAMME PRINCIPAL
# ============================================================

if __name__ == "__main__":

    print("\n================================")
    print("PRÉTRAITEMENT PLANTVILLAGE")
    print("================================")


    # --------------------------------------------------------
    # Création inventaire
    # --------------------------------------------------------

    print("\nCréation de l'inventaire...")

    df = creer_inventaire()

    print(
        "Nombre total d'images :",
        len(df)
    )

    print(
        "Nombre de classes :",
        df["classe"].nunique()
    )


    # --------------------------------------------------------
    # Split
    # --------------------------------------------------------

    print("\nCréation du split stratifié...")

    train_df, val_df, test_df = creer_split_stratifie(df)


    afficher_repartition(
        train_df,
        val_df,
        test_df
    )


    verifier_classes(
        train_df,
        val_df,
        test_df
    )


    # --------------------------------------------------------
    # Création des dossiers
    # --------------------------------------------------------

    print("\nCréation des dossiers...")

    creer_dossiers_split()


    # --------------------------------------------------------
    # Sauvegarde des images
    # --------------------------------------------------------

    sauvegarder_split(
        train_df,
        "train"
    )

    sauvegarder_split(
        val_df,
        "val"
    )

    sauvegarder_split(
        test_df,
        "test"
    )


    # --------------------------------------------------------
    # Fin
    # --------------------------------------------------------

    print("\n================================")
    print("PRÉTRAITEMENT TERMINÉ")
    print("================================")

    print("\nLes données sont disponibles dans :")

    print("data/processed/train")
    print("data/processed/val")
    print("data/processed/test")