"""Script pour créer un dataset pour l'app 

    Return : tennis_dataset_app.csv
"""
import os
import polars as pl

current_dir = os.getcwd()

output_path = os.path.join(current_dir, "data", "tennis_dataset_app.csv")
dataset_path = os.path.join(current_dir, "data", "tennis_dataset_clean.csv")

df = pl.read_csv(dataset_path)

df = df.with_columns(
    pl.col("date").str.strptime(pl.Date, format="%d.%m.%y").alias("date")
)

joueurs = set(list(df.select(pl.col("player1_name")).to_numpy().flatten()) + list(df.select(pl.col("player2_name")).to_numpy().flatten()))
assert len(joueurs) == 200, f"nombre de joueurs incomplet, joueurs = {len(joueurs)}"

derniers_matches = pl.DataFrame()
for joueur in joueurs:
    dernier_match = (
        df.filter(
            (pl.col("player1_name") == joueur) | (pl.col("player2_name") == joueur)
        )
        .sort(by="date", descending=True)
        .head(1)
    )
    if derniers_matches.is_empty():
        derniers_matches = dernier_match
    else:
        derniers_matches = pl.concat([derniers_matches, dernier_match], how="vertical")
        
df_player1 = derniers_matches.select([col for col in derniers_matches.columns if "player1" in col] + ["date"])
df_player2 = derniers_matches.select([col for col in derniers_matches.columns if "player2" in col] + ["date"]).rename({col: col.replace("player2", "player1") for col in derniers_matches.columns})
        
df_combined = pl.concat([df_player1, df_player2], how="vertical").sort(by="date", descending=True)
df_recent = df_combined.group_by("player1_name").agg(pl.col("*").first())

df_recent.drop("date").write_csv(output_path)