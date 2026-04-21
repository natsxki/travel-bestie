from backend.database import init_db, save_price_to_db
import random
from datetime import datetime, timedelta

def simulate_scraper(city_a, city_b, days_from_now):
    """
    Simule un bot qui va sur internet et trouve des prix aléatoires mais réalistes.
    """
    date_voyage = (datetime.now() + timedelta(days=days_from_now)).strftime("%Y-%m-%d")
    
    # On simule 2 ou 3 sources différentes (ex: Flixbus, SNCF, AirFrance)
    sources_possibles = [
        {"name": "SNCF", "base_min": 40, "base_max": 150},
        {"name": "FlixBus", "base_min": 15, "base_max": 45},
        {"name": "Blablacar", "base_min": 20, "base_max": 60}
    ]
    
    print(f"🔍 Scraping simulé pour {city_a} ➡️ {city_b} le {date_voyage}...")
    
    for source in sources_possibles:
        # On invente un prix réaliste
        prix_trouve = round(random.uniform(source["base_min"], source["base_max"]), 2)
        
        # ON SAUVEGARDE LE CONTENU DANS LA BASE SQLITE !
        save_price_to_db(city_a, city_b, date_voyage, source["name"], prix_trouve)
        print(f"   ✅ Ajouté à la base : {source['name']} à {prix_trouve} €")

def main():
    print("🚀 Initialisation de la base de données...")
    init_db() # Crée le fichier travel_cache.db s'il n'existe pas
    
    villes = ["Paris", "Amsterdam", "Berlin", "Bruges"]
    
    print("\n🤖 Lancement du Robot de Scraping Nocturne...\n")
    # On va générer des données pour les 15 prochains jours
    for jour in range(1, 16):
        # Pour chaque combinaison de villes possibles
        for i in range(len(villes)):
            for j in range(i + 1, len(villes)):
                ville_depart = villes[i]
                ville_arrivee = villes[j]
                
                # Le robot simule le scrap pour ce trajet
                simulate_scraper(ville_depart, ville_arrivee, jour)

    print("\n🎉 Terminé ! Ton fichier 'travel_cache.db' est maintenant rempli de données !")

if __name__ == "__main__":
    main()