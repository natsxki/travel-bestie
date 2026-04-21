from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from backend.phase1_duration import determine_stay_durations
from backend.phase2_routing import find_best_trip

app = FastAPI()

# IMPORTANT : Le CORS permet à ton React (port 3000) de parler à ton Python (port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En prod, on mettra l'URL précise
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèles de données pour valider ce que React nous envoie
class CityInput(BaseModel):
    name: str
    days: Optional[int] = None

class OptimizeRequest(BaseModel):
    cities: List[CityInput]
    startDate: str
    preferences: str

@app.post("/optimize")
async def optimize_trip(request: OptimizeRequest):
    # 1. On prépare les données pour la Phase 1
    city_names = [c.name for c in request.cities]
    
    # 2. Appel de l'IA (Phase 1)
    # On pourrait ici filtrer : si l'utilisateur a déjà mis les jours, on ne demande pas à l'IA
    trip_plan = determine_stay_durations(city_names, 12, request.preferences)
    
    # On fusionne les jours forcés par l'utilisateur avec ceux de l'IA
    final_stays = {}
    for city in request.cities:
        if city.days:
            final_stays[city.name] = city.days
        else:
            # On cherche ce que l'IA a proposé pour cette ville
            ia_stay = next((s for s in trip_plan.allocations if s.city_name == city.name), None)
            final_stays[city.name] = ia_stay.recommended_days if ia_stay else 3

    # 3. Appel de l'Optimiseur (Phase 2)
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

# Pour lancer : uvicorn api:app --reload