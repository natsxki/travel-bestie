import { useState, useRef } from 'react';

interface City {
  id: string;
  name: string;
  days?: number | '';
}

const PREFERENCES_OPTIONS = [
  "Culture & Histoire", "Vie nocturne & Fête", "Nature & Balades",
  "Budget Serré", "Lieux photogéniques", "Gastronomie"
];

export default function App() {
  const [cities, setCities] = useState<City[]>([
    { id: '1', name: 'Paris', days: '' },
    { id: '2', name: 'Amsterdam', days: '' }
  ]);
  
  // États des paramètres
  const [startDate, setStartDate] = useState('');
  const [totalDays, setTotalDays] = useState<number | ''>(12);
  const [totalDestinations, setTotalDestinations] = useState<number | ''>('');
  const [selectedPrefs, setSelectedPrefs] = useState<string[]>([]);
  
  // États des options de calcul
  const [isRoundTrip, setIsRoundTrip] = useState<boolean>(false);
  const [keepOrder, setKeepOrder] = useState<boolean>(false);
  const [includeTransport, setIncludeTransport] = useState<boolean>(true);
  const [includeHotel, setIncludeHotel] = useState<boolean>(true);
  
  const [loadingStep, setLoadingStep] = useState<string>('');
  const [errorMsg, setErrorMsg] = useState<string>('');
  const [result, setResult] = useState<any>(null);

  // Mémoire Drag & Drop
  const dragItem = useRef<number | null>(null);
  const dragOverItem = useRef<number | null>(null);

  const handleSort = () => {
    if (dragItem.current !== null && dragOverItem.current !== null) {
      const _cities = [...cities];
      const draggedItemContent = _cities.splice(dragItem.current, 1)[0];
      _cities.splice(dragOverItem.current, 0, draggedItemContent);
      setCities(_cities);
    }
    dragItem.current = null;
    dragOverItem.current = null;
  };

  const handleAddCity = () => setCities([...cities, { id: crypto.randomUUID(), name: '', days: '' }]);
  const handleRemoveCity = (id: string) => setCities(cities.filter(c => c.id !== id));
  
  const togglePreference = (pref: string) => {
    if (selectedPrefs.includes(pref)) setSelectedPrefs(selectedPrefs.filter(p => p !== pref));
    else setSelectedPrefs([...selectedPrefs, pref]);
  };

  const runOptimization = async () => {
    const validCities = cities.filter(c => c.name.trim() !== '');
    
    if (validCities.length < 2 && (!totalDestinations || totalDestinations < 2)) {
      setErrorMsg("Il faut au moins 2 destinations (ou demander à l'IA d'en générer).");
      return;
    }

    const userForcedDays = cities.reduce((acc, c) => acc + (typeof c.days === 'number' ? c.days : 0), 0);
    if (totalDays !== '' && userForcedDays > totalDays) {
      setErrorMsg(`Vous avez réparti manuellement ${userForcedDays} jours, mais la durée totale n'est que de ${totalDays} jours.`);
      return;
    }

    setErrorMsg(''); setResult(null);
    setLoadingStep("1/2 • L'IA construit votre carnet de route...");
    
    const phase2Timer = setTimeout(() => {
      setLoadingStep("2/2 • Calcul des prix et du trajet optimal...");
    }, 4000);

    try {
      const response = await fetch('http://localhost:8000/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cities: cities.map(c => ({ id: c.id, name: c.name, days: c.days === '' ? null : c.days })),
          startDate: startDate || null,
          preferences: selectedPrefs.length > 0 ? selectedPrefs.join(', ') : null,
          totalDays: totalDays === '' ? 12 : totalDays,
          totalDestinations: totalDestinations === '' ? null : totalDestinations,
          isRoundTrip, keepOrder, includeTransport, includeHotel
        })
      });

      const data = await response.json();
      clearTimeout(phase2Timer);
      
      if (!response.ok) throw new Error(data.detail || "Erreur inconnue");
      setResult(data);
    } catch (err: any) {
      setErrorMsg(`Erreur : ${err.message}`);
    } finally {
      setLoadingStep('');
    }
  };

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto', padding: '30px', fontFamily: 'system-ui, sans-serif', color: '#1f2937' }}>
      <h1 style={{ textAlign: 'center', marginBottom: '30px' }}>AI Travel Optimizer</h1>
      
      <div style={{ backgroundColor: '#f9fafb', padding: '25px', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
        
        <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
          {/* COLONNE GAUCHE : Paramètres */}
          <div style={{ flex: '1 1 300px' }}>
            <div style={{ marginBottom: '20px' }}>
              <h3 style={{ marginTop: 0, marginBottom: '5px' }}>Date de départ</h3>
              <p style={{ fontSize: '12px', color: '#6b7280', margin: '0 0 8px 0' }}>Vide = Date la moins chère</p>
              <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} style={{ padding: '10px', borderRadius: '6px', border: '1px solid #d1d5db', width: '100%', boxSizing: 'border-box' }} />
            </div>

            <div style={{ display: 'flex', gap: '15px', marginBottom: '20px' }}>
              <div style={{ flex: 1 }}>
                <h3 style={{ marginTop: 0, marginBottom: '8px' }}>Total Jours</h3>
                <input type="number" min="2" value={totalDays} onChange={(e) => setTotalDays(e.target.value === '' ? '' : parseInt(e.target.value))} style={{ padding: '10px', borderRadius: '6px', border: '1px solid #d1d5db', width: '100%', boxSizing: 'border-box' }} />
              </div>
              <div style={{ flex: 1 }}>
                <h3 style={{ marginTop: 0, marginBottom: '8px' }}>Étapes cibles</h3>
                <input type="number" min="2" placeholder="Auto" value={totalDestinations} onChange={(e) => setTotalDestinations(e.target.value === '' ? '' : parseInt(e.target.value))} style={{ padding: '10px', borderRadius: '6px', border: '1px solid #d1d5db', width: '100%', boxSizing: 'border-box' }} />
              </div>
            </div>

            <h3 style={{ marginTop: 0, marginBottom: '10px' }}>Options de Calcul</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', background: '#fff', padding: '15px', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
              <label style={{ cursor: 'pointer', fontSize: '14px', display: 'flex', gap: '8px' }}>
                <input type="checkbox" checked={isRoundTrip} onChange={e => setIsRoundTrip(e.target.checked)} /> 🔁 Boucler le trajet (Aller-retour)
              </label>
              <label style={{ cursor: 'pointer', fontSize: '14px', display: 'flex', gap: '8px' }}>
                <input type="checkbox" checked={keepOrder} onChange={e => setKeepOrder(e.target.checked)} /> 📌 Respecter l'ordre de ma liste
              </label>
              <hr style={{ border: 0, borderTop: '1px solid #e5e7eb', margin: '5px 0' }} />
              <label style={{ cursor: 'pointer', fontSize: '14px', display: 'flex', gap: '8px' }}>
                <input type="checkbox" checked={includeTransport} onChange={e => setIncludeTransport(e.target.checked)} /> 🚆 Inclure les Transports
              </label>
              <label style={{ cursor: 'pointer', fontSize: '14px', display: 'flex', gap: '8px' }}>
                <input type="checkbox" checked={includeHotel} onChange={e => setIncludeHotel(e.target.checked)} /> 🏨 Inclure les Hôtels
              </label>
            </div>
          </div>

          {/* COLONNE DROITE : Villes et Profil */}
          <div style={{ flex: '1 1 400px' }}>
            <h3 style={{ marginTop: 0, marginBottom: '15px' }}>Vos destinations</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '15px' }}>
              {cities.map((city, index) => (
                <div key={city.id} draggable onDragStart={() => dragItem.current = index} onDragEnter={() => dragOverItem.current = index} onDragEnd={handleSort} onDragOver={(e) => e.preventDefault()} style={{ background: '#ffffff', padding: '12px', borderRadius: '8px', border: '1px solid #e5e7eb', display: 'flex', gap: '10px', alignItems: 'center' }}>
                  <span style={{ cursor: 'grab', fontSize: '18px', color: '#9ca3af', userSelect: 'none' }}>☰</span>
                  <input placeholder={index === 0 ? "Ex: Paris (Départ)" : "Ex: Rome"} value={city.name} onChange={(e) => { const newCities = [...cities]; newCities[index] = { ...newCities[index], name: e.target.value }; setCities(newCities); }} style={{ flex: 2, padding: '8px', borderRadius: '6px', border: '1px solid #d1d5db', fontSize: '14px' }} />
                  <input type="number" placeholder="Jours" value={city.days} onChange={(e) => { const newCities = [...cities]; newCities[index] = { ...newCities[index], days: e.target.value === '' ? '' : parseInt(e.target.value) }; setCities(newCities); }} style={{ flex: 1, padding: '8px', borderRadius: '6px', border: '1px solid #d1d5db', fontSize: '14px' }} />
                  {cities.length > 2 ? (
                    <button onClick={() => handleRemoveCity(city.id)} style={{ padding: '8px 12px', background: '#fee2e2', color: '#ef4444', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>X</button>
                  ) : <div style={{ width: '34px' }}></div>}
                </div>
              ))}
            </div>
            <button onClick={handleAddCity} style={{ padding: '10px 15px', background: '#e0e7ff', color: '#4f46e5', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: '600', fontSize: '13px', marginBottom: '20px' }}>+ Ajouter une ville</button>

            <h3 style={{ marginTop: 0, marginBottom: '10px' }}>Profil IA</h3>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {PREFERENCES_OPTIONS.map(pref => (
                <label key={pref} style={{ background: selectedPrefs.includes(pref) ? '#eff6ff' : '#ffffff', color: selectedPrefs.includes(pref) ? '#1d4ed8' : '#4b5563', padding: '8px 12px', border: selectedPrefs.includes(pref) ? '1px solid #bfdbfe' : '1px solid #d1d5db', borderRadius: '20px', cursor: 'pointer', fontSize: '13px', fontWeight: '500', transition: 'all 0.2s' }}>
                  <input type="checkbox" style={{ display: 'none' }} checked={selectedPrefs.includes(pref)} onChange={() => togglePreference(pref)} />
                  {pref}
                </label>
              ))}
            </div>
          </div>
        </div>

        {errorMsg && <div style={{ color: '#ef4444', margin: '20px 0', fontWeight: '500', padding: '12px', background: '#fef2f2', borderRadius: '6px', border: '1px solid #fecaca' }}>{errorMsg}</div>}
        
        <button onClick={runOptimization} disabled={loadingStep !== ''} style={{ width: '100%', marginTop: '25px', padding: '16px', background: loadingStep ? '#9ca3af' : '#10b981', color: '#ffffff', border: 'none', borderRadius: '8px', fontSize: '18px', fontWeight: 'bold', cursor: loadingStep ? 'not-allowed' : 'pointer', transition: 'background 0.2s' }}>
          {loadingStep ? 'Patientez...' : '🚀 Générer mon Itinéraire'}
        </button>

        {loadingStep && <div style={{ textAlign: 'center', marginTop: '15px', color: '#4b5563', fontWeight: '500' }}>{loadingStep}</div>}
      </div>

      {/* RÉSULTATS */}
      {result && (
        <div style={{ marginTop: '30px', padding: '25px', border: '1px solid #86efac', borderRadius: '12px', background: '#f0fdf4' }}>
          <h2 style={{ color: '#166534', marginTop: 0, marginBottom: '15px' }}>Voyage Finalisé</h2>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', paddingBottom: '15px', borderBottom: '1px solid #bbf7d0' }}>
            <div>
              <p style={{ margin: 0, color: '#15803d', fontSize: '14px', fontWeight: '600', textTransform: 'uppercase' }}>Itinéraire</p>
              <p style={{ margin: '5px 0 0 0', fontSize: '18px', fontWeight: 'bold', color: '#14532d' }}>{result.best_order.join(' → ')}</p>
            </div>
            <div style={{ textAlign: 'right' }}>
              <p style={{ margin: 0, color: '#15803d', fontSize: '14px', fontWeight: '600', textTransform: 'uppercase' }}>Coût estimé</p>
              <p style={{ margin: '5px 0 0 0', fontSize: '28px', fontWeight: 'bold', color: '#16a34a' }}>{result.total_price.toFixed(2)} €</p>
            </div>
          </div>
          
          {result.suggested_cities && result.suggested_cities.length > 0 && (
            <div style={{ marginBottom: '20px', padding: '12px', background: '#e0f2fe', borderRadius: '6px', border: '1px solid #bae6fd', color: '#0369a1', fontSize: '14px' }}>
              <strong>✨ Villes ajoutées par l'IA :</strong> {result.suggested_cities.join(', ')}
            </div>
          )}

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {result.details.map((step: any, idx: number) => (
              <div key={idx} style={{ background: '#ffffff', padding: '16px', borderRadius: '8px', border: '1px solid #e5e7eb', borderLeft: '4px solid #10b981' }}>
                <div style={{ marginBottom: '10px' }}>
                  <span style={{ fontSize: '14px', color: '#6b7280', fontWeight: '600' }}>Le {step.date}</span>
                  <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#1f2937' }}>Voyage vers {step.to}</div>
                </div>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                  <div style={{ background: '#f9fafb', padding: '10px', borderRadius: '6px', border: '1px solid #f3f4f6', opacity: includeTransport ? 1 : 0.5 }}>
                    <div style={{ fontSize: '12px', color: '#6b7280', textTransform: 'uppercase', fontWeight: '600', marginBottom: '4px' }}>Transport</div>
                    <div style={{ fontSize: '14px', color: '#374151' }}>{step.transport_source}</div>
                    <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#111827' }}>{includeTransport ? `${step.transport_cost} €` : '-'}</div>
                  </div>
                  
                  <div style={{ background: '#f9fafb', padding: '10px', borderRadius: '6px', border: '1px solid #f3f4f6', opacity: includeHotel ? 1 : 0.5 }}>
                    <div style={{ fontSize: '12px', color: '#6b7280', textTransform: 'uppercase', fontWeight: '600', marginBottom: '4px' }}>Hébergement</div>
                    <div style={{ fontSize: '14px', color: '#374151' }}>{step.hotel_source}</div>
                    {step.stay_days > 0 ? (
                      <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#111827' }}>{includeHotel ? `${step.stay_days} nuits (${step.hotel_cost} €)` : `${step.stay_days} nuits`}</div>
                    ) : (
                      <div style={{ fontSize: '14px', color: '#111827' }}>Fin du voyage</div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}