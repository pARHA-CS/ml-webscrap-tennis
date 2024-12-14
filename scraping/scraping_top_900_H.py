# type: ignore
"""Description.

Script pour scraper le classement ATP via tennisendirect.net
"""

from requests import get
from bs4 import BeautifulSoup
from dataclasses import dataclass
import json
import os

ADRESSE = "https://www.tennisendirect.net/atp/classement/"

reponse = get(ADRESSE)
print(reponse.status_code)
assert reponse.status_code == 200

classement_soupe = BeautifulSoup(reponse.text, features="lxml")

tables = classement_soupe.find_all("table", attrs={"class": "table_pranks"})
assert len(tables) == 2

table_inter, _ = tables


def extraire_lignes(table):
    return table.find_all(
        "tr", class_=lambda class_name: class_name in ["pair", "unpair"]
    )


@dataclass
class Ligne:
    rank: str
    pays: str
    lien_joueur: str
    nom_joueur: str
    pays_abreviation: str
    age: str
    points: str


def genere_ligne(ligne):
    colonnes = [td.text.strip() for td in ligne.find_all("td")]
    
    if len(colonnes) == 3:
        rank, joueur_info, points = colonnes
    else:
        print("Format inattendu dans la ligne:", colonnes)
        return None

    try:
        lien_joueur = ligne.find("a")["href"]
        nom_joueur = ligne.find("a")["title"]
        pays_abreviation = joueur_info.split("(")[1].split(")")[0]
        pays = ligne.find("img")["alt"]
        age = joueur_info.split("(")[2].split(")")[0] if "(" in joueur_info else ""
    except (IndexError, AttributeError):
        lien_joueur, pays, pays_abreviation, nom_joueur, age = (
            "NA",
            "NA",
            "NA",
            "NA",
            "NA",
        )
        print("Problème d'extraction d'une ligne:", ligne)

    points = colonnes[-1]

    return Ligne(
        rank=rank,
        pays=pays,
        lien_joueur=lien_joueur,
        nom_joueur=nom_joueur,
        pays_abreviation=pays_abreviation,
        age=age,
        points=points,
    )


lignes_inter = extraire_lignes(table_inter)

joueurs = [genere_ligne(ligne) for ligne in lignes_inter if genere_ligne(ligne)]

current_dir: str = os.getcwd()

file_path: str = os.path.join(current_dir, "donnees", "joueurs.json")


with open(file_path, "w") as fichier:
    fichier.write(
        json.dumps(
            [joueur.__dict__ for joueur in joueurs], ensure_ascii=False, indent=4
        )
    )
