"""Module pour scrap la page pour collecter tous les joueurs
"""
from dataclasses import dataclass

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

    if len(colonnes) != 3:
        print("Format inattendu dans la ligne:", colonnes)
        return None

    rank, joueur_info, points = colonnes

    lien_joueur, pays, pays_abreviation, nom_joueur, age = "NA", "NA", "NA", "NA", "NA"

    try:
        a_tag = ligne.find("a")
        if a_tag:
            lien_joueur = a_tag.get("href", "NA")
            nom_joueur = a_tag.get("title", "NA")

        img_tag = ligne.find("img")
        if img_tag:
            pays = img_tag.get("alt", "NA")

        if "(" in joueur_info:
            parts = joueur_info.split("(")
            pays_abreviation = parts[1].split(")")[0]
            age = parts[2].split(")")[0] if len(parts) > 2 else "NA"

    except (IndexError, AttributeError) as e:
        print(f"Erreur d'extraction : {e}")
    
    return Ligne(
        rank=rank,
        pays=pays,
        lien_joueur=lien_joueur,
        nom_joueur=nom_joueur,
        pays_abreviation=pays_abreviation,
        age=age,
        points=points,
    )

