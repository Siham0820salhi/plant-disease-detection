import os
import json
import hashlib
import webbrowser
from datetime import datetime
from PIL import Image


# ============================================================
# CONFIGURATION
# ============================================================

TRAIN_DIR = "data/processed/train"
VAL_DIR = "data/processed/val"
TEST_DIR = "data/processed/test"

EXPECTED_SIZE = (224, 224)
EXPECTED_CLASSES = 15

IMAGE_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png"
)

REPORT_DIR = "reports"

REPORT_FILE = os.path.join(
    REPORT_DIR,
    "rapport_qualite.html"
)

GX_RESULTS_FILE = os.path.join(
    REPORT_DIR,
    "gx_results.json"
)


# ============================================================
# FONCTION : récupérer les classes
# ============================================================

def get_classes(directory):

    return sorted([
        name
        for name in os.listdir(directory)
        if os.path.isdir(
            os.path.join(
                directory,
                name
            )
        )
    ])


# ============================================================
# FONCTION : compter toutes les images
# ============================================================

def compter_images(directory):

    total = 0

    for classe in get_classes(directory):

        classe_dir = os.path.join(
            directory,
            classe
        )

        total += len([
            f
            for f in os.listdir(classe_dir)
            if f.lower().endswith(
                IMAGE_EXTENSIONS
            )
        ])

    return total


# ============================================================
# FONCTION : compter les images par classe
# ============================================================

def compter_par_classe(directory):

    resultats = {}

    for classe in get_classes(directory):

        classe_dir = os.path.join(
            directory,
            classe
        )

        resultats[classe] = len([
            f
            for f in os.listdir(classe_dir)
            if f.lower().endswith(
                IMAGE_EXTENSIONS
            )
        ])

    return resultats


# ============================================================
# FONCTION : vérifier les images
# ============================================================

def verifier_images(directory):

    corrompues = []
    mauvaises_dimensions = []

    for classe in get_classes(directory):

        classe_dir = os.path.join(
            directory,
            classe
        )

        for filename in os.listdir(classe_dir):

            if not filename.lower().endswith(
                IMAGE_EXTENSIONS
            ):
                continue

            path = os.path.join(
                classe_dir,
                filename
            )

            try:

                with Image.open(path) as img:
                    img.verify()

                with Image.open(path) as img:

                    if img.size != EXPECTED_SIZE:

                        mauvaises_dimensions.append(
                            (
                                path,
                                img.size
                            )
                        )

            except Exception:

                corrompues.append(
                    path
                )

    return (
        corrompues,
        mauvaises_dimensions
    )


# ============================================================
# FONCTION : calculer le hash d'une image
# ============================================================

def calculer_hash(path):

    h = hashlib.md5()

    with open(
        path,
        "rb"
    ) as f:

        for bloc in iter(
            lambda: f.read(65536),
            b""
        ):
            h.update(bloc)

    return h.hexdigest()


# ============================================================
# FONCTION : détecter les doublons entre les splits
# ============================================================

def detecter_doublons_entre_splits():

    hashes = {}
    doublons = []

    for nom_split, directory in [

        (
            "train",
            TRAIN_DIR
        ),

        (
            "val",
            VAL_DIR
        ),

        (
            "test",
            TEST_DIR
        )

    ]:

        for classe in get_classes(
            directory
        ):

            classe_dir = os.path.join(
                directory,
                classe
            )

            for filename in os.listdir(
                classe_dir
            ):

                if not filename.lower().endswith(
                    IMAGE_EXTENSIONS
                ):
                    continue

                path = os.path.join(
                    classe_dir,
                    filename
                )

                image_hash = calculer_hash(
                    path
                )

                if image_hash in hashes:

                    ancien_split, ancien_path = (
                        hashes[
                            image_hash
                        ]
                    )

                    if ancien_split != nom_split:

                        doublons.append(
                            (
                                ancien_split,
                                ancien_path,
                                nom_split,
                                path
                            )
                        )

                else:

                    hashes[
                        image_hash
                    ] = (
                        nom_split,
                        path
                    )

    return doublons


# ============================================================
# FONCTION : charger les résultats Great Expectations
# ============================================================

def charger_resultats_gx():

    if not os.path.exists(
        GX_RESULTS_FILE
    ):

        return {
            "disponible": False,
            "outil": "Great Expectations",
            "dataset": "PlantVillage",
            "total": 0,
            "passed": 0,
            "failed": 0,
            "status_global": "NOT RUN",
            "tests": []
        }

    try:

        with open(
            GX_RESULTS_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            donnees = json.load(f)

        donnees[
            "disponible"
        ] = True

        return donnees

    except Exception as e:

        return {
            "disponible": False,
            "outil": "Great Expectations",
            "dataset": "PlantVillage",
            "total": 0,
            "passed": 0,
            "failed": 0,
            "status_global": "ERROR",
            "tests": [],
            "error": str(e)
        }


# ============================================================
# FONCTION : formater un statut
# ============================================================

def badge_status(
    status
):

    status = str(
        status
    ).upper()

    if status in [
        "PASSED",
        "OK",
        "SUCCESS"
    ]:

        return (
            '<span class="badge badge-success">'
            'PASSED'
            '</span>'
        )

    elif status in [
        "FAILED",
        "ERROR"
    ]:

        return (
            '<span class="badge badge-error">'
            f'{status}'
            '</span>'
        )

    else:

        return (
            '<span class="badge badge-warning">'
            f'{status}'
            '</span>'
        )


# ============================================================
# FONCTION PRINCIPALE : générer le rapport
# ============================================================

def generer_rapport():

    print(
        "Analyse de la qualité des données..."
    )

    # ========================================================
    # CREER LE DOSSIER REPORTS
    # ========================================================

    os.makedirs(
        REPORT_DIR,
        exist_ok=True
    )


    # ========================================================
    # RECUPERER LES CLASSES
    # ========================================================

    train_classes = get_classes(
        TRAIN_DIR
    )

    val_classes = get_classes(
        VAL_DIR
    )

    test_classes = get_classes(
        TEST_DIR
    )


    # ========================================================
    # COMPTER LES IMAGES
    # ========================================================

    train_count = compter_images(
        TRAIN_DIR
    )

    val_count = compter_images(
        VAL_DIR
    )

    test_count = compter_images(
        TEST_DIR
    )

    total = (
        train_count
        + val_count
        + test_count
    )


    # ========================================================
    # POURCENTAGES DES SPLITS
    # ========================================================

    if total > 0:

        train_pct = (
            train_count
            / total
            * 100
        )

        val_pct = (
            val_count
            / total
            * 100
        )

        test_pct = (
            test_count
            / total
            * 100
        )

    else:

        train_pct = 0
        val_pct = 0
        test_pct = 0


    # ========================================================
    # REPARTITION PAR CLASSE
    # ========================================================

    repartition_train = (
        compter_par_classe(
            TRAIN_DIR
        )
    )


    # ========================================================
    # VERIFIER LES IMAGES
    # ========================================================

    corrompues = []
    mauvaises_dimensions = []

    for directory in [
        TRAIN_DIR,
        VAL_DIR,
        TEST_DIR
    ]:

        c, d = verifier_images(
            directory
        )

        corrompues.extend(c)

        mauvaises_dimensions.extend(
            d
        )


    # ========================================================
    # VERIFIER LES DOUBLONS
    # ========================================================

    doublons = (
        detecter_doublons_entre_splits()
    )


    # ========================================================
    # VERIFIER LES CLASSES
    # ========================================================

    meme_classes = (
        train_classes
        == val_classes
        == test_classes
    )

    nombre_classes_ok = (
        len(train_classes)
        == EXPECTED_CLASSES
    )


    # ========================================================
    # DESEQUILIBRE DES CLASSES
    # ========================================================

    if repartition_train:

        minimum = min(
            repartition_train.values()
        )

        maximum = max(
            repartition_train.values()
        )

        ratio = (
            maximum
            / minimum
            if minimum > 0
            else 0
        )

    else:

        minimum = 0
        maximum = 0
        ratio = 0


    # ========================================================
    # GREAT EXPECTATIONS
    # ========================================================

    gx_resultats = (
        charger_resultats_gx()
    )

    gx_status = (
        gx_resultats.get(
            "status_global",
            "NOT RUN"
        )
    )

    gx_total = (
        gx_resultats.get(
            "total",
            0
        )
    )

    gx_passed = (
        gx_resultats.get(
            "passed",
            0
        )
    )

    gx_failed = (
        gx_resultats.get(
            "failed",
            0
        )
    )

    gx_tests = (
        gx_resultats.get(
            "tests",
            []
        )
    )


    # ========================================================
    # STATUT GLOBAL FINAL
    # ========================================================

    controles_images_ok = (
        nombre_classes_ok
        and meme_classes
        and len(corrompues) == 0
        and len(mauvaises_dimensions) == 0
        and len(doublons) == 0
    )

    gx_ok = (
        gx_status == "PASSED"
    )

    qualite_globale_ok = (
        controles_images_ok
        and gx_ok
    )


    # ========================================================
    # GENERER LES LIGNES GREAT EXPECTATIONS
    # ========================================================

    gx_rows_html = ""

    if gx_tests:

        for test in gx_tests:

            nom_test = test.get(
                "test",
                "Contrôle inconnu"
            )

            statut = test.get(
                "status",
                "UNKNOWN"
            )

            gx_rows_html += f"""
                <tr>
                    <td>{nom_test}</td>
                    <td>{badge_status(statut)}</td>
                </tr>
            """

    else:

        gx_rows_html = """
            <tr>
                <td colspan="2">
                    Aucun résultat Great Expectations disponible.
                    Exécutez d'abord :
                    <code>python validation_gx.py</code>
                </td>
            </tr>
        """


    # ========================================================
    # GENERER LES LIGNES DES CLASSES
    # ========================================================

    classes_rows_html = ""

    for classe, nombre in sorted(
        repartition_train.items()
    ):

        classes_rows_html += f"""
            <tr>
                <td>{classe}</td>
                <td>{nombre}</td>
            </tr>
        """


    # ========================================================
    # CONSTRUCTION DU RAPPORT HTML
    # ========================================================

    html = f"""
<!DOCTYPE html>

<html lang="fr">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>
        PlantVillage - Data Quality Report
    </title>

    <style>

        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            padding: 0;
            background: #f4f7f6;
            font-family:
                Arial,
                Helvetica,
                sans-serif;
            color: #1f2937;
        }}

        .page {{
            max-width: 1200px;
            margin: 35px auto;
            background: white;
            border-radius: 16px;
            overflow: hidden;
            box-shadow:
                0 10px 35px
                rgba(0, 0, 0, 0.08);
        }}

        .header {{
            padding: 45px;
            background:
                linear-gradient(
                    135deg,
                    #0f5132,
                    #198754
                );
            color: white;
        }}

        .header h1 {{
            margin: 0;
            font-size: 34px;
        }}

        .header p {{
            margin-top: 10px;
            opacity: 0.9;
        }}

        .content {{
            padding: 35px 45px 50px 45px;
        }}

        h2 {{
            margin-top: 45px;
            margin-bottom: 20px;
            font-size: 24px;
            border-left:
                5px solid #198754;
            padding-left: 12px;
        }}

        .kpi-grid {{
            display: grid;
            grid-template-columns:
                repeat(
                    auto-fit,
                    minmax(180px, 1fr)
                );
            gap: 18px;
            margin-top: 25px;
        }}

        .kpi {{
            background: #f8faf9;
            border:
                1px solid #e2e8e5;
            border-radius: 12px;
            padding: 22px;
        }}

        .kpi-label {{
            font-size: 14px;
            color: #6b7280;
            margin-bottom: 8px;
        }}

        .kpi-value {{
            font-size: 27px;
            font-weight: bold;
            color: #111827;
        }}

        .success-value {{
            color: #198754;
        }}

        .error-value {{
            color: #dc3545;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            margin-bottom: 25px;
            overflow: hidden;
            border-radius: 8px;
        }}

        th {{
            background: #eef3f1;
            padding: 13px;
            text-align: left;
            font-weight: bold;
            border:
                1px solid #d9e2df;
        }}

        td {{
            padding: 12px 13px;
            border:
                1px solid #e3e8e6;
        }}

        tr:nth-child(even) {{
            background: #fafcfc;
        }}

        .badge {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: bold;
        }}

        .badge-success {{
            color: #146c43;
            background: #d1e7dd;
        }}

        .badge-error {{
            color: #842029;
            background: #f8d7da;
        }}

        .badge-warning {{
            color: #664d03;
            background: #fff3cd;
        }}

        .status-box {{
            margin-top: 30px;
            padding: 25px;
            border-radius: 12px;
        }}

        .status-success {{
            background: #d1e7dd;
            border:
                1px solid #badbcc;
            color: #0f5132;
        }}

        .status-error {{
            background: #f8d7da;
            border:
                1px solid #f5c2c7;
            color: #842029;
        }}

        .status-title {{
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 8px;
        }}

        .section-description {{
            color: #6b7280;
            margin-top: -8px;
            margin-bottom: 20px;
        }}

        .split-container {{
            margin-top: 20px;
        }}

        .split-item {{
            margin-bottom: 15px;
        }}

        .split-label {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
        }}

        .progress {{
            width: 100%;
            height: 13px;
            background: #e5e7eb;
            border-radius: 8px;
            overflow: hidden;
        }}

        .progress-value {{
            height: 100%;
            background: #198754;
        }}

        .footer {{
            margin-top: 50px;
            padding-top: 25px;
            border-top:
                1px solid #e5e7eb;
            color: #6b7280;
            font-size: 13px;
        }}

        code {{
            background: #eef2f1;
            padding: 2px 6px;
            border-radius: 5px;
        }}

    </style>

</head>


<body>

<div class="page">

    <div class="header">

        <h1>
            Plant Disease Detection
        </h1>

        <p>
            MLOps — Data Quality Report
        </p>

        <p>
            Dataset : PlantVillage
            &nbsp; | &nbsp;
            Pipeline Stage :
            Transformation & Data Quality
        </p>

    </div>


    <div class="content">


        <!-- ================================================= -->
        <!-- KPI -->
        <!-- ================================================= -->

        <div class="kpi-grid">

            <div class="kpi">

                <div class="kpi-label">
                    Total Images
                </div>

                <div class="kpi-value">
                    {total}
                </div>

            </div>


            <div class="kpi">

                <div class="kpi-label">
                    Classes
                </div>

                <div class="kpi-value">
                    {len(train_classes)}
                </div>

            </div>


            <div class="kpi">

                <div class="kpi-label">
                    Corrupted Images
                </div>

                <div class="kpi-value success-value">
                    {len(corrompues)}
                </div>

            </div>


            <div class="kpi">

                <div class="kpi-label">
                    Cross-Split Duplicates
                </div>

                <div class="kpi-value success-value">
                    {len(doublons)}
                </div>

            </div>


            <div class="kpi">

                <div class="kpi-label">
                    Great Expectations
                </div>

                <div class="kpi-value {
                    'success-value'
                    if gx_ok
                    else 'error-value'
                }">
                    {gx_passed}/{gx_total}
                </div>

            </div>

        </div>


        <!-- ================================================= -->
        <!-- 1 -->
        <!-- ================================================= -->

        <h2>
            1. Résumé du dataset
        </h2>

        <p class="section-description">
            Répartition du dataset préparé
            après le prétraitement et le split.
        </p>

        <table>

            <tr>
                <th>Split</th>
                <th>Nombre d'images</th>
                <th>Pourcentage</th>
            </tr>

            <tr>
                <td>Train</td>
                <td>{train_count}</td>
                <td>{train_pct:.2f}%</td>
            </tr>

            <tr>
                <td>Validation</td>
                <td>{val_count}</td>
                <td>{val_pct:.2f}%</td>
            </tr>

            <tr>
                <td>Test</td>
                <td>{test_count}</td>
                <td>{test_pct:.2f}%</td>
            </tr>

            <tr>
                <td><strong>Total</strong></td>
                <td><strong>{total}</strong></td>
                <td><strong>100%</strong></td>
            </tr>

        </table>


        <div class="split-container">

            <div class="split-item">

                <div class="split-label">
                    <span>Train</span>
                    <strong>{train_pct:.1f}%</strong>
                </div>

                <div class="progress">

                    <div
                        class="progress-value"
                        style="width: {train_pct}%;">
                    </div>

                </div>

            </div>


            <div class="split-item">

                <div class="split-label">
                    <span>Validation</span>
                    <strong>{val_pct:.1f}%</strong>
                </div>

                <div class="progress">

                    <div
                        class="progress-value"
                        style="width: {val_pct}%;">
                    </div>

                </div>

            </div>


            <div class="split-item">

                <div class="split-label">
                    <span>Test</span>
                    <strong>{test_pct:.1f}%</strong>
                </div>

                <div class="progress">

                    <div
                        class="progress-value"
                        style="width: {test_pct}%;">
                    </div>

                </div>

            </div>

        </div>


        <!-- ================================================= -->
        <!-- 2 -->
        <!-- ================================================= -->

        <h2>
            2. Contrôles qualité des images
        </h2>

        <p class="section-description">
            Vérification directe des fichiers
            après prétraitement.
        </p>

        <table>

            <tr>
                <th>Contrôle</th>
                <th>Résultat</th>
            </tr>

            <tr>

                <td>
                    Nombre de classes attendu
                    ({EXPECTED_CLASSES})
                </td>

                <td>
                    {
                        badge_status(
                            "PASSED"
                            if nombre_classes_ok
                            else "FAILED"
                        )
                    }
                </td>

            </tr>

            <tr>

                <td>
                    Même classes dans
                    train / val / test
                </td>

                <td>
                    {
                        badge_status(
                            "PASSED"
                            if meme_classes
                            else "FAILED"
                        )
                    }
                </td>

            </tr>

            <tr>

                <td>
                    Images lisibles /
                    non corrompues
                </td>

                <td>
                    {
                        badge_status(
                            "PASSED"
                            if len(corrompues) == 0
                            else "FAILED"
                        )
                    }
                    &nbsp;
                    {len(corrompues)}
                    image(s) problématique(s)
                </td>

            </tr>

            <tr>

                <td>
                    Dimensions attendues
                    {EXPECTED_SIZE[0]} × {EXPECTED_SIZE[1]}
                </td>

                <td>
                    {
                        badge_status(
                            "PASSED"
                            if len(mauvaises_dimensions) == 0
                            else "FAILED"
                        )
                    }
                    &nbsp;
                    {len(mauvaises_dimensions)}
                    erreur(s)
                </td>

            </tr>

            <tr>

                <td>
                    Absence de doublons
                    entre les splits
                </td>

                <td>
                    {
                        badge_status(
                            "PASSED"
                            if len(doublons) == 0
                            else "FAILED"
                        )
                    }
                    &nbsp;
                    {len(doublons)}
                    doublon(s)
                </td>

            </tr>

        </table>


        <!-- ================================================= -->
        <!-- 3 -->
        <!-- ================================================= -->

        <h2>
            3. Analyse du déséquilibre des classes
        </h2>

        <table>

            <tr>
                <th>Mesure</th>
                <th>Valeur</th>
            </tr>

            <tr>
                <td>
                    Classe la moins représentée
                </td>
                <td>
                    {minimum} images
                </td>
            </tr>

            <tr>
                <td>
                    Classe la plus représentée
                </td>
                <td>
                    {maximum} images
                </td>
            </tr>

            <tr>
                <td>
                    Ratio max / min
                </td>
                <td>
                    {ratio:.2f}
                </td>
            </tr>

        </table>


        <!-- ================================================= -->
        <!-- 4 -->
        <!-- ================================================= -->

        <h2>
            4. Répartition des classes du train
        </h2>

        <table>

            <tr>
                <th>Classe</th>
                <th>Nombre d'images</th>
            </tr>

            {classes_rows_html}

        </table>


        <!-- ================================================= -->
        <!-- 5 GREAT EXPECTATIONS -->
        <!-- ================================================= -->

        <h2>
            5. Validation Great Expectations
        </h2>

        <p class="section-description">
            Contrôles automatisés appliqués
            aux métadonnées structurées
            du dataset PlantVillage.
        </p>


        <div class="kpi-grid">

            <div class="kpi">

                <div class="kpi-label">
                    GX Tests
                </div>

                <div class="kpi-value">
                    {gx_total}
                </div>

            </div>


            <div class="kpi">

                <div class="kpi-label">
                    GX Passed
                </div>

                <div class="kpi-value success-value">
                    {gx_passed}
                </div>

            </div>


            <div class="kpi">

                <div class="kpi-label">
                    GX Failed
                </div>

                <div class="kpi-value {
                    'success-value'
                    if gx_failed == 0
                    else 'error-value'
                }">
                    {gx_failed}
                </div>

            </div>


            <div class="kpi">

                <div class="kpi-label">
                    GX Global Status
                </div>

                <div class="kpi-value">
                    {badge_status(gx_status)}
                </div>

            </div>

        </div>


        <table>

            <tr>
                <th>
                    Great Expectations Check
                </th>

                <th>
                    Status
                </th>
            </tr>

            {gx_rows_html}

        </table>


        <!-- ================================================= -->
        <!-- 6 CONCLUSION -->
        <!-- ================================================= -->

        <h2>
            6. Conclusion et statut final
        </h2>
"""

    if qualite_globale_ok:

        html += """
        <div class="
            status-box
            status-success
        ">

            <div class="status-title">
                ✅ DATA QUALITY PASSED
            </div>

            <p>
                Tous les contrôles principaux
                de qualité ont été validés.
            </p>

            <p>
                Le dataset préparé est conforme
                aux règles définies et peut
                poursuivre le pipeline vers
                l'étape d'entraînement du modèle.
            </p>

        </div>
        """

    else:

        html += """
        <div class="
            status-box
            status-error
        ">

            <div class="status-title">
                ❌ DATA QUALITY FAILED
            </div>

            <p>
                Au moins un contrôle de qualité
                n'est pas validé.
            </p>

            <p>
                Le dataset doit être corrigé
                ou revalidé avant l'entraînement
                du modèle.
            </p>

        </div>
        """


    html += f"""

        <div class="footer">

            Rapport généré automatiquement
            le
            {
                datetime.now().strftime(
                    "%d/%m/%Y à %H:%M:%S"
                )
            }.

            <br><br>

            Pipeline :
            Plant Disease Detection —
            Transformation & Data Quality

            <br>

            Outils :
            Python,
            Pillow,
            pytest,
            Great Expectations,
            YAML.

        </div>

    </div>

</div>

</body>

</html>
"""


    # ========================================================
    # SAUVEGARDER LE RAPPORT
    # ========================================================

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            html
        )


    # ========================================================
    # CHEMIN ABSOLU
    # ========================================================

    rapport_path = os.path.abspath(
        REPORT_FILE
    )


    print()
    print(
        "=" * 60
    )

    print(
        "RAPPORT DE QUALITE TERMINE"
    )

    print(
        "=" * 60
    )

    print(
        "Rapport généré :",
        rapport_path
    )

    print(
        "Great Expectations :",
        gx_status
    )

    print(
        "GX Passed :",
        gx_passed,
        "/",
        gx_total
    )


    # ========================================================
    # OUVERTURE AUTOMATIQUE
    # ========================================================

    try:

        url_rapport = (
            "file:///"
            + rapport_path.replace(
                "\\",
                "/"
            )
        )

        ouverture = (
            webbrowser.open_new_tab(
                url_rapport
            )
        )

        if ouverture:

            print(
                "Ouverture automatique "
                "du rapport..."
            )

        else:

            print(
                "Rapport créé, mais "
                "le navigateur ne s'est "
                "pas ouvert automatiquement."
            )

    except Exception as e:

        print(
            "Impossible d'ouvrir "
            "automatiquement le rapport :",
            e
        )


# ============================================================
# LANCEMENT
# ============================================================

if __name__ == "__main__":

    generer_rapport()