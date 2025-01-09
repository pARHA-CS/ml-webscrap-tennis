import polars as pl
import os
import random
import numpy as np

def select_percentage(df):
    """
    Cette fonction calcule le nombre de ligne à selctionner pour rééquilibrer le dataframe
    
    Args:
        df : DataFrame Polars d'entrée

    Returns:
        int: le nombre de ligne à sélectionner pour équilibrer le dataframe
    """
    inds_0 = df.filter(df["target"] == 0).shape[0]
    inds_1 = df.filter(df["target"] == 1).shape[0]
    inds = tuple((inds_0, inds_1))
    
    mean_ind = int(np.mean(inds))
    print(f"moyenne = {mean_ind}")
    print(f"le max = {max(inds)}")
    
    nb_select = round(max(inds) - mean_ind, 0)
    print(f"nombre de ligne à changer {nb_select}")
    
    percentage = nb_select / inds_1
    print(f"pourcentage de ligne {percentage}")
    
    return percentage

def modify_players(df):
    """
    Cette fonction modifie aléatoirement un pourcentage de lignes du DataFrame où target == 1.
    Les colonnes des joueurs 1 et 2 sont inversées sur ces lignes sélectionnées.

    Parameters:
    - df : DataFrame Polars d'entrée
    - percentage : pourcentage de lignes à sélectionner et modifier (0-1)

    Returns:
    - df_final : DataFrame modifié avec les lignes sélectionnées et inversées ajoutées
    """

    # Étape 0 : Ajouter l'index des lignes
    df_with_index = df.with_row_index()

    # Étape 1 : Sélectionner un pourcentage de lignes avec target == 1
    df_target_1 = df_with_index.filter(pl.col("target") == 1)

    # Récupération des indices
    index = df_target_1.select(pl.col("index")).to_numpy().flatten().tolist()

    # Calculer le nombre de lignes à sélectionner
    row_selected_pct = select_percentage(df)
    num_to_select = int(len(index) * row_selected_pct)

    # Sélectionner aléatoirement les indices
    selected_indices = random.sample(index, num_to_select)

    # Étape 2 : Sélectionner les lignes avec les indices collectés
    df_selected = df_with_index.filter(pl.col("index").is_in(selected_indices))

    # Étape 4 : Inverser les données des joueurs 1 et 2 sur la sélection dans le nouveau dataframe
    columns_to_swap = [col for col in df_selected.columns if "player1" in col or "player2" in col]

    swap_expressions = []
    for col in columns_to_swap:
        if "player1" in col:
            swap_expressions.append(pl.col(col).alias(col.replace("player1", "player2")))
        elif "player2" in col:
            swap_expressions.append(pl.col(col).alias(col.replace("player2", "player1")))

    # Appliquer les modifications sur le DataFrame sélectionné
    df_selected_swapped = df_selected.with_columns(swap_expressions)
    
    df_selected_swapped = df_selected_swapped.with_columns(
        pl.lit(0).cast(pl.Int64).alias("target")
    )

    # Étape 5 : Supprimer les lignes avec les indices récupérés dans le df initial
    df_without_selected = df_with_index.filter(~pl.col("index").is_in(selected_indices))

    # Ajouter les lignes modifiées du DataFrame sélectionné à celui d'origine
    df_final = df_without_selected.vstack(df_selected_swapped)

    return df_final

current_dir = os.getcwd()
print(current_dir)

dataset_path = os.path.join(current_dir, "data", "tennis_dataset_raw.csv")
output_path = os.path.join(current_dir, "data", "tennis_dataset_clean_essaie.csv")

df = pl.read_csv(dataset_path)

df_unique = df.unique('url_match')

df_unique = df_unique.with_columns([
    (df_unique["surface"] == "dure").cast(pl.Int8).alias("surface_dure"),
    (df_unique["surface"] == "salle").cast(pl.Int8).alias("surface_salle"),
    (df_unique["surface"] == "terre battue").cast(pl.Int8).alias("surface_terre_batue"),
    (df_unique["surface"] == "gazon").cast(pl.Int8).alias("surface_gazon")
])

columns_to_drop = ["player1_name", "player2_name", "url_match", "surface"]
df_clean = df_unique.drop(columns_to_drop).drop_nulls()

df_modified = modify_players(df_clean)

df_modified = df_modified.with_columns([
    (abs(df_modified["player1_ranking"] - df_modified["player2_ranking"])).alias("ranking_diff"),
    (abs(df_modified["player1_points"] - df_modified["player2_points"])).alias("points_diff"),
    (abs(df_modified["player1_win_rate"] - df_modified["player2_win_rate"])).alias("win_rate_diff"),
    (abs(df_modified["player1_win_rate_3_sets"] - df_modified["player2_win_rate_3_sets"])).alias("win_rate_diff_3_sets"),
    (abs(df_modified["player1_win_rate_tiebreak"] - df_modified["player1_win_rate_tiebreak"])).alias("win_rate_tiebreak_diff"),
    (abs(df_modified["player1_avg_aces"] - df_modified["player2_avg_aces"])).alias("aces_diff"),
    (abs(df_modified["player1_avg_double_fautes"] - df_modified["player2_avg_double_fautes"])).alias("double_faults_diff"),
    (abs(df_modified["player1_win_rate_dure"] - df_modified["player2_win_rate_dure"])).alias("win_rate_dure_diff"),
    (abs(df_modified["player1_win_rate_terre battue"] - df_modified["player2_win_rate_terre battue"])).alias("win_rate_terre_diff"),
    (abs(df_modified["player1_win_rate_gazon"] - df_modified["player2_win_rate_gazon"])).alias("win_rate_gazon_diff"),
    (abs(df_modified["player1_win_rate_salle"] - df_modified["player2_win_rate_salle"])).alias("win_rate_salle_diff"),
])

df_modified.write_csv(output_path)