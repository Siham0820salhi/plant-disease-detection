"""
data_loaders.py
----------------
Personne 6 - ML Engineer : Modèle + MLflow

Rôle (Tâche 1 du cahier des charges) :
  - Récupérer les images prétraitées (train/val/test) de Personne 4
  - Construire les générateurs (batching, augmentation à la volée)

Contient aussi le filtrage des images augmentées hors-ligne par P4
(fichiers préfixés "aug_", voir augmentation.py de P4), nécessaire pour
comparer proprement class_weight vs augmentation ciblée (Tâche 2) sans
jamais cumuler deux augmentations sur les mêmes images.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras.preprocessing.image import ImageDataGenerator

IMG_SIZE = (224, 224)
BATCH_SIZE = 32
DATA_DIR = Path("data/processed")

# Comparaison insensible à la casse : un simple glob("*.jpg") ignorerait
# silencieusement les fichiers .JPG (bug fréquent sous Windows).
_IMG_EXTENSIONS = {".jpg", ".jpeg", ".png"}

OFFLINE_AUGMENTED_PREFIX = "aug_"  # doit rester synchronisé avec augmentation.py de P4


# ============================================================
# Construction du DataFrame train (path, classe) avec filtre optionnel
# ============================================================

def build_train_dataframe(train_dir: Path, include_offline_augmented: bool = True) -> pd.DataFrame:
    """
    Scanne train_dir/<classe>/*.* et retourne un DataFrame [path, classe].

    - include_offline_augmented=True  : toutes les images (originales +
      images "aug_*" ajoutées hors-ligne par P4). Comportement historique.
    - include_offline_augmented=False : uniquement les images originales
      (les fichiers "aug_*" de P4 sont exclus). Utile pour mesurer le
      déséquilibre réel du dataset brut, ou pour tester class_weight /
      l'augmentation en ligne sans double augmentation.
    """
    train_dir = Path(train_dir)

    if not train_dir.exists():
        raise FileNotFoundError(
            f"Dossier introuvable : {train_dir}. "
            f"Vérifiez que les données prétraitées de P4 sont bien présentes "
            f"(data/processed/train)."
        )

    rows = []
    for class_dir in sorted(train_dir.iterdir()):
        if not class_dir.is_dir():
            continue

        for img_path in class_dir.iterdir():
            if img_path.suffix.lower() not in _IMG_EXTENSIONS:
                continue

            est_augmentee_offline = img_path.name.startswith(OFFLINE_AUGMENTED_PREFIX)
            if est_augmentee_offline and not include_offline_augmented:
                continue

            rows.append({"path": str(img_path), "classe": class_dir.name})

    df = pd.DataFrame(rows)

    if df.empty:
        raise RuntimeError(
            f"Aucune image trouvée dans {train_dir} "
            f"(include_offline_augmented={include_offline_augmented}). "
            f"Vérifiez le pipeline de P4 et l'emplacement de data/processed/train."
        )

    return df


# ============================================================
# Construction des générateurs
# ============================================================

def build_generators(
    data_dir: Path = DATA_DIR,
    img_size: tuple = IMG_SIZE,
    batch_size: int = BATCH_SIZE,
    augment_online: bool = False,
    preprocessing_function=None,
    include_offline_augmented: bool = True,
):
    """
    Retourne (train_gen, val_gen, test_gen, class_indices).

    - preprocessing_function : fonction de prétraitement spécifique au
      modèle (ex: tensorflow.keras.applications.resnet50.preprocess_input).
      Si None, on utilise un simple rescale=1/255 (baseline_cnn).
    - augment_online : active/désactive l'augmentation EN LIGNE (à la
      volée, appliquée par Keras à chaque epoch). Dimension INDÉPENDANTE
      de include_offline_augmented (l'augmentation hors-ligne de P4,
      déjà présente sur disque) : les deux ne sont jamais combinées dans
      les stratégies définies par train.py, pour éviter un cumul de
      distorsions sur les mêmes images.
    - include_offline_augmented : si False, exclut du train set les
      images "aug_*" ajoutées hors-ligne par P4.
    - val_gen / test_gen : jamais d'augmentation (ni offline ni online),
      via flow_from_directory (P4 n'augmente que le train, rien à
      filtrer ici).
    """
    data_dir = Path(data_dir)

    base_kwargs = (
        {"preprocessing_function": preprocessing_function}
        if preprocessing_function is not None
        else {"rescale": 1.0 / 255}
    )

    train_datagen = ImageDataGenerator(
        **base_kwargs,
        rotation_range=15 if augment_online else 0,
        horizontal_flip=augment_online,
        vertical_flip=augment_online,
        zoom_range=0.1 if augment_online else 0,
        brightness_range=(0.9, 1.1) if augment_online else None,
    )
    val_test_datagen = ImageDataGenerator(**base_kwargs)

    # ---- Train : via DataFrame pour pouvoir filtrer les images "aug_*" ----
    train_df = build_train_dataframe(
        data_dir / "train",
        include_offline_augmented=include_offline_augmented,
    )

    train_gen = train_datagen.flow_from_dataframe(
        train_df,
        x_col="path",
        y_col="classe",
        target_size=img_size,
        batch_size=batch_size,
        class_mode="categorical",
        shuffle=True,
        seed=42,
    )

    # ---- Val / Test : comportement inchangé (flow_from_directory) ----
    val_gen = val_test_datagen.flow_from_directory(
        data_dir / "val",
        target_size=img_size,
        batch_size=batch_size,
        class_mode="categorical",
        shuffle=False,
    )
    test_gen = val_test_datagen.flow_from_directory(
        data_dir / "test",
        target_size=img_size,
        batch_size=batch_size,
        class_mode="categorical",
        shuffle=False,
    )

    return train_gen, val_gen, test_gen, train_gen.class_indices


def compute_class_weights(train_gen) -> dict:
    """
    Calcule les class_weight (stratégie 'balanced') à partir des labels
    du générateur d'entraînement, pour compenser le déséquilibre entre
    classes.

    .tolist() : convertit les clés/valeurs numpy en types Python natifs,
    pour éviter des soucis de sérialisation (ex. lors du logging MLflow
    ou de tests de comparaison).
    """
    labels = train_gen.classes  # array d'entiers, un par image
    classes = np.unique(labels)
    weights = compute_class_weight(
        class_weight="balanced", classes=classes, y=labels
    )
    return dict(zip(classes.tolist(), weights.tolist()))


if __name__ == "__main__":
    print("=== Train set COMPLET (originales + augmentées P4) ===")
    train_gen, val_gen, test_gen, class_indices = build_generators(
        include_offline_augmented=True
    )
    print(f"Classes ({len(class_indices)}): {list(class_indices.keys())}")
    print(f"Train: {train_gen.samples} images")
    print(f"Val  : {val_gen.samples} images")
    print(f"Test : {test_gen.samples} images")

    print("\n=== Train set PROPRE (originales uniquement, sans aug_ de P4) ===")
    train_gen_clean, _, _, _ = build_generators(
        include_offline_augmented=False
    )
    print(f"Train (propre): {train_gen_clean.samples} images")
    print(f"Images ajoutées par P4 (offline) : "
          f"{train_gen.samples - train_gen_clean.samples}")

    weights = compute_class_weights(train_gen_clean)
    print("\nClass weights (balanced, sur train propre):")
    for idx, w in weights.items():
        print(f"  {idx}: {w:.3f}")