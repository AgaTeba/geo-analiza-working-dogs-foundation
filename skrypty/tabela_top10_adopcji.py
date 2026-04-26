"""
PROJEKT: Geoanaliza Working Dogs Foundation
MODUŁ: Tabela Top 10 Adopcji (Grafika)
AUTOR: Trzciałkowska Agnieszka
KONTAKT: www.linkedin.com/in/agnieszka-trzciałkowska
DATA: 20 kwietnia 2026
OPIS: Skrypt agreguje dane o adopcjach na poziomie powiatów i generuje grafikę PNG.
      Zdecydowano się na dataframe_image zamiast matplotlib, ponieważ pozwala na
      renderowanie tabel z wykorzystaniem nowoczesnych fontów i stylów CSS,
      co zapewnia wyższą estetykę raportu.
"""

import pandas as pd
import dataframe_image as dfi
import os

# --- KONFIGURACJA I ŚCIEŻKI ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "dane")
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "wizualizacje")

INPUT_FILE = os.path.join(DATA_DIR, "tabela_adopcje_powiaty.xlsx")
OUTPUT_IMAGE = os.path.join(OUTPUT_DIR, "top10_adopcje_tabela.png")

COL_ADOPCJE = 'Liczba zwierząt adoptowanych w 2024 roku'


# --- FUNKCJE POMOCNICZE ---
def stylizuj_tabele(styler, data):
    """
    Definiuje style CSS zgodnie z wytycznymi wizualnymi projektu.
    """
    styler.set_table_styles([
        # Styl dla NAGŁÓWKA (Clash Grotesk)
        {'selector': 'th', 'props': [
            ('background-color', '#092e5a'),
            ('color', 'white'),
            ('font-family', 'Clash Grotesk'),
            ('font-size', '20px'),
            ('font-weight', '500'),
            ('text-align', 'center'),
            ('border', '1px solid #343a40'),
            ('padding', '12px')
        ]},
        # Styl dla KOMÓREK (Hauora)
        {'selector': 'td', 'props': [
            ('font-family', 'Hauora'),
            ('font-size', '16px'),
            ('text-align', 'center'),
            ('padding', '10px'),
            ('border', '1px solid #343a40'),
            ('color', '#092e5a')
        ]},
        # Styl dla TYTUŁU nad tabelą (Caption)
        {'selector': 'caption', 'props': [
            ('font-family', 'Clash Grotesk'),
            ('font-size', '24px'),
            ('font-weight', '500'),
            ('color', '#092e5a'),
            ('padding-bottom', '15px'),
            ('text-align', 'left')
        ]}
    ])

    # Napis nad tabelą
    styler.set_caption("Adopcje psów top 10")

    # Ukrycie indeksu wierszy
    styler.set_td_classes(pd.DataFrame('', index=data.index, columns=data.columns))  # techniczne wsparcie dla hide
    styler.hide(axis="index")

    # Co drugi wiersz szary (paski)
    styler.set_properties(
        subset=pd.IndexSlice[data.index[::2], :],
        **{'background-color': '#f0f4f7'}
    )
    return styler


# --- GŁÓWNA CZĘŚĆ PROGRAMU ---
def main():
    # Wczytywanie danych
    try:
        df = pd.read_excel(INPUT_FILE)
        print(f" Sukces: Wczytano dane z {INPUT_FILE}")
    except Exception as e:
        print(f" BŁĄD wczytywania pliku: {e}")
        return

    # Przetwarzanie danych (Top 10)
    df_top10 = df.groupby('powiat')[COL_ADOPCJE].sum().nlargest(10).reset_index()

    # Usuwamy słowo 'powiat' w ywświetlanych wierszach tabeli
    df_top10['powiat'] = df_top10['powiat'].str.replace('powiat', '', case=False).str.strip()

    # Dodajemy m. przed nazwą powiató grodzkich
    df_top10['powiat'] = df_top10['powiat'].apply(
        lambda x: f"m. {x}" if not str(x).lower().endswith(('ski', 'cki', 'ny')) else x
    )

    # Nazwy kolumn wyświetlane w tabeli
    df_top10.columns = ['Powiat', 'Liczba adopcji']

    # Generowanie stylizowanego widoku
    df_styled = stylizuj_tabele(df_top10.style, df_top10)

    # Zapis do pliku graficznego
    try:
        print(" Generowanie grafiki PNG (wymaga silnika Chrome)...")
        dfi.export(
            df_styled,
            OUTPUT_IMAGE,
            table_conversion='chrome'
        )
        print(f" Tabela gotowa! Zapisano w: {OUTPUT_IMAGE}")
    except Exception as e:
        print(f" BŁĄD eksportu grafiki: {e}")


if __name__ == "__main__":
    main()
