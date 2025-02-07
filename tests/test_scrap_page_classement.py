from src.scraping.scrap_page_classement import extraire_lignes, genere_ligne, Ligne
from bs4 import BeautifulSoup

def test_genere_ligne_valide():
    ligne_html = """
    <tr class="pair">
        <td class="w20">153.</td>
        <td>
            <img 
                src="https://www.tennisendirect.net/flags/flag_spain.png" 
                alt="Spain" 
                width="16" 
                height="16" 
            />
            <a 
                href="https://www.tennisendirect.net/atp/rafael-nadal/" 
                title="Rafael Nadal"
            >
                Rafael Nadal
            </a> 
            (ESP) (38 ans)
        </td>
        <td class="w50">380</td>
    </tr>
    """
    ligne = BeautifulSoup(ligne_html, "html.parser")

    resultat = genere_ligne(ligne)

    attendu = Ligne(
        rank="153.",
        pays="Spain",
        lien_joueur="https://www.tennisendirect.net/atp/rafael-nadal/",
        nom_joueur="Rafael Nadal",
        pays_abreviation="ESP",
        age="38 ans",
        points="380",
    )
    assert resultat == attendu

def test_genere_ligne_invalide_format():
    ligne_html = """
    <tr class="pair">
        <td>1</td>
        <td>Incomplete Data</td>
    </tr>
    """
    ligne = BeautifulSoup(ligne_html, "html.parser")

    resultat = genere_ligne(ligne)

    assert resultat is None

def test_genere_ligne_attributs_manquants():
    ligne_html = """
    <tr class="pair">
        <td class="w20">7.</td>
        <td>
            <img 
                src="https://www.tennisendirect.net/flags/flag_serbia.png" 
                alt="Serbia" 
                width="16" 
                height="16" 
            />
            <a 
                href="https://www.tennisendirect.net/atp/novak-djokovic/" 
                title="Novak Djokovic"
            >
                Novak Djokovic
            </a> 
        </td>
        <td class="w50">3910</td>
    </tr>
    """
    ligne = BeautifulSoup(ligne_html, "html.parser")

    resultat = genere_ligne(ligne)

    attendu = Ligne(
        rank="7.",
        pays="Serbia",
        lien_joueur="https://www.tennisendirect.net/atp/novak-djokovic/",
        nom_joueur="Novak Djokovic",
        pays_abreviation="NA",
        age="NA",
        points="3910",
    )
    assert resultat == attendu

def test_extraire_lignes():
    html = """
    <table>
        <tr class="pair"><td>1</td></tr>
        <tr class="unpair"><td>2</td></tr>
        <tr class="pair"><td>3</td></tr>
        <tr class="unpair"><td>4</td></tr>
        <tr class="other"><td>5</td></tr> <!-- Cette ligne ne doit pas être incluse -->
    </table>
    """
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")

    lignes = extraire_lignes(table)
    assert len(lignes) == 4  

    assert all(ligne.get("class")[0] in ["pair", "unpair"] for ligne in lignes)

    assert not any("other" in ligne.get("class", []) for ligne in lignes)

def test_extraire_lignes_que_pair_et_unpair():
    html = """
    <table>
        <tr class="pair"><td>1</td></tr>
        <tr class="unpair"><td>2</td></tr>
        <tr class="pair"><td>3</td></tr>
    </table>
    """
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")

    lignes = extraire_lignes(table)

    assert len(lignes) == 3  


def test_extraire_lignes_table_vide():
    html = "<table></table>"
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")

    lignes = extraire_lignes(table)

    assert len(lignes) == 0
