import { useState } from 'react';

// --- TYPES ---
interface City {
  id: string;
  name: string;
  days?: number | '';
}

const PREFERENCES_OPTIONS = [
  "🏛️ Culture & Histoire",
  "🎉 Vie nocturne & Fête",
  "🌲 Nature & Balades",
  "💰 Budget Serré",
  "📸 Lieux ultra-photogéniques",
  "🍔 Gastronomie"
];

export default function App() {
  // --- ÉTATS (State) ---
  const [cities, setCities] = useState<City[]>([
    { id: '1', name: 'Paris', days: '' },
    { id: '2', name: 'Amsterdam', days: '' }
  ]);
  const [startDate, setStartDate] = useState('');
  const [selectedPrefs, setSelectedPrefs] = useState<string[]>([]);
  
  // Nouveaux États pour l'IA Générative
  const [totalDays, setTotalDays] = useState<number | ''>(12);
  const [totalDestinations, setTotalDestinations] = useState<number | ''>('');
  
  // États de l'interface
  const [loadingStep, setLoadingStep] = useState<string>(''); // Gère le texte de chargement
  const [errorMsg, setErrorMsg] = useState<string>('');
  const [result, setResult] = useState<any>(null);

  // --- LOGIQUE ---
  const handleAddCity = () => {
    setCities([...cities, { id: crypto.randomUUID(), name: '', days: '' }]);
  };

  const handleRemoveCity = (id: string) => {
    setCities(cities.filter(c => c.id !== id));
  };

  const togglePreference = (pref: string) => {
    if (selectedPrefs.includes(pref)) {
      setSelectedPrefs(selectedPrefs.filter(p => p !== pref));
    } else {
      setSelectedPrefs([...selectedPrefs, pref]);
    }
  };

  const runOptimization = async () => {

    if (cities.filter(c => c.name.trim() !== '').length < 2 && (!totalDestinations || totalDestinations < 2)) {
      setErrorMsg("⚠️ Il faut au moins 2 destinations (ou demander à l'IA d'en générer).");
      return;
    }

    setErrorMsg('');
    setResult(null);
    
    // 2. Lancement des animations de chargement
    setLoadingStep("🧠 Phase 1 : Analyse de votre profil et suggestions par l'IA...");
    
    // On simule le passage à la Phase 2 après 3 secondes pour l'UX
    const phase2Timer = setTimeout(() => {
      setLoadingStep(
        startDate 
          ? "🚂 Phase 2 : Recherche des meilleurs prix et calcul du trajet..." 
          : "📅 Phase 2 : Recherche de la date la moins chère (Scan sur 30 jours)..."
      );
    }, 3000);

    // 3. La requête vers le Backend Python
    try {
      const response = await fetch('http://localhost:8000/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cities: cities.map(c => ({ name: c.name, days: c.days === '' ? null : c.days })),
          startDate: startDate || null,
          preferences: selectedPrefs.length > 0 ? selectedPrefs.join(', ') : null,
          totalDays: totalDays === '' ? 12 : totalDays,
          totalDestinations: totalDestinations === '' ? null : totalDestinations
        })
      });

      const data = await response.json();
      
      clearTimeout(phase2Timer); // On annule le timer si le serveur a répondu vite
      
      if (!response.ok) {
        throw new Error(data.detail || "Erreur inconnue");
      }

      setResult(data);
    } catch (err: any) {
      setErrorMsg(`❌ Erreur : ${err.message}`);
    } finally {
      setLoadingStep(''); // On arrête le chargement
    }
  };

  // --- RENDU VISUEL (CSS en ligne pour faire simple) ---
  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '30px', fontFamily: 'system-ui, sans-serif' }}>
      <h1 style={{ textAlign: 'center' }}>🌍 AI Travel Optimizer</h1>
      
      <div style={{ backgroundColor: '#f8f9fa', padding: '20px', borderRadius: '10px', marginTop: '20px' }}>
        
        {/* LA DATE (Optionnelle) */}
        <div style={{ marginBottom: '20px' }}>
          <h3>📅 Date de départ <span style={{ fontSize: '14px', color: '#6b7280', fontWeight: 'normal' }}>(Optionnel)</span></h3>
          <p style={{ fontSize: '12px', color: '#6b7280', marginTop: '-10px' }}>Laissez vide pour trouver la date la moins chère du mois.</p>
          <input 
            type="date" 
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)} 
            style={{ padding: '10px', borderRadius: '5px', border: '1px solid #ccc', width: '100%' }}
          />
        </div>

        {/* LES PARAMÈTRES GLOBAUX */}
        <div style={{ display: 'flex', gap: '20px', marginBottom: '20px' }}>
          <div style={{ flex: 1 }}>
            <h3>⏳ Durée du voyage</h3>
            <p style={{ fontSize: '12px', color: '#6b7280', marginTop: '-10px' }}>Nombre de jours total</p>
            <input 
              type="number" 
              min="2"
              value={totalDays}
              onChange={(e) => setTotalDays(e.target.value === '' ? '' : parseInt(e.target.value))} 
              style={{ padding: '10px', borderRadius: '5px', border: '1px solid #ccc', width: '100%' }}
            />
          </div>
          <div style={{ flex: 1 }}>
            <h3>🎯 Nombre d'étapes <span style={{ fontSize: '14px', color: '#6b7280', fontWeight: 'normal' }}>(Optionnel)</span></h3>
            <p style={{ fontSize: '12px', color: '#6b7280', marginTop: '-10px' }}>Si &gt; à vos villes, l'IA complète</p>
            <input 
              type="number" 
              min="2"
              placeholder="Auto"
              value={totalDestinations}
              onChange={(e) => setTotalDestinations(e.target.value === '' ? '' : parseInt(e.target.value))} 
              style={{ padding: '10px', borderRadius: '5px', border: '1px solid #ccc', width: '100%' }}
            />
          </div>
        </div>

        {/* LE PROFIL (Cases à cocher) */}
        <div style={{ marginBottom: '20px' }}>
          <h3>✨ Votre profil de voyageur</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
            {PREFERENCES_OPTIONS.map(pref => (
              <label key={pref} style={{ background: selectedPrefs.includes(pref) ? '#e0f2fe' : '#fff', padding: '8px 12px', border: '1px solid #cbd5e1', borderRadius: '20px', cursor: 'pointer' }}>
                <input 
                  type="checkbox" 
                  style={{ display: 'none' }}
                  checked={selectedPrefs.includes(pref)}
                  onChange={() => togglePreference(pref)}
                />
                {pref}
              </label>
            ))}
          </div>
        </div>
        
        {/* LES VILLES */}
        <div style={{ marginBottom: '20px' }}>
          <h3>📍 Vos destinations</h3>
          {cities.map((city, index) => (
            <div key={city.id} style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
              <input 
                placeholder="Ex: Berlin" 
                value={city.name} 
                onChange={(e) => {
                  const newCities = [...cities];
                  newCities[index] = { ...newCities[index], name: e.target.value }; 
                  setCities(newCities);
                }}
                style={{ flex: 2, padding: '10px', borderRadius: '5px', border: '1px solid #ccc' }}
              />
              <input 
                type="number" 
                placeholder="Jours (Auto si vide)" 
                value={city.days}
                onChange={(e) => {
                  const newCities = [...cities];
                  newCities[index] = { ...newCities[index], days: e.target.value === '' ? '' : parseInt(e.target.value) };
                  setCities(newCities);
                }}
                style={{ flex: 1, padding: '10px', borderRadius: '5px', border: '1px solid #ccc' }}
              />
              {cities.length > 2 && (
                <button onClick={() => handleRemoveCity(city.id)} style={{ padding: '10px', background: '#fee2e2', color: '#ef4444', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>
                  ✖
                </button>
              )}
            </div>
          ))}
          <button onClick={handleAddCity} style={{ padding: '10px 15px', background: '#e0e7ff', color: '#4f46e5', border: 'none', borderRadius: '5px', cursor: 'pointer', fontWeight: 'bold' }}>
            + Ajouter une étape
          </button>
        </div>
        
        {/* BOUTON D'ACTION ET MESSAGES */}
        {errorMsg && <div style={{ color: 'red', marginBottom: '10px', fontWeight: 'bold' }}>{errorMsg}</div>}
        
        <button 
          onClick={runOptimization} 
          disabled={loadingStep !== ''}
          style={{ width: '100%', padding: '15px', background: loadingStep ? '#9ca3af' : '#2563eb', color: 'white', border: 'none', borderRadius: '8px', fontSize: '18px', fontWeight: 'bold', cursor: loadingStep ? 'not-allowed' : 'pointer' }}
        >
          {loadingStep ? 'Patientez...' : '🚀 Générer mon Itinéraire'}
        </button>

        {/* ANIMATION DE CHARGEMENT */}
        {loadingStep && (
          <div style={{ textAlign: 'center', marginTop: '20px', color: '#4b5563', fontWeight: 'bold' }}>
            <span style={{ fontSize: '24px', display: 'inline-block', animation: 'spin 2s linear infinite' }}>⏳</span>
            <p>{loadingStep}</p>
          </div>
        )}
      </div>

      {/* AFFICHAGE DES RÉSULTATS */}
      {result && (
        <div style={{ marginTop: '30px', padding: '20px', border: '2px solid #22c55e', borderRadius: '10px', background: '#f0fdf4' }}>
          <h2 style={{ color: '#166534', margin: '0 0 10px 0' }}>✅ Voyage Optimisé !</h2>
          <h3 style={{ margin: '0' }}>Prix total estimé : {result.total_price.toFixed(2)} €</h3>
          <p style={{ fontSize: '18px', fontWeight: 'bold' }}>🗺️ Trajet : {result.best_order.join(' ➡️ ')}</p>
          
          {/* NOUVEAU : Affichage des villes suggérées par l'IA */}
          {result.suggested_cities && result.suggested_cities.length > 0 && (
            <div style={{ marginTop: '10px', padding: '10px', background: '#e0f2fe', borderRadius: '5px', border: '1px solid #bae6fd' }}>
              <strong>✨ Villes ajoutées par l'IA :</strong> {result.suggested_cities.join(', ')}
            </div>
          )}

          <div style={{ marginTop: '20px' }}>
            {result.details.map((step: any, idx: number) => (
              <div key={idx} style={{ background: 'white', padding: '15px', borderRadius: '8px', marginBottom: '10px', borderLeft: '4px solid #3b82f6' }}>
                <strong>📅 Le {step.date} :</strong> Voyage vers {step.to}
                <br />🚆 {step.transport_source} ({step.transport_cost} €)
                <br />🏨 {step.hotel_source} - {step.stay_days} nuits ({step.hotel_cost} €)
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}