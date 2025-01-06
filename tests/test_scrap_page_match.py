from bs4 import BeautifulSoup
from src.scraping.scrap_page_match import (
    extraire_colonnes, 
    lignes_statistiques, 
    creer_stats_joueur, 
    creer_stats_pour_deux_joueurs,
    StatsMatch
)

def test_extraire_colonnes():
    html = """
     <tr class="tour_head"><td width="38%"></td>
        <td width="30%" align="center"><a href="https://www.tennisendirect.net/atp/kokoro-isomura/" title="Kokoro Isomura">Kokoro Isomura</a></td>
        <td width="30%" align="center"><a href="https://www.tennisendirect.net/atp/jurij-rodionov/" title="Jurij Rodionov">Jurij Rodionov</a></td>
     </tr>
     <tr><td width="38%" class="info_txt">premier service en pourcentage </td>
        <td width="30%" align="center">38/71 (54%)</td><td width="30%" align="center">33/59 (56%)</td>
     </tr>
     <tr>
        <td width="38%" class="info_txt">Points gagnés sur 1er service</td>
        <td width="30%" align="center">26/38 (68%)</td><td width="30%" align="center">24/33 (73%)</td>
    </tr>
    <tr>
        <td width="38%" class="info_txt">Points gagnés sur 2e service</td>
        <td width="30%" align="center">22/33 (67%)</td>
        <td width="30%" align="center">14/26 (54%)</td>
    </tr>
    <tr>
        <td width="38%" class="info_txt">Balles de break gagnées</td>
        <td width="30%" align="center">2/9 (22%)</td><td width="30%" align="center">0/5 (0%)</td>
    </tr>
    <tr>
        <td width="38%" class="info_txt">Points gagnés sur retour</td><td width="30%" align="center">21/59 (36%)</td>
        <td width="30%" align="center">23/71 (32%)</td>
    </tr>
    <tr>
        <td width="38%" class="info_txt">Total de points gagnés</td>
        <td width="30%" align="center">69/130 (53%)</td><td width="30%" align="center">61/130 (47%)</td>
    </tr>
    <tr>
        <td width="38%" class="info_txt">Double fautes</td>
        <td width="30%" align="center">6</td><td width="30%" align="center">3</td>
    </tr>
    <tr>
        <td width="38%" class="info_txt">Aces</td>
        <td width="30%" align="center">0</td><td width="30%" align="center">3</td>
    </tr>     
    """
    soup = BeautifulSoup(html, "lxml")
    colonnes = extraire_colonnes(soup)

    attendu = [
        "", "Kokoro Isomura", "Jurij Rodionov",
        "premier service en pourcentage", "38/71 (54%)", "33/59 (56%)",
        "Points gagnés sur 1er service", "26/38 (68%)", "24/33 (73%)",
        "Points gagnés sur 2e service", "22/33 (67%)", "14/26 (54%)",
        "Balles de break gagnées", "2/9 (22%)", "0/5 (0%)",
        "Points gagnés sur retour", "21/59 (36%)", "23/71 (32%)",
        "Total de points gagnés", "69/130 (53%)", "61/130 (47%)",
        "Double fautes", "6", "3",
        "Aces", "0", "3"
    ]

    assert colonnes == attendu

def test_extraire_colonnes_table_vide():
    html = "<table></table>"
    soup = BeautifulSoup(html, "lxml")
    colonnes = extraire_colonnes(soup)

    assert colonnes == []
    
def test_extraire_colonnes_malformed_table():
    html = """
    <table>
        <tr><td></td><td>Valid Data</td></tr>
        <tr><td></td></tr>
    </table>
    """
    soup = BeautifulSoup(html, "lxml")
    colonnes = extraire_colonnes(soup)

    attendu = ["", "Valid Data", ""]
    assert colonnes == attendu


def test_lignes_statistiques():
    table_data = ["Stat A", "Value 1", "Value 2", "Stat B", "Value 3", "Value 4"]
    stats_dict = lignes_statistiques(table_data)

    assert stats_dict == {
        "Stat A": ["Value 1", "Value 2"],
        "Stat B": ["Value 3", "Value 4"],
    }

def test_lignes_statistiques_donnees_incompletes():
    table_data = ["Stat A", "Value 1"]  
    stats_dict = lignes_statistiques(table_data)

    assert stats_dict == {
        "Stat A": ["Value 1"]
    }

def test_lignes_statistiques_incomplete_data():
    table_data = ["Stat A", "Value 1", "Value 2", "Stat B"]
    stats_dict = lignes_statistiques(table_data)

    attendu = {
        "Stat A": ["Value 1", "Value 2"],
        "Stat B": []  
    }
    assert stats_dict == attendu


def test_creer_stats_joueur():
    stats_dict = {
        "premier service en pourcentage": ["60%", "55%"],
        "Points gagnés sur 1er service": ["30", "25"],
        "Points gagnés sur 2e service": ["15", "10"],
        "Balles de break gagnées": ["3/5", "2/4"],
        "Points gagnés sur retour": ["20", "18"],
        "Total de points gagnés": ["65", "53"],
        "Double fautes": ["2", "3"],
        "Aces": ["5", "4"],
        "": ["Joueur A", "Joueur B"]
    }

    stats_joueur = creer_stats_joueur(stats_dict, index_joueur=0)

    attendu = StatsMatch(
        nom_joueur="Joueur A",
        premier_service="60%",
        pnts_gagnes_ps="30",
        pnts_gagnes_ss="15",
        balles_break_gagnees="3/5",
        retours_gagnes="20",
        total_points_gagnes="65",
        double_fautes="2",
        aces="5",
    )

    assert stats_joueur == attendu

def test_creer_stats_joueur_valeurs_manquantes():
    stats_dict = {
        "premier service en pourcentage": ["60%"],
        # Clés manquantes
        "": ["Joueur A"]
    }

    stats_joueur = creer_stats_joueur(stats_dict, index_joueur=0, valeur_par_defaut="NA")

    attendu = StatsMatch(
        nom_joueur="Joueur A",
        premier_service="60%",
        pnts_gagnes_ps="NA",
        pnts_gagnes_ss="NA",
        balles_break_gagnees="NA",
        retours_gagnes="NA",
        total_points_gagnes="NA",
        double_fautes="NA",
        aces="NA",
    )

    assert stats_joueur == attendu
    
def test_creer_stats_joueur_all_missing():
    stats_dict = {}
    stats_joueur = creer_stats_joueur(stats_dict, index_joueur=0, valeur_par_defaut="NA")

    attendu = StatsMatch(
        nom_joueur="NA",
        premier_service="NA",
        pnts_gagnes_ps="NA",
        pnts_gagnes_ss="NA",
        balles_break_gagnees="NA",
        retours_gagnes="NA",
        total_points_gagnes="NA",
        double_fautes="NA",
        aces="NA",
    )

    assert stats_joueur == attendu


def test_creer_stats_pour_deux_joueurs():
    stats_dict = {
        "premier service en pourcentage": ["60%", "55%"],
        "Points gagnés sur 1er service": ["30", "25"],
        "Points gagnés sur 2e service": ["15", "10"],
        "Balles de break gagnées": ["3/5", "2/4"],
        "Points gagnés sur retour": ["20", "18"],
        "Total de points gagnés": ["65", "53"],
        "Double fautes": ["2", "3"],
        "Aces": ["5", "4"],
        "": ["Joueur A", "Joueur B"]
    }

    joueur_A, joueur_B = creer_stats_pour_deux_joueurs(stats_dict)

    attendu_A = StatsMatch(
        nom_joueur="Joueur A",
        premier_service="60%",
        pnts_gagnes_ps="30",
        pnts_gagnes_ss="15",
        balles_break_gagnees="3/5",
        retours_gagnes="20",
        total_points_gagnes="65",
        double_fautes="2",
        aces="5",
    )

    attendu_B = StatsMatch(
        nom_joueur="Joueur B",
        premier_service="55%",
        pnts_gagnes_ps="25",
        pnts_gagnes_ss="10",
        balles_break_gagnees="2/4",
        retours_gagnes="18",
        total_points_gagnes="53",
        double_fautes="3",
        aces="4",
    )

    assert joueur_A == attendu_A
    assert joueur_B == attendu_B
