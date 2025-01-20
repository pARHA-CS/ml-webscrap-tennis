"""Module pour scrap la page pour collecter tous les joueurs
"""

from dataclasses import dataclass
from bs4 import BeautifulSoup

def extraire_lignes(table: BeautifulSoup) -> list:
    """
    Extrait les lignes d'une table HTML en fonction de leurs classes.

    Args:
        table (BeautifulSoup): Objet BeautifulSoup représentant la table HTML.

    Returns:
        list: Liste des éléments `<tr>` correspondant aux lignes ayant la classe "pair" ou "unpair".
    """
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


def genere_ligne(ligne)-> Ligne | None:
    """
    Génère une instance de `Ligne` représentant les informations extraites d'une ligne HTML.

    Args:
        ligne (BeautifulSoup): Élément `<tr>` représentant une ligne de la table.

    Returns:
        Ligne: Objet contenant les informations suivantes :
            - rank (str): Classement du joueur.
            - pays (str): Nom du pays du joueur.
            - lien_joueur (str): Lien vers le profil du joueur.
            - nom_joueur (str): Nom complet du joueur.
            - pays_abreviation (str): Abréviation du pays.
            - age (str): Âge du joueur.
            - points (str): Points attribués au joueur.
        Retourne `None` si le format de la ligne est inattendu.
    """
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
