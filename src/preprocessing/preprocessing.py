"""Module pour creer et changer les datasets
"""

import polars as pl
import numpy as np
import json
import logging
import random
from datetime import datetime
from tqdm import tqdm

logger = logging.getLogger(__name__)


def create_player_features(
    player_data, matches, stats_matches_data, current_match
) -> dict:
    """
    Génère les caractéristiques d'un joueur à partir des données et statistiques disponibles.

    Args:
        player_data (dict): Informations du joueur (nom, âge, classement, points).
        matches (list): Historique des matchs.
        stats_matches_data (list): Statistiques détaillées des matchs.
        current_match (dict): Détails du match en cours (ex. date, surface).

    Returns:
        dict: Caractéristiques du joueur (données de base, taux de victoire, 
        stats par surface, performance).
    """

    logger.info(f"Création des features pour le joueur {player_data['nom_joueur']}.")
    player_features = {
        "name": str(player_data["nom_joueur"]),
        "age": int(player_data["age"].split(" ")[0]),
        "ranking": int(player_data["rank"].replace(".", "")),
        "points": int(player_data["points"]),
    }

    try:
        before_match_date = current_match["date"]
        recent_matches = filter_matches_before_date(matches, before_match_date)

        win_rates = calculate_win_rates(recent_matches)
        player_features.update(win_rates)

        surface_stats = calculate_surface_stats(recent_matches)
        player_features.update(surface_stats)

        performance_stats = calculate_performance_stats(
            stats_matches_data, player_data["nom_joueur"], current_match, matches
        )
        player_features.update(performance_stats.items())

        logger.info(f"Features créées pour le joueur {player_data['nom_joueur']}.")
    except Exception as e:
        logger.error(
            f"Erreur lors de la création des features pour {player_data['nom_joueur']} : {e}"
        )
        raise

    return player_features


def filter_matches_before_date(matches, current_match_date) -> list:
    """
    Filtre les matchs ayant une date antérieure à une date donnée.

    Args:
        matches (list): Liste des matchs.
        current_match_date (str): Date du match actuel au format 'DD.MM.YY'.

    Returns:
        list: Matchs ayant une date antérieure à `current_match_date`.
    """
    try:
        current_date = datetime.strptime(current_match_date, "%d.%m.%y")
        filtered_matches = [
            match
            for match in matches
            if "date" in match
            and datetime.strptime(match["date"], "%d.%m.%y") < current_date
        ]
        return filtered_matches
    except Exception as e:
        logger.error(f"Erreur lors du filtrage des matchs : {e}")
        raise


def calculate_win_rates(matches) -> dict:
    """
    Calcule les taux de victoire globaux.

    Args:
        matches (list): Liste des matchs.

    Returns:
        dict: Taux de victoire globaux ou valeurs par défaut si aucun match.
    """
    if not matches:
        logger.warning("Aucun match disponible pour calculer les taux de victoire.")
        return {"win_rate": 0, "win_rate_3_sets": 0, "win_rate_tiebreak": 0}

    # Calcul des statistiques si des matchs existent
    victories = sum(1 for m in matches if m["resultat"] == "victoire")
    total_matches = len(matches)
    tiebreak_matches = sum(
        1
        for m in matches
        if any(("7-6" or "6-7") in set_score for set_score in m["score"].split(", "))
    )
    three_set_matches = sum(1 for m in matches if len(m["score"].split(", ")) >= 3)

    win_rates = {
        "win_rate": victories / total_matches,
        "win_rate_3_sets": sum(
            1
            for m in matches
            if len(m["score"].split(", ")) >= 3 and m["resultat"] == "victoire"
        )
        / max(1, three_set_matches),
        "win_rate_tiebreak": sum(
            1
            for m in matches
            if (
                any("7-6" in set_score for set_score in m["score"].split(", "))
                and m["resultat"] == "victoire"
            )
            or (
                any("6-7" in set_score for set_score in m["score"].split(", "))
                and m["resultat"] == "défaite"
            )
        )
        / max(1, tiebreak_matches),
    }

    return win_rates


def calculate_surface_stats(matches) -> dict[str, float]:
    """
    Calcule les statistiques liées aux différentes surfaces de terrain pour un ensemble de matchs.

    Args:
        matches (list[dict[str, str]]): Liste des matchs, où chaque match est un dictionnaire contenant :
            - "type_terrain" (str) : La surface de jeu (ex. "dure", "gazon").
            - "resultat" (str) : Le résultat du match (ex. "victoire", "defaite").

    Returns:
        dict[str, float]: Dictionnaire contenant les statistiques pour chaque surface, notamment :
            - "total_matches_<surface>" (int) : Nombre total de matchs joués sur la surface.
            - "win_rate_<surface>" (float) : Taux de victoires (0 si aucun match joué).
    """


    surfaces = ["dure", "terre battue", "gazon", "salle", "carpet", "acryl"]
    stats = {}

    for surface in surfaces:
        if not matches:
            logger.warning("Aucun match disponible pour calculer les taux de victoire.")
            stats[f"win_rate_{surface}"] = 0

        surface_matches = [m for m in matches if m["type_terrain"] == surface]

        total_matches = len(surface_matches)
        stats[f"total_matches_{surface}"] = total_matches

        if surface_matches:
            wins = sum(1 for m in surface_matches if m["resultat"] == "victoire")
            stats[f"win_rate_{surface}"] = wins / total_matches
        else:
            logger.warning(f"Pas de stats pour la surface : {surface}")
            stats[f"win_rate_{surface}"] = 0

    return stats


def get_match_date(match_link, matches) -> datetime | None:
    """
    Récupère la date d'un match spécifique depuis detail_joueurs.json.

    Args:
        player_name (str): Nom du joueur.
        match_link (str): Lien du match.
        detail_joueurs_data (dict): Données détaillées des joueurs.

    Returns:
        datetime: Date du match au format datetime.
    """
    for match in matches:
        if match["lien_detail_match"] == match_link:
            return datetime.strptime(match["date"], "%d.%m.%y")
    return None


def filter_previous_matches(
    player_name: str, 
    current_match_date: datetime, 
    stats_matches_data: dict, 
    matches: list
) -> list:
    """
    Filtre les matchs pour ne garder que ceux antérieurs à une date donnée.

    Args:
        player_name (str): Nom du joueur dont on veut filtrer les matchs.
        current_match_date (datetime): Date du match actuel pour effectuer la comparaison.
        stats_matches_data (dict): Dictionnaire des données des matchs, contenant les informations des joueurs gagnants et perdants.
        matches (list): Liste des matchs, qui contient des liens vers les détails des matchs pour récupérer les dates.

    Returns:
        list: Liste des données des matchs avant la date donnée.
    """
    previous_matches = []

    for match in stats_matches_data.values():
        if match["joueur_gagnant"]["nom_joueur"] == player_name:
            match_date = get_match_date(match["lien_match"], matches)
            if match_date and match_date < current_match_date:
                previous_matches.append(match["joueur_gagnant"])
        elif match["joueur_perdant"]["nom_joueur"] == player_name:
            match_date = get_match_date(match["lien_match"], matches)
            if match_date and match_date < current_match_date:
                previous_matches.append(match["joueur_perdant"])

    return previous_matches



def calculate_performance_stats(
    stats_matches_data: dict, 
    player_name: str, 
    current_match: dict, 
    matches: list
) -> dict:
    """
    Calcule les moyennes des statistiques de performance pour un joueur,
    en ne prenant en compte que les matchs avant le match actuel.

    Args:
        stats_matches_data (dict): Dictionnaire contenant les données des matchs, incluant les statistiques par joueur.
        player_name (str): Nom du joueur à analyser.
        current_match (dict): Détail du match en cours, utilisé pour obtenir la date et les statistiques actuelles.
        matches (list): Liste des matchs d'un joueur, nécessaire pour récupérer la date du match actuel.

    Returns:
        dict: Dictionnaire des statistiques combinées du match actuel et des moyennes des performances du joueur dans les matchs précédents.
    """
    current_match_date = get_match_date(current_match["lien_detail_match"], matches)
    if not current_match_date:
        raise ValueError(
            f"La date du match pour {current_match['lien_detail_match']} est introuvable."
        )

    previous_matches = filter_previous_matches(
        player_name, current_match_date, stats_matches_data, matches
    )

    if not previous_matches:
        logger.warning(
            f"Aucun match trouvé pour {player_name} avant {current_match_date.strftime('%d.%m.%y')}"
        )
        averages = {
            "avg_first_serve_pct": 0,
            "avg_first_serve_won_pct": 0,
            "avg_second_serve_won_pct": 0,
            "avg_return_points_won_pct": 0,
            "avg_break_point_won_pct": 0,
            "avg_double_fautes": 0,
            "avg_aces": 0,
        }
    else:
        averages = {
            "avg_first_serve_pct": calculate_average_stat_ratio(
                previous_matches, "premier_service"
            ),
            "avg_first_serve_won_pct": calculate_average_stat_ratio(
                previous_matches, "pnts_gagnes_ps"
            ),
            "avg_second_serve_won_pct": calculate_average_stat_ratio(
                previous_matches, "pnts_gagnes_ss"
            ),
            "avg_return_points_won_pct": calculate_average_stat_ratio(
                previous_matches, "retours_gagnes"
            ),
            "avg_break_point_won_pct": calculate_average_stat_ratio(
                previous_matches, "balles_break_gagnees"
            ),
            "avg_double_fautes": calculate_average_stat_absolue(
                previous_matches, "double_fautes"
            ),
            "avg_aces": calculate_average_stat_absolue(previous_matches, "aces"),
        }

    stats = {}

    stats.update(averages)
    return stats


def extract_stat_percentage(value) -> float:
    """
    Extrait le pourcentage d'une chaîne au format 'XX/YY (ZZ%)'.
    Args:
        value (str): Chaîne contenant les statistiques.
    Returns:
        int: Pourcentage extrait ou 0 si le format est invalide.
    """
    if not value:
        return 0
    try:
        return float(value.split("(")[-1].split("%")[0].strip()) / 100
    except (IndexError, ValueError):
        return 0


def calculate_average_stat_ratio(matches, stat_key) -> float:
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
                numerator, denominator = map(int, ratio.split("/"))
                total_numerator += numerator
                total_denominator += denominator
            except (ValueError, IndexError):
                logger.error(
                    f"Problème pour la stat : {stat_key}, dans le match : {match}"
                )
                continue

    return total_numerator / total_denominator if total_denominator > 0 else 0


def calculate_average_stat_absolue(matches: list, stat_key: str) -> float|int:
    """
    Calcule la moyenne d'une statistique donnée (absolue) sur une liste de matchs.

    Args:
        matches (list): Liste des matchs contenant les statistiques à analyser.
        stat_key (str): Clé représentant la statistique pour laquelle calculer la moyenne (ex: 'double_fautes').

    Returns:
        float: La moyenne des valeurs de la statistique spécifiée. Retourne 0 si aucune donnée valide n'est trouvée.
    """
    values = []
    for match in matches:
        if match[stat_key] != "NA":
            try:
                percentage = int(match[stat_key])
                values.append(percentage)
            except (ValueError, IndexError):
                logger.error(
                    f"Problème pour la stat : {stat_key}, dans le match : {match}"
                )
                continue

    return np.mean(values) if values else 0



def prepare_match_data(player1_data: dict, player2_data: dict, match_info: dict) -> dict:
    """
    Combine les features des deux joueurs pour un match donné, ainsi que les informations relatives au match.

    Args:
        player1_data (dict): Dictionnaire contenant les données du premier joueur.
        player2_data (dict): Dictionnaire contenant les données du deuxième joueur.
        match_info (dict): Dictionnaire contenant les informations sur le match (surface, tournoi, etc.).

    Returns:
        dict: Un dictionnaire combiné contenant les features des deux joueurs ainsi que les informations du match.
    """
    features = {}
    for key, value in player1_data.items():
        features[f"player1_{key}"] = value

    for key, value in player2_data.items():
        features[f"player2_{key}"] = value

    # Features du match
    features.update(
        {
            "surface": match_info["type_terrain"],
            "tournament_category": get_tournament_category(match_info["tournoi"]),
            "url_match": match_info["lien_detail_match"],
        }
    )
    logger.info(
        f"Les features des joueurs : {player1_data['name']} et {player2_data['name']} sont réussies"
    )

    return features



def get_tournament_category(tournament_name) -> int:
    """
    Détermine la catégorie du tournoi en fonction de son nom.

    Args:
        tournament_name (str): Nom du tournoi.

    Returns:
        int: La catégorie du tournoi (4 = Grand Slam, 3 = Masters ou ATP Finals, 2 = ATP 500, 1 = ATP 250).
    """
    tournament_name = tournament_name.lower()

    if any(
        grand_slam in tournament_name
        for grand_slam in ["australian open", "roland garros", "wimbledon", "u.s. open"]
    ):
        return 4

    elif "atp finals" in tournament_name or "laver cup" in tournament_name:
        return 3

    elif any(
        masters in tournament_name
        for masters in [
            "indian wells",
            "miami",
            "monte carlo",
            "madrid",
            "rome",
            "canada",
            "cincinnati",
            "shanghai",
            "paris",
        ]
    ):
        return 3

    elif any(
        atp_500 in tournament_name
        for atp_500 in [
            "rotterdam",
            "dubai",
            "acapulco",
            "barcelona",
            "queen",
            "halle",
            "hamburg",
            "beijing",
            "tokyo",
            "vienna",
            "basel",
        ]
    ):
        return 2

    else:
        return 1


def load_data(joueurs_file: str, detail_joueurs_file: str, stats_match_file: str):
    """
    Charge les données depuis les fichiers JSON avec gestion explicite de l'encodage.

    Args:
        joueurs_file (str): Le chemin vers le fichier JSON contenant les données des joueurs.
        detail_joueurs_file (str): Le chemin vers le fichier JSON contenant les détails des joueurs.
        stats_match_file (str): Le chemin vers le fichier JSON contenant les données des matchs.

    Returns:
        tuple: Un tuple contenant les trois jeux de données chargés à partir des fichiers :
               - `joueurs_data` (dict) : Données des joueurs.
               - `detail_joueurs` (dict) : Détails des joueurs.
               - `stats_matches` (dict) : Statistiques des matchs.
    """
    logger.info("Chargement des données.")

    with open(joueurs_file, "r", encoding="utf-8") as f:
        joueurs_data = json.load(f)
    with open(detail_joueurs_file, "r", encoding="utf-8") as f:
        detail_joueurs = json.load(f)
    with open(stats_match_file, "r", encoding="utf-8") as f:
        stats_matches = json.load(f)

    logger.info("Données chargées avec succès.")
    return joueurs_data, detail_joueurs, stats_matches



def create_training_dataset(
    joueurs_data: dict, detail_joueurs: dict, stats_matches: dict
) -> pl.DataFrame:
    """
    Crée un dataset d'entraînement à partir des données avec suivi de progression.

    Args:
        joueurs_data (list): Liste des données des joueurs.
        detail_joueurs (dict): Dictionnaire contenant les détails des joueurs et leurs matchs.
        stats_matches (dict): Dictionnaire contenant les statistiques des matchs.

    Returns:
        pl.DataFrame: DataFrame contenant les features des matchs avec la cible (1 ou 0 pour la victoire/perte).
    """
    logger.info("Début de la création du dataset d'entraînement.")
    dataset = []

    for player_name, player_details in tqdm(
        detail_joueurs.items(), desc="Traitement des joueurs", unit="joueur"
    ):
        logger.info(f"Traitement du joueur : {player_name}")

        player_base = next(
            (j for j in joueurs_data if j["nom_joueur"] == player_name), None
        )
        if not player_base:
            logger.warning(
                f"Joueur non trouvé dans les données de base : {player_name}"
            )
            continue

        for match in player_details["matchs"]:
            opponent_name = match["nom_opposant"]
            logger.debug(
                f"Traitement du match contre {opponent_name} pour le joueur {player_name}."
            )

            opponent_base = next(
                (j for j in joueurs_data if j["nom_joueur"] == opponent_name), None
            )
            if not opponent_base:
                logger.warning(f"Adversaire non trouvé : {opponent_name}")
                continue

            opponent_details = next(
                (
                    details
                    for name, details in detail_joueurs.items()
                    if details["profil"]["nom"] == opponent_name
                ),
                None,
            )
            if not opponent_details:
                logger.warning(f"Détails manquants pour l'adversaire : {opponent_name}")
                continue

            try:
                player_features = create_player_features(
                    player_base, player_details["matchs"], stats_matches, match
                )

                opponent_features = create_player_features(
                    opponent_base, opponent_details["matchs"], stats_matches, match
                )

                match_info = {
                    "type_terrain": match["type_terrain"],
                    "tournoi": match["tournoi"],
                    "lien_detail_match": match["lien_detail_match"],
                }

                features = prepare_match_data(
                    player_features, opponent_features, match_info
                )
                features["target"] = 1 if match["resultat"] == "victoire" else 0
                features["date"] = match["date"]
                dataset.append(features)

            except Exception as e:
                logger.error(
                    f"Erreur lors du traitement du match {match['date']} entre {player_name} et {opponent_name} : {e}"
                )
                continue

    logger.info("Création du dataset terminée.")

    df = pl.DataFrame(dataset)
    return df


def select_percentage(df) -> float:
    """
    Cette fonction calcule le nombre de ligne à selctionner pour rééquilibrer le dataframe

    Args:
        df : DataFrame Polars d'entrée

    Returns:
        int: le nombre de ligne à sélectionner pour équilibrer le dataframe
    """
    inds_0 = df.filter(df["target"] == 0).shape[0]
    inds_1 = df.filter(df["target"] == 1).shape[0]
    inds = tuple((inds_0, inds_1))

    mean_ind = int(np.mean(inds))
    print(f"moyenne = {mean_ind}")
    print(f"le max = {max(inds)}")

    nb_select = round(max(inds) - mean_ind, 0)
    print(f"nombre de ligne à changer {nb_select}")

    percentage = nb_select / inds_1
    print(f"pourcentage de ligne {percentage}")

    return percentage


def modify_players(df) -> pl.DataFrame:
    """
    Cette fonction modifie aléatoirement un pourcentage de lignes du DataFrame où target == 1.
    Les colonnes des joueurs 1 et 2 sont inversées sur ces lignes sélectionnées.

    Parameters:
    - df : DataFrame Polars d'entrée
    - percentage : pourcentage de lignes à sélectionner et modifier (0-1)

    Returns:
    - df_final : DataFrame modifié avec les lignes sélectionnées et inversées ajoutées
    """

    # Étape 0 : Ajouter l'index des lignes
    df_with_index = df.with_row_index()

    # Étape 1 : Sélectionner un pourcentage de lignes avec target == 1
    df_target_1 = df_with_index.filter(pl.col("target") == 1)

    # Récupération des indices
    index = df_target_1.select(pl.col("index")).to_numpy().flatten().tolist()

    # Calculer le nombre de lignes à sélectionner
    row_selected_pct = select_percentage(df)
    num_to_select = int(len(index) * row_selected_pct)

    # Sélectionner aléatoirement les indices
    selected_indices = random.sample(index, num_to_select)

    # Étape 2 : Sélectionner les lignes avec les indices collectés
    df_selected = df_with_index.filter(pl.col("index").is_in(selected_indices))

    # Étape 3 : Inverser les données des joueurs 1 et 2 sur la sélection dans le nouveau dataframe
    columns_to_swap = [
        col for col in df_selected.columns if "player1" in col or "player2" in col
    ]

    swap_expressions = []
    for col in columns_to_swap:
        if "player1" in col:
            swap_expressions.append(
                pl.col(col).alias(col.replace("player1", "player2"))
            )
        elif "player2" in col:
            swap_expressions.append(
                pl.col(col).alias(col.replace("player2", "player1"))
            )

    # Appliquer les modifications sur le DataFrame sélectionné
    df_selected_swapped = df_selected.with_columns(swap_expressions)

    df_selected_swapped = df_selected_swapped.with_columns(
        pl.lit(0).cast(pl.Int64).alias("target")
    )

    # Étape 4 : Supprimer les lignes avec les indices récupérés dans le df initial
    df_without_selected = df_with_index.filter(~pl.col("index").is_in(selected_indices))

    # Ajouter les lignes modifiées du DataFrame sélectionné à celui d'origine
    df_final = df_without_selected.vstack(df_selected_swapped)

    return df_final


def replace_empty_values_with_na(data):
    """
    Remplace toutes les valeurs vides dans un dictionnaire JSON par 'NA'.

    Args:
        data (dict | list | str): Les données JSON à nettoyer.

    Returns:
        dict | list | str: Les données nettoyées.
    """
    if isinstance(data, dict):
        return {key: replace_empty_values_with_na(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [replace_empty_values_with_na(item) for item in data]
    elif data == "":
        return "NA"
    else:
        return data


def invert_match(row: dict) -> dict:
    """
    Inverse les informations d'un match en échangeant les données des deux joueurs et en inversant la cible.

    Args:
        row (dict): Une ligne représentant un match, incluant les caractéristiques des deux joueurs et la cible.

    Returns:
        dict: Une nouvelle ligne avec les données des joueurs inversées et la cible modifiée.
    """
    inverted_row = row.copy()
    for col in row.keys():
        if col.startswith("player1_"):
            inverted_row[col.replace("player1_", "player2_")] = row[col]
        elif col.startswith("player2_"):
            inverted_row[col.replace("player2_", "player1_")] = row[col]
    inverted_row["target"] = 1 - row["target"]
    return inverted_row
