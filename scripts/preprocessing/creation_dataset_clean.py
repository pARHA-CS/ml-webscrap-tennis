"""Script pour créer via tennis_dataset_raw.parquet un dataset pour le ml

    Return : tennis_dataset_clean.parquet
"""

import polars as pl
import os
from src.preprocessing.preprocessing import invert_match


current_dir: str = os.getcwd()

dataset_path: str = os.path.join(current_dir, "data", "tennis_dataset_raw.parquet")
output_path: str = os.path.join(current_dir, "data", "tennis_dataset_clean.parquet")

df: pl.DataFrame = pl.read_parquet(dataset_path)

unique_matches: pl.DataFrame = df.group_by("url_match").len().filter(pl.col("len") == 1)
unique_urls: list[str] = unique_matches["url_match"].to_list()

inverted_matches = []
for row in df.filter(pl.col("url_match").is_in(unique_urls)).iter_rows(named=True):
    inverted_matches.append(invert_match(row))

df_inverted = pl.DataFrame(inverted_matches)
df_symmetric: pl.DataFrame = pl.concat([df, df_inverted])

df_symmetric = df_symmetric.with_columns(
    [
        (df_symmetric["surface"] == "dure").cast(pl.Int8).alias("surface_dure"),
        (df_symmetric["surface"] == "salle").cast(pl.Int8).alias("surface_salle"),
        (df_symmetric["surface"] == "terre battue")
        .cast(pl.Int8)
        .alias("surface_terre_batue"),
        (df_symmetric["surface"] == "gazon").cast(pl.Int8).alias("surface_gazon"),
    ]
)

columns_to_drop: list[str] = ["url_match", "surface"]
df_clean: pl.DataFrame = df_symmetric.drop(columns_to_drop).drop_nulls()

df_modified: pl.DataFrame = df_clean.with_columns(
    [
        ((df_clean["player1_ranking"] - df_clean["player2_ranking"])).alias(
            "ranking_diff"
        ),
        ((df_clean["player1_points"] - df_clean["player2_points"])).alias(
            "points_diff"
        ),
        ((df_clean["player1_win_rate"] - df_clean["player2_win_rate"])).alias(
            "win_rate_diff"
        ),
        (
            (df_clean["player1_win_rate_3_sets"] - df_clean["player2_win_rate_3_sets"])
        ).alias("win_rate_diff_3_sets"),
        (
            (
                df_clean["player1_win_rate_tiebreak"]
                - df_clean["player1_win_rate_tiebreak"]
            )
        ).alias("win_rate_tiebreak_diff"),
        ((df_clean["player1_avg_aces"] - df_clean["player2_avg_aces"])).alias(
            "aces_diff"
        ),
        (
            (
                df_clean["player1_avg_double_fautes"]
                - df_clean["player2_avg_double_fautes"]
            )
        ).alias("double_faults_diff"),
        ((df_clean["player1_win_rate_dure"] - df_clean["player2_win_rate_dure"])).alias(
            "win_rate_dure_diff"
        ),
        (
            (
                df_clean["player1_win_rate_terre battue"]
                - df_clean["player2_win_rate_terre battue"]
            )
        ).alias("win_rate_terre_diff"),
        (
            (df_clean["player1_win_rate_gazon"] - df_clean["player2_win_rate_gazon"])
        ).alias("win_rate_gazon_diff"),
        (
            (df_clean["player1_win_rate_salle"] - df_clean["player2_win_rate_salle"])
        ).alias("win_rate_salle_diff"),
    ]
)

df_modified.write_parquet(output_path)
