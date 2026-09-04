# Détection de dérive (Data Drift)

## Objectif

Répondre à la question : **est-ce que les nouvelles images reçues par
l'API ressemblent toujours aux images utilisées pour entraîner le
modèle ?**

Le modèle a été entraîné sur le dataset PlantVillage, composé d'images
prises dans des conditions plutôt contrôlées. En production, un
agriculteur peut envoyer des photos avec des conditions très différentes
(luminosité naturelle, arrière-plan, angle, humidité sur la feuille...).
Si l'écart devient trop important, les performances du modèle peuvent se
dégrader silencieusement — d'où l'intérêt de le détecter tôt.

## Où se trouve le code

`src/monitoring/drift.py`

## Méthode

### Caractéristiques comparées

Pour chaque image, on calcule 4 caractéristiques simples :

| Caractéristique | Description |
|---|---|
| `luminosite` | Moyenne globale des pixels (tous canaux confondus) |
| `rouge_moyen` | Moyenne du canal rouge |
| `vert_moyen` | Moyenne du canal vert |
| `bleu_moyen` | Moyenne du canal bleu |

### Jeux de données comparés

```
REFERENCE                          CURRENT
data/processed/train/      vs      data/new_data/
(images d'entraînement)            (nouvelles images simulées)
```

Si `data/processed/train` n'existe pas encore (pipeline de P4 pas encore
exécuté), le script utilise automatiquement `data/raw` comme repli — les
statistiques restent pertinentes car le redimensionnement n'affecte pas
significativement la luminosité ou les couleurs moyennes d'une image.

### Test statistique

Le script utilise le **test de Kolmogorov-Smirnov** (`scipy.stats.ks_2samp`),
qui compare deux distributions et renvoie une p-value : la probabilité que
la différence observée soit due au hasard.

**Règle de décision** :

```
p-value < 0.05   →  ⚠️ Drift détecté
p-value >= 0.05  →  ✅ Pas de drift statistiquement significatif
```

⚠️ **Nuance importante** : ce seuil est un signal statistique, pas une
preuve absolue que le modèle est devenu mauvais. Un drift détecté indique
qu'un changement mérite d'être investigué (éventuellement un
réentraînement), pas que le modèle a nécessairement failli.

## Lancer le script

Depuis la racine du projet :

```bash
python -m src.monitoring.drift
```

## Exemple de sortie

```
Reference trouvee dans : data/processed/train
  -> 500 images de reference chargees.
Chargement des nouvelles images depuis data/new_data...
  -> 80 nouvelles images chargees.

=== Rapport de derive (drift) ===
luminosite      | p-value=0.7978 | ref_mean=113.66 | new_mean=114.92 | ✅ OK
rouge_moyen     | p-value=0.6898 | ref_mean=116.54 | new_mean=116.95 | ✅ OK
vert_moyen      | p-value=0.4042 | ref_mean=120.37 | new_mean=121.77 | ✅ OK
bleu_moyen      | p-value=0.9265 | ref_mean=104.08 | new_mean=106.04 | ✅ OK

✅ Aucune derive significative detectee.
```

## Simuler `data/new_data`

En attendant de vraies photos envoyées par des utilisateurs, `data/new_data`
peut être peuplé avec un échantillon d'images existantes :

```bash
python -c "
import shutil, random
from pathlib import Path

src = Path('data/processed/train')
dst = Path('data/new_data')
dst.mkdir(exist_ok=True)

images = list(src.rglob('*.jpg')) + list(src.rglob('*.JPG')) + list(src.rglob('*.png'))
sample = random.sample(images, min(80, len(images)))
for img in sample:
    shutil.copy(img, dst / img.name)
"
```

## Piège technique rencontré : doublons sous Windows

Le système de fichiers Windows ne distingue pas majuscules/minuscules dans
les extensions. Rechercher `*.jpg` puis `*.JPG` séparément renvoyait donc
deux fois les mêmes fichiers, faussant les moyennes calculées et
provoquant de faux positifs de drift. Corrigé en utilisant un `set` plutôt
qu'une liste pour dédupliquer les chemins collectés (voir
`collect_features()` dans `drift.py`).

## Tests automatisés

Voir `tests/test_drift.py`, qui valide deux scénarios :
- Référence et données actuelles identiques → aucun drift ne doit être
  signalé.
- Référence et données actuelles très différentes (décalage artificiel de
  moyenne) → un drift doit être signalé sur toutes les caractéristiques.

## Pistes d'amélioration (non implémentées)

- Génération d'un rapport HTML automatique avec la librairie **Evidently**
  (`reports/monitoring/drift_report.html`), pour une visualisation plus
  riche en démo/soutenance.
- Simulation d'une dérive réaliste (ex : assombrissement artificiel des
  images de `data/new_data`) pour démontrer que le script détecte bien un
  vrai changement, pas seulement l'absence de changement.
