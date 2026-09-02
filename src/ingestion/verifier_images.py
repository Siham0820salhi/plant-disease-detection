import os
from PIL import Image

RAW_DATA_DIR = "data/raw"


def verifier_images(raw_dir=RAW_DATA_DIR):
    """Parcourt toutes les images et vérifie qu'elles s'ouvrent correctement."""
    images_corrompues = []
    total = 0

    for nom_dossier in os.listdir(raw_dir):
        chemin_dossier = os.path.join(raw_dir, nom_dossier)
        if not os.path.isdir(chemin_dossier):
            continue

        for nom_image in os.listdir(chemin_dossier):
            chemin_image = os.path.join(chemin_dossier, nom_image)
            total += 1

            try:
                with Image.open(chemin_image) as img:
                    img.verify()  # vérifie que le fichier n'est pas corrompu
            except Exception as e:
                images_corrompues.append((chemin_image, str(e)))

    return total, images_corrompues


if __name__ == "__main__":
    total, corrompues = verifier_images()

    print(f"Total d'images vérifiées : {total}")
    print(f"Images corrompues trouvées : {len(corrompues)}")

    if corrompues:
        print("\nListe des images corrompues :")
        for chemin, erreur in corrompues:
            print(f"  - {chemin} : {erreur}")
    else:
        print("Toutes les images sont valides !")