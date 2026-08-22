# API Plant Disease Detection — Guide de démarrage

Documentation de l'API FastAPI de diagnostic de maladies des feuilles de plantes (tomate, poivron, pomme de terre).

---

## Prérequis

- Python 3.10+
- Les dépendances listées dans `requirements.txt` à la racine du projet.

---

## Installation des dépendances

Depuis la **racine du projet** :

```bash
pip install -r requirements.txt
```

---

## Lancer l'API en local

Depuis la **racine du projet** (important : ne pas lancer depuis `api/`) :

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

L'API sera accessible sur : [http://localhost:8000](http://localhost:8000)

La documentation interactive Swagger est disponible sur : [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Endpoints disponibles

### `GET /health` — Vérification de l'état de l'API

Vérifie que l'API est opérationnelle.

**Réponse exemple :**
```json
{
  "status": "ok",
  "model_version": "dummy-v0"
}
```

**Commande curl :**
```bash
curl http://localhost:8000/health
```

---

### `POST /predict` — Diagnostic d'une feuille de plante

Envoie une image de feuille et reçoit un diagnostic (plante + maladie + score de confiance).

**Contraintes :**
- Formats acceptés : `.jpg`, `.jpeg`, `.png`
- Taille maximale : **5 Mo**

**Réponse exemple :**
```json
{
  "plante": "Tomate",
  "maladie": "Mildiou (brûlure tardive)",
  "confidence": 0.8731
}
```

**Commande curl avec upload d'image :**
```bash
curl -X POST \
  -F "file=@chemin/vers/image.jpg" \
  http://localhost:8000/predict
```

**Exemple concret :**
```bash
curl -X POST \
  -F "file=@/home/utilisateur/images/feuille_tomate.jpg" \
  http://localhost:8000/predict
```

**Exemple avec HTTPie :**
```bash
http POST http://localhost:8000/predict file@chemin/vers/image.jpg
```

---

## Lancer les tests

Depuis la **racine du projet** :

```bash
pytest api/tests/ -v
```

---

## Structure du dossier `api/`

```
api/
├── __init__.py           # Déclaration du package Python
├── main.py               # Application FastAPI (endpoints /predict et /health)
├── models.py             # Schémas Pydantic de réponse
├── class_mapping.py      # Mapping classe brute → (plante, maladie) en français
├── tests/
│   ├── __init__.py
│   ├── test_health.py    # Tests de l'endpoint /health
│   └── test_predict.py   # Tests de l'endpoint /predict
└── README.md             # Ce fichier
```

---

## Notes d'intégration (pour l'équipe)

> **TODO :** Le modèle de prédiction est actuellement une simulation aléatoire.
> Il doit être remplacé par le vrai modèle CNN fourni via **MLflow** par le membre P6.
> Voir le commentaire `# TODO: remplacer par le vrai modèle MLflow (fourni par P6)` dans `main.py`.
