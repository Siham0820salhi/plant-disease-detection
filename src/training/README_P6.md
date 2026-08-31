# Personne 6 — ML Engineer : Modèle + MLflow

Pipeline d'entraînement, de comparaison de stratégies, d'évaluation et
d'enregistrement automatique du meilleur modèle dans le MLflow Model Registry,
pour la détection de maladies des feuilles de plantes (dataset PlantVillage).

## Fichiers

| Fichier | Rôle |
|---|---|
| `train.py` | Pipeline complet : data loaders, entraînement, comparaison de stratégies, évaluation, MLflow, Registry. Point d'entrée unique (CLI + `run_training()` pour Dagster). |
| `models.py` | Architectures : CNN baseline (from scratch) + Transfer Learning (MobileNetV2, ResNet50, EfficientNetB0). |
| `evaluate.py` | Calcul des métriques (accuracy, precision/recall/F1 macro), matrice de confusion, courbes d'apprentissage. |
| `data_loaders.py` | Générateurs d'images (batching, augmentation à la volée), calcul des `class_weight`. |

## Prérequis

Les images prétraitées de P4 doivent être présentes dans `data/processed/{train,val,test}/<classe>/`.

## Utilisation

### En ligne de commande

Une seule stratégie de gestion du déséquilibre :
```bash
python train.py --model resnet50 --epochs 10 --imbalance-strategy class_weight
```

Comparer plusieurs stratégies sur un ou plusieurs modèles (le vrai meilleur
résultat global est automatiquement enregistré en production) :
```bash
python train.py --model all --epochs 10 --imbalance-strategy class_weight augmentation_p4
```

Modèles disponibles : `baseline_cnn`, `mobilenetv2`, `resnet50`, `efficientnetb0`, `all`
Stratégies disponibles : `none`, `class_weight`, `augmentation_p4`, `augmentation_online`, `both`, `auto`

### Depuis Dagster (P5)

```python
from train import run_training

run_id, model_name, f1 = run_training(
    model="all",
    epochs=10,
    imbalance_strategy=["class_weight", "augmentation_p4"],
)
```

## MLflow

### Lancer l'interface MLflow

```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db
```
Puis ouvrir [http://127.0.0.1:5000](http://127.0.0.1:5000).

### Tracking

Chaque run logge : les paramètres (modèle, stratégie, epochs...), les métriques
(accuracy, f1_macro, precision_macro, recall_macro, f1 par classe), la matrice
de confusion, les courbes de loss/accuracy, le rapport de classification, et
le modèle entraîné en artefact.

### Model Registry

Le meilleur modèle est automatiquement enregistré sous le nom
`plant-disease-classifier`, avec l'alias `production` — **jamais de
downgrade** : l'alias n'est déplacé que si le nouveau modèle bat le score
actuel de production (comparaison sur `f1_macro`).

Pour charger le modèle de production (ex. depuis l'API de P7) :
```python
import mlflow
model = mlflow.pyfunc.load_model("models:/plant-disease-classifier@production")
```

⚠️ **Configuration partagée requise** : par défaut, MLflow utilise une base
SQLite locale (`sqlite:///mlflow.db`). Pour que toute l'équipe (P5, P7, P8)
accède au même Registry, définir la variable d'environnement
`MLFLOW_TRACKING_URI` vers un emplacement partagé (serveur MLflow commun ou
chemin réseau/drive partagé) — à convenir en équipe.

## Résultats actuels (production)

| Modèle | Stratégie | f1_macro |
|---|---|---|
| **ResNet50** | **augmentation_p4** | **0.9756** ← en production |
| ResNet50 | class_weight | 0.9696 |
| EfficientNetB0 | class_weight | 0.9692 |
| EfficientNetB0 | augmentation_p4 | 0.9642 |
| Baseline CNN | augmentation_p4 | 0.9638 |
| Baseline CNN | class_weight | 0.9427 |
| MobileNetV2 | augmentation_p4 | 0.9245 |
| MobileNetV2 | class_weight | 0.9117 |

**Conclusion** : l'augmentation ciblée hors-ligne (P4) sur les classes
minoritaires bat `class_weight='balanced'` sur 3 des 4 architectures testées.
ResNet50 est l'architecture la plus performante sur ce dataset.

*Note : les résultats peuvent varier de ±1-2 points de f1_macro entre deux
runs identiques (pas de seed fixée) ; les tendances entre modèles et
stratégies restent cohérentes d'un run à l'autre.*
