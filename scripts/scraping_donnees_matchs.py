"""Script pour scraper les données d'une page de match entre deux joueurs
"""

import json
import os
import time
import logging
from requests import get
from bs4 import BeautifulSoup
import src.scraping.scrap_page_match as spb

# Configuration du logger
logging.basicConfig(
    filename=os.path.join(os.getcwd(), "logs", "scraping_donnees_matchs.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode= "w",
    encoding="utf-8"
)
logger = logging.getLogger(__name__)

current_dir = os.getcwd()
output_file: str = os.path.join(current_dir, "data", "stats_matchs.json")

path_detail_joueurs = os.path.join(current_dir, "data", "detail_joueurs.json")
try:
    with open(path_detail_joueurs, "r") as fichier:
        detail_joueurs = json.load(fichier)
        logger.info(f"Fichier {path_detail_joueurs} chargé avec succès.")
except Exception as e:
    logger.error(f"Erreur lors du chargement de {path_detail_joueurs}: {e}")
    raise

liens_match = set()
for key, value in detail_joueurs.items():
    joueur = detail_joueurs[key]
    matchs = joueur['matchs']
    
    for i in range(len(matchs)):
        lien_match = matchs[i]['lien_detail_match']
        liens_match.add(lien_match)

id_matchs = {f"match_{i+1}": lien for i, lien in enumerate(liens_match)}

nombre_matchs_scrap = 100
premiers_liens_avec_id = {key: id_matchs[key] for key in list(id_matchs.keys())[:nombre_matchs_scrap]}

if os.path.exists(output_file):
    try:
        with open(output_file, "r", encoding="utf-8") as fichier:
            match_data = json.load(fichier)
            logger.info(f"Fichier {output_file} chargé avec succès.")
    except json.JSONDecodeError:
        logger.warning(f"Le fichier {output_file} est corrompu ou vide. Il sera remplacé.")
        match_data = {}
else:
    match_data = {}
    logger.info(f"Aucun fichier {output_file} trouvé. Un nouveau sera créé.")

for id_match, lien_match in premiers_liens_avec_id.items():
    logger.info(f"Début du scraping pour {id_match} : {lien_match}...")
    
    try:
        reponse = get(lien_match)
        assert reponse.status_code == 200, f"Erreur HTTP {reponse.status_code}: {lien_match}"
        
        detail_match = BeautifulSoup(reponse.text, features="lxml")
        statistiques = detail_match.find_all("table", attrs={"class": "table_stats_match"})[0]
        
        table_data = spb.extraire_colonnes(statistiques)
        stats_dict = spb.lignes_statistiques(table_data)
        
        # Crée les objets StatsMatch
        stats_joueur_A, stats_joueur_B = spb.creer_stats_pour_deux_joueurs(stats_dict)
        
        match_data[id_match] = {
            "lien_match": lien_match,
            "joueur_gagnant": stats_joueur_A.__dict__,
            "joueur_perdant": stats_joueur_B.__dict__
        }
        
        with open(output_file, "w", encoding="utf-8") as fichier:
            json.dump(match_data, fichier, ensure_ascii=False, indent=4)
        
        logger.info(f"Données de {id_match} sauvegardées avec succès.")

    except Exception as e:
        logger.error(f"Erreur lors du traitement de {id_match} : {lien_match} -> {e}")
        
    time.sleep(2)
    
logger.info(f"Tous les matchs ont été traités et sauvegardés dans {output_file}")
