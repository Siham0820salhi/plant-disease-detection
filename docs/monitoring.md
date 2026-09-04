# Monitoring — Suivi des requêtes de l'API

## Objectif

Chaque fois qu'une prédiction est faite via `POST /predict`, l'API doit
enregistrer ce qui s'est passé : quand, combien de temps ça a pris, quelle
maladie a été détectée et avec quelle confiance. Ces informations permettent
de surveiller l'usage réel de l'API après déploiement, et servent de base
à l'endpoint `/metrics` et à la détection de dérive (drift).

## Architecture

```
Utilisateur
    │  image
    ▼
FastAPI
    │
    ▼
Middleware (monitoring_middleware)
    │  note l'heure de début
    ▼
POST /predict
    │
    ▼
Modèle ML
    │
    ▼
maladie + confiance
    │
    ▼
Middleware (calcule la durée, récupère la prédiction)
    │
    ├──► MetricsStore (mémoire, pour /metrics)
    └──► logs/predictions.csv (disque, persistant)
```

## Où se trouve le code

- **Middleware** : `src/api/main.py`, fonction `monitoring_middleware` — mesure
  le temps de traitement de chaque requête et déclenche l'enregistrement pour
  les appels à `/predict`.
- **Stockage** : `src/api/monitoring.py` — contient la classe `MetricsStore`,
  qui garde les métriques en mémoire ET les persiste dans un fichier CSV.

## Ce qui est enregistré

Pour chaque prédiction réussie :

| Champ | Description | Exemple |
|---|---|---|
| `timestamp` | Date et heure UTC de la requête (format ISO 8601) | `2026-09-04T13:17:25.656452+00:00` |
| `latency_ms` | Temps de traitement de la requête, en millisecondes | `320.5` |
| `disease` | Maladie détectée par le modèle (en français) | `Mildiou (brûlure tardive)` |
| `confidence` | Score de confiance de la prédiction (entre 0 et 1) | `0.95` |

## Double persistance : pourquoi ?

- **En mémoire** (`MetricsStore`) : rapide, utilisé directement par l'endpoint
  `GET /metrics` pour répondre instantanément sans lire un fichier à chaque
  requête.
- **Sur disque** (`logs/predictions.csv`) : garantit que l'historique des
  prédictions n'est **pas perdu** si l'API redémarre (crash, redéploiement,
  mise à jour). C'est la source de vérité durable.

Le fichier CSV est créé automatiquement (dossier `logs/` inclus) dès la
première prédiction, avec les en-têtes suivants :

```
timestamp,latency_ms,disease,confidence
```

## Robustesse

L'écriture dans le CSV est protégée par un `try/except` : si l'écriture
échoue pour une raison quelconque (disque plein, permissions...), la
prédiction continue de fonctionner normalement pour l'utilisateur. Le
monitoring ne doit jamais faire planter l'API.

## Tests

Voir `tests/test_monitoring.py` : vérifie que chaque appel à `log()`
incrémente bien les compteurs en mémoire, écrit bien une ligne dans le CSV
avec les bonnes colonnes, et que plusieurs requêtes s'accumulent sans se
remplacer.

## Limite connue

Les données en mémoire sont perdues au redémarrage (normal, c'est de la
RAM) — mais le fichier CSV, lui, persiste. En cas de besoin de recharger
l'historique en mémoire après un redémarrage, une amélioration future
possible serait de relire `logs/predictions.csv` au démarrage de l'API.
