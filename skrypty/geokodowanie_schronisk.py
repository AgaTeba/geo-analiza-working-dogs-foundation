"""
PROJEKT: Geoanaliza Working Dogs Foundation
MODUŁ: Geokodowanie Schronisk
AUTOR: Trzciałkowska Agnieszka
KONTAKT: www.linkedin.com/in/agnieszka-trzciałkowska
DATA: 20 kwietnia 2026
OPIS: Skrypt konwertuje adresy schronisk z pliku Excel na współrzędne geograficzne
      wykorzystując silnik ArcGIS i zapisuje wynik do formatu GeoJSON.
"""

import pandas as pd
import geopandas as gpd
from geopy.geocoders import ArcGIS
from geopy.extra.rate_limiter import RateLimiter
import os

# --- KONFIGURACJA I ŚCIEŻKI ---

# Ścieżki relatywne pozwalają na uruchomienie projektu na dowolnym komputerze
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "dane")

INPUT_FILE = os.path.join(DATA_DIR, "schroniska_psy_PL_2024.xlsx")
SHEET_NAME = 'P_2024_schroniska_psy'

OUTPUT_GEOJSON = os.path.join(DATA_DIR, "schroniska_wspolrzedne.geojson")
OUTPUT_ERRORS = os.path.join(DATA_DIR, "braki_geokodowania.xlsx")


# --- FUNKCJE POMOCNICZE ---

def clean_address(text):
    """Usuwa zbędne białe znaki z adresu."""
    if pd.isna(text):
        return None
    return " ".join(str(text).split())

# --- GŁÓWNA CZĘŚĆ PROGRAMU ---

def main():
    # Wczytywanie danych
    try:
        df = pd.read_excel(INPUT_FILE, sheet_name=SHEET_NAME)
        print(f" wczytano dane z pliku: {INPUT_FILE}")
    except Exception as e:
        print(f" Błąd wczytywania pliku: {e}")
        return

    # Przygotowanie danych
    df['cleaned_address'] = df['Adres'].apply(clean_address)

    # Konfiguracja Geokodera
    # ArcGIS nie wymaga klucza API dla podstawowych zapytań
    geolocator = ArcGIS(timeout=10)
    geocode_service = RateLimiter(geolocator.geocode, min_delay_seconds=0.2)

    # Proces Geokodowania
    print(" Rozpoczynam proces geokodowania (ArcGIS)... Proszę czekać.")
    df['location'] = df['cleaned_address'].apply(geocode_service)

    # Wyodrębnienie współrzędnych
    df['lat'] = df['location'].apply(lambda loc: loc.latitude if loc else None)
    df['lon'] = df['location'].apply(lambda loc: loc.longitude if loc else None)

    # Obsługa błędów (adresy nieodnalezione)
    errors = df[df['location'].isnull()]
    if not errors.empty:
        errors.to_excel(OUTPUT_ERRORS, index=False)
        print(f" UWAGA: Nie odnaleziono {len(errors)} adresów. Szczegóły w: {OUTPUT_ERRORS}")

    # Eksport do formatu przestrzennego (GeoJSON)
    # Usuwamy rekordy bez współrzędnych przed konwersją na GeoDataFrame
    df_valid = df.dropna(subset=['lat', 'lon']).copy()

    gdf = gpd.GeoDataFrame(
        df_valid,
        geometry=gpd.points_from_xy(df_valid.lon, df_valid.lat),
        crs="EPSG:4326"
    )

    # Zapis do pliku GeoJSON
    gdf.to_file(OUTPUT_GEOJSON, driver='GeoJSON')
    print(f" Przetworzone dane zapisano w: {OUTPUT_GEOJSON}")


if __name__ == "__main__":
    main()