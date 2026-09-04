"""
drift.py
--------
Détection de dérive (drift) entre les images de référence (entraînement)
et les nouvelles images reçues (data/new_data), sur la luminosité et
la couleur dominante (moyennes RGB).

Cherche automatiquement les images de référence dans plusieurs emplacements
possibles selon l'avancement du pipeline (P3/P4) :
  1. data/processed/train  (prétraitement terminé, idéal)
  2. data/raw              (ingestion brute, fallback)
"""

from pathlib import Path

import numpy as np
from PIL import Image
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[2]  # remonte src/monitoring -> racine
REFERENCE_CANDIDATES = [
    PROJECT_ROOT / "data" / "processed" / "train",
    PROJECT_ROOT / "data" / "raw",
]
NEW_DATA_DIR = PROJECT_ROOT / "data" / "new_data"
ALPHA = 0.05  # seuil de significativite
FEATURE_NAMES = ["luminosite", "rouge_moyen", "vert_moyen", "bleu_moyen"]
IMAGE_EXTENSIONS = ("*.jpg", "*.JPG", "*.jpeg", "*.JPEG", "*.png", "*.PNG")


def find_reference_dir() -> Path | None:
    """Renvoie le premier dossier candidat qui existe et contient des images."""
    for candidate in REFERENCE_CANDIDATES:
        if candidate.exists():
            has_images = any(candidate.rglob(ext) for ext in IMAGE_EXTENSIONS)
            if has_images:
                return candidate
    return None


def compute_image_features(image_path: Path) -> tuple[float, float, float, float]:
    """Calcule luminosite moyenne + moyennes RGB pour une image."""
    with Image.open(image_path) as img:
        arr = np.asarray(img.convert("RGB"), dtype=np.float32)
    return arr.mean(), arr[..., 0].mean(), arr[..., 1].mean(), arr[..., 2].mean()


def collect_features(directory: Path, max_images: int = 500) -> np.ndarray:
    """Parcourt un dossier (recursif) et calcule les features d'un echantillon d'images.

    Utilise un set pour eviter les doublons : sous Windows, le systeme de
    fichiers ne distingue pas majuscules/minuscules, donc "*.jpg" et "*.JPG"
    renverraient sinon deux fois les memes fichiers.
    """
    paths: set[Path] = set()
    for ext in IMAGE_EXTENSIONS:
        paths.update(directory.rglob(ext))
    paths_list = list(paths)[:max_images]

    features = []
    for p in paths_list:
        try:
            features.append(compute_image_features(p))
        except Exception:
            continue
    return np.array(features)


def detect_drift(reference: np.ndarray, new: np.ndarray) -> dict:
    """Compare les distributions reference vs nouvelles donnees avec un test KS."""
    results = {}
    for i, name in enumerate(FEATURE_NAMES):
        stat, p_value = stats.ks_2samp(reference[:, i], new[:, i])
        results[name] = {
            "ks_statistic": round(float(stat), 4),
            "p_value": round(float(p_value), 4),
            "drift_detected": bool(p_value < ALPHA),
            "reference_mean": round(float(reference[:, i].mean()), 2),
            "new_mean": round(float(new[:, i].mean()), 2),
        }
    return results


def main() -> None:
    reference_dir = find_reference_dir()
    if reference_dir is None:
        print("❌ Aucune donnee de reference trouvee.")
        print("   Emplacements verifies :")
        for c in REFERENCE_CANDIDATES:
            print(f"     - {c} (existe: {c.exists()})")
        print("   -> Demande a P3/P4 si l'ingestion/pretraitement a ete lancee,")
        print("      ou utilise un echantillon manuel (voir instructions).")
        return

    print(f"Reference trouvee dans : {reference_dir}")
    reference = collect_features(reference_dir)
    print(f"  -> {len(reference)} images de reference chargees.")

    if not NEW_DATA_DIR.exists() or len(list(NEW_DATA_DIR.rglob("*"))) == 0:
        print(f"❌ {NEW_DATA_DIR} est vide ou n'existe pas.")
        print("   -> Ajoute quelques images pour simuler des nouvelles photos.")
        return

    print(f"Chargement des nouvelles images depuis {NEW_DATA_DIR}...")
    new = collect_features(NEW_DATA_DIR)
    print(f"  -> {len(new)} nouvelles images chargees.")

    if len(reference) == 0 or len(new) == 0:
        print("Pas assez d'images valides pour effectuer le test de drift.")
        return

    results = detect_drift(reference, new)

    print("\n=== Rapport de derive (drift) ===")
    any_drift = False
    for feature, r in results.items():
        any_drift = any_drift or r["drift_detected"]
        status = "⚠️  DERIVE DETECTEE" if r["drift_detected"] else "✅ OK"
        print(
            f"{feature:15s} | p-value={r['p_value']:.4f} | "
            f"ref_mean={r['reference_mean']:.2f} | new_mean={r['new_mean']:.2f} | {status}"
        )

    if any_drift:
        print("\n⚠️  Derive detectee sur au moins une feature — envisager un re-entrainement.")
    else:
        print("\n✅ Aucune derive significative detectee.")


if __name__ == "__main__":
    main()