import os
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from models import TripAllocation
from dotenv import load_dotenv

# Charge la clé API depuis le fichier .env
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def determine_stay_durations(cities: list[str], total_days: int, user_preferences: str) -> TripAllocation:

    # Demande à Gemini de répartir les jours de voyage selon les villes et les préférences.
    
    # Initialisation du modèle Pro, idéal pour le raisonnement et le respect des contraintes
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        system_instruction="Tu es un planificateur de voyage algorithmique. Ton but est d'optimiser le temps passé dans chaque ville."
    )

    prompt = f"""
    Un client veut faire un voyage de {total_days} jours.
    Il veut visiter les villes suivantes : {', '.join(cities)}.
    Voici ses préférences : "{user_preferences}"
    
    Répartis le nombre de jours idéal pour chaque ville. 
    La somme des 'recommended_days' DOIT être exactement égale à {total_days}.
    Prends en compte les préférences du client pour justifier la durée avec un raisonnement court et précis.
    """

    # Appel à l'API en forçant le format de sortie
    response = model.generate_content(
        prompt,
        generation_config=GenerationConfig(
            response_mime_type="application/json",
            response_schema=TripAllocation,
            temperature=0.2 # Température basse pour un résultat plus analytique et constant
        )
    )

    # Gemini renvoie le résultat sous forme de chaîne JSON brute.
    # On utilise Pydantic pour la parser et vérifier qu'elle respecte le contrat.
    return TripAllocation.model_validate_json(response.text)