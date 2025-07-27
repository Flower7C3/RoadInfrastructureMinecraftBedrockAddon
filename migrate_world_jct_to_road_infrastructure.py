#!/usr/bin/env python3
"""
Skrypt do migracji bloków na świecie z namespace 'jct' na 'road_infrastructure'
Uruchom ten skrypt w świecie Minecraft, aby zaktualizować wszystkie bloki
"""

import os
import json
import glob
import shutil
from pathlib import Path

# Konfiguracja migracji
OLD_NAMESPACE = "jct"
NEW_NAMESPACE = "road_infrastructure"

def find_minecraft_worlds():
    """Znajduje światy Minecraft"""
    home = str(Path.home())
    worlds = []
    
    # macOS
    mac_path = os.path.join(home, "Library/Application Support/minecraftpe")
    if os.path.exists(mac_path):
        worlds.extend(glob.glob(os.path.join(mac_path, "minecraftWorlds/*")))
    
    # mcpelauncher
    mcpelauncher_path = os.path.join(home, "Library/Application Support/mcpelauncher/games/com.mojang")
    if os.path.exists(mcpelauncher_path):
        worlds.extend(glob.glob(os.path.join(mcpelauncher_path, "minecraftWorlds/*")))
    
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
    
    print(f"🔧 Migracja: {os.path.basename(world_path)}")
    
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
            print(f"  ⚠️  Nie znaleziono namespace jct w level.dat")
            return False
            
    except Exception as e:
        print(f"  ❌ Błąd migracji level.dat: {e}")
        # Przywróć kopię zapasową
        shutil.copy2(backup_path, level_dat_path)
        return False

def migrate_chunk_files(world_path):
    """Migruje pliki chunk w świecie"""
    chunks_dir = os.path.join(world_path, "db")
    if not os.path.exists(chunks_dir):
        return False
    
    print(f"🔧 Migracja chunków w: {os.path.basename(world_path)}")
    
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
                print(f"  ⚠️  Błąd migracji {chunk_file}: {e}")
        
        print(f"  ✅ Zaktualizowano {updated_count} plików chunk")
        return True
        
    except Exception as e:
        print(f"  ❌ Błąd migracji chunków: {e}")
        return False

def main():
    """Główna funkcja migracji"""
    print("🌍 MIGRACJA NAMESPACE W ŚWIATACH MINECRAFT")
    print("=" * 60)
    print(f"Zmiana z: {OLD_NAMESPACE} → {NEW_NAMESPACE}")
    print()
    
    # Znajdź światy
    worlds = find_minecraft_worlds()
    if not worlds:
        print("❌ Nie znaleziono światów Minecraft")
        return
    
    print(f"📁 Znaleziono {len(worlds)} światów:")
    for world in worlds:
        print(f"  - {os.path.basename(world)}")
    
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
        print(f"🌍 Migracja świata: {world_name}")
        
        # Migruj level.dat
        level_success = migrate_world_level_dat(world)
        
        # Migruj chunki
        chunks_success = migrate_chunk_files(world)
        
        if level_success or chunks_success:
            success_count += 1
            print(f"✅ Świat {world_name} zaktualizowany")
        else:
            print(f"❌ Błąd migracji świata {world_name}")
        
        print()
    
    print("=" * 60)
    print(f"📊 PODSUMOWANIE:")
    print(f"   🌍 Światy znalezione: {len(worlds)}")
    print(f"   ✅ Światy zaktualizowane: {success_count}")
    print(f"   ❌ Błędy: {len(worlds) - success_count}")
    
    if success_count > 0:
        print()
        print("🎉 Migracja zakończona!")
        print("Uruchom Minecraft i sprawdź czy bloki działają poprawnie")
    else:
        print()
        print("❌ Migracja nie powiodła się")

if __name__ == "__main__":
    main()
