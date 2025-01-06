from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List
import logging

logger: logging.Logger = logging.getLogger(__name__)
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
    logger.debug("Extraction des colonnes de la table...")
    try:
        colonnes = [td.text.strip() for td in table.find_all("td")]
        logger.debug(f"{len(colonnes)} colonnes extraites.")
        return colonnes
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction des colonnes : {e}")
        return []

def lignes_statistiques(table_data: List[str]) -> dict:
    """
    Sépare les données de la table en groupes de 3 éléments et les stocke dans un dictionnaire.
    """
    logger.debug("Séparation des données en groupes de 3 éléments.")
    stats_dict = {}
    try:
        for i in range(0, len(table_data), 3):
            key = table_data[i]
            values = table_data[i + 1:i + 3]
            stats_dict[key] = values
        logger.debug(f"Statistiques extraites : {stats_dict}")
    except Exception as e:
        logger.error(f"Erreur lors de la séparation des données : {e}")
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