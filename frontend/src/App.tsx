import React, { useState } from 'react';

// Définition des types pour éviter le rouge
interface City {
  id: string;
  name: string;
  days?: number;
}

export default function App() {
  const [cities, setCities] = useState<City[]>([{ id: '1', name: 'Paris' }]);
  const [startDate, setStartDate] = useState('');
  const [result, setResult] = useState<any>(null);

  const runOptimization = async () => {
    const response = await fetch('http://localhost:8000/optimize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        cities: cities.map(c => ({ name: c.name, days: c.days })),
        startDate,
        preferences: "Voyage optimisé"
      })
    });
    const data = await response.json();
    setResult(data);
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>Mon Travel Optimizer</h1>
      
      {/* Formulaire */}
      <input type="date" onChange={(e) => setStartDate(e.target.value)} />
      
      {cities.map((city, index) => (
        <div key={city.id} style={{ margin: '10px 0' }}>
          <input 
            placeholder="Ville" 
            value={city.name} 
            onChange={(e) => {
              const newCities = [...cities];
              newCities[index].name = e.target.value;
              setCities(newCities);
            }} 
          />
          <input 
            type="number" 
            placeholder="Jours (IA si vide)" 
            onChange={(e) => {
              const newCities = [...cities];
              newCities[index].days = parseInt(e.target.value);
              setCities(newCities);
            }} 
          />
        </div>
      ))}
      
      <button onClick={runOptimization}>Lancer l'optimisation 🚀</button>

      {/* Affichage des résultats */}
      {result && (
        <div style={{ marginTop: '20px', borderTop: '1px solid #ccc' }}>
          <h3>Meilleur prix : {result.total_price}€</h3>
          <p>Ordre : {result.best_order.join(' → ')}</p>
        </div>
      )}
    </div>
  );
}