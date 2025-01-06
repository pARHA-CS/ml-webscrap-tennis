import polars as pl
import os

current_dir = os.getcwd()
print(current_dir)

dataset_path = os.path.join(current_dir, "data", "tennis_dataset_raw.csv")
output_path = os.path.join(current_dir, "data", "tennis_dataset_clean.csv")

df = pl.read_csv(dataset_path)

df_unique = df.unique('url_match')

columns_to_drop = ["player1_name", "player2_name", "url_match"]
df_clean = df_unique.drop(columns_to_drop)

df_clean.write_csv(output_path)