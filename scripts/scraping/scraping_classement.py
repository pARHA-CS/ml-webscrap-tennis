# type: ignore
"""Description.

Script pour scraper le classement ATP via tennisendirect.net
"""

from requests import Response, get
from bs4 import BeautifulSoup
import src.scraping.scrap_page_classement as spp, Ligne
import json
import os

ADRESSE = "https://www.tennisendirect.net/atp/classement/"

reponse: Response = get(ADRESSE)
print(reponse.status_code)
assert reponse.status_code == 200

# Sauvegarder l'HTML de la page pour des tests ultérieurs
current_dir: str = os.getcwd()
html_file_path: str = os.path.join(current_dir, "html", "page_source.html")

os.makedirs(os.path.dirname(html_file_path), exist_ok=True) 

with open(html_file_path, "w", encoding="utf-8") as html_file:
    html_file.write(reponse.text)

# Analyse de l'HTML avec BeautifulSoup
classement_soupe = BeautifulSoup(reponse.text, features="lxml")

tables = classement_soupe.find_all("table", attrs={"class": "table_pranks"})
assert len(tables) == 2

table_inter, _ = tables


lignes_inter = spp.extraire_lignes(table_inter)

joueurs: list[Ligne | None] = [spp.genere_ligne(ligne) for ligne in lignes_inter if spp.genere_ligne(ligne)]

current_dir: str = os.getcwd()

file_path: str = os.path.join(current_dir, "data", "joueurs.json")

print(f"Chargement du module depuis : {__file__}")

with open(file_path, "w") as fichier:
    fichier.write(
        json.dumps(
            [joueur.__dict__ for joueur in joueurs], ensure_ascii=False, indent=4
        )
    )

