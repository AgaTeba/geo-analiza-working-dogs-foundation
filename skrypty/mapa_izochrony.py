"""
PROJEKT: Geoanaliza Working Dogs Foundation
MODUŁ: Generowanie Izochron (Zasięgi trenerów)
AUTOR: Trzciałkowska Agnieszka
KONTAKT: www.linkedin.com/in/agnieszka-trzciałkowska
DATA: 20 kwietnia 2026
OPIS: Skrypt łączy się z API OpenRouteService, aby wygenerować obszary dojazdu
      (60 min) dla każdego trenera. Wynik zapisywany jest jako poligon w GeoJSON.
"""

import geopandas as gpd
import pandas as pd
import openrouteservice
import os
import time
from dotenv import load_dotenv

# --- KONFIGURACJA I ŚCIEŻKI ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "dane")
ENV_PATH = os.path.join(BASE_DIR, "openrouteservice_isochrone_key.env")

load_dotenv(ENV_PATH)
MY_API_KEY = os.getenv('ORS_API_KEY')

INPUT_FILE = os.path.join(DATA_DIR, "trenerzy_wspolrzedne.geojson")
OUTPUT_FILE = os.path.join(DATA_DIR, "trenerzy_izochrony.geojson")

if not MY_API_KEY:
    print(" BŁĄD: Nie znaleziono klucza API w pliku .env!")
    exit()

# --- PRZYGOTOWANIE DANYCH ---
try:
    trenerzy = gpd.read_file(INPUT_FILE)
    # API ORS wymaga układu współrzędnych WGS84
    trenerzy = trenerzy.to_crs(epsg=4326)
    print(f" Wczytano {len(trenerzy)} lokalizacji trenerów.")
except Exception as e:
    print(f" BŁĄD wczytywania pliku wejściowego: {e}")
    exit()

# --- INICJALIZACJA API ---
client = openrouteservice.Client(key=MY_API_KEY)
all_isochrones = []

print(f" Rozpoczynam pobieranie zasięgów (izochron 60 min)...")

# --- PĘTLA POBIERANIA (Z MECHANIZMEM RETRY) ---
for idx, row in trenerzy.iterrows():
    # Pobieramy współrzędne [lon, lat]
    coords = (row.geometry.x, row.geometry.y)

    success = False
    retries = 0
    max_retries = 3

    while not success and retries < max_retries:
        try:
            # Zapytanie do API
            iso = client.isochrones(
                locations=[coords],
                profile='driving-car',
                range=[3600],  # 60 minut w sekundach
                smoothing=5
            )

            # Konwersja GeoJSON (dict) na GeoDataFrame
            single_iso = gpd.GeoDataFrame.from_features(iso)

            # Przypisanie atrybutów trenera do izochrony
            for col in trenerzy.columns:
                if col != 'geometry':
                    single_iso[col] = row[col]

            all_isochrones.append(single_iso)
            print(f" [{idx + 1}/{len(trenerzy)}] OK: Zasięg dla trenera w: {row.get('miasto', 'Nieznane')}")
            success = True

            # Pauza między zapytaniami (bezpieczna dla darmowego limitu ORS)
            time.sleep(2.0)

        except Exception as e:
            retries += 1
            print(f" [!] Próba {retries}/{max_retries} dla trenera {idx} nieudana: {e}")
            time.sleep(5)  # Dłuższa pauza przy błędzie

# --- ŁĄCZENIE I ZAPIS ---
if all_isochrones:
    # Łączenie wszystkich pobranych izochron (GeoDataFrames) w jeden obiekt używając concat
    combined_iso_df = pd.concat(all_isochrones, ignore_index=True)

    # Tworzenie GeoDataFrame, biorąc geometrię i dane, a następnie dopiero nadajemy CRS
    gdf_iso = gpd.GeoDataFrame(
        combined_iso_df,
        geometry='geometry',
        crs="EPSG:4326"
    )

    # Finalne sprawdzenie poprawności geometrii
    gdf_iso = gdf_iso[gdf_iso.geometry.notnull()]

    # Zapis
    gdf_iso.to_file(OUTPUT_FILE, driver='GeoJSON')

    print(f"\n SUKCES! Wygenerowano {len(gdf_iso)} zasięgów.")
    print(f" Plik wynikowy: {OUTPUT_FILE}")
else:
    print("\n BŁĄD: Nie udało się pobrać żadnych danych z API.")