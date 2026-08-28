import os
import hashlib

TRAIN_DIR = "data/processed/train"
VAL_DIR = "data/processed/val"
TEST_DIR = "data/processed/test"

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")


def calculer_hash(image_path, block_size=65536):
    h = hashlib.md5()

    with open(image_path, "rb") as f:
        for bloc in iter(lambda: f.read(block_size), b""):
            h.update(bloc)

    return h.hexdigest()


def scanner_split(nom_split, dossier_split, hashes):
    doublons = []

    for classe in os.listdir(dossier_split):

        classe_dir = os.path.join(dossier_split, classe)

        if not os.path.isdir(classe_dir):
            continue

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

                if ancien_split != nom_split:

                    doublons.append({
                        "split_1": ancien_split,
                        "image_1": ancien_path,
                        "split_2": nom_split,
                        "image_2": image_path
                    })

            else:

                hashes[image_hash] = (
                    nom_split,
                    image_path
                )

    return doublons


def supprimer_copies_val_test(doublons):

    compteur = 0

    for doublon in doublons:

        # On garde toujours la copie du train
        # et on supprime celle de val/test

        if doublon["split_2"] in ["val", "test"]:

            fichier_a_supprimer = doublon["image_2"]

        elif doublon["split_1"] in ["val", "test"]:

            fichier_a_supprimer = doublon["image_1"]

        else:
            continue

        if os.path.exists(fichier_a_supprimer):

            os.remove(fichier_a_supprimer)

            print(
                "Supprimé :",
                fichier_a_supprimer
            )

            compteur += 1

    print(
        f"\nNombre total de copies supprimées : {compteur}"
    )


if __name__ == "__main__":

    hashes = {}
    tous_les_doublons = []

    print("Scan du train...")
    tous_les_doublons += scanner_split(
        "train",
        TRAIN_DIR,
        hashes
    )

    print("Scan de validation...")
    tous_les_doublons += scanner_split(
        "val",
        VAL_DIR,
        hashes
    )

    print("Scan du test...")
    tous_les_doublons += scanner_split(
        "test",
        TEST_DIR,
        hashes
    )

    print("\n==============================")
    print("RÉSULTAT AVANT NETTOYAGE")
    print("==============================")

    print(
        "Nombre de doublons entre splits :",
        len(tous_les_doublons)
    )

    for i, doublon in enumerate(
        tous_les_doublons,
        start=1
    ):

        print(f"\nDoublon {i}")

        print(
            doublon["split_1"],
            ":",
            doublon["image_1"]
        )

        print(
            doublon["split_2"],
            ":",
            doublon["image_2"]
        )

    if len(tous_les_doublons) > 0:

        print("\n==============================")
        print("NETTOYAGE")
        print("==============================")

        supprimer_copies_val_test(
            tous_les_doublons
        )

    else:
        print("\nAucun doublon à supprimer.")