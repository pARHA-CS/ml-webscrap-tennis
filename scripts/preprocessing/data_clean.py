import json

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

# Charger le fichier JSON
input_file = "data/stats_matchs.json"
output_file = "data/stats_matchs_cleaned.json"

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Nettoyer les données
cleaned_data = replace_empty_values_with_na(data)

# Sauvegarder les données nettoyées
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(cleaned_data, f, ensure_ascii=False, indent=4)

print(f"Fichier nettoyé sauvegardé dans {output_file}")
