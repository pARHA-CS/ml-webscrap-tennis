import pytest
from src.preprocessing.preprocessing import (
    create_player_features, filter_matches_before_date, calculate_win_rates,
    calculate_surface_stats, calculate_performance_stats, extract_stat_percentage,
    calculate_average_stat_ratio, calculate_average_stat_absolue,
    prepare_match_data, get_tournament_category, load_data, create_training_dataset
)


@pytest.fixture
def sample_matches():
    return [
        {"date": "01.01.23", "type_terrain": "dure", "resultat": "victoire", "score": "6-3, 7-6"},
        {"date": "02.01.23", "type_terrain": "terre battue", "resultat": "défaite", "score": "3-6, 6-4, 6-7"},
    ]


@pytest.fixture
def sample_player_data():
    return {
        "nom_joueur": "Joueur A",
        "age": "25 ans",
        "rank": "5",
        "points": "1000",
    }


@pytest.fixture
def sample_stats_matches_data():
    return {
        "match_1": {
            "joueur_gagnant": {"nom_joueur": "Joueur A", "premier_service": "60/100"},
            "joueur_perdant": {"nom_joueur": "Joueur B", "premier_service": "50/90"},
        }
    }


def test_filter_matches_before_date(sample_matches):
    filtered = filter_matches_before_date(sample_matches, "02.01.23")
    assert len(filtered) == 1
    assert filtered[0]["date"] == "01.01.23"


def test_calculate_win_rates(sample_matches):
    win_rates = calculate_win_rates(sample_matches)
    assert win_rates["win_rate"] == 0.5
    assert win_rates["win_rate_3_sets"] == 0.0
    assert win_rates["win_rate_tiebreak"] == 1.0


def test_calculate_surface_stats(sample_matches):
    surface_stats = calculate_surface_stats(sample_matches)
    assert surface_stats["total_matches_dure"] == 1
    assert surface_stats["win_rate_dure"] == 1.0
    assert surface_stats["total_matches_terre battue"] == 1
    assert surface_stats["win_rate_terre battue"] == 0.0


def test_create_player_features(sample_player_data, sample_matches, sample_stats_matches_data):
    current_match = {"date": "02.01.23"}
    player_features = create_player_features(
        sample_player_data, sample_matches, sample_stats_matches_data, current_match
    )
    assert player_features["name"] == "Joueur A"
    assert player_features["age"] == 25
    assert "win_rate" in player_features


def test_extract_stat_percentage():
    assert extract_stat_percentage("50/100 (50%)") == 0.5
    assert extract_stat_percentage("NA") == 0.0
    assert extract_stat_percentage("") == 0.0


def test_calculate_average_stat_ratio(sample_stats_matches_data):
    matches = sample_stats_matches_data.values()
    average = calculate_average_stat_ratio(matches, "premier_service")
    assert average == 0.6


def test_calculate_average_stat_absolue(sample_stats_matches_data):
    matches = sample_stats_matches_data.values()
    average = calculate_average_stat_absolue(matches, "premier_service")
    assert average == 0.0  


def test_get_tournament_category():
    assert get_tournament_category("Roland Garros") == 4
    assert get_tournament_category("ATP Finals") == 3
    assert get_tournament_category("Rotterdam") == 2
    assert get_tournament_category("Unknown") == 1


def test_create_training_dataset(sample_player_data, sample_matches, sample_stats_matches_data):
    dataset = create_training_dataset(
        sample_player_data,
        {"Joueur A": {"matchs": sample_matches}},
        sample_stats_matches_data
    )

    assert len(dataset) > 0
    assert "player1_name" in dataset.columns


