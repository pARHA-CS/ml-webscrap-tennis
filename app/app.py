import streamlit as st
import polars as pl
import joblib
import numpy as np


model = joblib.load("data/best_model.joblib")
player_data = pl.read_csv("data/tennis_dataset_app.csv")



def display_top_200():
    st.header("ATP Top 200")

    top_200 = (
        player_data
        .select(["player1_name", "player1_age", "player1_ranking", "player1_points", "player1_win_rate"])
        .sort("player1_ranking")
    )
    
    top_200 = top_200.rename({
        "player1_name": "Nom",
        "player1_age": "Âge",
        "player1_ranking": "Classement",
        "player1_points": "Points",
        "player1_win_rate": "Taux de victoire (%)"
    })
    
    top_200 = top_200.with_columns(
        (pl.col("Taux de victoire (%)") * 100).round(1)
    )
    
    top_200 = top_200.select(["Classement", "Nom", "Âge", "Points", "Taux de victoire (%)"])
    
    st.dataframe(top_200)



def predict_match():
    st.title("Prédiction de match de tennis 🎾")

    players_list = sorted(player_data["player1_name"].unique().to_list())
    player1 = st.selectbox("Sélectionnez le premier joueur", players_list)
    players_list2 = [p for p in players_list if p != player1]
    player2 = st.selectbox("Sélectionnez le second joueur", players_list2)

    st.subheader("Type de tournoi")
    tournament_type = st.selectbox("Type de tournoi :", ["Grand Slam", "Masters 1000", "ATP 500", "ATP 250"], index=0)

    tournament_type_mapping = {"Grand Slam": 4, "Masters 1000": 3, "ATP 500": 2, "ATP 250": 1}
    tournament_encoded = tournament_type_mapping[tournament_type]

    st.subheader("Surface du terrain")
    surface = st.radio("Choisissez une surface", ["Dure", "Salle", "Terre Battue", "Gazon"])
    surface_mapping = {"Dure": [1, 0, 0, 0], "Salle": [0, 1, 0, 0], "Terre Battue": [0, 0, 1, 0], "Gazon": [0, 0, 0, 1]}
    surface_one_hot = surface_mapping[surface]

    if st.button("Prédire l'issue du match"):
        player1_stats = player_data.filter(pl.col("player1_name") == player1).select(pl.col(player_data.columns[1:26])).to_numpy()
        player2_stats = player_data.filter(pl.col("player1_name") == player2).select(pl.col(player_data.columns[1:26])).to_numpy()

        match_data = np.concatenate([player1_stats[0], player2_stats[0]]).reshape(1, -1)

        additional_features = [
            abs(match_data[0][1] - match_data[0][26]),  
            abs(match_data[0][2] - match_data[0][27]),  
            abs(match_data[0][3] - match_data[0][28]),  
            abs(match_data[0][4] - match_data[0][29]),  
            abs(match_data[0][5] - match_data[0][30]),  
            abs(match_data[0][24] - match_data[0][49]),  
            abs(match_data[0][23] - match_data[0][48]),  
            abs(match_data[0][7] - match_data[0][32]),  
            abs(match_data[0][9] - match_data[0][34]),  
            abs(match_data[0][11] - match_data[0][36]),  
            abs(match_data[0][13] - match_data[0][38])   
        ]

        tournament_and_surface_features = [tournament_encoded] + surface_one_hot
        match_data_with_all_features = np.append(match_data, additional_features + tournament_and_surface_features).reshape(1, -1)

        if match_data_with_all_features.shape[1] != 66:
            st.error(f"Erreur : Le modèle attend 66 colonnes, mais l'entrée en contient {match_data_with_all_features.shape[1]}.")
            return

        probabilities = model.predict_proba(match_data_with_all_features)

        st.header("Probabilités de victoire :")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(player1, f"{probabilities[0][0] * 100:.1f}%")
        with col2:
            st.metric(player2, f"{probabilities[0][1] * 100:.1f}%")



st.sidebar.title("Menu")
menu = st.sidebar.radio(
    "",
    ["Prédiction de match", "Top 200 joueurs"]
)

if menu == "Prédiction de match":
    predict_match()
elif menu == "Top 200 joueurs":
    display_top_200()
