import pytest
from src.ingestion.pipeline_ingestion import parse_plante_maladie, generer_lots, generer_metadonnees

@pytest.mark.parametrize("folder, expected", [
    ("Tomato___Late_blight", ("Tomato", "Late_blight")),
    ("Potato_healthy", ("Potato", "healthy")),
    ("Grape__Black_rot", ("Grape", "Black_rot")),
    ("UnknownFolder", ("UnknownFolder", "unknown"))
])
def test_parse_logic(folder, expected):
    assert parse_plante_maladie(folder) == expected

def test_lot_generation():
    data = list(range(2500))
    lots = generer_lots(data, taille_lot=1000)
    assert len(lots) == 3
    assert len(lots[0]) == 1000
    assert len(lots[2]) == 500

def test_metadata_structure(tmp_path):
    d = tmp_path / "Tomato___Healthy"
    d.mkdir()
    (d / "img1.jpg").write_text("data")
    (d / "img2.png").write_text("data")
    (tmp_path / "not_a_dir.txt").write_text("data")

    meta = generer_metadonnees(str(tmp_path))
    assert len(meta) == 2
    assert meta[0]["plante"] == "Tomato"
    assert meta[0]["chemin_image"].endswith("img1.jpg")

def test_empty_metadata():
    assert generer_metadonnees("/tmp/non_existent_folder_xyz") == []
