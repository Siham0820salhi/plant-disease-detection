"""
simulate_drift.py
------------------
Cree data/new_data_drift : une copie assombrie d'un echantillon d'images
de data/processed/train, pour demontrer que detect_drift() reagit bien
a un vrai changement (et pas seulement a l'absence de changement).
"""

import random
from pathlib import Path

from PIL import Image, ImageEnhance

# --- Paramètres ---
SRC = Path("data/processed/train")
DST = Path("data/new_data_drift")
N_IMAGES = 80
BRIGHTNESS_FACTOR = 0.5  # 0.5 = moitie moins lumineux ; plus proche de 0 = plus sombre

def main():
    if not SRC.exists():
        print(f"Erreur : {SRC} n'existe pas. Verifie le chemin.")
        return

    DST.mkdir(parents=True, exist_ok=True)

    # Collecte des images, dedupliquee (meme piege que dans drift.py sous Windows)
    images = set(SRC.rglob("*.jpg")) | set(SRC.rglob("*.JPG")) | set(SRC.rglob("*.png"))
    images = list(images)

    if len(images) == 0:
        print(f"Aucune image trouvee dans {SRC}.")
        return

    sample = random.sample(images, min(N_IMAGES, len(images)))
    print(f"{len(sample)} images selectionnees. Assombrissement en cours...")

    for i, img_path in enumerate(sample, start=1):
        img = Image.open(img_path).convert("RGB")
        enhancer = ImageEnhance.Brightness(img)
        img_sombre = enhancer.enhance(BRIGHTNESS_FACTOR)
        img_sombre.save(DST / img_path.name)
        print(f"  [{i}/{len(sample)}] {img_path.name} -> assombrie")

    print(f"\nTermine. {len(sample)} images assombries dans {DST}")

if __name__ == "__main__":
    main()