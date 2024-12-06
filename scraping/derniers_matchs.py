from dataclasses import dataclass
from typing import Tuple


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


def filtre_tour_head(ligne) -> Tuple[Matchs, str, str]:
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