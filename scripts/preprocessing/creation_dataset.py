"""Script pour créer le dataset à partir des données scraper

    Return : tennis_dataset_raw.csv
"""
from polars import DataFrame
import src.preprocessing.preprocessing as pre
from src.logging.logging_config import setup_logging
import logging

setup_logging("preprocessing.log")
logger: logging.Logger = logging.getLogger(__name__)  

logger.info("Script de scraping des données des joueurs démarré.")
logger.info("Chargement des données...")

output_file = 'data/tennis_dataset_raw.parquet'

try:
    joueurs_data, detail_joueurs, stats_matches = pre.load_data(
        'data/joueurs.json',
        'data/detail_joueurs.json',
        'data/stats_matchs_cleaned.json'
    )
    logger.info("Données chargées avec succès.")
except Exception as e:
    logger.error(f"Erreur lors du chargement des données : {e}")
    raise

try:
    logger.info("Création du dataset d'entraînement...")
    df: DataFrame = pre.create_training_dataset(joueurs_data, detail_joueurs, stats_matches)
    df.write_parquet(output_file)
    logger.info("Dataset brut sauvegardé dans 'data/tennis_dataset_raw.parquet'.")
except Exception as e:
    logger.error(f"Erreur lors de la création du dataset : {e}")
    raise