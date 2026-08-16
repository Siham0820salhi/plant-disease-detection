import subprocess
import sys


def lancer_commande(nom_etape, commande):
    print("\n" + "=" * 60)
    print(nom_etape)
    print("=" * 60)

    resultat = subprocess.run(
        commande,
        shell=True
    )

    if resultat.returncode != 0:
        print(f"\n❌ Échec : {nom_etape}")
        sys.exit(resultat.returncode)

    print(f"\n✅ Terminé : {nom_etape}")


if __name__ == "__main__":

    # 1. Tests pytest
    lancer_commande(
        "1. TESTS PYTEST",
        "python -m pytest tests/test_qualite_donnees.py -v"
    )

    # 2. Great Expectations
    lancer_commande(
        "2. GREAT EXPECTATIONS",
        "python validation_gx.py"
    )

    # 3. Rapport HTML
    lancer_commande(
        "3. GENERATION DU RAPPORT",
        "python rapport/rapport_qualite.py"
    )

    print("\n" + "=" * 60)
    print("PIPELINE DATA QUALITY TERMINÉ ✅")
    print("=" * 60)