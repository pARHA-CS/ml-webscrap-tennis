from dataclasses import dataclass
from typing import Tuple

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
    nom_joueur: str
    nom_opposant: str
    score: str
    resultat: str
    lien_detail_match: str
    tournoi: str
    type_terrain :str
    
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
        age = div.find_all("b")[2].text.strip().split(", ")[1].split(" ")[0]
        classement_atp = div.find_all("b")[3].text.strip()
        points = div.find_all("b")[5].text.strip()
        primes = div.find_all("b")[6].text.strip().split(" ")[0]
        total_match = div.find_all("b")[7].text.strip()
        victoires = div.find_all("b")[8].text.strip()
        taux_reussite = div.find_all("b")[9].text.strip().split(" ")[0]
    
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
    
def genere_statistiques_dict(ligne):
    """
    Génère un dictionnaire de statistiques annuelles à partir d'une ligne HTML.

    Args:
        ligne (BeautifulSoup): Élément HTML représentant une ligne `<tr>` contenant les statistiques.

    Returns:
        dict: Dictionnaire avec des clés du type 'annee_statistique' et des valeurs correspondantes.
    """
    colonnes = [td.text.strip() for td in ligne.find_all("td")]
    
    if len(colonnes) == 8:
        annee, sommaire, dure, terre_battue, salle, carpet, gazon, acryl = colonnes
    else:
        print("Format inattendu dans la ligne:", colonnes)
        return None

    return {
        f"{annee}_sommaire": sommaire,
        f"{annee}_dure": dure,
        f"{annee}_terre_battue": terre_battue,
        f"{annee}_salle": salle,
        f"{annee}_carpet": carpet,
        f"{annee}_gazon": gazon,
        f"{annee}_acryl": acryl
    }

def generer_statistiques_agregrees(lignes_stats):
    """
    Agrège les statistiques d'un joueur en un seul dictionnaire.

    Args:
        lignes_stats (list): Liste des lignes contenant les statistiques d'un joueur.

    Returns:
        dict: Dictionnaire contenant toutes les statistiques agrégées du joueur.
    """
    aggregated_stats = {}

    for ligne in lignes_stats:
        stats = genere_statistiques_dict(ligne)
        if stats:
            aggregated_stats.update(stats)

    return aggregated_stats

   
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
        nom_joueur = ligne.find_all("b")[0].text.strip()
        nom_opposant = ligne.find_all("a")[0].text.strip()
        resultat = ligne.find_all("img")[0]["alt"]
        lien_detail_match = ligne.find_all("a")[1]["href"]
        tournoi = ligne.find_all("a")[2]["title"]
    
    except (IndexError, AttributeError):
        nom_joueur, nom_opposant, resultat, lien_detail_match, tournoi =(
            "NA",
            "NA",
            "NA",
            "NA",
            "NA",
        )
        
    return Matchs(
        date=date,
        stage=stage,
        nom_joueur=nom_joueur,
        nom_opposant=nom_opposant,
        score=score,
        resultat=resultat,
        lien_detail_match=lien_detail_match,
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
            - nom_opposant (str): Nom du joueur perdant.
            - score (str): Score du match.
            - resultat (str): Résultat du match (par exemple, "victoire" ou "défaite").
            - lien_detail_match (str): Lien vers les détails du match.
    """
    
    (
        date, stage, _, _, score, _, _
    ) = [td.text.strip() for td in ligne.find_all("td")]

    try:
        nom_joueur = ligne.find_all("b")[0].text.strip()
        nom_opposant = ligne.find_all("a")[0].text.strip()
        resultat = ligne.find_all("img")[0]["alt"]
        lien_detail_match = ligne.find_all("a")[1]["href"]
        
    except (IndexError, AttributeError):
        nom_joueur, nom_opposant, resultat, lien_detail_match =(
            "NA",
            "NA",
            "NA",
            "NA",
        )
        
    return date, stage, nom_joueur, nom_opposant, score, resultat, lien_detail_match

def genere_derniers_matchs(ligne_derniers_matchs):
    """
    Génère une liste des derniers matchs à partir des lignes HTML d'une table.

    Args:
        ligne_derniers_matchs (list): Liste d'éléments HTML représentant les lignes `<tr>` d'une table de matchs.

    Returns:
        list: Une liste d'objets `Matchs`, chacun représentant un match avec les informations suivantes :
            - date (str): Date du match.
            - stage (str): Phase du tournoi (par exemple, finale, demi-finale).
            - nom_joueur (str): Nom du joueur vainqueur.
            - nom_perdant (str): Nom du joueur perdant.
            - score (str): Score du match.
            - resultat (str): Résultat du match (par exemple, victoire, défaite).
            - lien_detail_match (str): Lien vers les détails du match.
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
            date, stage, nom_joueur, nom_opposant, score, resultat, lien_detail_match = filtre_no_tour_head(ligne)

            tournoi = tournoi_precedent
            type_terrain = type_terrain_precedent

            match = Matchs(
                date=date,
                stage=stage,
                nom_joueur=nom_joueur,
                nom_opposant=nom_opposant,
                score=score,
                resultat=resultat,
                lien_detail_match=lien_detail_match,
                tournoi=tournoi,
                type_terrain=type_terrain
            )
            matchs.append(match)
            
    return matchs


