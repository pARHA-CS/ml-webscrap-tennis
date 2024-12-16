"""Script pour récupérer les données d'un joueur et de les stocker dans 3 json à part (peut être à supprimer)
"""

from requests import get
from bs4 import BeautifulSoup
from dataclasses import dataclass
import json
from typing import TypedDict
import os
import time
from typing import Tuple
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

parent_dir: str = os.path.dirname(current_dir)

file_path: str = os.path.join(current_dir, "donnees", "joueurs.json")

# Charger le JSON
with open(file_path, "r") as fichier:
    joueurs:list[dict] = json.load(fichier)
    assert len(joueurs) == 900
    
liens_joueurs = (joueurs[i]['lien_joueur'] for i in range(len(joueurs)))


# Test de récupération des stats d'un joueur (Sinner)

Sinner = "https://www.tennisendirect.net/atp/jannik-sinner/"

reponse = get(Sinner)
print(Sinner, reponse.status_code)
assert reponse.status_code == 200

detail_Sinner = BeautifulSoup(reponse.text, features="lxml")

profil = detail_Sinner.find_all("div", attrs={"class": "player_stats"})
assert len(profil) == 1
statistiques = detail_Sinner.find_all("table", attrs={"class": "table_stats"})
assert len(statistiques) == 1
*_, derniers_match = detail_Sinner.find_all("table", attrs={"class": "table_pmatches"})

@dataclass
class Profil:
    nom: str
    pays: str
    date_naissance: str
    age: str
    classement_atp: str
    points: str
    primes: str
    total_match: str
    victoires: str
    taux_reussite: str
    
@dataclass
class Statistiques:
    annee: str
    sommaire: str
    dure: str
    terre_battue: str
    salle: str
    carpet: str
    gazon: str
    acryl: str
    
@dataclass
class Matchs:
    date: str
    stage: str
    nom_vainqueur: str
    nom_perdant: str
    score: str
    resultat: str
    lien_detail: str
    tournoi: str
    type_terrain :str
    
## Profil 
print(profil)
def genere_profil(profil):
    """
    Génère un profil de joueur de tennis à partir des informations HTML fournies.

    Args:
        profil (list): Une liste d'éléments HTML, où le premier élément contient les informations du joueur.

    Returns:
        Profil: Un objet contenant les informations du joueur, telles que le nom, le pays, 
        la date de naissance, l'âge, le classement ATP, les points, les primes, le total de matchs, 
        les victoires, et le taux de réussite.

    Remarque:
        En cas d'erreur d'extraction (par exemple, si les balises ne sont pas présentes ou sont mal formées),
        des valeurs par défaut ("NA") sont utilisées pour les champs.
    """
    div = profil[0]

    try:
        nom_joueur = div.find("a").text.strip()
        pays = div.find_all("b")[1].text.strip()
        date_naissance = div.find_all("b")[2].text.strip().split(", ")[0]
        age = div.find_all("b")[2].text.strip().split(", ")[1]
        classement_atp = div.find_all("b")[3].text.strip()
        points = div.find_all("b")[5].text.strip()
        primes = div.find_all("b")[6].text.strip()
        total_match = div.find_all("b")[7].text.strip()
        victoires = div.find_all("b")[8].text.strip()
        taux_reussite = div.find_all("b")[9].text.strip()
    
    except (IndexError, AttributeError):
        nom_joueur, pays, date_naissance, age, classement_atp, points, primes, total_match, victoires, taux_reussite =(
            "NA",
            "NA",
            "NA",
            "NA",
            "NA",
            "NA",
            "NA",
            "NA",
            "NA",
            "NA",
        )
        
    return Profil(
        nom=nom_joueur,
        pays=pays,
        date_naissance=date_naissance,
        age=age,
        classement_atp=classement_atp,
        points=points,
        primes=primes,
        total_match=total_match,
        victoires=victoires,
        taux_reussite=taux_reussite,
    )  

Sinner_profil = genere_profil(profil)


## Statistiques
def extraire_lignes(table):
    """
    Extrait les lignes d'une table HTML ayant des classes spécifiques.

    Args:
        table (BeautifulSoup): Objet représentant une table HTML.

    Returns:
        list: Liste des éléments `<tr>` avec les classes "pair" ou "unpair".
    """
    return table.find_all(
        "tr", class_=lambda class_name: class_name in ["pair", "unpair"]
    )
def genere_statistiques(ligne):
    """
    Génère des statistiques annuelles d'un joueur à partir d'une ligne HTML.

    Args:
        ligne (BeautifulSoup): Élément HTML représentant une ligne `<tr>` contenant les statistiques.

    Returns:
        Statistiques: Objet contenant les statistiques suivantes :
            - annee (str): Année des statistiques.
            - sommaire (str): Résumé des performances.
            - dure (str): Performances sur surface dure.
            - terre_battue (str): Performances sur terre battue.
            - salle (str): Performances en salle.
            - carpet (str): Performances sur moquette.
            - gazon (str): Performances sur gazon.
            - acryl (str): Performances sur acrylique.

    Raises:
        None: Retourne `None` si le format de la ligne est inattendu.
    """

    colonnes = [td.text.strip() for td in ligne.find_all("td")]
    
    if len(colonnes) == 8:
        annee, sommaire, dure, terre_battue, salle, carpet, gazon, acryl = colonnes
    else:
        print("Format inattendu dans la ligne:", colonnes)
        return None

    return Statistiques(
        annee = annee,
        sommaire = sommaire,
        dure = dure,
        terre_battue = terre_battue,
        salle = salle,
        carpet = carpet,
        gazon = gazon,
        acryl = acryl,
    ) 
lignes_stats = extraire_lignes(statistiques[0])
Sinner_statistiques = [genere_statistiques(ligne) for ligne in lignes_stats if genere_statistiques(ligne)]


##Matchs
def filtre_tour_head(ligne) -> Tuple[Matchs, str, str]:
    """
    Filtre les informations d'une ligne HTML pour extraire les données d'un match et des détails du tournoi.

    Args:
        ligne (BeautifulSoup): Élément HTML représentant une ligne `<tr>` contenant les informations du match.

    Returns:
        Tuple[Matchs, str, str]: 
            - Un objet `Matchs` avec les détails du match (date, stage, vainqueur, perdant, score, etc.).
            - Le nom du tournoi (str).
            - Le type de terrain (str).
    """

    (
        date, stage, _, _, score, _, _, _, type_terrain
    ) = [td.text.strip() for td in ligne.find_all("td")]

    try:
        nom_vainqueur = ligne.find_all("b")[0].text.strip()
        nom_perdant = ligne.find_all("a")[0].text.strip()
        resultat = ligne.find_all("img")[0]["alt"]
        lien_detail = ligne.find_all("a")[1]["href"]
        tournoi = ligne.find_all("a")[2]["title"]
    
    except (IndexError, AttributeError):
        nom_vainqueur, nom_perdant, resultat, lien_detail, tournoi =(
            "NA",
            "NA",
            "NA",
            "NA",
            "NA",
        )
        
    return Matchs(
        date=date,
        stage=stage,
        nom_vainqueur=nom_vainqueur,
        nom_perdant=nom_perdant,
        score=score,
        resultat=resultat,
        lien_detail=lien_detail,
        tournoi=tournoi,
        type_terrain=type_terrain,
    ), tournoi, type_terrain
    
def filtre_no_tour_head(ligne) -> tuple:
    """
    Extrait les informations d'une ligne HTML pour un match sans détails sur le tournoi.

    Args:
        ligne (BeautifulSoup): Élément HTML représentant une ligne `<tr>` contenant les informations du match.

    Returns:
        tuple: Une tuple contenant :
            - date (str): Date du match.
            - stage (str): Phase du tournoi (par exemple, finale, demi-finale).
            - nom_vainqueur (str): Nom du joueur vainqueur.
            - nom_perdant (str): Nom du joueur perdant.
            - score (str): Score du match.
            - resultat (str): Résultat du match (par exemple, "victoire" ou "défaite").
            - lien_detail (str): Lien vers les détails du match.
    """
    
    (
        date, stage, _, _, score, _, _
    ) = [td.text.strip() for td in ligne.find_all("td")]

    try:
        nom_vainqueur = ligne.find_all("b")[0].text.strip()
        nom_perdant = ligne.find_all("a")[0].text.strip()
        resultat = ligne.find_all("img")[0]["alt"]
        lien_detail = ligne.find_all("a")[1]["href"]
        
    except (IndexError, AttributeError):
        nom_vainqueur, nom_perdant, resultat, lien_detail =(
            "NA",
            "NA",
            "NA",
            "NA",
        )
        
    return date, stage, nom_vainqueur, nom_perdant, score, resultat, lien_detail

def genere_derniers_matchs(ligne_derniers_matchs):
    """
    Génère une liste des derniers matchs à partir des lignes HTML d'une table.

    Args:
        ligne_derniers_matchs (list): Liste d'éléments HTML représentant les lignes `<tr>` d'une table de matchs.

    Returns:
        list: Une liste d'objets `Matchs`, chacun représentant un match avec les informations suivantes :
            - date (str): Date du match.
            - stage (str): Phase du tournoi (par exemple, finale, demi-finale).
            - nom_vainqueur (str): Nom du joueur vainqueur.
            - nom_perdant (str): Nom du joueur perdant.
            - score (str): Score du match.
            - resultat (str): Résultat du match (par exemple, victoire, défaite).
            - lien_detail (str): Lien vers les détails du match.
            - tournoi (str): Nom du tournoi associé au match.
            - type_terrain (str): Type de terrain sur lequel le match a été joué.
    """

    tournoi_precedent = ""
    type_terrain_precedent = ""
    
    matchs = []
    for ligne in ligne_derniers_matchs:
        if "tour_head" in ligne["class"]:
            match, tournoi_precedent, type_terrain_precedent = filtre_tour_head(ligne)
            matchs.append(match)
            
        elif "pair" in ligne["class"] or "unpair" in ligne["class"]:
            date, stage, nom_vainqueur, nom_perdant, score, resultat, lien_detail = filtre_no_tour_head(ligne)

            tournoi = tournoi_precedent
            type_terrain = type_terrain_precedent

            match = Matchs(
                date=date,
                stage=stage,
                nom_vainqueur=nom_vainqueur,
                nom_perdant=nom_perdant,
                score=score,
                resultat=resultat,
                lien_detail=lien_detail,
                tournoi=tournoi,
                type_terrain=type_terrain
            )
            matchs.append(match)
            
    return matchs

ligne_derniers_matchs = extraire_lignes(derniers_match)
Sinner_derniers_matchs = genere_derniers_matchs(ligne_derniers_matchs)

file_path_profil: str = os.path.join(current_dir, "donnees", "profil_sinner.json")
with open(file_path_profil, "w") as fichier:
    fichier.write(
        json.dumps(
            [Sinner_profil.__dict__], ensure_ascii=False, indent=4
        )
    )
    
file_path_statistiques: str = os.path.join(current_dir, "donnees", "stats_sinner.json")
with open(file_path_statistiques, "w") as fichier:
    fichier.write(
        json.dumps(
            [stats.__dict__ for stats in Sinner_statistiques], ensure_ascii=False, indent=4
        )
    )
    
file_path_matchs: str = os.path.join(current_dir, "donnees", "matchs_sinner.json")
with open(file_path_matchs, "w") as fichier:
    fichier.write(
        json.dumps(
            [match.__dict__ for match in Sinner_derniers_matchs], ensure_ascii=False, indent=4
        )
    )