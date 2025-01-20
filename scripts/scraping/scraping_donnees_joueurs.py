"""Script pour collecter les données de chaque joueur en scrapant leur page 

    Return:
        Un json avec les données de chaque joueurs 
"""
import os
import json
import time
import logging
import random
from tqdm import tqdm
from requests import Response, get
from bs4 import BeautifulSoup
import src.scraping.scrap_page_joueur as spj


logging.basicConfig(
    filename=os.path.join(os.getcwd(), "logs", "scraping_donnees_joueurs.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode = 'w',
    encoding="utf-8"
)
logger = logging.getLogger(__name__)

logger.info("Script de scraping des données des joueurs démarré.")

current_dir: str = os.getcwd()
file_path: str = os.path.join(current_dir, "data", "joueurs.json")
output_file: str = os.path.join(current_dir, "data", "detail_joueurs.json")

try:
    with open(file_path, "r") as fichier:
        joueurs: list[dict] = json.load(fichier)
        assert len(joueurs) == 900
    logger.info("Fichier joueurs chargé avec succès.")
except FileNotFoundError:
    logger.critical(f"Le fichier {file_path} est introuvable.")
    raise
except AssertionError:
    logger.error("Le nombre de joueurs dans le fichier ne correspond pas à 900.")
    raise
except json.JSONDecodeError:
    logger.error("Erreur de décodage JSON lors du chargement du fichier joueurs.")
    raise

if os.path.exists(output_file):
    try:
        with open(output_file, "r", encoding="utf-8") as fichier:
            joueurs_data = json.load(fichier)
        logger.info(f"Fichier {output_file} chargé avec succès.")
    except json.JSONDecodeError:
        logger.warning(f"Le fichier {output_file} est corrompu ou vide. Un nouveau fichier sera créé.")
        joueurs_data = {}
else:
    joueurs_data = {}
    logger.info(f"Le fichier {output_file} n'existe pas. Un nouveau fichier sera créé.")

nombre_joueurs_scrap = 200
generateur_joueurs = (joueurs[i] for i in range(nombre_joueurs_scrap))  # génère les 100 premiers joueurs 

for joueur in tqdm(generateur_joueurs, desc="Scraping des joueurs", unit="joueur", total=nombre_joueurs_scrap):
    nom_joueur = joueur['nom_joueur']
    lien = joueur['lien_joueur']
    
    logger.info(f"Début du scraping pour {nom_joueur}...")

    try:
        reponse: Response = get(lien)
        reponse.raise_for_status()
        detail_joueur = BeautifulSoup(reponse.text, features="lxml")
        
        profil = detail_joueur.find_all("div", attrs={"class": "player_stats"})
        statistiques = detail_joueur.find_all("table", attrs={"class": "table_stats"})
        *_, derniers_match = detail_joueur.find_all("table", attrs={"class": "table_pmatches"})

        if len(profil) != 1 or len(statistiques) != 1:
            raise ValueError(f"Erreur dans la structure des données pour {nom_joueur}")

        joueur_profil: spj.Profil = spj.genere_profil(profil)
        
        lignes_stats = spj.extraire_lignes(statistiques[0])
        joueur_statistiques_agregees = spj.genere_statistiques_agregrees(lignes_stats)
        
        lignes_derniers_matchs = spj.extraire_lignes(derniers_match)
        joueur_derniers_matchs: spj.List[spj.Matchs] = spj.genere_derniers_matchs(lignes_derniers_matchs)

        joueurs_data[nom_joueur] = {
            "profil": joueur_profil.__dict__,
            "statistiques": joueur_statistiques_agregees,
            "matchs": [match.__dict__ for match in joueur_derniers_matchs]
        }
        with open(output_file, "w", encoding="utf-8") as fichier:
            json.dump(joueurs_data, fichier, ensure_ascii=False, indent=4)
        
        logger.info(f"Données de {nom_joueur} sauvegardées avec succès.")
    
    except Exception as e:
        logger.error(f"Erreur lors du traitement de {nom_joueur}: {e}", exc_info=True)
    
    time.sleep(random.uniform(2,5))

logger.info(f"Tous les joueurs ont été traités et sauvegardés dans {output_file}.")