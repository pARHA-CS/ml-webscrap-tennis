from dataclasses import dataclass

@dataclass
class Statistiques:
    annee: str
    sommaire: str
    dure: str
    terre_battue: str
    salle: str
    carpet: str
    gazon: str
    acryl: str
    
def genere_statistiques(ligne):
    colonnes = [td.text.strip() for td in ligne.find_all("td")]
    
    if len(colonnes) == 8:
        annee, sommaire, dure, terre_battue, salle, carpet, gazon, acryl = colonnes
    else:
        print("Format inattendu dans la ligne:", colonnes)
        return None

    return Statistiques(
        annee = annee,
        sommaire = sommaire,
        dure = dure,
        terre_battue = terre_battue,
        salle = salle,
        carpet = carpet,
        gazon = gazon,
        acryl = acryl,
    ) 