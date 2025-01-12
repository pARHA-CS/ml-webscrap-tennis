import streamlit as st
import pandas as pd

# Chargement du fichier CSV
st.title("Modification de la base de données Tennis")
uploaded_file = st.file_uploader("Chargez votre base de données CSV", type=["csv"])

if uploaded_file:
    # Lire la base de données
    df = pd.read_csv(uploaded_file)
    st.write("Aperçu des données :")
    st.write(df.head())
    
    # Sélection des options de modification
    st.subheader("Ajout/Modification des données")

    # Ajouter le type de tournoi
    tournament_type = st.selectbox("Type de tournoi (1 à 4)", [1, 2, 3, 4])
    # Ajouter la surface
    surface_options = ['Clay', 'Hard', 'Grass', 'Carpet']
    selected_surfaces = {surf: st.checkbox(surf) for surf in surface_options}

    if st.button("Appliquer les modifications"):
        # Ajouter les colonnes si elles n'existent pas
        if 'Tournament_Type' not in df.columns:
            df['Tournament_Type'] = 0  # Valeur par défaut

        for surf in surface_options:
            if surf not in df.columns:
                df[surf] = 0  # Initialiser à 0 pour one-hot

        # Modifier les valeurs
        df['Tournament_Type'] = tournament_type
        for surf in surface_options:
            df[surf] = int(selected_surfaces[surf])  # 1 si coché, sinon 0

        st.success("Modifications appliquées !")
        st.write("Données mises à jour :")
        st.write(df.head())

    # Télécharger le fichier modifié
    st.subheader("Exporter la base de données mise à jour")
    csv = df.to_csv(index=False)
    st.download_button("Télécharger le fichier CSV modifié", data=csv, file_name="modified_database.csv", mime="text/csv")
