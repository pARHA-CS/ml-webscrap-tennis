"""Script pour collecter les données de chaque joueur en scrapant leur page 

    Return:
        Un json avec les données de chaque joueurs 
"""
import os
import json
import time
from requests import get
from bs4 import BeautifulSoup
import scrap_page_joueur as spj


current_dir: str = os.getcwd()
file_path: str = os.path.join(current_dir, "donnees", "joueurs.json")
output_file: str = os.path.join(current_dir, "donnees", "detail_joueurs.json")

with open(file_path, "r") as fichier:
    joueurs: list[dict] = json.load(fichier)
    assert len(joueurs) == 900

generateur_joueurs = (joueurs[i] for i in range(10))

if os.path.exists(output_file):
    with open(output_file, "r", encoding="utf-8") as fichier:
        try:
            joueurs_data = json.load(fichier)
        except json.JSONDecodeError:
            print(f"Le fichier {output_file} est corrompu ou vide. Il sera remplacé.")
            joueurs_data = {}
else:
    joueurs_data = {}

for joueur in generateur_joueurs:
    nom_joueur = joueur['nom_joueur'].replace(" ", "_")
    lien = joueur['lien_joueur']
    
    print(f"Scraping des données pour {nom_joueur}...")
    
    try:
        reponse = get(lien)
        assert reponse.status_code == 200, f"Erreur HTTP {reponse.status_code}: {lien}"
        detail_joueur = BeautifulSoup(reponse.text, features="lxml")
        
        
        profil = detail_joueur.find_all("div", attrs={"class": "player_stats"})
        statistiques = detail_joueur.find_all("table", attrs={"class": "table_stats"})
        *_, derniers_match = detail_joueur.find_all("table", attrs={"class": "table_pmatches"})

        if len(profil) != 1 or len(statistiques) != 1:
            raise ValueError(f"Erreur dans la structure des données pour {nom_joueur}")

        
        joueur_profil = spj.genere_profil(profil)
        lignes_stats = spj.extraire_lignes(statistiques[0])
        joueur_statistiques_agregees = spj.genere_statistiques_agregrees(lignes_stats)
        lignes_derniers_matchs = spj.extraire_lignes(derniers_match)
        joueur_derniers_matchs = spj.genere_derniers_matchs(lignes_derniers_matchs)

        
        joueurs_data[nom_joueur] = {
            "profil": joueur_profil.__dict__,
            "statistiques": joueur_statistiques_agregees,
            "matchs": [match.__dict__ for match in joueur_derniers_matchs]
        }

        
        with open(output_file, "w", encoding="utf-8") as fichier:
            json.dump(joueurs_data, fichier, ensure_ascii=False, indent=4)
        
        print(f"Données de {nom_joueur} sauvegardées.")
    
    except Exception as e:
        print(f"Erreur lors du traitement de {nom_joueur}: {e}")
    
    
    time.sleep(2)

print(f"Tous les joueurs ont été traités et sauvegardés dans {output_file}")
