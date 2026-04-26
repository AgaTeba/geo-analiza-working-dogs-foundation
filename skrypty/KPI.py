"""
PROJEKT: Geoanaliza Working Dogs Foundation
MODUŁ: Obliczenia KPI (Zasięg terytorialny % powierzchni Polski)
AUTOR: Trzciałkowska Agnieszka
KONTAKT: www.linkedin.com/in/agnieszka-trzciałkowska
DATA: 20 kwietnia 2026
OPIS: Skrypt oblicza jaki % terytorium Polski jest pokryty przez 60-minutowe
      izochrony dojazdu trenerów. Wykorzystuje układ EPSG:2180 dla precyzji metrycznej.
"""

import geopandas as gpd
import os

# --- KONFIGURACJA I ŚCIEŻKI ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "dane")

PATH_IZOCHRONY = os.path.join(DATA_DIR, "trenerzy_izochrony.geojson")
URL_POWIATY = "https://raw.githubusercontent.com/ppatrzyk/polska-geojson/master/powiaty/powiaty-min.geojson"


def main():
    # Wczytywanie i ujednolicenie układu (EPSG:2180 to standard dla obliczeń powierzchni w PL)
    try:
        print(" Wczytywanie danych i przeliczanie na metry (EPSG:2180)...")
        powiaty = gpd.read_file(URL_POWIATY).to_crs(epsg=2180)
        izochrony = gpd.read_file(PATH_IZOCHRONY).to_crs(epsg=2180)
    except Exception as e:
        print(f" BŁĄD wczytywania: {e}")
        return

    # Naprawa geometrii (Kluczowe dla stabilności operacji przestrzennych)
    # make_valid() usuwa błędy topologiczne, buffer(0) domyka poligony
    powiaty['geometry'] = powiaty.geometry.make_valid().buffer(0)
    izochrony['geometry'] = izochrony.geometry.make_valid().buffer(0)

    # Obliczenia powierzchni
    print(" Analiza konturu Polski...")
    kontur_polski = powiaty.geometry.union_all()
    powierzchnia_pl_m2 = kontur_polski.area

    print(" Analiza zasięgu trenerów (łączenie izochron)...")
    # union_all zespala wszystkie izochrony w jeden wspólny obszar
    zasieg_total = izochrony.geometry.union_all()

    # Przycinamy zasięg do granic kraju (wykluczamy zasięg np. na morzu lub za granicą)
    zasieg_w_polsce = zasieg_total.intersection(kontur_polski)
    powierzchnia_zasiegu_m2 = zasieg_w_polsce.area

    # Statystyki
    procent_w_zasiegu = (powierzchnia_zasiegu_m2 / powierzchnia_pl_m2) * 100
    procent_poza = 100 - procent_w_zasiegu

    # Konwersja na km2 dla czytelności
    pl_km2 = powierzchnia_pl_m2 / 1_000_000
    zasieg_km2 = powierzchnia_zasiegu_m2 / 1_000_000

    # --- WYŚWIETLENIE WYNIKÓW ---
    print("\n" + "="*45)
    print(" KPI: ZASIĘG TERYTORIALNY FUNDACJI")
    print("="*45)
    print(f" Powierzchnia Polski:      {pl_km2:,.2f} km2")
    print(f" Zasięg operacyjny (60m):  {zasieg_km2:,.2f} km2")
    print("-" * 45)
    print(f" PROCENT KRAJU W ZASIĘGU:  {procent_w_zasiegu:.1f}%")
    print(f" OBSZAR DO ZAGOSPODAROWANIA: {procent_poza:.1f}%")
    print("="*45)

    # Zapis wyniku do pliku tekstowego
    with open(os.path.join(DATA_DIR, "KPI_Working_Dogs.txt"), "w", encoding="utf-8") as f:
        f.write(f"Zasięg terytorialny: {procent_w_zasiegu:.1f}% Polski")

if __name__ == "__main__":
    main()