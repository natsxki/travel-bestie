from datetime import datetime, timedelta
import itertools

# --- DONNÉES MOCK AVEC SOURCES ---
# On simule ici les résultats de tes futurs scrapers
BASE_TRANSPORT = {
    ("Paris", "Amsterdam"): [{"source": "Eurostar", "price": 120}, {"source": "FlixBus", "price": 35}],
    ("Paris", "Bruges"): [{"source": "SNCF", "price": 50}, {"source": "BlaBlaCar", "price": 25}],
    ("Paris", "Berlin"): [{"source": "AirFrance", "price": 150}, {"source": "EasyJet", "price": 80}],
    ("Amsterdam", "Bruges"): [{"source": "Train Régional", "price": 30}, {"source": "FlixBus", "price": 15}],
    ("Amsterdam", "Berlin"): [{"source": "KLM", "price": 110}, {"source": "Train de nuit OBB", "price": 60}],
    ("Bruges", "Berlin"): [{"source": "Ryanair (depuis Bruxelles)", "price": 40}, {"source": "FlixBus", "price": 45}],
}
# On duplique les trajets pour le sens inverse (MVP)
for (a, b), offers in list(BASE_TRANSPORT.items()):
    BASE_TRANSPORT[(b, a)] = offers

BASE_HOTELS = {
    "Paris": [{"source": "Booking.com (Hôtel 3*)", "price": 130}, {"source": "Airbnb (Chambre)", "price": 75}],
    "Amsterdam": [{"source": "Booking.com (Hôtel centre)", "price": 160}, {"source": "Auberge de jeunesse", "price": 45}],
    "Bruges": [{"source": "Maison d'hôtes", "price": 95}, {"source": "Airbnb (Appartement)", "price": 110}],
    "Berlin": [{"source": "Booking.com (Hôtel)", "price": 90}, {"source": "Airbnb (Studio)", "price": 60}]
}

def is_weekend(date_obj):
    return date_obj.weekday() >= 5

def get_best_transport(city_a, city_b, departure_date):
    """Trouve le transport le moins cher parmi toutes les sources pour un jour donné."""
    offers = BASE_TRANSPORT.get((city_a, city_b), [{"source": "Inconnu", "price": 999}])
    best_offer = None
    lowest_price = float('inf')
    
    for offer in offers:
        # Copie du prix pour ne pas modifier la base
        current_price = offer["price"]
        if is_weekend(departure_date):
            current_price *= 1.4  # Majoration week-end
            
        if current_price < lowest_price:
            lowest_price = current_price
            best_offer = {"source": offer["source"], "price": current_price}
            
    return best_offer

def get_best_hotel(city, arrival_date, stay_duration):
    """Trouve l'hébergement le moins cher pour toute la durée du séjour."""
    offers = BASE_HOTELS.get(city, [{"source": "Inconnu", "price": 999}])
    best_offer = None
    lowest_total = float('inf')
    
    for offer in offers:
        total_price = 0
        current_date = arrival_date
        
        # On calcule le prix total de CE logement pour tous les jours du séjour
        for _ in range(stay_duration):
            daily_rate = offer["price"]
            if is_weekend(current_date):
                daily_rate *= 1.5
            total_price += daily_rate
            current_date += timedelta(days=1)
            
        if total_price < lowest_total:
            lowest_total = total_price
            best_offer = {"source": offer["source"], "total_price": total_price}
            
    return best_offer

def find_best_trip(city_stays, start_city, start_date_str):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    cities = list(city_stays.keys())
    if start_city in cities: cities.remove(start_city)
    
    best_route = None
    lowest_total_trip_cost = float('inf')
    best_trip_details = [] # Pour stocker la facture détaillée

    for path in itertools.permutations(cities):
        full_path = (start_city,) + path
        current_total_cost = 0
        current_date = start_date
        trip_details = []
        
        for i in range(len(full_path) - 1):
            city_a, city_b = full_path[i], full_path[i+1]
            stay_days = city_stays[city_b]
            
            # 1. Sélection du meilleur transport
            transport = get_best_transport(city_a, city_b, current_date)
            
            # 2. Sélection du meilleur hôtel à l'arrivée
            hotel = get_best_hotel(city_b, current_date, stay_days)
            
            # On ajoute au coût total de la boucle en cours
            step_cost = transport["price"] + hotel["total_price"]
            current_total_cost += step_cost
            
            # On sauvegarde les détails de cette étape
            trip_details.append({
                "from": city_a,
                "to": city_b,
                "date": current_date.strftime("%Y-%m-%d"),
                "transport_source": transport["source"],
                "transport_cost": transport["price"],
                "hotel_source": hotel["source"],
                "hotel_cost": hotel["total_price"],
                "stay_days": stay_days
            })
            
            current_date += timedelta(days=stay_days)
            
        if current_total_cost < lowest_total_trip_cost:
            lowest_total_trip_cost = current_total_cost
            best_route = full_path
            best_trip_details = trip_details # On garde la facture du meilleur trajet
            
    return best_route, lowest_total_trip_cost, best_trip_details