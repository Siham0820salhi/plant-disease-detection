import pytest
import numpy as np
import pandas as pd
from PIL import Image
from src.preprocessing.preprocessing import preprocess_image, creer_split_stratifie

@pytest.fixture
def dummy_img(tmp_path):
    path = tmp_path / "test.jpg"
    Image.new("RGB", (300, 300), color="green").save(path)
    return str(path)

@pytest.fixture
def dummy_df():
    data = {
        "chemin_image": [f"p_{i}" for i in range(100)],
        "classe": ["cls1"] * 50 + ["cls2"] * 50,
        "nom_image": [f"img_{i}.jpg" for i in range(100)]
    }
    return pd.DataFrame(data)

def test_preprocess_output(dummy_img):
    output = preprocess_image(dummy_img)
    assert output.shape == (224, 224, 3)
    assert output.dtype in [np.float32, np.float64]
    assert output.max() <= 1.0 and output.min() >= 0.0

def test_stratified_split(dummy_df):
    train, val, test = creer_split_stratifie(dummy_df)
    assert len(train) == 70
    assert len(val) == 15
    assert len(test) == 15
    assert train["classe"].nunique() == val["classe"].nunique() == test["classe"].nunique() == 2

def test_preprocess_error():
    with pytest.raises(Exception):
        preprocess_image("invalid_path.png")
