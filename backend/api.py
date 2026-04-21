from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from phase1_duration import determine_stay_durations, suggest_additional_cities
from phase2_routing import find_best_trip

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class CityInput(BaseModel):
    id: str
    name: str
    days: Optional[int] = None

class OptimizeRequest(BaseModel):
    cities: List[CityInput]
    startDate: Optional[str] = None
    preferences: Optional[str] = None
    totalDays: int = 12 
    totalDestinations: Optional[int] = None 
    # LES NOUVELLES OPTIONS
    isRoundTrip: bool = False
    keepOrder: bool = False
    includeTransport: bool = True
    includeHotel: bool = True

@app.post("/optimize")
async def optimize_trip(request: OptimizeRequest):
    # 1. PRÉPARATION ET SUGGESTIONS IA
    valid_cities = [c for c in request.cities if c.name.strip() != ""]
    city_names = [c.name for c in valid_cities]
    ia_prompt = request.preferences if request.preferences else "Voyage équilibré."

    target_dest = max(2, request.totalDestinations or len(city_names))
    missing = target_dest - len(city_names)
    
    suggested_names = []
    if missing > 0:
        suggested_names = suggest_additional_cities(city_names, missing, ia_prompt)
        city_names.extend(suggested_names)
        for new_city in suggested_names:
            valid_cities.append(CityInput(id="temp", name=new_city, days=None))

    if len(city_names) < 2:
        raise HTTPException(status_code=400, detail="Veuillez saisir au moins 2 villes.")

    # 2. RÉPARTITION DES JOURS (IA)
    final_stays = {}
    ia_success = False
    try:
        trip_plan = determine_stay_durations(city_names, request.totalDays, ia_prompt)
        ia_success = True
    except:
        pass # Mode secours si l'IA plante

    for city in valid_cities:
        if city.days and city.days > 0:
            final_stays[city.name] = city.days
        elif ia_success and trip_plan:
            ia_stay = next((s for s in trip_plan.allocations if s.city_name == city.name), None)
            final_stays[city.name] = ia_stay.recommended_days if ia_stay else 3
        else:
            final_stays[city.name] = 3

    # Lisseur mathématique (Somme des jours)
    actual_total = sum(final_stays.values())
    diff = request.totalDays - actual_total
    if diff != 0:
        longest = max(final_stays, key=final_stays.get)
        final_stays[longest] += diff
        if final_stays[longest] < 1: final_stays[longest] = 1

    # 3. MOTEUR MATHÉMATIQUE (Prix & Trajet)
    try:
        # Note : On conserve l'ordre de `city_names` tel qu'il a été envoyé par le Frontend (grâce au drag & drop)
        best_order, total_price, details = find_best_trip(
            city_stays=final_stays,
            start_city=city_names[0], # La ville tout en haut de la liste
            start_date_str=request.startDate,
            is_round_trip=request.isRoundTrip,
            keep_order=request.keepOrder,
            include_transport=request.includeTransport,
            include_hotel=request.includeHotel
        )

        return {
            "best_order": best_order,
            "total_price": total_price,
            "details": details,
            "ai_used": ia_success,
            "suggested_cities": suggested_names
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))