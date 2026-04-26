
# Geoanaliza potencjału rozwoju sieci trenerów #Adopsiaki Working Dogs Foundation

Projekt realizowany w ramach **BI_NGO 2026** dla Working Dogs Foundation
[Link(]https://bingo.jezykdanych.pl/)
Analiza przestrzenna i statystyczna rozwoju Fundacji, która skupia się na pomocy rodzinom adoptującym psy ze schronisk oraz organizacji warsztatów i eventów przez trenerów w całej Polsce. [Link](https://workingdogs.pl/)

**Cel:** Głównym celem analizy było zidentyfikowanie korelacji między liczbą adopcji psów w 2024 roku (dane GIW) a realnym zasięgiem wsparcia oferowanego przez sieć trenerów Fundacji Working Dogs. 
Projekt służy jako narzędzie decyzyjne do optymalizacji rekrutacji nowych trenerów oraz planowania działań edukacyjnych w regionach o największym zapotrzebowaniu.

## Kluczowe wnioski i KPI

### Potencjał rozwoju
79% powierzchni Polski znajduje się obecnie poza stałym zasięgiem operacyjnym trenerów (przy założeniu 60-minutowego dojazdu).

### Obszary do intensywnego poszukiwania trenerów
Zidentyfikowano liczne powiaty o bardzo wysokiej aktywności adopcyjnej (powyżej 500-1000 psów rocznie), które nie posiadają wsparcia trenerskiego (m.in. powiaty: **augustowski, bydgoski, wieruszowski**)

### Nierównomierność zasięgu
Centralna i południowa Polska wykazują wykazują najlepsze nasycenie usługami Fundacji, podczas gdy ściana wschodnia i zachodnia stanowi ogromny, niezagospodarowany potencjał dla misji Fundacji i wymagają intensyfikacji działań rekrutacyjnych trenerów i wolontariuszy.

![Geoanaliza_Working_Dogs](wizualizacje/BI_NGO_Working_Dogs_Trzcialkowska.png)

---

## Metodologia projektu

Całość prac została wykonana w języku **Python** przy wykorzystaniu zewnętrznych API i bibliotek analitycznych. Projekt utworzony w oparciu o ścieżki relatywne. 
Kod starałam się pisać zgodnie ze standardami PEP 8.
**Użyte w projekcie biblioteki Python:** 
* **pandas** - praca na danych tabelarycznych, agregacja statystyk adopcji
* **geopandas** - główny silnik do pracy na danych przestrzennych (GeoJSON, układy współrzędnych)
* **geopy** - geokodowanie adresów (zamiana lokalizacji tekstowych na współrzędne geograficzne)
* **os** - zarządzanie dynamicznymi ścieżkami dostępu do plików w strukturze projektu
* **openpyxl** - obsługa i odczyt danych bezpośrednio z arkuszy Excel (źródła GIW)
* **dataframe_image** - renderowanie tabel z danymi do formatu plików graficznych (PNG)
* **openrouteservice** - integracja z API w celu generowania izochron (zasięgów czasowych dojazdu)
* **python-dotenv** - bezpieczne zarządzanie kluczami API poza kodem źródłowym
* **shapely** - zaawansowane operacje geometryczne (walidacja topologii, buforowanie i przycinanie do konturu Polski)
* **matplotlib** - zaawansowana wizualizacja danych, projektowanie kompozycji arkusza i finalny rendering mapy
* **mapclassify** - obliczenia statystyczne dla kartogramu (klasyfikacja danych metodą User Defined)

Proces analizy został podzielony na trzy główne etapy: 

### 1. Pozyskanie i transformacja danych (ETL)

1. **Źródła danych**
   Dane statystyczne dotyczące liczby adopcji oraz lokalizacji placówek zostały pozyskane bezpośrednio z rejestrów Głównego Inspektoratu Weterynarii (GIW) (udostęnione na mój wniosek o udostęnienie danych publicznych) - znajdują się w folderze `/dane`
   Dane dotyczące lokalizacji trenerów i działalności Fundacji pochodzą z zasobów Working Dogs Foundation - [Link](https://github.com/bi-ngo-wolontariat/BI_NGO-2026-Working-Dogs-Foundation/blob/main/README.md)
   Dane dotyczące lokalizacji powiatów - z zewnętrznego źródła GeoJSON: [Link](https://raw.githubusercontent.com/ppatrzyk/polska-geojson/master/powiaty/powiaty-min.geojson)

2. **Transformacja**
   Przygotowanie danych statystycznych do analizy (Excel i Power Query). Oczyszczenie danych, złączenie danych z wielu plików, usunięcie niepotrzebnych rekordów, wyciągnięcie czystych adresów.

3. **Geokodowanie**
   Autorski skrypt Python do automatycznej konwersji adresów tekstowych na współrzędne geograficzne (latitude, longitude).
   * [geokodowanie_schronisk.py](skrypty/geokodowanie_schronisk.py)
   * [geokodowanie_trenerow.py](skrypty/geokodowanie_trenerow.py)

4. **Agregacja**
   Dane o liczbie adopcji w schroniskach zostały zsumowane do poziomu powiatów w celu stworzenia czytelnego obrazu natężenia zjawiska. Przypisanie nazw powiatów do poszczególnych rekordów na podstawie adresów schronisk.
   * [przypisane_nazw_powiatu.py](skrypty/przypisane_nazw_powiatu.py)

5. **Serializacja**
   Przetworzone dane zostały zapisane w formacie **GEOJSON**, co umożliwiło szybkie wczytywanie współrzędnych w kolejnych etapach bez konieczności powtarzań zapytań do API.

### 2. Analiza przestrzenna i dostępność

1. **Kartogram**
   Utworzenie warstwy natężenia adopcji w 5-stopniowej skali nasycenia koloru (od 0 do >1000 adopcji), aby zobrazować intensywność zjawiska w poszczególnych powiatach.

2. **Izochrony**
   Przy użyciu API **OpenRouteService**, dla każdej lokalizacji trenera wygenerowano izochrony, czyli obszary wskazujące czas rzeczywistego dojazdu (uwzględniające infrastrukturę drogową). Założono wariant optymistyczny - trener jest w stanie obsługiwać teren do 60 minut dojazdu. Zasięgi obliczono przy użyciu algorytmów OpenRouteService w oparciu o sieć drogową OpenStreetMap, przyjmując 60-minutowy czas dojazdu samochodem w warunkach płynnego ruchu.

3. **Warstwy danych**
   Projekt wykorzystuje nakładanie warstw – na statystyczny obraz adopcji (kartogram) nałożono punkty lokalizacji trenerów oraz zasięgi ich dojazdu (izochrony).

4. **Wskaźnik KPI**
   Utworzenie skryptu liczącego obszar wolny od działań Fundacji. Obliczono różnicę między łączną powierzchnią izochron (przez rozpuszczanie), a całkowitą powierzchnią kraju, wyznaczając procentowy brak pokrycia usługami Fundacji.
   * skrypt: [KPI.py](skrypty/KPI.py)

   Utworzenie skryptu tworzącego tabelę Top 10 powiatów wg liczby adopcji, ułatwiająca szybką identyfikację priorytetowych obszarów
   * skrypt: [tabela_top10_adopcji.py](skrypty/tabela_top10_adopcji.py)

### 3. Wizualizacja i wnioskowanie

1. **Wizualizacja**
   Autorski skrypt łączący pliki cząstkowe (GeoJSON, xlsx) w jedną mapę. W celu prawidłowej percepcji mapy na obrazie wynikowym skryptu dodano tytuł, legendę oraz skalę mapy, zachowując zgodność z zasadami kartografii. Jest to zaawansowana wizualizacja przestrzenna łącząca metodę kartogramu (liczba adopcji w powiatach) z metodą sygnaturową punktową (lokalizacje trenerów) oraz metodą izochron (zasięg dojazdu 60 min). Skrypt integruje dane geograficzne z elementami Business Intelligence (KPI) w celu identyfikacji luk w sieci wsparcia Fundacji.
   * [geo_analiza_wdf_2024.py](skrypty/geo_analiza_wdf_2024.py)

2. **Wnioski**
   Analiza wskazuje na istnienie powiatów o bardzo wysokiej aktywności adopcyjnej (powyżej 500-1000 psów rocznie), które znajdują się całkowicie poza zasięgiem operacyjnym trenerów (poza strefą 1h dojazdu). 
   
   Zielone strefy (izochrony) pokrywają znaczną część zachodniej i centralnej Polski, co potwierdza dobre osadzenie projektu #Adopsiaki w tych regionach, jednak wschodnia część kraju wykazuje duży, niezagospodarowany potencjał. Potencjał rozwoju Fundacji w Polsce: **79% obszaru do zagospodarowania** przez działalność Fundacji.

   Rejony o najwyższym nasyceniu adopcji to miejsca, gdzie zapotrzebowanie na warsztaty behawioralne i eventy edukacyjne jest największe, a obecnie nie jest w pełni zaspokojone, są to m.in. powiaty: **wieruszowski, bydgoski, augustowski, czarnkowsko - trzcianecki, m. Toruń, grudziądzki, choszczeński, ostrołęcki**. Obszary o wysokiej liczbie adopcji (kartogram) poza zasięgiem trenerów stanowią priorytet dla przyszłego rozwoju sieci #Adopsiaki, niesienia pomocy pomocy rodzinom z adopcją, warsztatów szkolnych i eventów firmowych.

3. **Rekomendacje**
   * Poszukiwać trenerów w obszarach o wysokiej adopcji (wg skali kartogramu), a znajdujących się poza obszarem izochron (zielony). 
   * Skierować działania rekrutacyjne do trenerów z powiatów: wieruszowskiego, bydgoskiego oraz augustowskiego, czarnkowsko-trzcianeckiego, m. Toruń...
   * Skupić działania wizerunkowe w powiatach o niskiej adopcji, ale obecności trenerów.
   * Realizować duże wydarzenia edukacyjne w "ciemnych" powiatach o wysokiej adopcji w celu przyciągnięcia lokalnych specjalistów do współpracy.

4. **Refleksja**
   Projekt ten jest nie tylko analizą danych, ale krokiem w stronę zwiększenia dobrostanu zwierząt po adopcji. Celem nadrzędnym jest doprowadzenie do momentu, w którym cała mapa Polski pokryje się zielonymi strefami dostępnego wsparcia behawioralnego.

**Użyte technologie:** Python (Pandas, Matplotlib, Requests), OpenRouteService API, JSON, Excel/Power Query.

---

### Instalacja i przygotowanie środowiska

W celu uruchomienia skryptu należy zainstalować biblioteki użyte w projekcie: 

```bash
pip install pandas geopandas geopy matplotlib mapclassify shapely openpyxl dataframe_image openrouteservice python-dotenv
```

## Licencja

Copyright (c) 2026 Agnieszka Trzciałkowska. Wszystkie prawa zastrzeżone.
Kopiowanie, rozpowszechnianie oraz wykorzystywanie kodu bez zgody autora jest zabronione.
