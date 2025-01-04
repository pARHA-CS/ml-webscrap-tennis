"""Module pour créer le dataset
"""
import polars as pl
import numpy as np
import json
import logging
from tqdm import tqdm

logger = logging.getLogger(__name__)

def create_player_features(player_data, matches, stats_matches_data):
    """
    Crée les features pour un joueur donné.
    """
    logger.info(f"Création des features pour le joueur {player_data['nom_joueur']}.")
    player_features = {
        'name': str(player_data['nom_joueur']),
        'age': int(player_data['age'].split(" ")[0]),
        'ranking': int(player_data['rank'].replace('.', '')),
        'points': int(player_data['points']),
    }
    
    try:
        recent_matches = [match for match in matches]
        
        win_rates = calculate_win_rates(recent_matches)
        player_features.update(win_rates)

        surface_stats = calculate_surface_stats(recent_matches)
        player_features.update(surface_stats)

        performance_stats = calculate_performance_stats(stats_matches_data, player_data['nom_joueur'])
        player_features.update(performance_stats.items())

        logger.info(f"Features créées pour le joueur {player_data['nom_joueur']}.")
    except Exception as e:
        logger.error(f"Erreur lors de la création des features pour {player_data['nom_joueur']} : {e}")
        raise
    
    return player_features

def calculate_win_rates(matches):
    """
    Calcule les taux de victoire globaux
    """
    logger.info(f"Calcul des taux de victoire pour {len(matches)} matches.")
    if not matches:
        logger.warning("Aucun match disponible pour calculer les taux de victoire.")
        return {'win_rate': 0, 'win_rate_3_sets': 0, 'win_rate_tiebreak': 0}
    
    try:
        victories = sum(1 for m in matches if m['resultat'] == 'victoire')
        total_matches = len(matches)
        tiebreak_matches = sum(
            1 for m in matches if any(('7-6' or '6-7') in set_score for set_score in m['score'].split(', '))
        )
        three_set_matches = sum(1 for m in matches if len(m['score'].split(', ')) >= 3)

        win_rates = {
            'win_rate': victories / total_matches,
            'win_rate_3_sets': sum(
                1 for m in matches if len(m['score'].split(', ')) >= 3 and m['resultat'] == 'victoire'
            ) / max(1, three_set_matches),
            'win_rate_tiebreak': sum(
                1 for m in matches 
                if (any('7-6' in set_score for set_score in m['score'].split(', ')) and m['resultat'] == 'victoire')
                or (any('6-7' in set_score for set_score in m['score'].split(', ')) and m['resultat'] == 'défaite')
            ) / max(1, tiebreak_matches)
        }

        logger.debug(f"Taux de victoire calculés : {win_rates}")
        return win_rates
    except Exception as e:
        logger.error(f"Erreur lors du calcul des taux de victoire : {e}")
        raise

def calculate_surface_stats(matches):
    """
    Calcule les statistiques par surface
    """
    surfaces = ['dure', 'terre battue', 'gazon', 'salle', 'carpet', 'acryl']
    stats = {}
    
    for surface in surfaces:
        surface_matches = [m for m in matches if m['type_terrain'] == surface]
        
        total_matches = len(surface_matches)
        stats[f'total_matches_{surface}'] = total_matches
        
        if surface_matches:
            wins = sum(1 for m in surface_matches if m['resultat'] == 'victoire')
            stats[f'win_rate_{surface}'] = wins / total_matches
        else:
            logger.warning(f"Pas de stats pour la surface : {surface}")
            stats[f'win_rate_{surface}'] = 0
        
    return stats

def calculate_performance_stats(stats_matches_data, player_name):
    """
    Calcule les moyennes des statistiques de performance
    """
    player_matches = []
    for match in stats_matches_data.values():
        if match['joueur_gagnant']['nom_joueur'] == player_name:
            player_matches.append(match['joueur_gagnant'])
        elif match['joueur_perdant']['nom_joueur'] == player_name:
            player_matches.append(match['joueur_perdant'])
    
    if not player_matches:
        logger.warning(f"{player_name} pas reconnue dans le fichier 'stats_matchs.json'")
        return {
            'avg_first_serve_pct': 0,
            'avg_first_serve_won_pct': 0,
            'avg_second_serve_won_pct': 0,
            'avg_return_points_won_pct': 0,
            'avg_break_point_won_pct': 0,
            'avg_double_fautes': 0,
            'avg_aces': 0
        }
    
    stats = {
        'avg_first_serve_pct': calculate_average_stat_ratio(player_matches, 'premier_service'),
        'avg_first_serve_won_pct': calculate_average_stat_ratio(player_matches, 'pnts_gagnes_ps'),
        'avg_second_serve_won_pct': calculate_average_stat_ratio(player_matches, 'pnts_gagnes_ss'),
        'avg_return_points_won_pct': calculate_average_stat_ratio(player_matches, 'retours_gagnes'),
        'avg_break_point_won_pct': calculate_average_stat_ratio(player_matches, 'balles_break_gagnees'),
        'avg_double_fautes': calculate_average_stat_absolue(player_matches, 'double_fautes'),
        'avg_aces': calculate_average_stat_absolue(player_matches, 'aces')
    }
    
    return stats

def calculate_average_stat_ratio(matches, stat_key):
    """
    Calcule la moyenne pondérée d'une statistique donnée à partir des ratios.

    Args:
        matches (list): Liste de dictionnaires représentant les matchs.
        stat_key (str): Clé correspondant à la statistique à analyser.

    Returns:
        float: Moyenne pondérée de la statistique ou 0 si aucune donnée n'est disponible.
    """
    total_numerator = 0
    total_denominator = 0

    for match in matches:
        if stat_key in match and match[stat_key] != "NA":
            try:
                ratio = match[stat_key].split(" ")[0]
                numerator, denominator = map(int, ratio.split('/'))
                total_numerator += numerator
                total_denominator += denominator
            except (ValueError, IndexError):
                logger.error(f"Problème pour la stat : {stat_key}, dans le match : {match}")
                continue

    return total_numerator / total_denominator if total_denominator > 0 else 0


def calculate_average_stat_absolue(matches, stat_key):
    """
    Calcule la moyenne d'une statistique donnée
    """
    values = []
    for match in matches:
        if match[stat_key] != "NA":
            try:
                percentage = int(match[stat_key])
                values.append(percentage)
            except (ValueError, IndexError):
                logger.error(f"Problème pour la stat : {stat_key}, dans le match : {match}")
                continue
            
    return np.mean(values) if values else 0

def prepare_match_data(player1_data, player2_data, match_info):
    """
    Combine les features des deux joueurs pour un match
    """
    features = {}
    for key, value in player1_data.items():
        features[f'player1_{key}'] = value
        
    for key, value in player2_data.items():
        features[f'player2_{key}'] = value
        
    # Features du match
    features.update({
        'surface': match_info['type_terrain'],
        'tournament_category': get_tournament_category(match_info['tournoi'])
    })
    logger.info(f"Les features des joueurs : {player1_data['name']} et {player2_data['name']} sont réussies")
    
    return features

def get_tournament_category(tournament_name):
    """
    Détermine la catégorie du tournoi en fonction de son nom.

    Args:
        tournament_name (str): Nom du tournoi.

    Returns:
        int: La catégorie du tournoi (4 = Grand Slam, 3 = Masters ou ATP Finals, 2 = ATP 500, 1 = ATP 250).
    """
    tournament_name = tournament_name.lower()

    if any(grand_slam in tournament_name for grand_slam in ['australian open', 'roland garros', 'wimbledon', 'us open']):
        return 4
    
    elif 'atp finals' in tournament_name or 'laver cup' in tournament_name:
        return 3
    
    elif any(masters in tournament_name for masters in [
        'indian wells', 'miami', 'monte carlo', 'madrid', 'rome', 
        'canada', 'cincinnati', 'shanghai', 'paris'
    ]):
        return 3

    elif any(atp_500 in tournament_name for atp_500 in [
        'rotterdam', 'dubai', 'acapulco', 'barcelona', 'queen', 
        'halle', 'hamburg', 'beijing', 'tokyo', 'vienna', 'basel'
    ]):
        return 2

    else:
        return 1

def load_data(joueurs_file, detail_joueurs_file, stats_match_file):
    """
    Charge les données depuis les fichiers JSON avec gestion explicite de l'encodage.
    """
    logger.info("Chargement des données.")
    
    with open(joueurs_file, 'r', encoding='utf-8') as f:
        joueurs_data = json.load(f)
    with open(detail_joueurs_file, 'r', encoding='utf-8') as f:
        detail_joueurs = json.load(f)
    with open(stats_match_file, 'r', encoding='utf-8') as f:
        stats_matches = json.load(f)
    
    logger.info("Données chargées avec succès.")
    return joueurs_data, detail_joueurs, stats_matches


def create_training_dataset(joueurs_data, detail_joueurs, stats_matches):
    """
    Crée un dataset d'entraînement à partir des données avec suivi de progression.
    """
    logger.info("Début de la création du dataset d'entraînement.")
    dataset = []
    
    for player_name, player_details in tqdm(detail_joueurs.items(), desc="Traitement des joueurs", unit="joueur"):
        logger.info(f"Traitement du joueur : {player_name}")
        player_base = next((j for j in joueurs_data if j["nom_joueur"] == player_name), None)
        
        if not player_base:
            logger.warning(f"Joueur non trouvé dans les données de base : {player_name}")
            continue
            
        for match in player_details['matchs']:
            opponent_name = match['nom_opposant']
            logger.debug(f"Traitement du match contre {opponent_name} pour le joueur {player_name}.")
            
            opponent_base = next((j for j in joueurs_data if j["nom_joueur"] == opponent_name), None)
            if not opponent_base:
                logger.warning(f"Adversaire non trouvé : {opponent_name}")
                continue
                
            opponent_details = next((details for name, details in detail_joueurs.items() 
                                if details['profil']['nom'] == opponent_name), None)
            if not opponent_details:
                logger.warning(f"Détails manquants pour l'adversaire : {opponent_name}")
                continue
                
            try:
                player_features = create_player_features(
                    player_base,
                    player_details['matchs'],
                    stats_matches,
                )
                
                opponent_features = create_player_features(
                    opponent_base,
                    opponent_details['matchs'],
                    stats_matches,
                )
                
                match_info = {
                    'type_terrain': match['type_terrain'],
                    'tournoi': match['tournoi']
                }
                
                features = prepare_match_data(player_features, opponent_features, match_info)
                features['target'] = 1 if match['resultat'] == 'victoire' else 0
                dataset.append(features)
                
            except Exception as e:
                logger.error(f"Erreur lors du traitement du match {match['date']} entre {player_name} et {opponent_name} : {e}")
                continue
    
    logger.info("Création du dataset terminée.")
    
    df = pl.DataFrame(dataset)
    return df



