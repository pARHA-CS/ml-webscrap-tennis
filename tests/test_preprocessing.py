from src.preprocessing.preprocessing import (
    calculate_win_rates,
    calculate_surface_stats,
    prepare_match_data,
    create_training_dataset
)
import pytest
def test_calculate_win_rates():
    matches = [
        {"resultat": "victoire", "score": "6-3, 6-4"},
        {"resultat": "victoire", "score": "7-6, 4-6, 6-3"},
        {"resultat": "défaite", "score": "6-7, 7-5, 6-4"}
    ]
    win_rates = calculate_win_rates(matches)

    attendu = {
        'win_rate': 2 / 3,
        'win_rate_3_sets': 1 / 2,
        'win_rate_tiebreak': 1 / 2
    }

    assert win_rates == pytest.approx(attendu)

def test_calculate_surface_stats():
    matches = [
        {"type_terrain": "dure", "resultat": "victoire"},
        {"type_terrain": "terre battue", "resultat": "défaite"},
        {"type_terrain": "dure", "resultat": "victoire"},
    ]

    stats = calculate_surface_stats(matches)

    attendu = {
        'total_matches_dure': 2,
        'win_rate_dure': 1.0,
        'total_matches_terre battue': 1,
        'win_rate_terre battue': 0.0,
        'total_matches_gazon': 0,
        'win_rate_gazon': 0,
        'total_matches_salle': 0,
        'win_rate_salle': 0,
        'total_matches_carpet': 0,
        'win_rate_carpet': 0,
        'total_matches_acryl': 0,
        'win_rate_acryl': 0
    }

    assert stats == attendu

def test_prepare_match_data():
    player1_data = {"name": "Player 1", "ranking": 10}
    player2_data = {"name": "Player 2", "ranking": 15}
    match_info = {"type_terrain": "dure", "tournoi": "Australian Open"}

    features = prepare_match_data(player1_data, player2_data, match_info)

    attendu = {
        'player1_name': "Player 1",
        'player1_ranking': 10,
        'player2_name': "Player 2",
        'player2_ranking': 15,
        'surface': "dure",
        'tournament_category': 4
    }

    assert features == attendu

def test_create_training_dataset():
    joueurs_data = [{"nom_joueur": "Player 1", "rank": "1"}, {"nom_joueur": "Player 2", "rank": "2"}]
    detail_joueurs = {
        "Player 1": {"matchs": [{"nom_opposant": "Player 2", "type_terrain": "dure", "tournoi": "Australian Open", "resultat": "victoire"}]},
        "Player 2": {"matchs": [{"nom_opposant": "Player 1", "type_terrain": "dure", "tournoi": "Australian Open", "resultat": "défaite"}]}
    }
    stats_matches = {}

    df = create_training_dataset(joueurs_data, detail_joueurs, stats_matches)

    assert df.shape[0] == 1
    assert df.columns == [
        "player1_name", "player1_rank", "player2_name", "player2_rank",
        "surface", "tournament_category", "target"
    ]
