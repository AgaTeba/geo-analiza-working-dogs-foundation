"""
PROJEKT: Geoanaliza Working Dogs Foundation
MODUŁ: Przypisanie powiatów (Spatial Join)
AUTOR: Trzciałkowska Agnieszka
KONTAKT: www.linkedin.com/in/agnieszka-trzciałkowska
DATA: 20 kwietnia 2026
OPIS: Skrypt nakłada lokalizacje GPS schronisk na mapę podziału administracyjnego Polski,
      automatycznie przypisując każdemu schronisku właściwy powiat.
"""

import geopandas as gpd
import pandas as pd
import os

# --- KONFIGURACJA I ŚCIEŻKI ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "dane")

# Dane wejściowe
INPUT_GEOJSON = os.path.join(DATA_DIR, "schroniska_wspolrzedne.geojson")
# Mapa powiatów (zewnętrzne źródło GeoJSON)
URL_POWIATY = "https://raw.githubusercontent.com/ppatrzyk/polska-geojson/master/powiaty/powiaty-min.geojson"

# Dane wyjściowe
OUTPUT_EXCEL = os.path.join(DATA_DIR, "tabela_adopcje_powiaty.xlsx")


# --- GŁÓWNA CZĘŚĆ PROGRAMU ---
def main():
    # Wczytywanie danych
    try:
        schroniska = gpd.read_file(INPUT_GEOJSON)
        powiaty = gpd.read_file(URL_POWIATY)
        print(f" Sukces: Wczytano {len(schroniska)} schronisk i mapę powiatów.")
    except Exception as e:
        print(f" BŁĄD podczas wczytywania danych: {e}")
        return

    # Ujednolicenie układów współrzędnych (CRS)
    # Aby spatial join zadziałał, oba pliki muszą mieć identyczny układ
    if schroniska.crs != powiaty.crs:
        schroniska = schroniska.to_crs(powiaty.crs)

    # Spatial Join (Złączenie przestrzenne)
    # Sprawdzamy, które schronisko znajduje się 'wewnątrz' (within) danego powiatu
    print(" Trwa analiza przestrzenna i przypisywanie powiatów...")
    wynik = gpd.sjoin(
        schroniska,
        powiaty[['nazwa', 'geometry']],
        predicate='within',
        how='left'
    )

    # Porządkowanie tabeli
    wynik = wynik.rename(columns={'nazwa': 'powiat'})

    # Usuwamy kolumny techniczne z biblioteki GeoPandas (index_right tworzy się przy sjoin)
    if 'index_right' in wynik.columns:
        wynik = wynik.drop(columns=['index_right'])

    # Eksport do Excela
    # Excel nie obsługuje kolumny 'geometry', więc zamieniamy GeoDataFrame na zwykły DataFrame
    tabela_finalna = pd.DataFrame(wynik.drop(columns='geometry'))

    try:
        tabela_finalna.to_excel(OUTPUT_EXCEL, index=False)
        print(f" SUKCES! Przypisano powiaty i zapisano tabelę w: {OUTPUT_EXCEL}")
    except Exception as e:
        print(f" BŁĄD podczas zapisu do Excela: {e}")


if __name__ == "__main__":
    main()
