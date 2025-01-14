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
        {
            "date": "03.10.24",
            "stage": "1er tour",
            "nom_joueur": "Pedro Martinez Portero",
            "nom_opposant": "Jakub Mensik",
            "score": "6-1, 5-7, 6-4",
            "resultat": "défaite",
            "lien_detail_match": "https://www.tennisendirect.net/atp/match/jakub-mensik-VS-pedro-martinez-portero/shanghai-rolex-masters-shanghai-2024/",
            "tournoi": "Shanghai Rolex Masters - Shanghai / $10.2M",
            "type_terrain": "dure"
        },
        {
            "date": "26.09.24",
            "stage": "1er tour",
            "nom_joueur": "Pedro Martinez Portero",
            "nom_opposant": "Jiri Lehecka",
            "score": "7-6(4), 6-2",
            "resultat": "victoire",
            "lien_detail_match": "https://www.tennisendirect.net/atp/match/jiri-lehecka-VS-pedro-martinez-portero/china-open-beijing-2024/",
            "tournoi": "China Open - Beijing / $3.891M",
            "type_terrain": "dure"
        },
    ]


@pytest.fixture
def sample_player_data():
    return {
        "rank": "48.",
        "pays": "Czech Republic",
        "lien_joueur": "https://www.tennisendirect.net/atp/jakub-mensik/",
        "nom_joueur": "Jakub Mensik",
        "pays_abreviation": "CZE",
        "age": "19 ans",
        "points": "1136"
    }


@pytest.fixture
def sample_stats_matches_data():
    return {
        "match_1": {
            "lien_match": "https://www.tennisendirect.net/atp/match/jakub-mensik-VS-pedro-martinez-portero/shanghai-rolex-masters-shanghai-2024/",
            "joueur_gagnant": {
                "nom_joueur": "Jakub Mensik",
                "premier_service": "53/81 (65%)",
                "pnts_gagnes_ps": "41/53 (77%)",
                "pnts_gagnes_ss": "16/28 (57%)",
                "balles_break_gagnees": "4/6 (67%)",
                "retours_gagnes": "34/81 (42%)",
                "total_points_gagnes": "91/162 (56%)",
                "double_fautes": "4",
                "aces": "14"
            },
            "joueur_perdant": {
                "nom_joueur": "Pedro Martinez Portero",
                "premier_service": "58/81 (72%)",
                "pnts_gagnes_ps": "35/58 (60%)",
                "pnts_gagnes_ss": "12/23 (52%)",
                "balles_break_gagnees": "2/4 (50%)",
                "retours_gagnes": "24/81 (30%)",
                "total_points_gagnes": "71/162 (44%)",
                "double_fautes": "3",
                "aces": "3"
            }
        }
    }


def test_filter_matches_before_date(sample_matches):
    filtered = filter_matches_before_date(sample_matches, "03.10.24")
    assert len(filtered) == 1
    assert filtered[0]["date"] == "26.09.24"


def test_calculate_win_rates(sample_matches):
    win_rates = calculate_win_rates(sample_matches)
    assert win_rates["win_rate"] == 0.5
    assert win_rates["win_rate_3_sets"] == 0.5
    assert win_rates["win_rate_tiebreak"] == 1.0


def test_calculate_surface_stats(sample_matches):
    surface_stats = calculate_surface_stats(sample_matches)
    assert surface_stats["total_matches_dure"] == 2
    assert surface_stats["win_rate_dure"] == 0.5


def test_create_player_features(sample_player_data, sample_matches, sample_stats_matches_data):
    current_match = sample_matches[0]
    player_features = create_player_features(
        sample_player_data, sample_matches, sample_stats_matches_data, current_match
    )
    assert player_features["name"] == "Jakub Mensik"
    assert player_features["age"] == 19
    assert "win_rate" in player_features


def test_extract_stat_percentage():
    assert extract_stat_percentage("50/100 (50%)") == 0.5
    assert extract_stat_percentage("NA") == 0.0
    assert extract_stat_percentage("") == 0.0


def test_calculate_average_stat_ratio(sample_stats_matches_data):
    matches = sample_stats_matches_data.values()
    average = calculate_average_stat_ratio(matches, "premier_service")
    assert average == 0.65


def test_calculate_average_stat_absolue(sample_stats_matches_data):
    matches = sample_stats_matches_data.values()
    average = calculate_average_stat_absolue(matches, "aces")
    assert average == 8.5


def test_get_tournament_category():
    assert get_tournament_category("Roland Garros") == 4
    assert get_tournament_category("ATP Finals") == 3
    assert get_tournament_category("Rotterdam") == 2
    assert get_tournament_category("Unknown") == 1


def test_create_training_dataset(sample_player_data, sample_matches, sample_stats_matches_data):
    dataset = create_training_dataset(
        sample_player_data,
        {"Jakub Mensik": {"matchs": sample_matches}},
        sample_stats_matches_data
    )
    assert len(dataset) > 0
    assert "player1_name" in dataset.columns
