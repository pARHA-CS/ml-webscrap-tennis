"""Script pour enlever les NA dans stats_matchs.json 

    Return : stats_matchs_cleaned.json
""" 
import json
from src.preprocessing.preprocessing import replace_empty_values_with_na

input_file = "data/stats_matchs.json"
output_file = "data/stats_matchs_cleaned.json"

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

cleaned_data = replace_empty_values_with_na(data)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(cleaned_data, f, ensure_ascii=False, indent=4)

print(f"Fichier nettoyé sauvegardé dans {output_file}")
