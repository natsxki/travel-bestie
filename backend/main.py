from phase1_duration import determine_stay_durations
# On importe la bonne fonction de la Phase 2 !
from phase2_routing import find_best_trip 

def main():
    target_cities = ["Paris", "Amsterdam", "Bruges", "Berlin"]
    available_days = 12
    preferences = "J'adore les musées d'art classique, je veux prendre mon temps."
    
    # NOUVEAU : La date de départ souhaitée (Année-Mois-Jour)
    start_date = "2025-05-15" # C'est un jeudi, parfait pour voir l'impact du week-end
    
    # --- PHASE 1 : L'Intelligence (Durée) ---
    print("🧠 [PHASE 1] Analyse de l'itinéraire par l'IA en cours...\n")
    trip_plan = determine_stay_durations(target_cities, available_days, preferences)

    city_stays_dict = {stay.city_name: stay.recommended_days for stay in trip_plan.allocations}
    
    print("-" * 40)
    for city, days in city_stays_dict.items():
        print(f"📍 {city} : {days} jours")
    print("-" * 40, "\n")

    # --- PHASE 2 : L'Optimisation (Prix, Ordre et Sources) ---
    print(f"🚂 [PHASE 2] Calcul du meilleur itinéraire avec départ le {start_date}...\n")
    
    best_order, total_price, details = find_best_trip(
        city_stays=city_stays_dict, 
        start_city="Paris", 
        start_date_str=start_date
    )
    
    print(f"✅ Itinéraire le moins cher trouvé : {total_price:.2f} €")
    print(f"🗺️  Ordre global : {' ➡️  '.join(best_order)}\n")
    
    print("📝 --- CARNET DE VOYAGE DÉTAILLÉ ---")
    for step in details:
        print(f"\n📅 Le {step['date']} : Voyage {step['from']} ➡️  {step['to']}")
        print(f"   🚆 Transport : {step['transport_source']} ({step['transport_cost']:.2f} €)")
        print(f"   🏨 Logement  : {step['hotel_source']} pour {step['stay_days']} nuits ({step['hotel_cost']:.2f} €)")

if __name__ == "__main__":
    main()