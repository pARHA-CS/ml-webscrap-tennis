import polars as pl
import os

current_dir = os.getcwd()
print(current_dir)

dataset_path = os.path.join(current_dir, "data", "tennis_dataset_raw.csv")
output_path = os.path.join(current_dir, "data", "tennis_dataset_clean.csv")

df = pl.read_csv(dataset_path)

df_unique = df.unique('url_match')

# Encodage one-hot pour les surfaces:
df_unique = df_unique.with_columns([
    (df_unique["surface"] == "dure").cast(pl.Int8).alias("surface_dure"),
    (df_unique["surface"] == "salle").cast(pl.Int8).alias("surface_salle"),
    (df_unique["surface"] == "terre battue").cast(pl.Int8).alias("surface_terre_batue"),
    (df_unique["surface"] == "gazon").cast(pl.Int8).alias("surface_gazon")
])

columns_to_drop = ["player1_name", "player2_name", "url_match", "surface"]
df_clean = df_unique.drop(columns_to_drop).drop_nulls()

df_clean.write_csv(output_path)