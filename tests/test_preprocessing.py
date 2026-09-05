import os
import pytest
import numpy as np
import pandas as pd
from PIL import Image
# كنعيطو للخدمة ديال سلمى بصح
from src.preprocessing.preprocessing import preprocess_image, creer_split_stratifie

@pytest.fixture
def temp_image(tmp_path):
    """Fixture لتصنيع صورة وهمية لإجراء الاختبارات."""
    img_path = tmp_path / "test_image.jpg"
    img = Image.new('RGB', (500, 500), color='red')
    img.save(img_path)
    return str(img_path)

def test_preprocess_image_logic(temp_image):
    """Vérifier le redimensionnement et la normalisation (Tâche P2/P4)."""
    # 1. تنفيذ الدالة
    processed_img = preprocess_image(temp_image, target_size=(224, 224))
    
    # 2. التحقق من الأبعاد (Resize)
    assert processed_img.shape == (224, 224, 3), "Le resize n'est pas correct !"
    
    # 3. التحقق من التقييس (Normalization 0-1)
    assert processed_img.max() <= 1.0, "La normalisation a échoué : max > 1"
    assert processed_img.min() >= 0.0, "La normalisation a échoué : min < 0"
    assert processed_img.dtype == np.float32 or processed_img.dtype == np.float64

def test_creer_split_stratifie():
    """Vérifier que le split respecte les proportions 70/15/15 (Tâche P2/P4)."""
    # صاوبنا بيانات وهمية (100 سطر)
    data = {
        "chemin_image": [f"path_{i}" for i in range(100)],
        "classe": ["A"] * 50 + ["B"] * 50, # 50 تصويرة لكل صنف
        "nom_image": [f"img_{i}.jpg" for i in range(100)]
    }
    df = pd.DataFrame(data)
    
    train, val, test = creer_split_stratifie(df)
    
    # التحقق من النسب
    assert len(train) == 70, "Le split Train doit être de 70%"
    assert len(val) == 15, "Le split Val doit être de 15%"
    assert len(test) == 15, "Le split Test doit être de 15%"
    
    # التحقق من أن جميع الأصناف (Classes) موجودة في كل الأقسام (Stratification)
    assert train["classe"].nunique() == 2
    assert val["classe"].nunique() == 2
    assert test["classe"].nunique() == 2
