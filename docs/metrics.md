# Endpoint `/metrics` — Statistiques d'utilisation de l'API

## Objectif

Exposer en temps réel des statistiques sur l'usage de l'API, calculées à
partir des données enregistrées par le monitoring (`src/api/monitoring.py`).

## Endpoint

```
GET /metrics
```

Aucun paramètre requis.

## Exemple de réponse

```json
{
  "total_requests": 42,
  "average_latency_ms": 336.9,
  "disease_distribution": {
    "Mildiou (brûlure tardive)": 12,
    "Saine (aucune maladie détectée)": 25,
    "Alternariose (brûlure précoce)": 5
  }
}
```

## Détail des champs

| Champ | Type | Description |
|---|---|---|
| `total_requests` | int | Nombre total de prédictions réussies traitées par l'API depuis son démarrage. |
| `average_latency_ms` | float | Temps de réponse moyen des requêtes `/predict`, en millisecondes. |
| `disease_distribution` | dict | Nombre de prédictions par maladie détectée. |

## Comment ces valeurs sont calculées

- `total_requests` : incrémenté de 1 à chaque appel de `metrics_store.log()`.
- `average_latency_ms` : moyenne cumulative — `total_response_time_ms / total_requests`.
  Renvoie `0.0` si aucune requête n'a encore été traitée (pas de division par zéro).
- `disease_distribution` : un compteur (`Counter`) qui incrémente le nom de
  la maladie prédite à chaque requête.

## Comportement avant toute prédiction

Si l'API vient de démarrer et qu'aucune image n'a encore été envoyée à
`/predict`, `/metrics` renvoie :

```json
{
  "total_requests": 0,
  "average_latency_ms": 0.0,
  "disease_distribution": {}
}
```

## Tester l'endpoint

**Avec curl (PowerShell : utiliser `curl.exe`)** :
```bash
curl.exe http://127.0.0.1:8000/metrics
```

**Avec Swagger UI** : ouvrir `http://127.0.0.1:8000/docs`, dérouler
`GET /metrics`, cliquer sur "Try it out" puis "Execute".

**Workflow de test complet** :
1. Lancer l'API.
2. Appeler `/metrics` → vérifier `total_requests: 0`.
3. Envoyer une ou plusieurs images à `POST /predict`.
4. Rappeler `/metrics` → vérifier que `total_requests` a augmenté et que
   `disease_distribution` contient les maladies prédites.

## Tests automatisés

Voir `tests/test_metrics.py` : vérifie le calcul du total, de la latence
moyenne, de la distribution par maladie, ainsi que le comportement à vide
(avant toute requête).

## Lien avec le drift

Les mêmes données de prédiction (via `logs/predictions.csv`) pourraient à
l'avenir alimenter une comparaison entre les maladies prédites en
production et leur répartition dans le jeu d'entraînement — une piste
d'amélioration au-delà du drift sur les caractéristiques d'image (voir
`drift.md`).
