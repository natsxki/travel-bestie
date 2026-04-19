from pydantic import BaseModel
from typing import List

class CityStay(BaseModel):
    city_name: str
    recommended_days: int
    reasoning: str # Toujours demander à l'IA d'expliquer, ça améliore sa précision

class TripAllocation(BaseModel):
    total_days: int
    allocations: List[CityStay]