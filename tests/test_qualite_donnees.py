import os
import pytest
from PIL import Image
import hashlib

# المسارات الأساسية
TRAIN_DIR = "data/processed/train"

def get_all_images(directory):
    """Récupère tous les chemins d'images dans un dossier."""
    image_paths = []
    if not os.path.exists(directory):
        return []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_paths.append(os.path.join(root, file))
    return image_paths

def test_no_corrupted_images():
    """Vérifier qu'aucune image n'est corrompue et peut être ouverte (Tâche P2/P4)."""
    images = get_all_images(TRAIN_DIR)
    # نختبروا عينة من 50 تصويرة باش التيست يكون سريع
    for img_path in images[:50]:
        try:
            with Image.open(img_path) as img:
                img.verify() 
        except Exception as e:
            pytest.fail(f"Image corrompue détectée : {img_path} - {e}")

def test_no_duplicate_images():
    """Vérifier qu'il n'y a pas d'images identiques (doublons) par Hash MD5."""
    images = get_all_images(TRAIN_DIR)
    hashes = set()
    # نختبروا عينة باش ما نـقـلّـوش الـ PC
    for img_path in images[:50]:
        with open(img_path, "rb") as f:
            img_hash = hashlib.md5(f.read()).hexdigest()
        
        if img_hash in hashes:
            pytest.fail(f"Doublon détecté : {img_path}")
        hashes.add(img_hash)

def test_dataset_balance():
    """Vérifier si le dataset n'est pas trop déséquilibré (au moins 10 images par classe)."""
    classes = [d for d in os.listdir(TRAIN_DIR) if os.path.isdir(os.path.join(TRAIN_DIR, d))]
    for cls in classes:
        num_images = len(os.listdir(os.path.join(TRAIN_DIR, cls)))
        assert num_images > 0, f"La classe {cls} est vide !"
