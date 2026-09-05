import pytest
from src.api.class_mapping import parse_class_name, CLASS_MAPPING

def test_parse_class_name_valid_keys():
    for raw_name in CLASS_MAPPING.keys():
        plante, maladie = parse_class_name(raw_name)
        assert isinstance(plante, str)
        assert isinstance(maladie, str)
        assert len(plante) > 0
        assert len(maladie) > 0

def test_parse_class_name_error():
    with pytest.raises(KeyError):
        parse_class_name("Invalid_Class_Name_123")

def test_specific_mapping_values():
    p, m = parse_class_name("Potato___Late_blight")
    assert p == "Pomme de terre"
    assert "Mildiou" in m

def test_healthy_status_mapping():
    p, m = parse_class_name("Tomato_healthy")
    assert p == "Tomate"
    assert "Saine" in m

def test_mapping_dictionary_integrity():
    assert len(CLASS_MAPPING) == 15
    for key, value in CLASS_MAPPING.items():
        assert isinstance(value, tuple)
        assert len(value) == 2
