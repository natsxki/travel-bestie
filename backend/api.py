from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from phase1_duration import determine_stay_durations, suggest_additional_cities # NOUVEL IMPORT
from phase2_routing import find_best_trip

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

class CityInput(BaseModel):
    name: str
    days: Optional[int] = None

class OptimizeRequest(BaseModel):
    cities: List[CityInput]
    startDate: Optional[str] = None
    preferences: Optional[str] = None
    # NOUVEAUX CHAMPS
    totalDays: Optional[int] = 12 
    totalDestinations: Optional[int] = None 

@app.post("/optimize")
async def optimize_trip(request: OptimizeRequest):
    # 1. On récupère les villes saisies par l'utilisateur
    valid_cities = [c for c in request.cities if c.name.strip() != ""]
    city_names = [c.name for c in valid_cities]
    
    ia_prompt = request.preferences if request.preferences else "Voyage équilibré, découverte classique."

    # 2. IA : SUGGESTION DE VILLES MANQUANTES
    target_destinations = request.totalDestinations or len(city_names)
    target_destinations = max(2, target_destinations) # Au moins 2 villes obligatoires
    
    missing_count = target_destinations - len(city_names)
    
    if missing_count > 0:
        print(f"🔍 L'utilisateur veut {target_destinations} villes, il en a mis {len(city_names)}. L'IA va en trouver {missing_count}.")
        suggested_names = suggest_additional_cities(city_names, missing_count, ia_prompt)
        city_names.extend(suggested_names)
        
        # On ajoute ces nouvelles villes à notre liste d'objets valid_cities avec "days = None"
        for new_city in suggested_names:
            valid_cities.append(CityInput(name=new_city, days=None))

    if len(city_names) < 2:
        raise HTTPException(status_code=400, detail="Veuillez saisir au moins 2 villes valides.")

    final_stays = {}
    ia_success = False
    trip_plan = None
    
    # 3. IA : RÉPARTITION DES JOURS
    try:
        # On passe maintenant request.totalDays au lieu du "12" en dur !
        trip_plan = determine_stay_durations(city_names, request.totalDays, ia_prompt)
        ia_success = True
    except Exception as e:
        print(f"⚠️ AVERTISSEMENT IA DURÉE : {e}")

    # Répartition finale
    for city in valid_cities:
        if city.days and city.days > 0:
            final_stays[city.name] = city.days
        elif ia_success and trip_plan:
            ia_stay = next((s for s in trip_plan.allocations if s.city_name == city.name), None)
            final_stays[city.name] = ia_stay.recommended_days if ia_stay else 3
        else:
            final_stays[city.name] = 3

    # 4. PHASE 2 : L'OPTIMISATION MATHÉMATIQUE
    try:
        best_order, total_price, details = find_best_trip(
            city_stays=final_stays,
            start_city=city_names[0],
            start_date_str=request.startDate
        )

        return {
            "best_order": best_order,
            "total_price": total_price,
            "details": details,
            "ai_used": ia_success,
            "suggested_cities": [c.name for c in valid_cities[len(request.cities):]] # On renvoie les villes ajoutées par l'IA
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'optimisation : {str(e)}")