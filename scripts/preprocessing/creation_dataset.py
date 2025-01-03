"""Script pour créer le dataset à partir des données scraper
"""
import src.preprocessing.preprocessing as pre
from src.logging.manage_log_preprocessing import preprocessing_setup_logging
import logging
import os

preprocessing_setup_logging()
logging.basicConfig(
    filename=os.path.join(os.getcwd(), "logs", "preprocessing.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode= "w",
    encoding="utf-8"
)
logger = logging.getLogger(__name__)

logger.info("Chargement des données...")
joueurs_data, detail_joueurs, stats_matches = pre.load_data(
    'data/joueurs.json',
    'data/detail_joueurs.json',
    'data/stats_matchs.json'
)

logger.info("Création du dataset d'entraînement...")
df = pre.create_training_dataset(joueurs_data, detail_joueurs, stats_matches)

df.to_csv('data/tennis_dataset_raw.csv', index=False)
logger.info("Dataset brut sauvegardé dans 'data/tennis_dataset_raw.csv'")