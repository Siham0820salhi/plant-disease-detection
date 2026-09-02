import os
import json
import pandas as pd
import great_expectations as gx


# ============================================================
# CONFIGURATION
# ============================================================

TRAIN_DIR = "data/processed/train"
VAL_DIR = "data/processed/val"
TEST_DIR = "data/processed/test"

IMAGE_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png"
)

REPORT_DIR = "reports"
GX_RESULTS_FILE = os.path.join(
    REPORT_DIR,
    "gx_results.json"
)


# ============================================================
# FONCTION : CREER LE DATAFRAME DES IMAGES
# ============================================================

def creer_dataframe_images():

    donnees = []

    datasets = {
        "train": TRAIN_DIR,
        "validation": VAL_DIR,
        "test": TEST_DIR
    }

    for split, directory in datasets.items():

        if not os.path.exists(directory):
            raise FileNotFoundError(
                f"Le dossier suivant n'existe pas : {directory}"
            )

        for classe in os.listdir(directory):

            classe_dir = os.path.join(
                directory,
                classe
            )

            if not os.path.isdir(classe_dir):
                continue

            for filename in os.listdir(classe_dir):

                if not filename.lower().endswith(
                    IMAGE_EXTENSIONS
                ):
                    continue

                chemin_image = os.path.join(
                    classe_dir,
                    filename
                )

                donnees.append({
                    "split": split,
                    "classe": classe,
                    "filename": filename,
                    "path": chemin_image
                })

    df = pd.DataFrame(donnees)

    return df


# ============================================================
# FONCTION : AFFICHER LES INFORMATIONS DU DATASET
# ============================================================

def afficher_resume_dataset(df):

    print("=" * 60)
    print("GREAT EXPECTATIONS - PLANTVILLAGE")
    print("=" * 60)

    print(
        "\nNombre total d'images :",
        len(df)
    )

    print("\nColonnes :")
    print(
        df.columns.tolist()
    )

    print("\nRépartition par split :")
    print(
        df["split"].value_counts()
    )

    print("\nNombre de classes :")
    print(
        df["classe"].nunique()
    )

    print("\nAperçu :")
    print(
        df.head()
    )


# ============================================================
# FONCTION : CREER LE BATCH GREAT EXPECTATIONS
# ============================================================

def creer_batch_gx(df):

    # --------------------------------------------------------
    # Création du contexte Great Expectations
    # --------------------------------------------------------

    context = gx.get_context()

    # --------------------------------------------------------
    # Création d'une Data Source Pandas
    # --------------------------------------------------------

    data_source = context.data_sources.add_pandas(
        name="plantvillage_source"
    )

    # --------------------------------------------------------
    # Création du Data Asset
    # --------------------------------------------------------

    data_asset = data_source.add_dataframe_asset(
        name="plantvillage_metadata"
    )

    # --------------------------------------------------------
    # Définition du batch
    # --------------------------------------------------------

    batch_definition = (
        data_asset.add_batch_definition_whole_dataframe(
            "plantvillage_batch"
        )
    )

    # --------------------------------------------------------
    # Récupération du batch
    # --------------------------------------------------------

    batch = batch_definition.get_batch(
        batch_parameters={
            "dataframe": df
        }
    )

    return batch


# ============================================================
# FONCTION : EXECUTER LES VALIDATIONS GREAT EXPECTATIONS
# ============================================================

def executer_validations_gx(batch):

    print("\n" + "=" * 60)
    print(
        "VALIDATION GREAT EXPECTATIONS - PLANTVILLAGE"
    )
    print("=" * 60)

    # ========================================================
    # LISTE DES EXPECTATIONS
    # ========================================================

    expectations = [

        # ----------------------------------------------------
        # TEST 1
        # Vérifier les valeurs autorisées dans split
        # ----------------------------------------------------

        (
            "Valeurs autorisées dans split",

            gx.expectations.ExpectColumnValuesToBeInSet(
                column="split",
                value_set=[
                    "train",
                    "validation",
                    "test"
                ]
            )
        ),

        # ----------------------------------------------------
        # TEST 2
        # split ne doit pas contenir de valeur nulle
        # ----------------------------------------------------

        (
            "Split non vide",

            gx.expectations.ExpectColumnValuesToNotBeNull(
                column="split"
            )
        ),

        # ----------------------------------------------------
        # TEST 3
        # classe ne doit pas contenir de valeur nulle
        # ----------------------------------------------------

        (
            "Classe non vide",

            gx.expectations.ExpectColumnValuesToNotBeNull(
                column="classe"
            )
        ),

        # ----------------------------------------------------
        # TEST 4
        # filename ne doit pas être vide
        # ----------------------------------------------------

        (
            "Nom du fichier non vide",

            gx.expectations.ExpectColumnValuesToNotBeNull(
                column="filename"
            )
        ),

        # ----------------------------------------------------
        # TEST 5
        # path ne doit pas être vide
        # ----------------------------------------------------

        (
            "Chemin image non vide",

            gx.expectations.ExpectColumnValuesToNotBeNull(
                column="path"
            )
        ),

        # ----------------------------------------------------
        # TEST 6
        # Vérifier le nombre de colonnes
        # ----------------------------------------------------

        (
            "Nombre de colonnes = 4",

            gx.expectations.ExpectTableColumnCountToEqual(
                value=4
            )
        ),

        # ----------------------------------------------------
        # TEST 7
        # Vérifier les colonnes attendues
        # ----------------------------------------------------

        (
            "Colonnes attendues",

            gx.expectations.ExpectTableColumnsToMatchOrderedList(
                column_list=[
                    "split",
                    "classe",
                    "filename",
                    "path"
                ]
            )
        ),

        # ----------------------------------------------------
        # TEST 8
        # Vérifier qu'il existe au moins une image
        # ----------------------------------------------------

        (
            "Nombre d'images supérieur à 0",

            gx.expectations.ExpectTableRowCountToBeBetween(
                min_value=1
            )
        )
    ]

    # ========================================================
    # EXECUTION DES TESTS
    # ========================================================

    nombre_passed = 0
    nombre_failed = 0

    resultats_tests = []

    print()

    for numero, (
        nom_test,
        expectation
    ) in enumerate(
        expectations,
        start=1
    ):

        try:

            resultat = batch.validate(
                expectation
            )

            if resultat.success:

                statut = "PASSED"
                nombre_passed += 1

                print(
                    f"{numero}. "
                    f"{nom_test:<45} "
                    f"PASSED ✅"
                )

            else:

                statut = "FAILED"
                nombre_failed += 1

                print(
                    f"{numero}. "
                    f"{nom_test:<45} "
                    f"FAILED ❌"
                )

            resultats_tests.append({
                "numero": numero,
                "test": nom_test,
                "status": statut,
                "success": bool(resultat.success)
            })

        except Exception as e:

            nombre_failed += 1

            resultats_tests.append({
                "numero": numero,
                "test": nom_test,
                "status": "ERROR",
                "success": False,
                "error": str(e)
            })

            print(
                f"{numero}. "
                f"{nom_test:<45} "
                f"ERROR ❌"
            )

            print(
                "   Erreur :",
                e
            )

    # ========================================================
    # RESUME FINAL
    # ========================================================

    print("\n" + "=" * 60)
    print(
        "RÉSUMÉ GREAT EXPECTATIONS"
    )
    print("=" * 60)

    print(
        "Tests exécutés :",
        len(expectations)
    )

    print(
        "Tests réussis  :",
        nombre_passed
    )

    print(
        "Tests échoués  :",
        nombre_failed
    )

    if nombre_failed == 0:

        statut_global = "PASSED"

        print(
            "\nSTATUT GLOBAL : "
            "DATA QUALITY PASSED ✅"
        )

    else:

        statut_global = "FAILED"

        print(
            "\nSTATUT GLOBAL : "
            "DATA QUALITY FAILED ❌"
        )

    # ========================================================
    # CREER LE RESULTAT GLOBAL
    # ========================================================

    resultat_global = {
        "outil": "Great Expectations",
        "dataset": "PlantVillage",
        "total": len(expectations),
        "passed": nombre_passed,
        "failed": nombre_failed,
        "status_global": statut_global,
        "tests": resultats_tests
    }

    # ========================================================
    # SAUVEGARDER LES RESULTATS EN JSON
    # ========================================================

    os.makedirs(
        REPORT_DIR,
        exist_ok=True
    )

    with open(
        GX_RESULTS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            resultat_global,
            f,
            indent=4,
            ensure_ascii=False
        )

    print()
    print("=" * 60)
    print("EXPORT DES RESULTATS")
    print("=" * 60)

    print(
        "Résultats Great Expectations enregistrés dans :"
    )

    print(
        GX_RESULTS_FILE
    )

    return resultat_global


# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # 1. Créer le DataFrame
    # --------------------------------------------------------

    df = creer_dataframe_images()

    # --------------------------------------------------------
    # 2. Afficher le résumé du dataset
    # --------------------------------------------------------

    afficher_resume_dataset(
        df
    )

    # --------------------------------------------------------
    # 3. Créer le batch Great Expectations
    # --------------------------------------------------------

    print(
        "\nCréation du batch Great Expectations..."
    )

    batch = creer_batch_gx(
        df
    )

    # --------------------------------------------------------
    # 4. Exécuter les validations
    # --------------------------------------------------------

    resultats = executer_validations_gx(
        batch
    )