"""Script pour scraper les données d'une page de match entre deux joueurs
"""

import json
import os
import time
import src.scraping.scrap_page_match as spb
from requests import get
from bs4 import BeautifulSoup

current_dir = os.getcwd()
output_file: str = os.path.join(current_dir, "donnees", "stats_matchs.json")

path_detail_joueurs = os.path.join(current_dir, "donnees", "detail_joueurs.json")
with open(path_detail_joueurs, "r") as fichier:
    detail_joueurs = json.load(fichier)
    
liens_match = set()
for key, value in detail_joueurs.items():
    joueur = detail_joueurs[key]
    matchs = joueur['matchs']
    
    for i in range(len(matchs)):
        lien_match = matchs[i]['lien_detail_match']
        liens_match.add(lien_match)
        
id_matchs = {f"match_{i+1}": lien for i, lien in enumerate(liens_match)}

premiers_liens_avec_id = {key: id_matchs[key] for key in list(id_matchs.keys())[:10]}


if os.path.exists(output_file):
    with open(output_file, "r", encoding="utf-8") as fichier:
        try:
            match_data = json.load(fichier)
        except json.JSONDecodeError:
            print(f"Le fichier {output_file} est corrompu ou vide. Il sera remplacé.")
            match_data = {}
else:
    match_data = {}
    
for id_match, lien_match in premiers_liens_avec_id.items():
    print(f"Scraping des données pour {id_match} : {lien_match}...")
    
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
        
        print(f"Données de {id_match} sauvegardées.")

    except Exception as e:
        print(f"Erreur lors du traitement de {id_match} : {lien_match} -> {e}")
        
    time.sleep(2)
    
print(f"Tous les matchs ont été traités et sauvegardés dans {output_file}")