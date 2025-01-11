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

    if st.button("Prédire l'issue du match"):
        
        player1_stats = player_data.filter(pl.col(player_data.columns[0]) == player1).select(
            pl.col(player_data.columns[1:26])
        ).to_numpy()

        player2_stats = player_data.filter(pl.col(player_data.columns[0]) == player2).select(
            pl.col(player_data.columns[1:26])
        ).to_numpy()

        
        match_data = np.concatenate([player1_stats[0], player2_stats[0]]).reshape(1, -1)


        ######################################################
        ####### Calcul des différences ########
        rank_difference = abs(match_data[0][1] - match_data[0][26])
        points_difference = abs(match_data[0][2] - match_data[0][27])
        win_rate_difference = abs(match_data[0][3] - match_data[0][28])
        win_rate_difference3 = abs(match_data[0][4] - match_data[0][29])
        win_rate_tiebreak_difference = abs(match_data[0][5] - match_data[0][30])
        aces_difference = abs(match_data[0][24] - match_data[0][49])
        double_faults_difference = abs(match_data[0][23] - match_data[0][48])
        win_rate_dure_difference = abs(match_data[0][7] - match_data[0][32])
        win_rate_terre_difference = abs(match_data[0][9] - match_data[0][34])
        win_rate_gazon_difference = abs(match_data[0][11] - match_data[0][36])
        win_rate_salle_difference = abs(match_data[0][13] - match_data[0][38])

        additional_features = [
            rank_difference,
            points_difference,
            win_rate_difference,
            win_rate_difference3,
            win_rate_tiebreak_difference,
            aces_difference,
            double_faults_difference,
            win_rate_dure_difference,
            win_rate_terre_difference,
            win_rate_gazon_difference,
            win_rate_salle_difference,
        ]

        # Ajouter ces nouvelles valeurs à la fin de match_data
        match_data_with_diff = np.append(match_data, [additional_features], axis=1)

        #######################################################################
        #######################################################################

        # Faire la prédiction
        probabilities = model.predict_proba(match_data_with_diff)

        # Afficher les résultats
        st.header("Probabilités de victoire :")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(player1, f"{probabilities[0][0]*100:.1f}%")
        with col2:
            st.metric(player2, f"{probabilities[0][1]*100:.1f}%")


# Ajouter une barre latérale pour la navigation
st.sidebar.title("Menu")
menu = st.sidebar.radio(
    "",
    ["Prédiction de match", "Top 200 joueurs"]
)

# Navigation entre les fonctionnalités
if menu == "Prédiction de match":
    predict_match()
elif menu == "Top 200 joueurs":
    display_top_200()
