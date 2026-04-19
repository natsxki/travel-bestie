from phase1_duration import determine_stay_durations

def main():
    # Inputs de test (plus tard, ça viendra d'une interface web)
    target_cities = ["Paris", "Amsterdam", "Bruges", "Berlin"]
    available_days = 12
    preferences = "J'adore les musées d'art classique, je veux prendre mon temps, et je n'aime pas trop la vie nocturne."

    print("Analyse de l'itinéraire par l'IA en cours...\n")
    
    # Appel de la Phase 1
    trip_plan = determine_stay_durations(
        cities=target_cities, 
        total_days=available_days, 
        user_preferences=preferences
    )

    # Affichage des résultats
    print(f"✈️ Répartition suggérée pour {trip_plan.total_days} jours :")
    print("-" * 40)
    for stay in trip_plan.allocations:
        print(f"📍 {stay.city_name} : {stay.recommended_days} jours")
        print(f"   💡 Raison : {stay.reasoning}\n")

if __name__ == "__main__":
    main()