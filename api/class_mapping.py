"""
class_mapping.py
----------------
Mapping des noms bruts de classes PlantVillage vers des libellés lisibles en français,
destinés à l'agriculteur utilisateur final.
"""

from typing import Tuple

# Dictionnaire : nom de classe brut → (plante, maladie) en français
CLASS_MAPPING: dict[str, Tuple[str, str]] = {
    "Pepper__bell___Bacterial_spot": (
        "Poivron",
        "Tache bactérienne",
    ),
    "Pepper__bell___healthy": (
        "Poivron",
        "Saine (aucune maladie détectée)",
    ),
    "Potato___Early_blight": (
        "Pomme de terre",
        "Alternariose (brûlure précoce)",
    ),
    "Potato___Late_blight": (
        "Pomme de terre",
        "Mildiou (brûlure tardive)",
    ),
    "Potato___healthy": (
        "Pomme de terre",
        "Saine (aucune maladie détectée)",
    ),
    "Tomato_Bacterial_spot": (
        "Tomate",
        "Tache bactérienne",
    ),
    "Tomato_Early_blight": (
        "Tomate",
        "Alternariose (brûlure précoce)",
    ),
    "Tomato_Late_blight": (
        "Tomate",
        "Mildiou (brûlure tardive)",
    ),
    "Tomato_Leaf_Mold": (
        "Tomate",
        "Moisissure des feuilles",
    ),
    "Tomato_Septoria_leaf_spot": (
        "Tomate",
        "Septoriose (tache septorienne)",
    ),
    "Tomato_Spider_mites_Two_spotted_spider_mite": (
        "Tomate",
        "Acariens (tétranyques à deux points)",
    ),
    "Tomato__Target_Spot": (
        "Tomate",
        "Tache cible (Corynespora)",
    ),
    "Tomato__Tomato_YellowLeaf__Curl_Virus": (
        "Tomate",
        "Virus de l'enroulement jaune des feuilles (TYLCV)",
    ),
    "Tomato__Tomato_mosaic_virus": (
        "Tomate",
        "Virus de la mosaïque de la tomate (ToMV)",
    ),
    "Tomato_healthy": (
        "Tomate",
        "Saine (aucune maladie détectée)",
    ),
}


def parse_class_name(raw_class: str) -> Tuple[str, str]:
    """Renvoie (plante, maladie) lisibles en français pour une classe brute.

    Args:
        raw_class: Nom brut de la classe PlantVillage.

    Returns:
        Tuple (plante, maladie) en français.

    Raises:
        KeyError: Si la classe n'est pas reconnue.
    """
    return CLASS_MAPPING[raw_class]
