# Metrics API

## Endpoint

GET /metrics

## Métriques collectées

- Nombre total de requêtes
- Latence moyenne
- Distribution des maladies prédites

## Exemple

{
    "total_requests": 10,
    "average_latency_ms": 250.4,
    "disease_distribution": {
        "Mildiou": 4,
        "Saine": 3,
        "Tache bactérienne": 3
    }
}