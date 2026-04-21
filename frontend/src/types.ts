export interface CityInput {
  id: string; // Pour gérer la liste dynamiquement dans React
  name: string;
  days?: number; // Le "?" signifie que c'est optionnel (IA prend le relais si vide)
}

export interface TripStep {
  from: string;
  to: string;
  date: string;
  transport_source: string;
  transport_cost: number;
  hotel_source: string;
  hotel_cost: number;
  stay_days: number;
}

export interface TripResult {
  best_order: string[];
  total_price: number;
  details: TripStep[];
}