import os
from google import genai
from google.genai import types
from backend.models import TripAllocation
from dotenv import load_dotenv

# Charge la clé API depuis le fichier .env
load_dotenv()

# Initialisation du nouveau client Gemini
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def determine_stay_durations(cities: list[str], total_days: int, user_preferences: str) -> TripAllocation:
    """
    Demande à Gemini de répartir les jours de voyage selon les villes et les préférences.
    """
    prompt = f"""
    Un client veut faire un voyage de {total_days} jours.
    Il veut visiter les villes suivantes : {', '.join(cities)}.
    Voici ses préférences : "{user_preferences}"
    
    Répartis le nombre de jours idéal pour chaque ville. 
    La somme des 'recommended_days' DOIT être exactement égale à {total_days}.
    Prends en compte les préférences du client pour justifier la durée avec un raisonnement court et précis.
    """

    # Appel à l'API avec la nouvelle syntaxe google-genai
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="Tu es un planificateur de voyage algorithmique. Ton but est d'optimiser le temps passé dans chaque ville.",
            response_mime_type="application/json",
            response_schema=TripAllocation,
            temperature=0.2 # Température basse pour un résultat plus analytique
        )
    )

    # Validation et transformation du JSON brut en objet Python via Pydantic
    return TripAllocation.model_validate_json(response.text)