import os
import hashlib
from PIL import Image


# ============================================================
# CONFIGURATION
# ============================================================

TRAIN_DIR = "data/processed/train"
VAL_DIR = "data/processed/val"
TEST_DIR = "data/processed/test"

EXPECTED_SIZE = (224, 224)
EXPECTED_CLASSES = 15

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")

# Seuil indicatif pour signaler un fort déséquilibre
MAX_IMBALANCE_RATIO = 10.0


# ============================================================
# FONCTION : récupérer les classes
# ============================================================

def get_classes(directory):
    return sorted([
        name
        for name in os.listdir(directory)
        if os.path.isdir(os.path.join(directory, name))
    ])


# ============================================================
# FONCTION : compter les images d'une classe
# ============================================================

def count_images(classe_dir):
    return len([
        f for f in os.listdir(classe_dir)
        if f.lower().endswith(IMAGE_EXTENSIONS)
    ])


# ============================================================
# FONCTION : calculer le hash MD5 d'une image
# ============================================================

def calculer_hash(image_path, block_size=65536):
    """
    Calcule une empreinte MD5 du fichier.
    Deux fichiers strictement identiques ont le même hash.
    """

    h = hashlib.md5()

    with open(image_path, "rb") as f:
        for bloc in iter(lambda: f.read(block_size), b""):
            h.update(bloc)

    return h.hexdigest()


# ============================================================
# TEST 1 : vérifier que les dossiers existent
# ============================================================

def test_dossiers_existent():

    assert os.path.exists(TRAIN_DIR), "Le dossier train n'existe pas"
    assert os.path.exists(VAL_DIR), "Le dossier val n'existe pas"
    assert os.path.exists(TEST_DIR), "Le dossier test n'existe pas"


# ============================================================
# TEST 2 : vérifier le nombre de classes
# ============================================================

def test_nombre_classes():

    assert len(get_classes(TRAIN_DIR)) == EXPECTED_CLASSES
    assert len(get_classes(VAL_DIR)) == EXPECTED_CLASSES
    assert len(get_classes(TEST_DIR)) == EXPECTED_CLASSES


# ============================================================
# TEST 3 : vérifier les mêmes classes dans train / val / test
# ============================================================

def test_memes_classes():

    train_classes = get_classes(TRAIN_DIR)
    val_classes = get_classes(VAL_DIR)
    test_classes = get_classes(TEST_DIR)

    assert train_classes == val_classes
    assert train_classes == test_classes


# ============================================================
# TEST 4 : vérifier que les images sont lisibles
# ============================================================

def test_images_lisibles():

    for dataset_dir in [TRAIN_DIR, VAL_DIR, TEST_DIR]:

        for classe in get_classes(dataset_dir):

            classe_dir = os.path.join(dataset_dir, classe)

            for filename in os.listdir(classe_dir):

                if not filename.lower().endswith(IMAGE_EXTENSIONS):
                    continue

                image_path = os.path.join(
                    classe_dir,
                    filename
                )

                try:
                    with Image.open(image_path) as img:
                        img.verify()

                except Exception as e:
                    raise AssertionError(
                        f"Image illisible/corrompue : "
                        f"{image_path} | {e}"
                    )


# ============================================================
# TEST 5 : vérifier les dimensions 224x224
# ============================================================

def test_dimensions_images():

    for dataset_dir in [TRAIN_DIR, VAL_DIR, TEST_DIR]:

        for classe in get_classes(dataset_dir):

            classe_dir = os.path.join(dataset_dir, classe)

            for filename in os.listdir(classe_dir):

                if not filename.lower().endswith(IMAGE_EXTENSIONS):
                    continue

                image_path = os.path.join(
                    classe_dir,
                    filename
                )

                with Image.open(image_path) as img:

                    assert img.size == EXPECTED_SIZE, (
                        f"Mauvaise dimension : "
                        f"{image_path} => {img.size}"
                    )


# ============================================================
# TEST 6 : chaque classe contient au moins une image
# ============================================================

def test_classes_non_vides():

    for dataset_dir in [TRAIN_DIR, VAL_DIR, TEST_DIR]:

        for classe in get_classes(dataset_dir):

            classe_dir = os.path.join(dataset_dir, classe)

            images = [
                f for f in os.listdir(classe_dir)
                if f.lower().endswith(IMAGE_EXTENSIONS)
            ]

            assert len(images) > 0, (
                f"Classe vide : {classe_dir}"
            )


# ============================================================
# TEST 7 : vérifier les doublons entre train / val / test
# ============================================================

def test_pas_de_doublons_entre_splits():

    hashes = {}

    for dataset_name, dataset_dir in [
        ("train", TRAIN_DIR),
        ("val", VAL_DIR),
        ("test", TEST_DIR)
    ]:

        for classe in get_classes(dataset_dir):

            classe_dir = os.path.join(
                dataset_dir,
                classe
            )

            for filename in os.listdir(classe_dir):

                if not filename.lower().endswith(IMAGE_EXTENSIONS):
                    continue

                image_path = os.path.join(
                    classe_dir,
                    filename
                )

                image_hash = calculer_hash(image_path)

                if image_hash in hashes:

                    ancien_split, ancien_path = hashes[image_hash]

                    assert ancien_split == dataset_name, (
                        "\nDoublon détecté entre deux splits !\n"
                        f"Image 1 : {ancien_path}\n"
                        f"Image 2 : {image_path}\n"
                        f"Splits : {ancien_split} / {dataset_name}"
                    )

                else:

                    hashes[image_hash] = (
                        dataset_name,
                        image_path
                    )


# ============================================================
# TEST 8 : contrôler le déséquilibre des classes du train
# ============================================================

def test_desequilibre_classes_train():

    classes = get_classes(TRAIN_DIR)

    repartition = {}

    for classe in classes:

        classe_dir = os.path.join(
            TRAIN_DIR,
            classe
        )

        repartition[classe] = count_images(classe_dir)

    classe_min = min(
        repartition,
        key=repartition.get
    )

    classe_max = max(
        repartition,
        key=repartition.get
    )

    nb_min = repartition[classe_min]
    nb_max = repartition[classe_max]

    ratio = nb_max / nb_min

    print("\n==============================")
    print("DÉSÉQUILIBRE DES CLASSES")
    print("==============================")

    print(
        f"Classe la plus petite : "
        f"{classe_min} ({nb_min} images)"
    )

    print(
        f"Classe la plus grande : "
        f"{classe_max} ({nb_max} images)"
    )

    print(
        f"Ratio max/min : {ratio:.2f}"
    )

    assert ratio <= MAX_IMBALANCE_RATIO, (
        f"Déséquilibre trop important : "
        f"ratio = {ratio:.2f}, "
        f"seuil autorisé = {MAX_IMBALANCE_RATIO}"
    )