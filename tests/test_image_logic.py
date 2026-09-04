import io
import numpy as np
from PIL import Image
from src.api.main import preprocess_image

def test_preprocess_dimensions():
    """Vérifier que le preprocessing redimensionne bien en 224x224 (Tâche P2/P4)."""
    # 1. صاوبي تصويرة وهمية كبيرة (500x500)
    img = Image.new('RGB', (500, 500), color='green')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_bytes = img_byte_arr.getvalue()

    # 2. خدمي الفونكسيون ديال أميمة اللي وسط main.py
    processed_img = preprocess_image(img_bytes)

    # 3. تأكدي بلي النتيجة هي 224x224 (مهم بزاف في MLOps)
    assert processed_img.shape == (1, 224, 224, 3)
    assert processed_img.dtype == np.float32
