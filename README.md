# Road Infrastructure – Minecraft Bedrock Addon

Infrastruktura drogowa dla Minecraft Bedrock Edition.

## 📋 Opis

Ten addon dodaje do Minecraft kompletną infrastrukturę drogową, w tym:

- Bloki dróg (różne szerokości i wzory)
- Oznaczenia drogowe (linie, strzałki, znaki)
- Elementy chodników (kostka brukowa, krawężniki)
- Przejścia dla pieszych
- Elementy bezpieczeństwa drogowego

## 🛣️ Zawartość

### Kategorie bloków

#### 🛣️ Drogi (Roads)

- **Drogi podstawowe** – 16 różnych wzorów dróg
- **Oznaczenia proste** — linie poziome i pionowe
- **Oznaczenia ukośne** — linie ukośne w różnych wzorach
- **Oznaczenia V-style** – wzory w kształcie litery V
- **Znaki drogowe** — strzałki, stop, znaki podporządkowania

#### 🚶 Chodniki (Pedestrian)

- **Kostka brukowa** — różne wzory i kolory
- **Krawężniki** — elementy krawędziowe
- **Przejścia dla pieszych** – pasy zebry

#### 🔄 Elementy skrętów

- **Oznaczenia skrętów 3D** – trójwymiarowe elementy
- **Oznaczenia kątowe** – elementy narożne

## 🏗️ Budowanie

### GitHub Actions (Automatyczne)

Projekt używa GitHub Actions do automatycznego budowania i wydawania wersji.

- **Weryfikacja projektu** — sprawdza integralność przed budowaniem
- **Automatyczne budowanie** przy każdym push do main/master
- **Testowanie** struktury projektu i manifestów
- **Automatyczne releases** z auto-version bump
- **Integracja** – jeden workflow dla build, test i release

### Wymagania

- **Minecraft Bedrock** — z eksperymentalnymi funkcjami
- **Python** 3.7+ – do budowania paczek

### Środowisko wirtualne (venv) - macOS

Przed uruchomieniem skryptów na macOS, zalecane jest utworzenie środowiska wirtualnego:

- Automatyczna konfiguracja (zalecane)
```bash
./setup_venv.sh
```

- Aktywuj środowisko
```bash
source venv/bin/activate
```

### Weryfikacja projektu

Przed budowaniem, możesz uruchomić pełną weryfikację projektu:

```bash
python3 verify_all.py
```

## 🛠️ Instalacja

### Lokalnie (Minecraft Bedrock)

#### Metoda 1: Automatyczna instalacja (zalecana)

1. Pobierz plik `.mcaddon` z
   sekcji [Releases](https://github.com/Flower7C3/road-infrastructure-minecraft-bedrock-addon/releases)
2. Uruchom skrypt instalacji:
   ```bash
   python3 build.py --mcaddon --test-on-local
   ```
3. Uruchom Minecraft i włącz paczki (patrz sekcja "Aktywacja w grze")

#### Metoda 2: Ręczna instalacja

1. Pobierz plik `.mcaddon` z
   sekcji [Releases](https://github.com/Flower7C3/road-infrastructure-minecraft-bedrock-addon/releases)
2. Otwórz plik w Minecraft Bedrock
3. Aktywuj paczkę w ustawieniach → Global Resources

### Na serwerze (Aternos)

1. Pobierz pliki `.mcpack` (BP i RP)
2. Wgraj oba pliki na serwer Aternos
3. Uruchom serwer

### Aktywacja w grze

Po zainstalowaniu paczek musisz je aktywować w Minecraft:

1. **Zamknij Minecraft** (jeśli jest uruchomiony)

2. **Otwórz Minecraft** i przejdź do:
    - Ustawienia → Zasoby globalne
    - Znajdź "Road Infrastructure RP" i włącz ją (przesuń na prawą stronę)

3. **Włącz eksperymenty**:
    - Przejdź do Ustawienia → Eksperymenty
    - Włącz "Holiday Creator Features" (wymagane dla niestandardowych bloków)

4. **Utwórz lub edytuj świat**:
    - Utwórz nowy świat lub edytuj istniejący
    - W ustawieniach świata upewnij się, że "Holiday Creator Features" jest włączone
    - Paczka zachowań powinna być automatycznie włączona po włączeniu paczki zasobów

5. **Przetestuj bloki**:
    - W grze otwórz swój ekwipunek
    - Znajdź infrastrukturę drogową w kreatywnym ekwipunku
    - Powinny pojawić się jako niestandardowe bloki

## Rozwiązywanie problemów

Jeśli nie widzisz bloków w grze:

1. **Sprawdź, czy używasz właściwego launcher'a Minecraft**: Paczki są zainstalowane dla mcpelauncher. Upewnij się, że
   używasz tego launcher'a, a nie oficjalnego launcher'a Minecraft.

2. **Spróbuj świeżego świata**: Utwórz całkowicie nowy świat z włączonymi "Holiday Creator Features".

3. **Sprawdź wersję gry**: Upewnij się, że używasz Minecraft Bedrock Edition w wersji 1.16.0 lub wyższej.

4. **Uruchom ponownie Minecraft**: Czasami musisz całkowicie uruchomić ponownie Minecraft po zainstalowaniu paczek.

5. **Sprawdź, czy paczki są zainstalowane**:
   ```bash
   # Sprawdź czy paczki są w odpowiednim katalogu
   ls "/Users/bartlomiej.kwiatek/Library/Application Support/mcpelauncher/games/com.mojang/behavior_packs/RoadInfrastructure"
   ls "/Users/bartlomiej.kwiatek/Library/Application Support/mcpelauncher/games/com.mojang/resource_packs/RoadInfrastructure"
   ```

## 🤝 Współpraca

### Dodawanie nowych bloków

1. Utwórz plik `.block.json` w odpowiednim katalogu
2. Dodaj teksturę w `RP/textures/blocks/`
3. Zaktualizuj `terrain_texture.json`
4. Dodaj tłumaczenia w `RP/texts/`
5. Zaktualizuj `crafting_item_catalog.json`

## 📝 Licencja

Ten projekt jest udostępniany na licencji MIT. Zobacz plik [LICENSE](LICENSE) dla szczegółów.

## 👥 Autorzy

- **Flower7C3** – główny developer
- **MrBoT10** – twórca pierwotnego dodatku
- **Współpraca** – poprawki i sugestie

---

**Road Infrastructure** – Tworzenie realistycznej infrastruktury drogowej w Minecraft Bedrock Edition.
