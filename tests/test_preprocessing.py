from src.preprocessing.preprocessing import (
    calculate_win_rates,
    calculate_surface_stats,
    prepare_match_data,
    create_training_dataset,
    calculate_average_stat_absolue,
    get_tournament_category,
    modify_players,
    replace_empty_values_with_na
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
    
def test_calculate_win_rates_edge_cases():
    matches = []
    win_rates = calculate_win_rates(matches)
    assert win_rates == {'win_rate': 0, 'win_rate_3_sets': 0, 'win_rate_tiebreak': 0}, "Échec pour 0 match"

    matches = [{"resultat": "victoire", "score": "6-4, 6-4"}]
    win_rates = calculate_win_rates(matches)
    assert win_rates == {'win_rate': 1.0, 'win_rate_3_sets': 0, 'win_rate_tiebreak': 0}, "Échec pour aucun tie-break/3 sets"


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
    
def test_calculate_surface_stats_edge_cases():
    matches = []
    stats = calculate_surface_stats(matches)
    attendu = {f'total_matches_{surface}': 0 for surface in ["dure", "terre battue", "gazon", "salle", "carpet", "acryl"]}
    attendu.update({f'win_rate_{surface}': 0 for surface in ["dure", "terre battue", "gazon", "salle", "carpet", "acryl"]})
    assert stats == attendu, "Échec pour 0 match"

    matches = [{"type_terrain": "inconnue", "resultat": "victoire"}]
    stats = calculate_surface_stats(matches)
    assert stats == attendu, "Échec pour une surface inconnue"


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

def test_calculate_average_stat_absolue():
    matches = [
        {"double_fautes": "3"},
        {"double_fautes": "5"},
        {"double_fautes": "NA"},
    ]
    result = calculate_average_stat_absolue(matches, "double_fautes")
    assert result == 4.0, f"Échec : attendu 4.0, obtenu {result}"

    matches = [{"double_fautes": "NA"}]
    result = calculate_average_stat_absolue(matches, "double_fautes")
    assert result == 0, f"Échec : attendu 0, obtenu {result}"

    matches = []
    result = calculate_average_stat_absolue(matches, "double_fautes")
    assert result == 0, f"Échec : attendu 0, obtenu {result}"

def test_get_tournament_category():
    assert get_tournament_category("Australian Open") == 4, "Échec : Grand Slam"
    assert get_tournament_category("Indian Wells") == 3, "Échec : Masters 1000"
    assert get_tournament_category("Rotterdam") == 2, "Échec : ATP 500"
    assert get_tournament_category("Unknown Tournament") == 1, "Échec : ATP 250 par défaut"

def test_modify_players():
    import polars as pl

    data = {
        "player1_name": ["Jannik Sinner"],
        "player2_name": ["Tallon Griekspoor"],
        "target": [1],
    }
    df = pl.DataFrame(data)
    modified_df = modify_players(df)

    assert modified_df.filter(pl.col("target") == 0).shape[0] > 0, "Échec : les lignes inversées ne sont pas ajoutées"
    assert modified_df.shape[0] > df.shape[0], "Échec : le nombre total de lignes est incorrect"


def test_replace_empty_values_with_na():
    data = {"key1": "", "key2": {"subkey": ""}, "key3": ["", "value"]}
    result = replace_empty_values_with_na(data)
    expected = {"key1": "NA", "key2": {"subkey": "NA"}, "key3": ["NA", "value"]}
    assert result == expected, f"Échec : attendu {expected}, obtenu {result}"

def test_replace_empty_values_with_na_complex():
    data = {
        "key1": "",
        "key2": {"subkey1": "", "subkey2": "valeur"},
        "key3": [{"sublist_key": ""}, {"sublist_key": "value"}],
    }
    result = replace_empty_values_with_na(data)
    attendu = {
        "key1": "NA",
        "key2": {"subkey1": "NA", "subkey2": "valeur"},
        "key3": [{"sublist_key": "NA"}, {"sublist_key": "value"}],
    }
    assert result == attendu, f"Échec pour structure complexe. Résultat : {result}"

def test_pipeline_integration():
    joueurs_data = [{"nom_joueur": "Player 1", "rank": "1"}, {"nom_joueur": "Player 2", "rank": "2"}]
    detail_joueurs = {
        "Player 1": {"matchs": [{"nom_opposant": "Player 2", "type_terrain": "dure", "tournoi": "Australian Open", "resultat": "victoire"}]},
        "Player 2": {"matchs": [{"nom_opposant": "Player 1", "type_terrain": "dure", "tournoi": "Australian Open", "resultat": "défaite"}]}
    }
    stats_matches = {}

    df = create_training_dataset(joueurs_data, detail_joueurs, stats_matches)

    modified_df = modify_players(df)

    assert modified_df.shape[0] == 2, "Échec : le dataset modifié devrait contenir deux lignes"
    assert set(modified_df["target"]) == {1, 0}, "Échec : les cibles devraient inclure 1 et 0"
