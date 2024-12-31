"""Script pour récupérer les données d'un joueur et de les stocker dans 3 json à part (peut être à supprimer)
"""

from requests import get
from bs4 import BeautifulSoup
import json
import os
import time
import src.scraping.scrap_page_joueur as spj

   
current_dir: str = os.getcwd()
file_path: str = os.path.join(current_dir, "data", "joueurs.json")

# Charger le JSON
with open(file_path, "r") as fichier:
    joueurs:list[dict] = json.load(fichier)
    assert len(joueurs) == 900
    
genereateur_joueurs = (joueurs[i] for i in range(10))

for joueur in genereateur_joueurs:
    nom_joueur = joueur['nom_joueur'].replace(" ", "_")
    lien = joueur['lien_joueur']
    
    print(nom_joueur)
    
    reponse = get(lien)
    assert reponse.status_code == 200
    
    detail_joueur = BeautifulSoup(reponse.text, features="lxml")
    
    profil = detail_joueur.find_all("div", attrs={"class": "player_stats"})
    assert len(profil) == 1
    statistiques = detail_joueur.find_all("table", attrs={"class": "table_stats"})
    assert len(statistiques) == 1
    *_, derniers_match = detail_joueur.find_all("table", attrs={"class": "table_pmatches"})

    joueur_profil = spj.genere_profil(profil)

    lignes_stats = spj.extraire_lignes(statistiques[0])
    joueur_statistiques_agregees = spj.genere_statistiques_agregrees(lignes_stats)

    lignes_derniers_matchs = spj.extraire_lignes(derniers_match)
    joueur_derniers_matchs = spj.genere_derniers_matchs(lignes_derniers_matchs)

    joueurs_data = {}

    joueurs_data[joueur_profil.nom] = {
        "profil": joueur_profil.__dict__,
        "statistiques": joueur_statistiques_agregees,
        "matchs": [match.__dict__ for match in joueur_derniers_matchs]
    }
    
    output_file = os.path.join(current_dir, "data", "detail_joueurs.json")
    
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as fichier:
            try:
                joueurs_data.update(json.load(fichier))
            except json.JSONDecodeError:
                print("Fichier JSON corrompu ou vide. Il sera remplacé.")
    
    with open(output_file, "w", encoding= "utf-8") as fichier:
        json.dump(joueurs_data, fichier, ensure_ascii=False, indent=4)
    
    time.sleep(2)
    

