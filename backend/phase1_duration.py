import os
from google import genai
from google.genai import types
from models import TripAllocation
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

# À rajouter à la fin de phase1_duration.py

def suggest_additional_cities(existing_cities: list, count_to_add: int, preferences: str) -> list:
    """Demande à l'IA de suggérer des villes supplémentaires selon le profil."""
    
    # Mode Secours direct (au cas où on veut tester sans cramer l'API ou si elle plante)
    backup_cities = ["Rome", "Barcelone", "Prague", "Vienne", "Budapest", "Florence", "Lisbonne"]
    
    prompt = f"""
    Je prévois un voyage en Europe. J'ai déjà prévu de visiter : {', '.join(existing_cities)}.
    J'ai besoin que tu me suggères EXACTEMENT {count_to_add} autres villes logiques à ajouter à ce trajet.
    Mon profil de voyageur : {preferences}.
    
    Règle stricte : Réponds UNIQUEMENT avec les noms des villes séparés par des virgules, rien d'autre.
    """
    
    try:
        # Assure-toi que ton "client" (Google GenAI) est bien initialisé en haut de ton fichier
        from google import genai
        client = genai.Client() # Adapte selon comment tu as initialisé Gemini
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        # Nettoyage de la réponse (ex: "Berlin, Madrid" -> ["Berlin", "Madrid"])
        suggested = [city.strip() for city in response.text.split(',')]
        
        # On s'assure d'avoir le bon nombre et de ne pas proposer une ville déjà prévue
        suggested = [c for c in suggested if c not in existing_cities][:count_to_add]
        
        # Si l'IA a mal répondu, on complète avec le backup
        while len(suggested) < count_to_add:
            for bc in backup_cities:
                if bc not in existing_cities and bc not in suggested:
                    suggested.append(bc)
                    break
                    
        return suggested
    except Exception as e:
        print(f"⚠️ IA Suggestion indisponible : {e}. Utilisation du backup.")
        # Filtrer le backup pour ne pas proposer des villes déjà dans la liste
        available_backups = [c for c in backup_cities if c not in existing_cities]
        return available_backups[:count_to_add]