import logging
import os

def preprocessing_setup_logging():
    log_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(log_dir, exist_ok=True)  # Crée le dossier "logs" s'il n'existe pas
    log_file = os.path.join(log_dir, "preprocessing.log")

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        encoding="utf-8"
    )
