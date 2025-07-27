# 🔄 Przewodnik Migracji Namespace

## 📋 Opis

Ten przewodnik opisuje proces migracji namespace z `cityroads` na `road_infrastructure` w projekcie City Roads.

## 🚀 Krok 1: Migracja Projektu

Projekt został już zaktualizowany przez skrypt `migrate_namespace.py`.

### Zmienione Pliki:
- ✅ `config.json` - namespace zaktualizowany
- ✅ Wszystkie pliki `.block.json` - identyfikatory zaktualizowane
- ✅ `crafting_item_catalog.json` - referencje zaktualizowane
- ✅ Pliki lokalizacji (`.lang`) - nazwy zaktualizowane
- ✅ `blocks.json` - klucze zaktualizowane

## 🌍 Krok 2: Migracja Świata

### Opcje Migracji:

#### Opcja A: Automatyczna Migracja (Zalecana)
```bash
python3 migrate_world_cityroads_to_road_infrastructure.py
```

#### Opcja B: Ręczna Migracja
1. **Zamknij Minecraft**
2. **Utwórz kopię zapasową świata**
3. **Zaktualizuj pliki świata** (level.dat, chunki)
4. **Uruchom Minecraft i przetestuj**

## ⚠️ Ważne Uwagi

### Przed Migracją:
- ✅ Zamknij Minecraft
- ✅ Utwórz kopię zapasową świata
- ✅ Sprawdź czy masz kopię zapasową projektu

### Po Migracji:
- ✅ Uruchom Minecraft
- ✅ Sprawdź czy bloki działają poprawnie
- ✅ Przetestuj wszystkie funkcjonalności

## 🔧 Rozwiązywanie Problemów

### Problem: Bloki nie wyświetlają się
**Rozwiązanie:** Sprawdź czy:
- Namespace został poprawnie zmieniony we wszystkich plikach
- Świat został zaktualizowany
- Minecraft został uruchomiony ponownie

### Problem: Błędy w grze
**Rozwiązanie:** 
- Przywróć kopię zapasową świata
- Sprawdź logi Minecraft
- Upewnij się, że wszystkie pliki są spójne

## 📊 Status Migracji

- ✅ Projekt: Zaktualizowany
- ⏳ Świat: Wymaga migracji
- ⏳ Testowanie: Wymagane

## 🎯 Następne Kroki

1. **Uruchom skrypt migracji świata**
2. **Przetestuj w Minecraft**
3. **Zaktualizuj dokumentację**
4. **Wypchnij zmiany na Git**

---
*Wygenerowano automatycznie przez skrypt migracji*
