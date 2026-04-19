import sqlite3
import time

DB_NAME = "travel_cache.db"

def init_db():
    """Crée la base de données et la table si elles n'existent pas."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Création de la table pour les prix de transport
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transport_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city_a TEXT,
            city_b TEXT,
            travel_date TEXT,
            source TEXT,
            price REAL,
            scraped_at REAL
        )
    ''')
    conn.commit()
    conn.close()
    print("🗄️ Base de données SQLite initialisée.")

def save_price_to_db(city_a, city_b, travel_date, source, price):
    """Sauvegarde une nouvelle offre dans la base de données."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    current_time = time.time()
    
    cursor.execute('''
        INSERT INTO transport_prices (city_a, city_b, travel_date, source, price, scraped_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (city_a, city_b, travel_date, source, price, current_time))
    
    conn.commit()
    conn.close()

def get_cached_prices(city_a, city_b, travel_date, max_age_hours=24):
    """
    Récupère toutes les offres pour un trajet, SI elles ont été cherchées 
    il y a moins de 'max_age_hours'.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # On calcule le timestamp limite (ex: il y a 24 heures)
    cutoff_time = time.time() - (max_age_hours * 3600)
    
    # On gère le fait que (A->B) est pareil que (B->A) pour certains trains
    cursor.execute('''
        SELECT source, price FROM transport_prices 
        WHERE ((city_a = ? AND city_b = ?) OR (city_a = ? AND city_b = ?))
        AND travel_date = ? 
        AND scraped_at > ?
    ''', (city_a, city_b, city_b, city_a, travel_date, cutoff_time))
    
    results = cursor.fetchall()
    conn.close()
    
    # On transforme le résultat SQL en liste de dictionnaires pour la Phase 2
    offers = [{"source": row[0], "price": row[1]} for row in results]
    return offers