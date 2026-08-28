import subprocess
import sys
import os
import webbrowser


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

    # ========================================================
    # 1. TESTS PYTEST
    # ========================================================

    lancer_commande(
        "1. TESTS PYTEST",
        "python -m pytest tests/test_qualite_donnees.py -v"
    )

    # ========================================================
    # 2. GREAT EXPECTATIONS
    # ========================================================

    lancer_commande(
        "2. GREAT EXPECTATIONS",
        "python validation_gx.py"
    )

    # ========================================================
    # 3. GENERATION DU RAPPORT HTML
    # ========================================================

    lancer_commande(
        "3. GENERATION DU RAPPORT",
        "python rapport/rapport_qualite.py"
    )

    # ========================================================
    # 4. OUVERTURE AUTOMATIQUE DU RAPPORT
    # ========================================================

    rapport_path = os.path.abspath(
        "reports/rapport_qualite.html"
    )

    if os.path.exists(rapport_path):
        print("\nOuverture du rapport dans le navigateur...")
        webbrowser.open(
            "file:///" + rapport_path.replace("\\", "/")
        )
    else:
        print(
            "\n⚠️ Le rapport HTML est introuvable :",
            rapport_path
        )

    # ========================================================
    # FIN
    # ========================================================

    print("\n" + "=" * 60)
    print("PIPELINE DATA QUALITY TERMINÉ ✅")
    print("=" * 60)
