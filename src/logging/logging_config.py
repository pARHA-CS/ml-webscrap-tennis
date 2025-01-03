import logging
import os

def setup_logging(log_name="application.log"):
    """
    Configure le système de logging.

    Args:
        log_name (str): Nom du fichier de log.
    """
    log_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(log_dir, exist_ok=True) 
    log_file = os.path.join(log_dir, log_name)

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        encoding="utf-8",
        filemode="w"
    )
