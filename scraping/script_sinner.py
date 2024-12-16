from requests import get
from bs4 import BeautifulSoup
import json
from typing import TypedDict
import os
import scrap_page_joueur as spj

class Joueur(TypedDict):
    rank: str
    pays: str
    lien_joueur: str
    nom_joueur: str
    pays_abreviation: str
    age: str
    points: str
    

current_dir: str = os.getcwd()

# file_path: str = os.path.join(current_dir, "donnees", "joueurs.json")

# # Charger le JSON
# with open(file_path, "r") as fichier:
#     joueurs:list[dict] = json.load(fichier)
#     assert len(joueurs) == 900
    
# liens_joueurs = (joueurs[i]['lien_joueur'] for i in range(len(joueurs)))

# Test de récupération des stats d'un joueur (Sinner)
Sinner = "https://www.tennisendirect.net/atp/jannik-sinner/"
Zverev = "https://www.tennisendirect.net/atp/alexander-zverev/"
Alcaraz = "https://www.tennisendirect.net/atp/carlos-alcaraz-garfia/"
Djokovic = "https://www.tennisendirect.net/atp/novak-djokovic/"

reponse = get(Djokovic)
reponse.encoding = 'utf-8'
print(reponse.encoding)
assert reponse.status_code == 200

detail_Sinner = BeautifulSoup(reponse.text, features="lxml")

profil = detail_Sinner.find_all("div", attrs={"class": "player_stats"})
assert len(profil) == 1

statistiques = detail_Sinner.find_all("table", attrs={"class": "table_stats"})
assert len(statistiques) == 1

*_, derniers_match = detail_Sinner.find_all("table", attrs={"class": "table_pmatches"})


Sinner_profil = spj.genere_profil(profil)

lignes_stats = spj.extraire_lignes(statistiques[0])
Sinner_statistiques_agregees = spj.generer_statistiques_agregrees(lignes_stats)

ligne_derniers_matchs = spj.extraire_lignes(derniers_match)
Sinner_derniers_matchs = spj.genere_derniers_matchs(ligne_derniers_matchs)


joueurs_data = {}

joueurs_data[Sinner_profil.nom] = {
    "profil": Sinner_profil.__dict__,
    "statistiques": Sinner_statistiques_agregees,
    "matchs": [match.__dict__ for match in Sinner_derniers_matchs]
}

nom_joueur = Sinner_profil.nom.replace(" ", "_")
file_path_joueurs: str = os.path.join(current_dir, "donnees", "joueurs", f"{nom_joueur}.json")

if os.path.exists(file_path_joueurs):
    with open(file_path_joueurs, "r", encoding="utf-8") as fichier:
        try:
            joueurs_data.update(json.load(fichier))
        except json.JSONDecodeError:
            print("Fichier JSON corrompu ou vide. Il sera remplacé.")

with open(file_path_joueurs, "w", encoding= "utf-8") as fichier:
    json.dump(joueurs_data, fichier, ensure_ascii=False, indent=4)


