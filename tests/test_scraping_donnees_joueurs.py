from bs4 import BeautifulSoup
from src.scraping.scrap_page_joueur import (genere_profil, 
                                            extraire_lignes,
                                            genere_statistiques_dict,
                                            genere_statistiques_agregrees,
                                            filtre_tour_head,
                                            filtre_no_tour_head,
                                            genere_derniers_matchs,
                                            Profil, Matchs)
     
def test_genere_profil_complet():
    html = """
    <div class="player_stats">
        Nom: <b><a href="https://www.tennisendirect.net/atp/novak-djokovic/" title="Novak Djokovic">Novak Djokovic</a></b><br>
        Pays: <b>Serbia</b><br>
        Date de naissance: <b>22.05.87, 37 ans</b><br>
        Taille: <b>187 cm</b><br>
        Poids: <b>80 kg</b><br>
        Début pro: <b>2003</b><br>
        Droitier(e)<br>
        <a href="https://www.tennisendirect.net/atp/classement/" title="Position dans le classement">Classement ATP</a>: <b>7</b><br>
        TOP position dans le classement: <b>1</b> (27.05.24, 9960 points)<br>
        Points: <b>3910</b><br>
        Primes: <b>185065269 $</b><br> 
        Total de matchs: <b>1525</b><br>
        Victoires: <b>1268</b><br>
        Taux de réussite: <b>83.15 %</b><br>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")
    profil = genere_profil([soup.div])
    attendu = Profil(
        nom="Novak Djokovic",
        pays="Serbia",
        date_naissance="22.05.87",
        age="37",
        classement_atp="7",
        points="3910",
        primes="185065269",
        total_match="1525",
        victoires="1268",
        taux_reussite="83.15",
    )
    assert profil == attendu

def test_genere_profil_incomplet():
    html = """
    <div class="player_stats">
        Nom: <b><a href="https://www.tennisendirect.net/atp/novak-djokovic/" title="Novak Djokovic">Novak Djokovic</a></b><br>
        Pays: <b>Serbia</b><br>
        
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")
    profil = genere_profil([soup.div])
    attendu = Profil(
        nom="NA",
        pays="NA",
        date_naissance="NA",
        age="NA",
        classement_atp="NA",
        points="NA",
        primes="NA",
        total_match="NA",
        victoires="NA",
        taux_reussite="NA",
    )
    assert profil == attendu

def test_extraire_lignes():
    html = """
    <table>
        <tr class="pair"><td>1</td></tr>
        <tr class="unpair"><td>2</td></tr>
        <tr class="pair"><td>3</td></tr>
    </table>
    """
    soup = BeautifulSoup(html, "html.parser")
    lignes = extraire_lignes(soup.table)
    assert len(lignes) == 3
    assert all(ligne.get("class")[0] in ["pair", "unpair"] for ligne in lignes)

def test_genere_statistiques_dict():
    html = """
    <tr>
        <td>2023</td>
        <td>50-10</td>
        <td>30-5</td>
        <td>10-2</td>
        <td>5-1</td>
        <td>2-1</td>
        <td>3-1</td>
        <td>0-0</td>
    </tr>
    """
    soup = BeautifulSoup(html, "html.parser")
    stats = genere_statistiques_dict(soup.tr)
    attendu = {
        "2023_sommaire": "50-10",
        "2023_dure": "30-5",
        "2023_terre_battue": "10-2",
        "2023_salle": "5-1",
        "2023_carpet": "2-1",
        "2023_gazon": "3-1",
        "2023_acryl": "0-0",
    }
    assert stats == attendu

def test_genere_statistiques_agregrees():
    html = """
    <tr>
        <td>2023</td>
        <td>50-10</td>
        <td>30-5</td>
        <td>10-2</td>
        <td>5-1</td>
        <td>2-1</td>
        <td>3-1</td>
        <td>0-0</td>
    </tr>
    <tr>
        <td>2022</td>
        <td>40-15</td>
        <td>25-10</td>
        <td>15-5</td>
        <td>10-0</td>
        <td>5-1</td>
        <td>2-1</td>
        <td>1-0</td>
    </tr>
    """
    soup = BeautifulSoup(html, "html.parser")
    lignes = soup.find_all("tr")
    agregats = genere_statistiques_agregrees(lignes)
    attendu = {
        "2023_sommaire": "50-10",
        "2023_dure": "30-5",
        "2023_terre_battue": "10-2",
        "2023_salle": "5-1",
        "2023_carpet": "2-1",
        "2023_gazon": "3-1",
        "2023_acryl": "0-0",
        "2022_sommaire": "40-15",
        "2022_dure": "25-10",
        "2022_terre_battue": "15-5",
        "2022_salle": "10-0",
        "2022_carpet": "5-1",
        "2022_gazon": "2-1",
        "2022_acryl": "1-0",
    }
    assert agregats == attendu

def test_filtre_tour_head():
    html = """
    <tr class="tour_head pair">
        <td class="w50" align="center">13.10.24</td>
        <td class="w50" align="center">Finale</td>
        <td class="w130"><a href="https://www.tennisendirect.net/atp/jannik-sinner/" title="">Jannik Sinner</a></td><td class="w130"><b>Novak Djokovic</b></td>
        <td class="w130">7-6<sup>4</sup>, 6-3  </td>
        <td class="w16"><img src="https://www.tennisendirect.net/styles/images/ko.gif" width="15" height="15" alt="défaite" /></td>
        <td class="w50" align="center"><a href="https://www.tennisendirect.net/atp/match/jannik-sinner-VS-novak-djokovic/shanghai-rolex-masters-shanghai-2024/" title="détail du match">détail du match</a></td>
        <td rowspan="6" class="w200"><img src="https://www.tennisendirect.net/flags/flag_china.png" alt="China" width="16" height="16" /> <a href="https://www.tennisendirect.net/hommes/shanghai-rolex-masters-shanghai-2024/" title="Shanghai Rolex Masters - Shanghai / $10.2M">Shanghai </a></td><td rowspan="6" class="w40 surf_1">dure</td>
    </tr>
    """
    soup = BeautifulSoup(html, "html.parser")
    match, tournoi, type_terrain = filtre_tour_head(soup.tr)
    attendu = Matchs(
        date="13.10.24",
        stage="Finale",
        nom_joueur="NA",
        nom_opposant="NA",
        score="6-4 6-4",
        resultat="NA",
        lien_detail_match="NA",
        tournoi="NA",
        type_terrain="Hard",
    )
    assert match == attendu
"""
    <tr class="tour_head pair">
        <td class="w50" align="center">13.10.24</td
        <td class="w50" align="center">Finale</td>
        <td class="w130"><a href="https://www.tennisendirect.net/atp/jannik-sinner/" title="">Jannik Sinner</a></td><td class="w130"><b>Novak Djokovic</b></td>
        <td class="w130">7-6<sup>4</sup>, 6-3  </td>
        <td class="w16"><img src="https://www.tennisendirect.net/styles/images/ko.gif" width="15" height="15" alt="défaite" /></td>
        <td class="w50" align="center"><a href="https://www.tennisendirect.net/atp/match/jannik-sinner-VS-novak-djokovic/shanghai-rolex-masters-shanghai-2024/" title="détail du match">détail du match</a></td>
        <td rowspan="6" class="w200"><img src="https://www.tennisendirect.net/flags/flag_china.png" alt="China" width="16" height="16" /> <a href="https://www.tennisendirect.net/hommes/shanghai-rolex-masters-shanghai-2024/" title="Shanghai Rolex Masters - Shanghai / $10.2M">Shanghai </a></td><td rowspan="6" class="w40 surf_1">dure</td>
    </tr>
    <tr class=" unpair"><td class="w50" align="center">12.10.24</td>
        <td class="w50" align="center">Demi-finale</td><td class="w130"><b>Novak Djokovic</b></td>
        <td class="w130"><a href="https://www.tennisendirect.net/atp/taylor-harry-fritz/" title="">Taylor Harry Fritz</a></td>
        <td class="w130">6-4, 7-6<sup>6</sup>  </td>
        <td class="w16"><img src="https://www.tennisendirect.net/styles/images/ok.gif" width="15" height="15" alt="victoire" /></td>
        <td class="w50" align="center"><a href="https://www.tennisendirect.net/atp/match/novak-djokovic-VS-taylor-harry-fritz/shanghai-rolex-masters-shanghai-2024/" title="détail du match">détail du match</a></td>
    </tr>
    """
def test_genere_derniers_matchs():
    html = """
    <tr class="tour_head pair">
        <td class="w50" align="center">13.10.24</td>
        <td class="w50" align="center">Finale</td>
        <td class="w130"><a href="https://www.tennisendirect.net/atp/jannik-sinner/" title="">Jannik Sinner</a></td><td class="w130"><b>Novak Djokovic</b></td>
        <td class="w130">7-6<sup>4</sup>, 6-3  </td>
        <td class="w16"><img src="https://www.tennisendirect.net/styles/images/ko.gif" width="15" height="15" alt="défaite" /></td>
        <td class="w50" align="center"><a href="https://www.tennisendirect.net/atp/match/jannik-sinner-VS-novak-djokovic/shanghai-rolex-masters-shanghai-2024/" title="détail du match">détail du match</a></td>
        <td rowspan="6" class="w200"><img src="https://www.tennisendirect.net/flags/flag_china.png" alt="China" width="16" height="16" /> <a href="https://www.tennisendirect.net/hommes/shanghai-rolex-masters-shanghai-2024/" title="Shanghai Rolex Masters - Shanghai / $10.2M">Shanghai </a></td><td rowspan="6" class="w40 surf_1">dure</td></tr>
    <tr class=" unpair"><td class="w50" align="center">12.10.24</td>
        <td class="w50" align="center">Demi-finale</td>
        <td class="w130"><b>Novak Djokovic</b></td>
        <td class="w130"><a href="https://www.tennisendirect.net/atp/taylor-harry-fritz/" title="">Taylor Harry Fritz</a></td>
        <td class="w130">6-4, 7-6<sup>6</sup>  </td>
        <td class="w16"><img src="https://www.tennisendirect.net/styles/images/ok.gif" width="15" height="15" alt="victoire" /></td>
        <td class="w50" align="center"><a href="https://www.tennisendirect.net/atp/match/novak-djokovic-VS-taylor-harry-fritz/shanghai-rolex-masters-shanghai-2024/" title="détail du match">détail du match</a></td>
    </tr>
    """
    soup = BeautifulSoup(html, "html.parser")
    lignes = soup.find_all("tr")
    matchs = genere_derniers_matchs(lignes)
    assert len(matchs) == 2
    assert matchs[0].stage == "Finale"
    assert matchs[1].stage == "Demi-finale"
