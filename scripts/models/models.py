import polars as pl
import logging
import os
from joblib import dump
from src.logging.logging_config import setup_logging
from src.models.models_selector import find_best_model, SEED

setup_logging("models.log")
logger: logging.Logger = logging.getLogger(__name__)  

current_dir = os.getcwd()
dataset_path = os.path.join(current_dir, "data", "tennis_dataset_clean_essaie.csv")
df = pl.read_csv(dataset_path)

df = df.drop("player1_name", "player2_name", "index", "date") 

results = find_best_model(df, SEED)

output_file = 'data/best_model.joblib'
dump(results['best_model'], output_file)
logger.info("Modele sauvergardé")

logger.info(f"Meilleur modèle : {results['model_name']}")
logger.info(f"Précision : {results['accuracy']}")
