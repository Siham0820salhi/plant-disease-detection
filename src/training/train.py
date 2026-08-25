

import argparse
import os
from pathlib import Path

import mlflow
import mlflow.keras
from mlflow.models import infer_signature
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

from data_loaders import DATA_DIR, build_generators, build_train_dataframe, compute_class_weights
from evaluate import evaluate_model, per_class_f1_metrics, plot_confusion_matrix, plot_learning_curves
from models import MODEL_REGISTRY, get_model, get_preprocessing_function

EXPERIMENT_NAME = "plant-disease-detection"
REGISTERED_MODEL_NAME = "plant-disease-classifier"
ARTIFACT_DIR = Path("artifacts")

TRANSFER_LEARNING_MODELS = {"mobilenetv2", "resnet50", "efficientnetb0"}

IMBALANCE_STRATEGIES = [
    "none",
    "class_weight",
    "augmentation_p4",
    "augmentation_online",
    "both",
]


AUTO_STRATEGY_THRESHOLDS = [
    (2,  "none"),              
    (5,  "class_weight"),       
    (15, "augmentation_p4"),    
   
]


# ---------------------------------------------------------------------------
# Résolution de stratégie
# ---------------------------------------------------------------------------

def compute_imbalance_ratio(data_dir: Path = DATA_DIR):
    """
    Ratio (classe majoritaire / classe minoritaire) sur les images
    ORIGINALES du train set (sans les aug_ de P4) : mesure le déséquilibre
    réel du dataset brut, pas celui déjà partiellement corrigé par P4.

    Retourne (ratio, counts) où counts est une Series pandas classe -> nb.
    """
    df = build_train_dataframe(Path(data_dir) / "train", include_offline_augmented=False)
    counts = df["classe"].value_counts()
    ratio = counts.max() / counts.min()
    return ratio, counts


def auto_select_strategy(ratio: float) -> str:
    """Choisit une stratégie parmi IMBALANCE_STRATEGIES à partir du ratio
    de déséquilibre mesuré, selon AUTO_STRATEGY_THRESHOLDS."""
    for seuil, strategy in AUTO_STRATEGY_THRESHOLDS:
        if ratio < seuil:
            return strategy
    return "both"


def _resolve_strategy_flags(strategy: str) -> tuple:
    """
    Traduit une stratégie EXPLICITE (jamais "auto" à ce stade -- déjà
    résolue en amont) en 3 booléens sans ambiguïté :
        (use_class_weights, augment_online, include_offline_augmented_p4)
    """
    mapping = {
        "none":                 (False, False, False),
        "class_weight":         (True,  False, False),
        "augmentation_p4":      (False, False, True),
        "augmentation_online":  (False, True,  False),
        "both":                 (True,  True,  False),
    }
    if strategy not in mapping:
        raise ValueError(
            f"Stratégie inconnue : '{strategy}'. "
            f"Choix possibles : {list(mapping.keys())} (ou 'auto')."
        )
    return mapping[strategy]


# ---------------------------------------------------------------------------
# Entraînement d'un modèle
# ---------------------------------------------------------------------------

def train_one_model(model_name: str, epochs: int, batch_size: int,
                     imbalance_strategy: str, fine_tune: bool,
                     requested_strategy: str = None, imbalance_ratio: float = None):
   
    use_class_weights, augment_online, include_offline_augmented = _resolve_strategy_flags(
        imbalance_strategy
    )

    preprocessing_function = get_preprocessing_function(model_name)
    train_gen, val_gen, test_gen, class_indices = build_generators(
        batch_size=batch_size,
        preprocessing_function=preprocessing_function,
        augment_online=augment_online,
        include_offline_augmented=include_offline_augmented,
    )
    class_names = list(class_indices.keys())
    class_weights = compute_class_weights(train_gen) if use_class_weights else None

    model_type = "transfer_learning" if model_name in TRANSFER_LEARNING_MODELS else "baseline"

    with mlflow.start_run(run_name=f"{model_name}_{imbalance_strategy}"):
        # ---- Tags (filtrage/comparaison facile dans l'UI MLflow) ----
        mlflow.set_tags({
            "model_type": model_type,
            "imbalance_strategy": imbalance_strategy,
            "requested_strategy": requested_strategy or imbalance_strategy,
            "p4_augmentation_included": include_offline_augmented,
        })

        # ---- Params ----
        mlflow.log_params({
            "model_name": model_name,
            "epochs": epochs,
            "batch_size": batch_size,
            "img_size": "224x224",
            "num_classes": len(class_names),
            "imbalance_strategy": imbalance_strategy,
            "use_class_weights": use_class_weights,
            "augment_online": augment_online,
            "include_offline_augmented_p4": include_offline_augmented,
            "train_samples": train_gen.samples,
            "fine_tune": fine_tune,
            "preprocessing": "model_specific" if preprocessing_function else "rescale_1_255",
        })
        if imbalance_ratio is not None:
            mlflow.log_metric("dataset_imbalance_ratio", float(imbalance_ratio))

        # ---- Modèle ----
        kwargs = {} if model_name == "baseline_cnn" else {"fine_tune": fine_tune}
        model = get_model(model_name, num_classes=len(class_names), **kwargs)

        callbacks = [
            EarlyStopping(monitor="val_loss", patience=4, restore_best_weights=True),
            ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=2),
        ]

        history = model.fit(
            train_gen,
            validation_data=val_gen,
            epochs=epochs,
            class_weight=class_weights,
            callbacks=callbacks,
            verbose=1,
        )

        # ---- Évaluation sur le test set ----
        results = evaluate_model(model, test_gen, class_names)
        mlflow.log_metrics(results["metrics"])
        mlflow.log_metrics(per_class_f1_metrics(results["report_dict"]))
        print(f"\n[{model_name} | {imbalance_strategy}] Métriques test : {results['metrics']}")
        print(results["report"])

        # ---- Artefacts graphiques + rapport texte ----
        run_artifact_dir = ARTIFACT_DIR / model_name / imbalance_strategy
        cm_path = run_artifact_dir / "confusion_matrix.png"
        curves_path = run_artifact_dir / "learning_curves.png"
        plot_confusion_matrix(results["confusion_matrix"], class_names, cm_path)
        plot_learning_curves(history, curves_path)
        mlflow.log_artifact(str(cm_path))
        mlflow.log_artifact(str(curves_path))

        report_path = run_artifact_dir / "classification_report.txt"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(results["report"])
        mlflow.log_artifact(str(report_path))

        # ---- Modèle en artefact MLflow, avec signature + input_example ----
        sample_batch_x, _ = next(train_gen)
        input_example = sample_batch_x[:1]
        signature = infer_signature(input_example, model.predict(input_example, verbose=0))
       
        mlflow.keras.log_model(
            model,
            name="model",
            signature=signature,
        )

        run_id = mlflow.active_run().info.run_id
        f1_macro = results["metrics"]["f1_macro"]
        return run_id, f1_macro


# ---------------------------------------------------------------------------
# Model Registry (sécurisé : jamais de downgrade de "production")
# ---------------------------------------------------------------------------

def get_current_production_f1(client) -> tuple:
    """
    Regarde si un modèle a déjà l'alias 'production' dans le Registry,
    et retourne son f1_macro (ou -1 s'il n'y en a pas encore).
    """
    try:
        current = client.get_model_version_by_alias(REGISTERED_MODEL_NAME, "production")
        run = client.get_run(current.run_id)
        return run.data.metrics.get("f1_macro", -1.0), current.version
    except Exception:
        return -1.0, None


def register_best_model(best_run_id: str, best_model_name: str, best_f1: float):
    """
    Enregistre le run dans le Model Registry, et ne met à jour l'alias
    'production' QUE si ce nouveau modèle est meilleur que celui déjà
    en production (comparaison sur f1_macro). Jamais de downgrade.
    """
    client = mlflow.MlflowClient()
    current_f1, current_version = get_current_production_f1(client)

    model_uri = f"runs:/{best_run_id}/model"
    result = mlflow.register_model(model_uri, REGISTERED_MODEL_NAME)

    if best_f1 > current_f1:
        client.set_registered_model_alias(
            name=REGISTERED_MODEL_NAME, alias="production", version=result.version,
        )
        print(f"\n>>> Nouveau meilleur modèle : {best_model_name} "
              f"(f1_macro={best_f1:.4f} > ancien production f1_macro={current_f1:.4f})")
        print(f">>> Enregistré comme '{REGISTERED_MODEL_NAME}' version {result.version} "
              f"avec l'alias 'production'.")
    else:
        print(f"\n>>> {best_model_name} (f1_macro={best_f1:.4f}) enregistré comme version "
              f"{result.version}, MAIS moins bon que le modèle déjà en production "
              f"(version {current_version}, f1_macro={current_f1:.4f}).")
        print(">>> L'alias 'production' n'a PAS été déplacé.")


# ---------------------------------------------------------------------------
# Point d'entrée réutilisable -- appelable depuis Dagster (P5) ou CLI
# ---------------------------------------------------------------------------

def run_training(model: str = "all", epochs: int = 15, batch_size: int = 32,
                  imbalance_strategy="class_weight", fine_tune: bool = False):
  
    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(EXPERIMENT_NAME)

   
    strategies_requested = (
        list(imbalance_strategy)
        if isinstance(imbalance_strategy, (list, tuple))
        else [imbalance_strategy]
    )

    
    imbalance_ratio = None
    if strategies_requested == ["auto"]:
        imbalance_ratio, _counts = compute_imbalance_ratio(DATA_DIR)
        resolved_strategies = [auto_select_strategy(imbalance_ratio)]
        print(f"[auto] Ratio de déséquilibre mesuré : {imbalance_ratio:.2f} "
              f"-> stratégie choisie automatiquement : '{resolved_strategies[0]}'")
    else:
        resolved_strategies = strategies_requested

    models_to_run = list(MODEL_REGISTRY.keys()) if model == "all" else [model]

    best_run_id, best_model_name, best_strategy, best_f1 = None, None, None, -1.0
    failed_runs = []
    all_results = []

    
    for model_name in models_to_run:
        for strategy in resolved_strategies:
            print("\n" + "=" * 70)
            print(f"MODELE : {model_name}  |  STRATEGIE : {strategy}")
            print("=" * 70)
            try:
                run_id, f1_macro = train_one_model(
                    model_name, epochs, batch_size, strategy, fine_tune,
                    requested_strategy=imbalance_strategy, imbalance_ratio=imbalance_ratio,
                )
                all_results.append({
                    "model": model_name, "strategy": strategy,
                    "run_id": run_id, "f1_macro": f1_macro,
                })
                if f1_macro > best_f1:
                    best_run_id = run_id
                    best_model_name = model_name
                    best_strategy = strategy
                    best_f1 = f1_macro
            except Exception as e:
                print(f"\n[ERREUR] Échec pour '{model_name}' | '{strategy}' : {e}")
                print("[ERREUR] Le pipeline continue avec les combinaisons suivantes.")
                failed_runs.append((model_name, strategy))
                continue

    if best_run_id is None:
        raise RuntimeError(
            f"Aucune combinaison modèle/stratégie n'a abouti à un run réussi. "
            f"Échecs : {failed_runs}"
        )

    # ---- Récapitulatif de la comparaison (visible dans les logs Dagster) ----
    if len(all_results) > 1:
        print("\n" + "=" * 70)
        print("COMPARAISON DES RUNS DE CE run_training()")
        print("=" * 70)
        for r in sorted(all_results, key=lambda r: r["f1_macro"], reverse=True):
            marqueur = " <== meilleur" if r["run_id"] == best_run_id else ""
            print(f"{r['model']:<18}{r['strategy']:<22}f1_macro={r['f1_macro']:.4f}{marqueur}")
        print("=" * 70)

    # ---- Enregistrement : UNE SEULE fois, sur le vrai meilleur run global ----
    print(f"\n>>> Meilleure combinaison : model={best_model_name} | "
          f"strategy={best_strategy} | f1_macro={best_f1:.4f}")
    register_best_model(best_run_id, best_model_name, best_f1)

    if failed_runs:
        print(f"\n[RÉSUMÉ] Combinaisons en échec (non prises en compte) : {failed_runs}")
        print("[RÉSUMÉ] Relancez-les individuellement une fois la cause corrigée "
              "(ex. espace disque) pour qu'elles entrent dans la comparaison.")

    return best_run_id, best_model_name, best_f1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Entraîne un ou plusieurs modèles de classification de maladies des feuilles."
    )
    parser.add_argument("--model", type=str, default="all",
                         choices=list(MODEL_REGISTRY.keys()) + ["all"],
                         help="Modèle à entraîner ('all' pour tout comparer)")
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--imbalance-strategy", type=str, nargs="+", default=["class_weight"],
                         choices=IMBALANCE_STRATEGIES + ["auto"],
                         help="Une ou plusieurs stratégies à comparer : "
                              "none | class_weight | augmentation_p4 | "
                              "augmentation_online | both | auto. "
                              "Ex: --imbalance-strategy class_weight augmentation_p4 "
                              "pour comparer les deux et enregistrer automatiquement "
                              "la meilleure en production.")
    parser.add_argument("--fine-tune", action="store_true", default=False,
                         help="Dégèle le backbone pour les modèles de transfer learning "
                              "(utilise automatiquement un learning rate plus faible)")
    return parser.parse_args()


def main():
    """Point d'entrée CLI uniquement -- toute la logique est dans run_training()."""
    args = parse_args()
    
    strategy_arg = args.imbalance_strategy[0] if len(args.imbalance_strategy) == 1 \
        else args.imbalance_strategy
    run_training(
        model=args.model,
        epochs=args.epochs,
        batch_size=args.batch_size,
        imbalance_strategy=strategy_arg,
        fine_tune=args.fine_tune,
    )


if __name__ == "__main__":
    main()
