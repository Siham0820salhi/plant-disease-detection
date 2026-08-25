"""
evaluate.py
-----------
Personne 6 - ML Engineer : Modèle + MLflow

Rôle (Tâche 4 du cahier des charges) : évaluation complète d'un modèle
- accuracy, precision/recall/F1 macro (important car 15 classes, dont
  certaines très minoritaires)
- matrice de confusion
- courbes d'apprentissage
Ne jamais se fier uniquement à l'accuracy globale.

matplotlib.use("Agg") : backend sans affichage interactif, nécessaire
pour exécuter ce module dans un environnement serveur/headless (scripts,
CI/CD de P7, assets Dagster de P5) où aucun écran n'est disponible.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score


def evaluate_model(model, test_gen, class_names: list) -> dict:
    """
    Fait des prédictions sur test_gen et calcule toutes les métriques.
    Retourne un dict prêt à être loggé dans MLflow, incluant "report_dict"
    (métriques par classe, format numérique exploitable).
    """
    test_gen.reset()
    y_true = test_gen.classes
    y_pred_probs = model.predict(test_gen, verbose=0)
    y_pred = np.argmax(y_pred_probs, axis=1)

    report_dict = classification_report(
        y_true, y_pred, target_names=class_names, output_dict=True, zero_division=0
    )
    report_text = classification_report(
        y_true, y_pred, target_names=class_names, zero_division=0
    )

    metrics = {
        "accuracy": accuracy_score(y_true, y_pred),
        "f1_macro": f1_score(y_true, y_pred, average="macro", zero_division=0),
        "precision_macro": report_dict["macro avg"]["precision"],
        "recall_macro": report_dict["macro avg"]["recall"],
    }

    return {
        "metrics": metrics,
        "report": report_text,
        "report_dict": report_dict,
        "confusion_matrix": confusion_matrix(y_true, y_pred),
        "y_true": y_true,
        "y_pred": y_pred,
    }


def per_class_f1_metrics(report_dict: dict) -> dict:
    """
    Extrait uniquement le f1-score par classe du report_dict, avec des
    noms de métriques MLflow-safe (préfixe 'f1_', pas d'espaces/slashs/
    virgules). Ignore les clés globales (accuracy, macro avg, weighted avg).
    """
    ignore_keys = {"accuracy", "macro avg", "weighted avg"}
    metrics = {}
    for class_name, values in report_dict.items():
        if class_name in ignore_keys:
            continue
        safe_name = class_name.replace(" ", "_").replace("/", "_").replace(",", "")
        metrics[f"f1_{safe_name}"] = values["f1-score"]
    return metrics


def plot_confusion_matrix(cm: np.ndarray, class_names: list, out_path: Path):
    """Sauvegarde la matrice de confusion en PNG (pour artefact MLflow)."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, annot=False, cmap="Blues",
                xticklabels=class_names, yticklabels=class_names)
    plt.xlabel("Prédiction")
    plt.ylabel("Vérité terrain")
    plt.title("Matrice de confusion")
    plt.xticks(rotation=90)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_learning_curves(history, out_path: Path):
    """Sauvegarde les courbes loss/accuracy train vs val (pour artefact MLflow)."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    axes[0].plot(history.history["loss"], label="train")
    axes[0].plot(history.history["val_loss"], label="val")
    axes[0].set_title("Loss")
    axes[0].set_xlabel("Epoch")
    axes[0].legend()

    axes[1].plot(history.history["accuracy"], label="train")
    axes[1].plot(history.history["val_accuracy"], label="val")
    axes[1].set_title("Accuracy")
    axes[1].set_xlabel("Epoch")
    axes[1].legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()