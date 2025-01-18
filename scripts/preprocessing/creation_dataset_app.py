"""Script pour créer un dataset pour l'app 

    Return : tennis_dataset_app.csv
"""
import os
import polars as pl

current_dir: str = os.getcwd()

output_path: str = os.path.join(current_dir, "data", "tennis_dataset_app.parquet")
dataset_path: str = os.path.join(current_dir, "data", "tennis_dataset_clean.parquet")

df: pl.DataFrame = pl.read_parquet(dataset_path)

df = df.with_columns(
    pl.col("date").str.strptime(pl.Date, format="%d.%m.%y").alias("date")
)

joueurs = set(list(df.select(pl.col("player1_name")).to_numpy().flatten()) + list(df.select(pl.col("player2_name")).to_numpy().flatten()))
assert len(joueurs) == 200, f"nombre de joueurs incomplet, joueurs = {len(joueurs)}"

derniers_matches = pl.DataFrame()
for joueur in joueurs:
    dernier_match: pl.DataFrame = (
        df.filter(
            (pl.col("player1_name") == joueur) | (pl.col("player2_name") == joueur)
        )
        .sort(by="date", descending=True)
        .head(1)
    )
    if derniers_matches.is_empty():
        derniers_matches: pl.DataFrame = dernier_match
    else:
        derniers_matches = pl.concat([derniers_matches, dernier_match], how="vertical")
        
df_player1: pl.DataFrame = derniers_matches.select([col for col in derniers_matches.columns if "player1" in col] + ["date"])
df_player2: pl.DataFrame = derniers_matches.select([col for col in derniers_matches.columns if "player2" in col] + ["date"]).rename({col: col.replace("player2", "player1") for col in derniers_matches.columns})
        
df_combined: pl.DataFrame = pl.concat([df_player1, df_player2], how="vertical").sort(by="date", descending=True)
df_recent: pl.DataFrame = df_combined.group_by("player1_name").agg(pl.col("*").first())

df_recent.drop("date").write_parquet(output_path)