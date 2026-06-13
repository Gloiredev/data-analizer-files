# app.py - Assemblé par Gloire pour l'équipe Data-Analyzer
import os
import streamlit as st
import time
import pandas as pd

# ==========================================
# IMPORTATION DE MES MODULES (MON CERVEAU PANDAS)
# ==========================================
# Ici, j'importe ma fonction de validation de fichier
from utils.load_file import load_file

# J'importe mes outils de nettoyage du fichier data_cleaner.py
from utils.data_cleaner import get_cleaning_report, delete_duplicates

# Et ici le module de statistiques globales que j'ai préparé
from utils.info import get_info

# mon visualizseur en attente
# from utils.visualizer import visualiser

# Configuration de la page faite par mon pote, je la laisse propre
st.set_page_config(page_title="Data-Analyzer files", page_icon="📊", layout="wide")

# STYLE CSS (Le design sombre pour que ça fasse application pro)
st.markdown(
    """
<style>
.main { background-color: #0E1117; color: white; }
.stButton>button { width: 100%; border-radius: 10px; height: 50px; font-size: 18px; font-weight: bold; }
.sidebar .sidebar-content { background-color: #111827; }
h1 { color: #4CAF50; }
</style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# LA SIDEBAR (MENU DE NAVIGATION)
# ==========================================
with st.sidebar:
    st.title("📌 Menu & navigation")
    # st.radio crée les boutons ronds. J'ai harmonisé les noms avec mes conditions plus bas.
    section = st.radio(
        "Aller vers",
        ["Accueil", "graphiques", "Analyse détaillée", "Synthèse IA", "collaboration"],
    )
    st.divider()
    st.subheader("🔗 Liens annexes")
    st.markdown(
        "- [Streamlit](https://streamlit.io)\n- [Pandas](https://pydata.org)\n- [Dépot github du projet](https://github.geniruphin-junior/data-files.git)"
    )


# ==========================================
# PAGE 1 : ACCUEIL (CHARGEMENT & NETTOYAGE)
# ==========================================
if section == "Accueil":
    st.title("Bienvenue sur Data-Analyzer files")
    st.write("Plateforme d’analyse de données et visualisation de fichiers.")

    # Le composant magique de Streamlit pour glisser-déposer le fichier
    uploaded_file = st.file_uploader(
        "Importer un fichier CSV ou Excel", type=["csv", "xlsx"]
    )

    # Si l'utilisateur a mis un fichier dans la zone de dépôt :
    if uploaded_file:

        # SÉCURITÉ ET PASSERELLE POUR MON LOAD_FILE :
        # Streamlit garde le fichier en mémoire vive. Mais ma fonction 'load_file' a absolument
        # besoin d'un chemin texte (un file_path) pour faire ses vérifications OS et Magic.
        # Du coup, je crée un chemin temporaire dans le dossier courant (le fameux point ".")
        temp_path = os.path.join(".", uploaded_file.name)

        # J'ouvre ce fichier vide sur le disque dur en mode écriture binaire ("wb")
        with open(temp_path, "wb") as f:
            # J'écris les octets du fichier téléversé dedans
            f.write(uploaded_file.getbuffer())

        # VÉRIFICATION : Si mon DataFrame n'est pas encore dans mon coffre-fort (session_state)
        if "df" not in st.session_state:
            # st.spinner affiche une animation de chargement super cool pendant les calculs
            with st.spinner(
                "Validation et chargement sécurisé des données par l'ia..."
            ):
                try:
                    # J'appelle MA fonction principale load_file en lui donnant le chemin du fichier sur le disque.
                    # Si le fichier viole mes règles (trop lourd, faux type MIME), ça va basculer direct dans le 'except'
                    st.session_state["df"] = load_file(temp_path)
                    st.success("Données validées et chargées avec succès !")
                    st.success(
                        "voici vos données pretes à l 'exploitation et manupulation"
                    )

                except Exception as e:
                    # Si ma fonction load_file a levé une erreur, je bloque tout et j'affiche l'alerte en rouge
                    st.error(f"Erreur de validation : {e}")

                finally:
                    # Quoi qu'il arrive (succès ou plantage), je supprime le fichier temporaire du disque dur.
                    # C'est ultra important pour ne pas saturer l'espace de stockage !
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

        # Si le fichier a passé mes tests avec succès et qu'il est bien stocké en session :
        if "df" in st.session_state:
            # Je récupère le DataFrame du coffre-fort pour travailler dessus tranquillement
            df_actuel = st.session_state["df"]

            # J'appelle mon rapport global issu de mon fichier data_cleaner.py
            report = get_cleaning_report(df_actuel)

            # J'affiche mes statistiques de nettoyage dans des jolies boîtes d'affichage (metrics)
            st.subheader("⚙️ Métriques globales de mon Data Cleaner")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Lignes", f"{report['rows']:,}")
            col2.metric("Colonnes", report["columns"])
            col3.metric("Cases vides", report["missing_values"])
            col4.metric("Doublons détectés", report["duplicates"])
            # Petite note technique pour rassurer sur la consommation RAM de nos machines à 4Go
            st.info(
                f"💾 Mémoire RAM consommée : {report['memory_mb_used']} Mo (Sécurisé pour vos 4Go)"
            )

            # BOUTONS D'ACTION RAPIDE (Nettoyage en un clic)
            st.subheader("🛠️ Actions rapides de nettoyage")
            c1, c2 = st.columns(2)

            if c1.button("Remplir les cases vides (Mode Auto)"):
                # Si on clique, on applique un fillna global et on met à jour la session
                st.session_state["df"] = df_actuel.fillna(0)
                st.success("Cases vides nettoyées !")
                # st.rerun() force Streamlit à recharger la page immédiatement pour voir le tableau mis à jour
                st.rerun()

            if c2.button("Supprimer les doublons détectés"):
                # J'appelle ma fonction delete_duplicates de mon fichier data_cleaner.py
                st.session_state["df"] = delete_duplicates(df_actuel)
                st.success("Doublons supprimés !")
                st.rerun()

            # L'aperçu dynamique des données (st.dataframe est interactif, contrairement à st.table)
            st.subheader(
                "👀 Aperçu des premières et dernières lignes de votre dataframe"
            )
            st.write("- voici vos premieres lignes")
            st.dataframe(df_actuel.head(5), use_container_width=True)
            st.write("Et voilà le terminus de votre programme")
            st.dataframe(df_actuel.tail(5), use_container_width=True)

            st.subheader(
                "📉 Graphiques sur votre fichier proposé par l'ia et l'application"
            )
# ======================================
# AVANT PAGE DEUX PASSONS AUX GRAPHIQUES
# ====================================
elif section == "graphiques":
    st.title("Visualisations des vos données")
    st.info("Les graphiques futuristes et manupulable seront d'ici là dispo")
# ==========================================
# PAGE 2 : ANALYSE DÉTAILLÉE (MON GET_RESULTS)
# ==========================================
elif section == "Analyse détaillée":
    st.title("Analyse détaillée & Statistiques avancées")

    # Si l'utilisateur vient ici sans avoir chargé de fichier en page d'accueil, je le bloque poliment et cruellement
    if "df" not in st.session_state:
        st.warning(
            "⚠️ Veuillez d'abord importer un fichier sur la page d'Accueil tu connais pas lire."
        )
    else:
        df_actuel = st.session_state["df"]

        st.subheader("📊 Configuration de l'analyse croisée (Group By)")
        col_g, col_t = st.columns(2)

        # selectbox crée une liste déroulante avec les vraies colonnes de notre fichier !
        group_col = col_g.selectbox(
            "Sélectionner la colonne de regroupement", df_actuel.columns
        )

        # Je filtre les colonnes pour ne proposer que des chiffres dans la cible des calculs
        cols_numeriques = df_actuel.select_dtypes(include="number").columns.tolist()
        if cols_numeriques:
            target_col = col_t.selectbox(
                "Sélectionner la colonne cible (Numérique)", cols_numeriques
            )
        else:
            target_col = None
            st.error("Aucune colonne numérique trouvée pour faire des calculs.")

        # J'appelle mon super module get_results.py conçu pour l'analyse
        # J'ai fixé max_rows=1000 à l'intérieur pour préserver nos ordinateurs à 4Go de RAM
        info_calculée = get_info(
            df_actuel, group_col=group_col, target_col=target_col, max_rows=1000
        )

        # Affichage des dtypes (Mise en forme de mon dictionnaire en tableau Pandas pour l'interface)
        st.subheader("🧬 Types des colonnes et valeurs manquantes")
        types_df = pd.DataFrame(
            {
                "Type de données": info_calculée["dtypes"],
                "Cases Manquantes": info_calculée["missing_values"],
            }
        )
        st.dataframe(types_df.T, use_container_width=True)

        # Si mon module get_results a généré une clé "groupby" dans son dictionnaire de retour :
        if "groupby" in info_calculée:
            st.subheader(
                f"📈 Résultat de l'analyse collective : {target_col} par {group_col}"
            )
            # Je transforme la liste de dictionnaires en DataFrame affichable
            df_group = pd.DataFrame(info_calculée["groupby"])
            st.dataframe(df_group, use_container_width=True)

            # Un petit graphique d'analyse rapide basé directement sur les moyennes de mon groupby
            st.bar_chart(df_group.set_index(group_col)["mean"])


# ==========================================
# PAGE 3 : LE MODE IA (EN ATTENTE DE SCRIPT)
# ==========================================
elif section == "Synthèse IA":
    st.title("Mode Intelligence Artificielle")
    st.info(
        "Section en cours de développement. Vos calculs Pandas y seront injectés très bientôt."
    )
