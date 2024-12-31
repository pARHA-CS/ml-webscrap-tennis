"""Script pour nettoyer les données de detail_joueurs.json
"""

import os 
import json
import logging

logging.basicConfig(
    filename=os.path.join(os.getcwd(), "logs", "preprocessing_details_joueurs.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode= "w",
    encoding="utf-8"
)
logger = logging.getLogger(__name__)

current_dir = os.getcwd()
output_file: str = os.path.join(current_dir, "data", "stats_matchs.json")

path_detail_joueurs = os.path.join(current_dir, "data", "detail_joueurs.json")

with open(path_detail_joueurs, "r", encoding= "utf-8") as file:
    detail_joueurs = json.load(file)
    
"""
details_joueurs : 
    - nom_joueur (dict):
        - profil (dict):
            - str: nom, pays, date de naissance, age, classement atp, points, primes, total_match, victoires, taux de reussite
        - statistiques (dict):
            - str: annee_(sommaire, dure, terre battue, salle, carpet, gazon, acryl)
        - matchs (list):
            - match (dict):
                - str: date, stage, nom joueur, nom opposant, score, resultat, lien du detail du match, le tournoi, le type de terrain
"""

for joueur, value in detail_joueurs.items():
    logger.info(f"key : {joueur}")
    
    for stats, value_2 in value.items():
        logger.info(f"key : {stats}")
        logger.info(type(value_2))
        
        if isinstance(value_2, dict):
            for key, value_3 in value_2.items():
                logger.info(f"  key : {key}, {value_3} ({type(value_3)})")
            
        else: 
            for i in range(len(value_2)):
                logger.info(f"  list: [{type(value_2[i])}]")
                
                for key_list, value_list in value_2[i].items():
                    logger.info(f"  key : {key_list}, {value_list}")
    