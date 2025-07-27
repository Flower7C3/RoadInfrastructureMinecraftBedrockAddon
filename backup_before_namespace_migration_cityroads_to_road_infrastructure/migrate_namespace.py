#!/usr/bin/env python3
"""
Skrypt do migracji namespace z 'jct' na 'cityroads'
Automatycznie aktualizuje wszystkie pliki projektu i tworzy skrypt do aktualizacji bloków na świecie
"""

import os
import json
import glob
import shutil
from pathlib import Path

# Konfiguracja migracji
OLD_NAMESPACE = "cityroads"
NEW_NAMESPACE = "road_infrastructure"

def backup_project():
    """Tworzy kopię zapasową projektu przed migracją"""
    backup_dir = f"backup_before_namespace_migration_{OLD_NAMESPACE}_to_{NEW_NAMESPACE}"
    if os.path.exists(backup_dir):
        shutil.rmtree(backup_dir)
    
    print(f"📦 Tworzenie kopii zapasowej: {backup_dir}")
    shutil.copytree(".", backup_dir, ignore=shutil.ignore_patterns(
        "backup_*", "dist", "venv", "__pycache__", "*.pyc", ".git"
    ))
    print(f"✅ Kopia zapasowa utworzona: {backup_dir}")
    return backup_dir

def update_config_json():
    """Aktualizuje config.json"""
    print("🔧 Aktualizacja config.json...")
    
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    
    config["namespace"] = NEW_NAMESPACE
    
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent="\t", ensure_ascii=False)
    
    print("✅ config.json zaktualizowany")

def update_block_files():
    """Aktualizuje wszystkie pliki .block.json"""
    print("🔧 Aktualizacja plików .block.json...")
    
    block_files = glob.glob("BP/blocks/**/*.block.json", recursive=True)
    updated_count = 0
    
    for block_file in block_files:
        with open(block_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        if f"{OLD_NAMESPACE}:" in content:
            content = content.replace(f"{OLD_NAMESPACE}:", f"{NEW_NAMESPACE}:")
            
            with open(block_file, "w", encoding="utf-8") as f:
                f.write(content)
            
            updated_count += 1
            print(f"  ✅ {block_file}")
    
    print(f"✅ Zaktualizowano {updated_count} plików .block.json")

def update_crafting_catalog():
    """Aktualizuje crafting_item_catalog.json"""
    print("🔧 Aktualizacja crafting_item_catalog.json...")
    
    catalog_file = "BP/item_catalog/crafting_item_catalog.json"
    with open(catalog_file, "r", encoding="utf-8") as f:
        catalog = json.load(f)
    
    def update_items_recursive(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str) and value.startswith(f"{OLD_NAMESPACE}:"):
                    obj[key] = value.replace(f"{OLD_NAMESPACE}:", f"{NEW_NAMESPACE}:")
                elif isinstance(value, (dict, list)):
                    update_items_recursive(value)
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, str) and item.startswith(f"{OLD_NAMESPACE}:"):
                    obj[obj.index(item)] = item.replace(f"{OLD_NAMESPACE}:", f"{NEW_NAMESPACE}:")
                elif isinstance(item, (dict, list)):
                    update_items_recursive(item)
    
    update_items_recursive(catalog)
    
    with open(catalog_file, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    
    print("✅ crafting_item_catalog.json zaktualizowany")

def update_localization_files():
    """Aktualizuje pliki lokalizacji"""
    print("🔧 Aktualizacja plików lokalizacji...")
    
    lang_files = ["RP/texts/en_US.lang", "RP/texts/pl_PL.lang"]
    
    for lang_file in lang_files:
        if os.path.exists(lang_file):
            with open(lang_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Zamień wszystkie wystąpienia jct: na cityroads:
            content = content.replace(f"{OLD_NAMESPACE}:", f"{NEW_NAMESPACE}:")
            
            with open(lang_file, "w", encoding="utf-8") as f:
                f.write(content)
            
            print(f"  ✅ {lang_file}")

def update_blocks_json():
    """Aktualizuje blocks.json"""
    print("🔧 Aktualizacja blocks.json...")
    
    blocks_file = "RP/blocks.json"
    with open(blocks_file, "r", encoding="utf-8") as f:
        blocks = json.load(f)
    
    # Zamień klucze bloków
    new_blocks = {}
    for key, value in blocks.items():
        if key.startswith(f"{OLD_NAMESPACE}:"):
            new_key = key.replace(f"{OLD_NAMESPACE}:", f"{NEW_NAMESPACE}:")
            new_blocks[new_key] = value
        else:
            new_blocks[key] = value
    
    with open(blocks_file, "w", encoding="utf-8") as f:
        json.dump(new_blocks, f, indent=2, ensure_ascii=False)
    
    print("✅ blocks.json zaktualizowany")

def create_world_migration_script():
    """Tworzy skrypt do migracji bloków na świecie"""
    print("🔧 Tworzenie skryptu migracji świata...")
    
    script_content = f'''#!/usr/bin/env python3
"""
Skrypt do migracji bloków na świecie z namespace '{OLD_NAMESPACE}' na '{NEW_NAMESPACE}'
Uruchom ten skrypt w świecie Minecraft, aby zaktualizować wszystkie bloki
"""

import os
import json
import glob
from pathlib import Path

# Konfiguracja migracji
OLD_NAMESPACE = "{OLD_NAMESPACE}"
NEW_NAMESPACE = "{NEW_NAMESPACE}"

def find_minecraft_worlds():
    """Znajduje światy Minecraft"""
    home = str(Path.home())
    worlds = []
    
    # macOS
    mac_path = os.path.join(home, "Library/Application Support/minecraftpe")
    if os.path.exists(mac_path):
        worlds.extend(glob.glob(os.path.join(mac_path, "minecraftWorlds/*")))
    
    # Windows
    win_path = os.path.join(home, "AppData/Local/Packages/Microsoft.MinecraftUWP_8wekyb3d8bbwe/LocalState/games/com.mojang")
    if os.path.exists(win_path):
        worlds.extend(glob.glob(os.path.join(win_path, "minecraftWorlds/*")))
    
    return worlds

def migrate_world_level_dat(world_path):
    """Migruje plik level.dat w świecie"""
    level_dat_path = os.path.join(world_path, "level.dat")
    if not os.path.exists(level_dat_path):
        return False
    
    print(f"🔧 Migracja: {{os.path.basename(world_path)}}")
    
    # Tworzenie kopii zapasowej
    backup_path = level_dat_path + ".backup"
    shutil.copy2(level_dat_path, backup_path)
    
    try:
        # Odczyt pliku level.dat (to jest plik NBT, ale możemy spróbować prostego replace)
        with open(level_dat_path, "rb") as f:
            content = f.read()
        
        # Zamień namespace w danych
        old_bytes = OLD_NAMESPACE.encode('utf-8')
        new_bytes = NEW_NAMESPACE.encode('utf-8')
        
        if old_bytes in content:
            content = content.replace(old_bytes, new_bytes)
            
            with open(level_dat_path, "wb") as f:
                f.write(content)
            
            print(f"  ✅ level.dat zaktualizowany")
            return True
        else:
            print(f"  ⚠️  Nie znaleziono namespace {OLD_NAMESPACE} w level.dat")
            return False
            
    except Exception as e:
        print(f"  ❌ Błąd migracji level.dat: {{e}}")
        # Przywróć kopię zapasową
        shutil.copy2(backup_path, level_dat_path)
        return False

def migrate_chunk_files(world_path):
    """Migruje pliki chunk w świecie"""
    chunks_dir = os.path.join(world_path, "db")
    if not os.path.exists(chunks_dir):
        return False
    
    print(f"🔧 Migracja chunków w: {{os.path.basename(world_path)}}")
    
    # Tworzenie kopii zapasowej
    backup_dir = chunks_dir + ".backup"
    if not os.path.exists(backup_dir):
        shutil.copytree(chunks_dir, backup_dir)
    
    try:
        # Znajdź wszystkie pliki chunk
        chunk_files = glob.glob(os.path.join(chunks_dir, "*.ldb"))
        
        updated_count = 0
        for chunk_file in chunk_files:
            try:
                with open(chunk_file, "rb") as f:
                    content = f.read()
                
                # Zamień namespace w danych
                old_bytes = OLD_NAMESPACE.encode('utf-8')
                new_bytes = NEW_NAMESPACE.encode('utf-8')
                
                if old_bytes in content:
                    content = content.replace(old_bytes, new_bytes)
                    
                    with open(chunk_file, "wb") as f:
                        f.write(content)
                    
                    updated_count += 1
            except Exception as e:
                print(f"  ⚠️  Błąd migracji {{chunk_file}}: {{e}}")
        
        print(f"  ✅ Zaktualizowano {{updated_count}} plików chunk")
        return True
        
    except Exception as e:
        print(f"  ❌ Błąd migracji chunków: {{e}}")
        return False

def main():
    """Główna funkcja migracji"""
    print("🌍 MIGRACJA NAMESPACE W ŚWIATACH MINECRAFT")
    print("=" * 60)
    print(f"Zmiana z: {{OLD_NAMESPACE}} → {{NEW_NAMESPACE}}")
    print()
    
    # Znajdź światy
    worlds = find_minecraft_worlds()
    if not worlds:
        print("❌ Nie znaleziono światów Minecraft")
        return
    
    print(f"📁 Znaleziono {{len(worlds)}} światów:")
    for world in worlds:
        print(f"  - {{os.path.basename(world)}}")
    
    print()
    print("⚠️  UWAGA: Przed migracją zamknij Minecraft!")
    print("⚠️  Ta operacja może uszkodzić światy - upewnij się, że masz kopię zapasową!")
    print()
    
    response = input("Czy chcesz kontynuować? (tak/nie): ").lower().strip()
    if response not in ["tak", "yes", "y"]:
        print("❌ Migracja anulowana")
        return
    
    print()
    
    # Migruj każdy świat
    success_count = 0
    for world in worlds:
        world_name = os.path.basename(world)
        print(f"🌍 Migracja świata: {{world_name}}")
        
        # Migruj level.dat
        level_success = migrate_world_level_dat(world)
        
        # Migruj chunki
        chunks_success = migrate_chunk_files(world)
        
        if level_success or chunks_success:
            success_count += 1
            print(f"✅ Świat {{world_name}} zaktualizowany")
        else:
            print(f"❌ Błąd migracji świata {{world_name}}")
        
        print()
    
    print("=" * 60)
    print(f"📊 PODSUMOWANIE:")
    print(f"   🌍 Światy znalezione: {{len(worlds)}}")
    print(f"   ✅ Światy zaktualizowane: {{success_count}}")
    print(f"   ❌ Błędy: {{len(worlds) - success_count}}")
    
    if success_count > 0:
        print()
        print("🎉 Migracja zakończona!")
        print("Uruchom Minecraft i sprawdź czy bloki działają poprawnie")
    else:
        print()
        print("❌ Migracja nie powiodła się")

if __name__ == "__main__":
    main()
'''
    
    script_path = f"migrate_world_{OLD_NAMESPACE}_to_{NEW_NAMESPACE}.py"
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_content)
    
    # Nadaj uprawnienia wykonywania
    os.chmod(script_path, 0o755)
    
    print(f"✅ Skrypt migracji utworzony: {script_path}")

def create_migration_guide():
    """Tworzy przewodnik po migracji"""
    print("📝 Tworzenie przewodnika migracji...")
    
    guide_content = f'''# 🔄 Przewodnik Migracji Namespace

## 📋 Opis

Ten przewodnik opisuje proces migracji namespace z `{OLD_NAMESPACE}` na `{NEW_NAMESPACE}` w projekcie City Roads.

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
python3 migrate_world_{OLD_NAMESPACE}_to_{NEW_NAMESPACE}.py
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
'''
    
    guide_path = "MIGRATION_GUIDE.md"
    with open(guide_path, "w", encoding="utf-8") as f:
        f.write(guide_content)
    
    print(f"✅ Przewodnik utworzony: {guide_path}")

def main():
    """Główna funkcja migracji"""
    print("🔄 MIGRACJA NAMESPACE")
    print("=" * 60)
    print(f"Zmiana z: {OLD_NAMESPACE} → {NEW_NAMESPACE}")
    print()
    
    # Potwierdzenie użytkownika
    print("⚠️  UWAGA: Ta operacja zmieni wszystkie identyfikatory bloków!")
    print("⚠️  Upewnij się, że masz kopię zapasową projektu!")
    print()
    
    response = input("Czy chcesz kontynuować? (tak/nie): ").lower().strip()
    if response not in ["tak", "yes", "y"]:
        print("❌ Migracja anulowana")
        return
    
    print()
    
    # Tworzenie kopii zapasowej
    backup_dir = backup_project()
    
    try:
        # Aktualizacja plików projektu
        update_config_json()
        update_block_files()
        update_crafting_catalog()
        update_localization_files()
        update_blocks_json()
        
        # Tworzenie skryptów pomocniczych
        create_world_migration_script()
        create_migration_guide()
        
        print()
        print("=" * 60)
        print("✅ MIGRACJA PROJEKTU ZAKOŃCZONA POMYŚLNIE!")
        print()
        print("📋 Następne kroki:")
        print("1. Przetestuj budowanie: python3 build.py --mcaddon --no-bump")
        print("2. Uruchom migrację świata: python3 migrate_world_jct_to_cityroads.py")
        print("3. Przetestuj w Minecraft")
        print("4. Wypchnij zmiany na Git")
        print()
        print(f"📦 Kopia zapasowa: {backup_dir}")
        print("📝 Przewodnik: MIGRATION_GUIDE.md")
        
    except Exception as e:
        print(f"❌ Błąd podczas migracji: {e}")
        print(f"📦 Przywracanie z kopii zapasowej: {backup_dir}")
        
        # Przywróć z kopii zapasowej
        if os.path.exists(backup_dir):
            for item in os.listdir("."):
                if item not in [backup_dir, ".git"]:
                    if os.path.isdir(item):
                        shutil.rmtree(item)
                    else:
                        os.remove(item)
            
            for item in os.listdir(backup_dir):
                src = os.path.join(backup_dir, item)
                dst = os.path.join(".", item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
            
            print("✅ Projekt przywrócony z kopii zapasowej")

if __name__ == "__main__":
    main() 