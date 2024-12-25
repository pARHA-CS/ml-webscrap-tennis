import json
import os
import time
from requests import get
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List

@dataclass
class StatsMatch:
    nom_joueur: str
    premier_service: str
    pnts_gagnes_ps: str
    pnts_gagnes_ss: str
    balles_break_gagnees: str
    retours_gagnes: str
    total_points_gagnes: str
    double_fautes: str
    aces: str

def extraire_colonnes(table: BeautifulSoup) -> List[str]:
    """
    Extrait les données des colonnes sous forme de liste de texte brut.
    """
    return [td.text.strip() for td in table.find_all("td")]

def lignes_statistiques(table_data: List[str]) -> dict:
    """
    Sépare les données de la table en groupes de 3 éléments et les stocke dans un dictionnaire.
    La première ligne de chaque groupe est utilisée comme clé.
    """
    stats_dict = {}
    for i in range(0, len(table_data), 3):
        key = table_data[i]
        values = table_data[i + 1:i + 3]
        stats_dict[key] = values
    return stats_dict

def creer_stats_joueur(stats_dict: dict[str, list], index_joueur: int, valeur_par_defaut: str = "NA") -> StatsMatch:
    """
    Crée une instance de StatsMatch pour un joueur donné, avec gestion des clés manquantes.
    stats_dict : dict { clé_statistique : [valeur_joueur1, valeur_joueur2] }
    index_joueur : Index du joueur dans la liste (0 pour le premier joueur, 1 pour le second joueur)
    valeur_par_defaut : Valeur utilisée si une statistique est absente.
    """
    
    cles_attendues = [
        "premier service en pourcentage",
        "Points gagnés sur 1er service",
        "Points gagnés sur 2e service",
        "Balles de break gagnées",
        "Points gagnés sur retour",
        "Total de points gagnés",
        "Double fautes",
        "Aces"
    ]

    nom_joueur = stats_dict.get('', [valeur_par_defaut, valeur_par_defaut])[index_joueur]

    stats = {
        key: stats_dict.get(key, [valeur_par_defaut, valeur_par_defaut])[index_joueur]
        for key in cles_attendues
    }

    return StatsMatch(
        nom_joueur=nom_joueur,
        premier_service=stats.get("premier service en pourcentage", valeur_par_defaut),
        pnts_gagnes_ps=stats.get("Points gagnés sur 1er service", valeur_par_defaut),
        pnts_gagnes_ss=stats.get("Points gagnés sur 2e service", valeur_par_defaut),
        balles_break_gagnees=stats.get("Balles de break gagnées", valeur_par_defaut),
        retours_gagnes=stats.get("Points gagnés sur retour", valeur_par_defaut),
        total_points_gagnes=stats.get("Total de points gagnés", valeur_par_defaut),
        double_fautes=stats.get("Double fautes", valeur_par_defaut),
        aces=stats.get("Aces", valeur_par_defaut)
    )

def creer_stats_pour_deux_joueurs(stats_dict: dict[str, list], valeur_par_defaut: str = "NA") -> tuple[StatsMatch, StatsMatch]:
    """
    Crée deux instances de StatsMatch pour deux joueurs à partir des données extraites.
    """
    stats_joueur_A = creer_stats_joueur(stats_dict, index_joueur=0, valeur_par_defaut=valeur_par_defaut)
    stats_joueur_B = creer_stats_joueur(stats_dict, index_joueur=1, valeur_par_defaut=valeur_par_defaut)

    return stats_joueur_A, stats_joueur_B


current_dir = os.getcwd()
output_file: str = os.path.join(current_dir, "donnees", "stats_matchs.json")

path_detail_joueurs = os.path.join(current_dir, "donnees", "detail_joueurs.json")
with open(path_detail_joueurs, "r") as fichier:
    detail_joueurs = json.load(fichier)
    
liens_match = set()
for key, value in detail_joueurs.items():
    joueur = detail_joueurs[key]
    matchs = joueur['matchs']
    
    for i in range(len(matchs)):
        lien_match = matchs[i]['lien_detail_match']
        liens_match.add(lien_match)
        
id_matchs = {f"match_{i+1}": lien for i, lien in enumerate(liens_match)}

premiers_liens_avec_id = {key: id_matchs[key] for key in list(id_matchs.keys())[:10]}


if os.path.exists(output_file):
    with open(output_file, "r", encoding="utf-8") as fichier:
        try:
            match_data = json.load(fichier)
        except json.JSONDecodeError:
            print(f"Le fichier {output_file} est corrompu ou vide. Il sera remplacé.")
            match_data = {}
else:
    match_data = {}
    
for id_match, lien_match in premiers_liens_avec_id.items():
    print(f"Scraping des données pour {id_match} : {lien_match}...")
    
    try:
        reponse = get(lien_match)
        assert reponse.status_code == 200, f"Erreur HTTP {reponse.status_code}: {lien_match}"
        
        detail_match = BeautifulSoup(reponse.text, features="lxml")
        statistiques = detail_match.find_all("table", attrs={"class": "table_stats_match"})[0]
        
        table_data = extraire_colonnes(statistiques)
        stats_dict = lignes_statistiques(table_data)
        
        # Crée les objets StatsMatch
        stats_joueur_A, stats_joueur_B = creer_stats_pour_deux_joueurs(stats_dict)
        
        match_data[id_match] = {
            "lien_match": lien_match,
            "joueur_gagnant": stats_joueur_A.__dict__,
            "joueur_perdant": stats_joueur_B.__dict__
        }
        
        with open(output_file, "w", encoding="utf-8") as fichier:
            json.dump(match_data, fichier, ensure_ascii=False, indent=4)
        
        print(f"Données de {id_match} sauvegardées.")

    except Exception as e:
        print(f"Erreur lors du traitement de {id_match} : {lien_match} -> {e}")
        
    time.sleep(2)
    
print(f"Tous les matchs ont été traités et sauvegardés dans {output_file}")