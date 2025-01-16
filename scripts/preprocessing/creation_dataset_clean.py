"""Script pour créer via tennis_dataset_raw.csv un dataset pour le ml

    Return : tennis_dataset_clean.csv
"""
import polars as pl
import os
from src.preprocessing.preprocessing import modify_players

current_dir = os.getcwd()
print(current_dir)

dataset_path = os.path.join(current_dir, "data", "tennis_dataset_raw.parquet")
output_path = os.path.join(current_dir, "data", "tennis_dataset_clean.parquet")

df = pl.read_parquet(dataset_path)

df_unique = df.unique('url_match')

df_unique = df_unique.with_columns([
    (df_unique["surface"] == "dure").cast(pl.Int8).alias("surface_dure"),
    (df_unique["surface"] == "salle").cast(pl.Int8).alias("surface_salle"),
    (df_unique["surface"] == "terre battue").cast(pl.Int8).alias("surface_terre_batue"),
    (df_unique["surface"] == "gazon").cast(pl.Int8).alias("surface_gazon")
])

columns_to_drop = ["url_match", "surface"]
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

df_modified.write_parquet(output_path)