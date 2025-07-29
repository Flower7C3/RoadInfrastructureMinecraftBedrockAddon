# Road Infrastructure – Minecraft Bedrock Addon

Infrastruktura drogowa dla Minecraft Bedrock Edition.

---

## 📋 Opis

Ten dodatek umożliwia tworzenie realistycznej infrastruktury drogowej, w tym:

- Bloki dróg (16 różnych wysokości)
- Oznaczenia drogowe (linie, strzałki, znaki poziome)
- Elementy chodników (kostka brukowa, krawężniki)
- Przejścia dla pieszych (pasy zebry)

---

## 🛠️ Instalacja

### 🏠 Lokalnie (Minecraft Bedrock) ze zbudowanych paczek

1. Pobierz plik `.mcaddon` z
   sekcji [Releases](https://github.com/Flower7C3/road-infrastructure-minecraft-bedrock-addon/releases)
2. Otwórz go w Minecraft Bedrock
3. Włącz paczki:
    - Ustawienia → Zasoby globalne
    - Znajdź "Road Infrastructure RP" i włącz ją (przesuń na prawą stronę)
4. Włącz eksperymenty:
    - Przejdź do Ustawienia → Eksperymenty
    - Włącz "Holiday Creator Features" (wymagane dla niestandardowych bloków)
5. Utwórz lub edytuj świat:
    - Utwórz nowy świat lub edytuj istniejący
    - W ustawieniach świata upewnij się, że "Holiday Creator Features" jest włączone
    - Paczka zachowań powinna być automatycznie włączona po włączeniu paczki zasobów

### 🌐 Na serwerze (Aternos)

1. Pobierz pliki `.mcpack` z
   sekcji [Releases](https://github.com/Flower7C3/road-infrastructure-minecraft-bedrock-addon/releases)
2. Wgraj je na serwer Aternos
3. Uruchom serwer i dołącz do gry

> Pliki paczki możesz również zbudować lokalnie. Zobacz więcej w sekcji [Budowanie](#%EF%B8%8F-budowanie)").

### 🔧 Rozwiązywanie problemów

Jeśli nie widzisz bloków w grze:

1. **Sprawdź, czy używasz właściwego launcher'a Minecraft**: Paczki są zainstalowane dla mcpelauncher. Upewnij się, że
   używasz tego launcher'a, a nie oficjalnego launcher'a Minecraft.

2. **Spróbuj świeżego świata**: Utwórz całkowicie nowy świat z włączonymi "Holiday Creator Features".

3. **Sprawdź wersję gry**: Upewnij się, że używasz Minecraft Bedrock Edition w wersji 1.16.0 lub wyższej.

4. **Uruchom ponownie Minecraft**: Czasami musisz całkowicie uruchomić ponownie Minecraft po zainstalowaniu paczek.

5. **Sprawdź, czy paczki są zainstalowane w odpowiednim katalogu**, np.:
   ```bash
   # Sprawdź czy paczki są w odpowiednim katalogu
   ls "/Users/bartlomiej.kwiatek/Library/Application Support/mcpelauncher/games/com.mojang/behavior_packs/RoadInfrastructure"
   ls "/Users/bartlomiej.kwiatek/Library/Application Support/mcpelauncher/games/com.mojang/resource_packs/RoadInfrastructure"
   ```

---

## 🏗️ Budowanie

### 🤖 GitHub Actions (Automatyczne)

Projekt używa GitHub Actions do automatycznego budowania i wydawania wersji.

- **Weryfikacja projektu** — sprawdza integralność przed budowaniem
- **Automatyczne budowanie** przy każdym push do main/master
- **Testowanie** struktury projektu i manifestów
- **Automatyczne releases** z auto-version bump
- **Integracja** – jeden workflow dla build, test i release

### 💻 Lokalnie

> #### Wymagania
> - **Minecraft Bedrock** — z eksperymentalnymi funkcjami
> - **Python** 3.7+ – do budowania paczek

Pobierz repozytorium i wejdź do katalogu projektu:

```bash
git clone https://github.com/Flower7C3/road-infrastructure-minecraft-bedrock-addon.git
cd road-infrastructure-minecraft-bedrock-addon
```

> #### Środowisko wirtualne (venv) - macOS
> Przed uruchomieniem skryptów na macOS, zalecane jest utworzenie i uruchomienie środowiska wirtualnego:
> ```bash
> ./setup_venv.sh
> source venv/bin/activate
> ```

Przed budowaniem, możesz uruchomić pełną weryfikację projektu:

```bash
python3 verify_all.py
```

Skrypt `verify_all.py` zawiera kompleksową weryfikację całego projektu, w tym:
- **Struktura projektu** - sprawdza wymagane pliki i katalogi
- **Manifesty** - weryfikuje poprawność manifestów BP i RP
- **Konfiguracja** - sprawdza `config.json` i namespace
- **Bloki** - weryfikuje wszystkie pliki bloków
- **Tekstury** - szczegółowa analiza mapowania w `terrain_texture.json`, weryfikacja bloków i tekstur, sprawdzanie nieużywanych tekstur
- **Lokalizacja** - sprawdza pliki tłumaczeń
- **Skrypt budowania** - weryfikuje `build.py`

Gdy już wszystko gotowe możesz uruchomić skrypt budowania, który pokaże dostępne opcje:

```bash
python3 build.py
```

Np. możesz uruchomić skrypt budowania z instalacją bez podnoszenia wersji:

```bash
python3 build.py --mcaddon --test-on-local --no-bump
```

### Dodawanie nowych bloków

1. Utwórz plik `.block.json` w odpowiednim katalogu
2. Dodaj teksturę w `RP/textures/blocks/`
3. Zaktualizuj `terrain_texture.json`
4. Dodaj tłumaczenia w `RP/texts/`
5. Zaktualizuj `crafting_item_catalog.json`

Gdy dodasz nowe bloki uruchom skrypt weryfikacji i zbuduj projekt.

---

## 🛠️ Narzędzia i stylizacja

### Stylizacja konsoli

Projekt używa zaawansowanej stylizacji konsoli z biblioteki `console_utils.py`:

- **Kolorowe komunikaty** - różne kolory dla różnych typów komunikatów
- **Emoji** - wizualne oznaczenia dla różnych operacji
- **Profesjonalne formatowanie** - nagłówki sekcji, separatory, statystyki
- **Obsługa trybu cichego** - dla CI/CD i automatyzacji

### Dostępne skrypty

| Skrypt | Opis | Użycie |
|--------|------|--------|
| `verify_all.py` | Kompleksowa weryfikacja projektu | `python3 verify_all.py` |
| `build.py` | Budowanie paczek Minecraft | `python3 build.py --help` |
| `console_utils.py` | Biblioteka stylizacji konsoli | Importowana przez inne skrypty |

### Przykłady użycia

```bash
# Weryfikacja projektu
python3 verify_all.py

# Budowanie z instalacją lokalną
python3 build.py --mcaddon --test-on-local --no-bump

# Budowanie wszystkich typów paczek
python3 build.py --all

# Tylko budowanie .mcpack
python3 build.py --mcpack
```

---

## 📝 Licencja

Ten projekt jest udostępniany na licencji MIT. Zobacz plik [LICENSE](LICENSE) dla szczegółów.

---

## 👥 Autorzy

- **Flower7C3** – główny developer
- **MrBoT10** – twórca pierwotnego dodatku
- **Współpraca** – poprawki i sugestie
