"""
PROJEKT: Geoanaliza Working Dogs Foundation
MODUŁ: Finałowa wizualizacja – Kartogram adopcji psów w 2024 roku i analiza dostępności działań Fundacji Working Dogs w Polsce
AUTOR: Agnieszka Trzciałkowska
KONTAKT: www.linkedin.com/in/agnieszka-trzciałkowska
DATA: 20 kwietnia 2026
OPIS: Zaawansowana wizualizacja przestrzenna łącząca metodę kartogramu (liczba adopcji
      w powiatach) z metodą sygnaturową punktową (lokalizacje trenerów) oraz metodą
      izochron (zasięg dojazdu 60 min). Skrypt integruje dane geograficzne z elementami
      Business Intelligence (KPI) w celu identyfikacji luk w sieci wsparcia Fundacji.
"""

import geopandas as gpd
import matplotlib.pyplot as plt
import os
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap
from shapely.geometry import Polygon, MultiPolygon

# --- KONFIGURACJA ŚCIEŻEK ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else os.getcwd()

DATA_DIR = os.path.join("..", "dane")
OUTPUT_DIR = os.path.join("..", "wizualizacje")
FONTS_DIR = os.path.join("..", "czcionki")
BRAND_DIR = os.path.join("..", "identyfikacja_wizualna_fundacji")

# Pliki wejściowe
PATH_GEOJSON = os.path.join(DATA_DIR, "schroniska_wspolrzedne.geojson")
PATH_TRENERZY = os.path.join(DATA_DIR, "trenerzy_wspolrzedne.geojson")
PATH_IZOCHRONY = os.path.join(DATA_DIR, "trenerzy_izochrony.geojson")
URL_POWIATY = "https://raw.githubusercontent.com/ppatrzyk/polska-geojson/master/powiaty/powiaty-min.geojson"

# Pliki graficzne (Assety)
PATH_CLASH = os.path.join(FONTS_DIR, "ClashGrotesk-Medium.otf")
PATH_HAUORA = os.path.join(FONTS_DIR, "Hauora-Regular.otf")
PATH_TABLE = os.path.join(OUTPUT_DIR, "top10_adopcje_tabela.png")
PATH_LOGO = os.path.join(BRAND_DIR, "WDF Logo_Dark Red_Filled Dog.png")
PATH_KPI1 = os.path.join(OUTPUT_DIR, "KPI_1.png")
PATH_KPI2 = os.path.join(OUTPUT_DIR, "KPI_2.png")

# Plik wynikowy
PATH_FINAL_PNG = os.path.join(OUTPUT_DIR, "BI_NGO_Working_Dogs_Trzcialkowska.png")

# --- CZCIONKI ---
prop_tytul = font_manager.FontProperties(fname=PATH_CLASH, size=20)
prop_tekst = font_manager.FontProperties(fname=PATH_HAUORA, size=12)
prop_tytul_legendy = font_manager.FontProperties(fname=PATH_CLASH, size=15, weight='400')
prop_tekst_legendy = font_manager.FontProperties(fname=PATH_HAUORA, size=10)

# --- WCZYTYWANIE DANYCH ---
schroniska = gpd.read_file(PATH_GEOJSON).to_crs(epsg=2180)
powiaty = gpd.read_file(URL_POWIATY).to_crs(epsg=2180)
trenerzy = gpd.read_file(PATH_TRENERZY).to_crs(epsg=2180)
izochrony = gpd.read_file(PATH_IZOCHRONY).to_crs(epsg=2180)

# --- PRZYGOTOWANIE DANYCH DO KARTOGRAMU ---
powiaty['geometry'] = powiaty.geometry.make_valid()
union_result = powiaty.geometry.union_all()

if union_result.geom_type == 'GeometryCollection':
    kontur_polski = union_result.buffer(0)
else:
    kontur_polski = union_result

izochrony['geometry'] = izochrony.geometry.make_valid()
izochrony = gpd.clip(izochrony, kontur_polski)

# Nazwa kolumny z danymi
col_adopcje = 'Liczba zwierząt adoptowanych w 2024 roku'

schroniska_w_powiatach = gpd.sjoin(schroniska, powiaty, predicate='within')
suma_adopcji = schroniska_w_powiatach.groupby('nazwa')[col_adopcje].sum().reset_index()
powiaty_dane = powiaty.merge(suma_adopcji, on='nazwa', how='left').fillna({col_adopcje: 0})

# KOLORY
kolory_szare_gradient = ['#e9ecef', '#adb5bd', '#343a40']
cmap_fundacji = LinearSegmentedColormap.from_list("WDF_Gray", kolory_szare_gradient)

# --- TWORZENIE MAPY ---
fig, ax = plt.subplots(figsize=(12, 12))

# Rysowanie powiatów
powiaty_dane.plot(
    column=col_adopcje,
    scheme='UserDefined',
    classification_kwds={'bins': [50, 200, 500, 1000]},
    cmap=cmap_fundacji,
    edgecolor='#092e5a',
    linewidth=0.4,
    ax=ax,
    legend=False
)

# Rysowanie izochron
izochrony.plot(ax=ax, color='#0fa589', alpha=0.25, edgecolor='#0fa589', linewidth=0.6, zorder=3)

# Rysowanie trenerów
trenerzy.plot(ax=ax, color='#ed4c3f', marker='o', markersize=90,
              edgecolor='#092e5a', linewidth=1, zorder=10, alpha=1)

# --- LEGENDA ---
n_klas = 5
kolory_z_mapy = [cmap_fundacji(i / (n_klas - 1)) for i in range(n_klas)]
etykiety = ['0 - 50', '51 - 200', '201 - 500', '501 - 1000', 'powyżej 1000']

legenda_elementy = [
    mpatches.Patch(facecolor=kolory_z_mapy[i], edgecolor='#092e5a', linewidth=0.5, label=etykiety[i])
    for i in range(len(etykiety))
]
legenda_elementy.append(Line2D([0], [0], color='none', label=' '))
legenda_elementy.append(Line2D([0], [0], marker='o', color='none', label='Jeden trener',
                               markerfacecolor='#ed4c3f', markeredgecolor='#092e5a',
                               markeredgewidth=1, markersize=10, ls=''))
legenda_elementy.append(Line2D([0], [0], color='none', label=' '))
legenda_elementy.append(mpatches.Patch(facecolor='#0fa589', alpha=0.25, edgecolor='#0fa589',
                                     linewidth=0.6, label='Obszar działań edukacyjnych\ni eventowych (do 1h dojazdu)'))

legenda = ax.legend(handles=legenda_elementy, title="Liczba adopcji (2024)\n", loc='lower right',
                    bbox_to_anchor=(1.24, 0.02), frameon=False, labelspacing=0.0,
                    handleheight=2.0, handlelength=2.5, prop=prop_tekst_legendy)

legenda._legend_box.align = "left"
plt.setp(legenda.get_texts(), color='#092e5a')
plt.setp(legenda.get_title(), fontproperties=prop_tytul_legendy, color='#092e5a', multialignment='center')

# --- PODZIAŁKA ---
def dodaj_podzialke_szachownicowa(ax, dlugosc_km=100):
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    x_start = xmin + (xmax - xmin) * 0.04
    y_start = ymin + (ymax - ymin) * 0.25
    dl_m = dlugosc_km * 1000
    segment = dl_m / 4
    wysokosc = (ymax - ymin) * 0.01
    for i in range(4):
        kolor = '#092e5a' if i % 2 == 0 else 'white'
        ax.add_patch(Rectangle((x_start + i * segment, y_start), segment, wysokosc,
                               facecolor=kolor, edgecolor='#092e5a', linewidth=0.8, zorder=10))
    offset = wysokosc * 1.5
    ax.text(x_start, y_start - offset, "0", ha='center', fontsize=8, fontproperties=prop_tekst, color='#092e5a')
    ax.text(x_start + 2 * segment, y_start - offset, f"{dlugosc_km // 2}", ha='center', fontsize=8, fontproperties=prop_tekst, color='#092e5a')
    ax.text(x_start + 4 * segment, y_start - offset, f"{dlugosc_km} km", ha='center', fontsize=8, fontproperties=prop_tekst, color='#092e5a')

dodaj_podzialke_szachownicowa(ax)

# --- ASSETY GRAFICZNE (tabela, logo Fundacji, KPI) ---
def wstaw_grafike(ax, path, pos, zoom, anchor=(0.5, 0.5)):
    if os.path.exists(path):
        img = mpimg.imread(path)
        ab = AnnotationBbox(OffsetImage(img, zoom=zoom, resample=True), pos,
                            xycoords='axes fraction', frameon=False, box_alignment=anchor)
        ax.add_artist(ab)

wstaw_grafike(ax, PATH_TABLE, (1.095, 0.60), 0.6)
wstaw_grafike(ax, PATH_LOGO, (1.22, 1.085), 0.10, anchor=(1, 1))
wstaw_grafike(ax, PATH_KPI1, (1.07, 0.93), 0.35)
wstaw_grafike(ax, PATH_KPI2, (0.025, 0.12), 0.35, anchor=(0, 0.5))

# --- OPISY ---
plt.title("Rozmieszczenie liczby adopcji psów ze schronisk wg powiatów 2024 \n Lokalizacje trenerów w projekcie Adopsiaki",
          fontproperties=prop_tytul, fontweight='bold', color='#092e5a', pad=10, linespacing=1.8)

plt.figtext(0.04, 0.06, "opracowanie: Agnieszka Trzciałkowska, 2026 | źródło: dane GIW, Working Dogs Foundation",
            fontsize=9, color='#092e5a', style='italic')

insight_tekst = (
    "Zielone strefy wyznaczają gotowość fundacji do pomocy #Adopsiakom, warsztatów szkolnych i eventów firmowych.\n"
    "Obszary o wysokiej liczbie adopcji poza zasięgiem trenerów stanowią priorytet dla przyszłego rozwoju Fundacji."
)
plt.figtext(0.04, 0.095, insight_tekst, fontproperties=font_manager.FontProperties(fname=PATH_HAUORA, size=12),
            color='#0fa589', ha='left', va='bottom', linespacing=1.6)

ax.set_axis_off()
plt.tight_layout()
plt.savefig(PATH_FINAL_PNG, dpi=1200, bbox_inches='tight')
print(f"Sukces! MApa została zapisana w: {PATH_FINAL_PNG}")
plt.show()