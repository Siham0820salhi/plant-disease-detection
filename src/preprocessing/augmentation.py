import os
import cv2
import albumentations as A

TRAIN_DIR = "data/processed/train"
TARGET_MIN_IMAGES = 1000

# ============================================================
# 1. PIPELINE D'AUGMENTATION
# ============================================================

augmentation = A.Compose([
    A.Rotate(limit=25, p=0.7),
    A.HorizontalFlip(p=0.5),
    A.VerticalFlip(p=0.3),
    A.RandomBrightnessContrast(
        brightness_limit=0.2,
        contrast_limit=0.2,
        p=0.5
    ),
    A.Affine(
        scale=(0.9, 1.1),
        p=0.5
    )
])


# ============================================================
# 2. LISTER LES IMAGES D'UNE CLASSE
# ============================================================

def get_images(classe_dir):
    return [
        f for f in os.listdir(classe_dir)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]


# ============================================================
# 3. AUGMENTER UNE CLASSE
# ============================================================

def augmenter_classe(classe_dir, target=TARGET_MIN_IMAGES):

    images = get_images(classe_dir)
    nb_initial = len(images)

    print(f"\nClasse : {os.path.basename(classe_dir)}")
    print(f"Nombre initial : {nb_initial}")

    if nb_initial >= target:
        print("Pas d'augmentation nécessaire.")
        return

    nb_a_creer = target - nb_initial

    print(f"Images à créer : {nb_a_creer}")

    compteur = 0
    index_source = 0

    while compteur < nb_a_creer:

        nom_source = images[index_source % len(images)]

        chemin_source = os.path.join(
            classe_dir,
            nom_source
        )

        image = cv2.imread(chemin_source)

        if image is None:
            index_source += 1
            continue

        image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )

        image_aug = augmentation(
            image=image
        )["image"]

        image_aug = cv2.cvtColor(
            image_aug,
            cv2.COLOR_RGB2BGR
        )

        nom_aug = f"aug_{compteur}_{nom_source}"

        chemin_aug = os.path.join(
            classe_dir,
            nom_aug
        )

        cv2.imwrite(
            chemin_aug,
            image_aug
        )

        compteur += 1
        index_source += 1

    print(
        f"Classe terminée : {nb_initial + compteur} images"
    )


# ============================================================
# 4. AUGMENTER TOUTES LES CLASSES MINORITAIRES
# ============================================================

def augmentation_train():

    print("\n================================")
    print("DATA AUGMENTATION - TRAIN")
    print("================================")

    for classe in os.listdir(TRAIN_DIR):

        classe_dir = os.path.join(
            TRAIN_DIR,
            classe
        )

        if not os.path.isdir(classe_dir):
            continue

        augmenter_classe(
            classe_dir
        )

    print("\n================================")
    print("DATA AUGMENTATION TERMINÉE")
    print("================================")


# ============================================================
# 5. PROGRAMME PRINCIPAL
# ============================================================

if __name__ == "__main__":
    augmentation_train()