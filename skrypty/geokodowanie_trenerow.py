"""
PROJEKT: Geoanaliza Working Dogs Foundation
MODUŁ: Geokodowanie Trenerów
AUTOR: Trzciałkowska Agnieszka
KONTAKT: www.linkedin.com/in/agnieszka-trzciałkowska
DATA: 20 kwietnia 2026
OPIS: Skrypt zamienia lokalizacje trenerów na współrzędne geograficzne
      i eksportuje dane do formatu GeoJSON.
"""

import pandas as pd
import geopandas as gpd
from geopy.geocoders import ArcGIS
from geopy.extra.rate_limiter import RateLimiter
import os

# --- KONFIGURACJA I ŚCIEŻKI ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "dane")

INPUT_FILE = os.path.join(DATA_DIR, "AdoPsiaki_trenerzy.xlsx")
SHEET_NAME = 'trenerzy'

OUTPUT_GEOJSON = os.path.join(DATA_DIR, "trenerzy_wspolrzedne.geojson")
OUTPUT_ERRORS = os.path.join(DATA_DIR, "braki_trenerzy_geokodowania.xlsx")


# --- FUNKCJE POMOCNICZE ---
def build_search_address(row):
    """Łączy kod pocztowy i miasto w jeden ciąg wyszukiwania."""
    kod = str(row['kod_pocztowy']).strip() if pd.notna(row['kod_pocztowy']) else ""
    miasto = str(row['miasto']).strip() if pd.notna(row['miasto']) else ""
    return f"{kod} {miasto}, Polska"


# --- GŁÓWNA CZĘŚĆ PROGRAMU ---
def main():
    # Wczytywanie danych
    try:
        df = pd.read_excel(INPUT_FILE, sheet_name=SHEET_NAME)
        print(f" Sukces: Wczytano dane z {INPUT_FILE}")
    except Exception as e:
        print(f" BŁĄD wczytywania: {e}")
        return

    # Przygotowanie danych
    df['search_address'] = df.apply(build_search_address, axis=1)

    # Konfiguracja Geokodera
    geolocator = ArcGIS(timeout=10)
    geocode_service = RateLimiter(geolocator.geocode, min_delay_seconds=0.2)

    # Proces Geokodowania
    print(f" Rozpoczynam geokodowanie ({len(df)} rekordów)...")
    df['location'] = df['search_address'].apply(geocode_service)

    # Wyodrębnienie współrzędnych
    df['lat'] = df['location'].apply(lambda loc: loc.latitude if loc else None)
    df['lon'] = df['location'].apply(lambda loc: loc.longitude if loc else None)

    # Obsługa błędów
    errors = df[df['location'].isnull()]
    if not errors.empty:
        errors.to_excel(OUTPUT_ERRORS, index=False)
        print(f" UWAGA: Nie znaleziono {len(errors)} lokalizacji. Zapisano w: {OUTPUT_ERRORS}")

    # Eksport do GeoJSON
    df_valid = df.dropna(subset=['lat', 'lon']).copy()

    gdf = gpd.GeoDataFrame(
        df_valid,
        geometry=gpd.points_from_xy(df_valid.lon, df_valid.lat),
        crs="EPSG:4326"
    )

    # Usuwamy kolumnę techniczną przed zapisem
    if 'location' in gdf.columns:
        gdf = gdf.drop(columns=['location'])

    gdf.to_file(OUTPUT_GEOJSON, driver='GeoJSON')
    print(f" Gotowe! Dane trenerów zapisano w: {OUTPUT_GEOJSON}")


if __name__ == "__main__":
    main()