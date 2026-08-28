

from tensorflow.keras import layers, models, optimizers
from tensorflow.keras.applications import MobileNetV2, ResNet50, EfficientNetB0
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input as _mobilenetv2_preprocess
from tensorflow.keras.applications.resnet50 import preprocess_input as _resnet50_preprocess
from tensorflow.keras.applications.efficientnet import preprocess_input as _efficientnetb0_preprocess

IMG_SHAPE = (224, 224, 3)


DEFAULT_LEARNING_RATE = 1e-3
DEFAULT_FINE_TUNE_LEARNING_RATE = 1e-5


def build_baseline_cnn(num_classes: int, img_shape: tuple = IMG_SHAPE,
                        learning_rate: float = DEFAULT_LEARNING_RATE):
    model = models.Sequential([
        layers.Input(shape=img_shape),

        layers.Conv2D(32, 3, activation="relu", padding="same"),
        layers.BatchNormalization(),
        layers.MaxPooling2D(),

        layers.Conv2D(64, 3, activation="relu", padding="same"),
        layers.BatchNormalization(),
        layers.MaxPooling2D(),

        layers.Conv2D(128, 3, activation="relu", padding="same"),
        layers.BatchNormalization(),
        layers.MaxPooling2D(),

        layers.Conv2D(256, 3, activation="relu", padding="same"),
        layers.BatchNormalization(),
        layers.MaxPooling2D(),

        layers.GlobalAveragePooling2D(),
        layers.Dense(256, activation="relu"),
        layers.Dropout(0.4),
        layers.Dense(num_classes, activation="softmax"),
    ], name="baseline_cnn")

    model.compile(
        optimizer=optimizers.Adam(learning_rate=learning_rate),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def _build_transfer_model(base_model, num_classes: int, fine_tune: bool,
                           learning_rate: float):
    """Squelette commun pour les modèles de Transfer Learning."""
    base_model.trainable = fine_tune

    inputs = layers.Input(shape=IMG_SHAPE)
    x = base_model(inputs, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(256, activation="relu")(x)
    x = layers.Dropout(0.4)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = models.Model(inputs, outputs, name=base_model.name + "_transfer")
    model.compile(
        optimizer=optimizers.Adam(learning_rate=learning_rate),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def _resolve_learning_rate(fine_tune: bool, learning_rate, fine_tune_learning_rate) -> float:
   
    if learning_rate is not None:
        return learning_rate
    return fine_tune_learning_rate if fine_tune else DEFAULT_LEARNING_RATE


def build_mobilenetv2(num_classes: int, fine_tune: bool = False,
                       learning_rate: float = None,
                       fine_tune_learning_rate: float = DEFAULT_FINE_TUNE_LEARNING_RATE):
    base = MobileNetV2(input_shape=IMG_SHAPE, include_top=False, weights="imagenet")
    lr = _resolve_learning_rate(fine_tune, learning_rate, fine_tune_learning_rate)
    return _build_transfer_model(base, num_classes, fine_tune, learning_rate=lr)


def build_resnet50(num_classes: int, fine_tune: bool = False,
                    learning_rate: float = None,
                    fine_tune_learning_rate: float = DEFAULT_FINE_TUNE_LEARNING_RATE):
    base = ResNet50(input_shape=IMG_SHAPE, include_top=False, weights="imagenet")
    lr = _resolve_learning_rate(fine_tune, learning_rate, fine_tune_learning_rate)
    return _build_transfer_model(base, num_classes, fine_tune, learning_rate=lr)


def build_efficientnetb0(num_classes: int, fine_tune: bool = False,
                          learning_rate: float = None,
                          fine_tune_learning_rate: float = DEFAULT_FINE_TUNE_LEARNING_RATE):
    base = EfficientNetB0(input_shape=IMG_SHAPE, include_top=False, weights="imagenet")
    lr = _resolve_learning_rate(fine_tune, learning_rate, fine_tune_learning_rate)
    return _build_transfer_model(base, num_classes, fine_tune, learning_rate=lr)


MODEL_REGISTRY = {
    "baseline_cnn": build_baseline_cnn,
    "mobilenetv2": build_mobilenetv2,
    "resnet50": build_resnet50,
    "efficientnetb0": build_efficientnetb0,
}


PREPROCESS_FUNCTIONS = {
    "baseline_cnn": None,
    "mobilenetv2": _mobilenetv2_preprocess,
    "resnet50": _resnet50_preprocess,
    "efficientnetb0": _efficientnetb0_preprocess,
}


def get_model(name: str, num_classes: int, **kwargs):
    if name not in MODEL_REGISTRY:
        raise ValueError(
            f"Modèle inconnu '{name}'. Choix possibles : {list(MODEL_REGISTRY)}"
        )
    return MODEL_REGISTRY[name](num_classes=num_classes, **kwargs)


def get_preprocessing_function(name: str):
   
    if name not in PREPROCESS_FUNCTIONS:
        raise ValueError(
            f"Modèle inconnu '{name}'. Choix possibles : {list(PREPROCESS_FUNCTIONS)}"
        )
    return PREPROCESS_FUNCTIONS[name]
