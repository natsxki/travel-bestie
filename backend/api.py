from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from phase1_duration import determine_stay_durations
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
    # Les deux champs suivants deviennent Optionnels
    startDate: Optional[str] = None
    preferences: Optional[str] = None

@app.post("/optimize")
async def optimize_trip(request: OptimizeRequest):
    valid_cities = [c for c in request.cities if c.name.strip() != ""]
    if len(valid_cities) < 2:
        raise HTTPException(status_code=400, detail="Veuillez saisir au moins 2 villes valides.")

    city_names = [c.name for c in valid_cities]
    
    # --- VALEURS PAR DÉFAUT ---
    # Si l'utilisateur n'a coché aucune préférence, on donne un profil basique à l'IA
    ia_prompt = request.preferences if request.preferences else "Voyage équilibré, découverte classique des incontournables, budget moyen."
    
    try:
        # Phase 1 : L'IA reçoit soit les vraies préférences, soit celles par défaut
        trip_plan = determine_stay_durations(city_names, 12, ia_prompt)
        
        final_stays = {}
        for city in valid_cities:
            if city.days and city.days > 0:
                final_stays[city.name] = city.days
            else:
                ia_stay = next((s for s in trip_plan.allocations if s.city_name == city.name), None)
                final_stays[city.name] = ia_stay.recommended_days if ia_stay else 3

        # Phase 2 : On envoie la startDate (qui peut être None)
        best_order, total_price, details = find_best_trip(
            city_stays=final_stays,
            start_city=city_names[0],
            start_date_str=request.startDate
        )

        return {
            "best_order": best_order,
            "total_price": total_price,
            "details": details
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")