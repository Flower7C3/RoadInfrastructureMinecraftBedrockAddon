# 🔍 Skrypt Weryfikacji Tekstur - CityBuildingKit

## 📋 Opis

Skrypt `verify_textures.py` służy do weryfikacji integralności tekstur w projekcie Minecraft CityBuildingKit. Sprawdza czy wszystkie bloki mają odpowiednie tekstury i czy wszystkie tekstury są poprawnie zmapowane.

## 🚀 Użycie

```bash
python3 verify_textures.py
```

## 🔍 Funkcje Weryfikacji

### 1. **Weryfikacja Mapowania Terrain_Texture.json**
- Sprawdza czy wszystkie wpisy w `RP/textures/terrain_texture.json` mają odpowiadające pliki tekstur
- Wykrywa brakujące pliki tekstur
- Wyświetla podsumowanie poprawnych i błędnych mapowań

### 2. **Weryfikacja Bloków i Tekstur**
- Analizuje wszystkie pliki `.block.json` w katalogu `BP/blocks/`
- Sprawdza czy bloki mają zdefiniowane tekstury
- Weryfikuje czy pliki tekstur istnieją dla każdego bloku
- Wyświetla bloki bez tekstur (używają domyślnych)

### 3. **Weryfikacja Nieużywanych Tekstur**
- Sprawdza czy wszystkie pliki tekstur są używane w `terrain_texture.json`
- Wykrywa nieużywane pliki tekstur
- Wyświetla podsumowanie używanych i nieużywanych tekstur

## 📊 Przykład Wyniku

```
🔍 WERYFIKACJA PROJEKTU CITYBUILDINGKIT
============================================================

🔍 WERYFIKACJA MAPOWANIA TERRAIN_TEXTURE.JSON
============================================================
✅ kerbstone -> kerbstone.png
✅ paving_slabs_squares -> paving_slabs_squares.png
✅ paving_slabs_flower -> paving_slabs_flower.png
✅ paving_slabs_ceramic -> paving_slabs_ceramic.png
...

📊 PODSUMOWANIE:
   ✅ Poprawne mapowania: 26
   ❌ Brakujące tekstury: 0

🔍 WERYFIKACJA BLOKÓW I TEKSTUR
============================================================
⚠️  jct:base_road_1 -> BRAK TEKSTURY
⚠️  jct:base_road_2 -> BRAK TEKSTURY
...
✅ jct:paving_slabs_ceramic -> paving_slabs_ceramic
✅ jct:paving_slabs_colorstone -> paving_slabs_colorstone
...

📊 PODSUMOWANIE BLOKÓW:
   ✅ Poprawne bloki: 49
   ❌ Błędne bloki: 20

🔍 WERYFIKACJA NIEUŻYWANYCH TEKSTUR
============================================================
📊 PODSUMOWANIE TEKSTUR:
   📁 Wszystkie tekstury: 26
   ✅ Używane tekstury: 26
   🗑️  Nieużywane tekstury: 0

✅ WERYFIKACJA ZAKOŃCZONA
```

## 🎯 Legenda

- **✅** - Poprawny wpis/tekstura
- **❌** - Błędny wpis/brakująca tekstura
- **⚠️** - Blok bez tekstury (używa domyślnej)

## 📁 Struktura Plików

Skrypt sprawdza następujące katalogi:
- `BP/blocks/` - pliki bloków (`.block.json`)
- `RP/textures/blocks/` - pliki tekstur (`.png`, `.jpg`, `.jpeg`)
- `RP/textures/terrain_texture.json` - mapowanie tekstur

## 🔧 Wymagania

- Python 3.6+
- Biblioteki standardowe: `json`, `os`, `glob`, `pathlib`

## 🛠️ Rozwiązywanie Problemów

### Brakujące Tekstury
Jeśli skrypt wykryje brakujące tekstury:
1. Sprawdź czy plik istnieje w `RP/textures/blocks/`
2. Sprawdź czy nazwa w `terrain_texture.json` odpowiada nazwie pliku
3. Upewnij się, że rozszerzenie pliku jest poprawne (`.png`, `.jpg`, `.jpeg`)

### Bloki Bez Tekstur
Bloki bez tekstur używają domyślnych tekstur Minecraft. To jest normalne dla:
- Bloków podstawowych (np. `base_road_X`)
- Bloków z domyślnymi teksturami

### Nieużywane Tekstury
Jeśli skrypt wykryje nieużywane tekstury:
1. Sprawdź czy tekstura jest rzeczywiście potrzebna
2. Dodaj wpis do `terrain_texture.json` jeśli tekstura jest używana
3. Usuń plik tekstury jeśli nie jest potrzebny

## 📝 Historia

- **v1.0** - Pierwsza wersja skryptu
- Dodano weryfikację mapowania terrain_texture.json
- Dodano weryfikację bloków i tekstur
- Dodano weryfikację nieużywanych tekstur
- Naprawiono problemy z duplikatami tekstur 