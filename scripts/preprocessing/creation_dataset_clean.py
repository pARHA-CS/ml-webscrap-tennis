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

def invert_match(row):
    inverted_row = row.copy()
    for col in row.keys():
        if col.startswith("player1_"):
            inverted_row[col.replace("player1_", "player2_")] = row[col]
        elif col.startswith("player2_"):
            inverted_row[col.replace("player2_", "player1_")] = row[col]
    inverted_row["target"] = 1 - row["target"]  
    return inverted_row

unique_matches = df.group_by("url_match").count().filter(pl.col("count") == 1)
unique_urls = unique_matches["url_match"].to_list()

inverted_matches = []
for row in df.filter(pl.col("url_match").is_in(unique_urls)).iter_rows(named=True):
    inverted_matches.append(invert_match(row))

# Ajouter les matchs inversés au DataFrame d'origine
df_inverted = pl.DataFrame(inverted_matches)
df_symmetric = pl.concat([df, df_inverted])

df_symmetric = df_symmetric.with_columns([
    (df_symmetric["surface"] == "dure").cast(pl.Int8).alias("surface_dure"),
    (df_symmetric["surface"] == "salle").cast(pl.Int8).alias("surface_salle"),
    (df_symmetric["surface"] == "terre battue").cast(pl.Int8).alias("surface_terre_batue"),
    (df_symmetric["surface"] == "gazon").cast(pl.Int8).alias("surface_gazon")
])

columns_to_drop = ["url_match", "surface"]
df_clean = df_symmetric.drop(columns_to_drop).drop_nulls()

df_modified = df_clean.with_columns([
    (abs(df_clean["player1_ranking"] - df_clean["player2_ranking"])).alias("ranking_diff"),
    (abs(df_clean["player1_points"] - df_clean["player2_points"])).alias("points_diff"),
    (abs(df_clean["player1_win_rate"] - df_clean["player2_win_rate"])).alias("win_rate_diff"),
    (abs(df_clean["player1_win_rate_3_sets"] - df_clean["player2_win_rate_3_sets"])).alias("win_rate_diff_3_sets"),
    (abs(df_clean["player1_win_rate_tiebreak"] - df_clean["player1_win_rate_tiebreak"])).alias("win_rate_tiebreak_diff"),
    (abs(df_clean["player1_avg_aces"] - df_clean["player2_avg_aces"])).alias("aces_diff"),
    (abs(df_clean["player1_avg_double_fautes"] - df_clean["player2_avg_double_fautes"])).alias("double_faults_diff"),
    (abs(df_clean["player1_win_rate_dure"] - df_clean["player2_win_rate_dure"])).alias("win_rate_dure_diff"),
    (abs(df_clean["player1_win_rate_terre battue"] - df_clean["player2_win_rate_terre battue"])).alias("win_rate_terre_diff"),
    (abs(df_clean["player1_win_rate_gazon"] - df_clean["player2_win_rate_gazon"])).alias("win_rate_gazon_diff"),
    (abs(df_clean["player1_win_rate_salle"] - df_clean["player2_win_rate_salle"])).alias("win_rate_salle_diff"),
])

df_modified.write_parquet(output_path)