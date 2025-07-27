#!/usr/bin/env python3
"""
Skrypt do migracji bloków na świecie z namespace 'jct' na 'road_infrastructure'
Użycie: python3 migrate_world_jct_to_road_infrastructure_with_path.py <ścieżka_do_świata>
Przykład: python3 migrate_world_jct_to_road_infrastructure_with_path.py ~/Library/Application\ Support/mcpelauncher/games/com.mojang/minecraftWorlds/mqKp4KnQBc8=
"""

import os
import json
import glob
import shutil
import sys
from pathlib import Path

# Konfiguracja migracji
OLD_NAMESPACE = "jct"
NEW_NAMESPACE = "road_infrastructure"

def validate_world_path(world_path):
    """Sprawdza czy ścieżka do świata jest poprawna"""
    if not os.path.exists(world_path):
        print(f"❌ Błąd: Ścieżka '{world_path}' nie istnieje")
        return False
    
    # Sprawdź czy to jest świat Minecraft (ma plik level.dat)
    level_dat_path = os.path.join(world_path, "level.dat")
    if not os.path.exists(level_dat_path):
        print(f"❌ Błąd: '{world_path}' nie jest światem Minecraft (brak pliku level.dat)")
        return False
    
    return True

def migrate_world_level_dat(world_path):
    """Migruje plik level.dat w świecie"""
    level_dat_path = os.path.join(world_path, "level.dat")
    print(f"🔧 Migracja level.dat w: {os.path.basename(world_path)}")
    
    # Tworzenie kopii zapasowej
    backup_path = level_dat_path + ".backup"
    shutil.copy2(level_dat_path, backup_path)
    print(f"  📦 Utworzono kopię zapasową: {backup_path}")
    
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
        print(f"  ❌ Błąd migracji level.dat: {e}")
        # Przywróć kopię zapasową
        shutil.copy2(backup_path, level_dat_path)
        return False

def migrate_chunk_files(world_path):
    """Migruje pliki chunk w świecie"""
    chunks_dir = os.path.join(world_path, "db")
    if not os.path.exists(chunks_dir):
        print(f"  ⚠️  Katalog chunków nie istnieje: {chunks_dir}")
        return False
    
    print(f"🔧 Migracja chunków w: {os.path.basename(world_path)}")
    
    # Tworzenie kopii zapasowej
    backup_dir = chunks_dir + ".backup"
    if not os.path.exists(backup_dir):
        shutil.copytree(chunks_dir, backup_dir)
        print(f"  📦 Utworzono kopię zapasową chunków: {backup_dir}")
    
    try:
        # Znajdź wszystkie pliki chunk
        chunk_files = glob.glob(os.path.join(chunks_dir, "*.ldb"))
        
        if not chunk_files:
            print(f"  ⚠️  Nie znaleziono plików chunk (.ldb)")
            return False
        
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
                    print(f"    ✅ Zaktualizowano: {os.path.basename(chunk_file)}")
                else:
                    print(f"    ⚠️  Brak namespace {OLD_NAMESPACE} w: {os.path.basename(chunk_file)}")
            except Exception as e:
                print(f"    ❌ Błąd migracji {os.path.basename(chunk_file)}: {e}")
        
        print(f"  ✅ Zaktualizowano {updated_count} plików chunk")
        return updated_count > 0
        
    except Exception as e:
        print(f"  ❌ Błąd migracji chunków: {e}")
        return False

def check_existing_blocks(world_path):
    """Sprawdza jakie bloki z naszym namespace istnieją w świecie"""
    print(f"🔍 Sprawdzanie bloków w świecie: {os.path.basename(world_path)}")
    
    # Sprawdź pliki log i ldb
    db_dir = os.path.join(world_path, "db")
    if os.path.exists(db_dir):
        for file_name in os.listdir(db_dir):
            file_path = os.path.join(db_dir, file_name)
            if os.path.isfile(file_path):
                try:
                    with open(file_path, "rb") as f:
                        content = f.read()
                    
                    # Sprawdź różne namespace
                    namespaces = [OLD_NAMESPACE, NEW_NAMESPACE, "cityroads", "bridge"]
                    found_blocks = []
                    
                    for ns in namespaces:
                        ns_bytes = ns.encode('utf-8')
                        if ns_bytes in content:
                            # Znajdź wszystkie wystąpienia
                            start = 0
                            while True:
                                pos = content.find(ns_bytes, start)
                                if pos == -1:
                                    break
                                
                                # Spróbuj wyciągnąć pełny identyfikator bloku
                                end = pos + len(ns_bytes)
                                while end < len(content) and content[end] in b'abcdefghijklmnopqrstuvwxyz0123456789_':
                                    end += 1
                                
                                block_id = content[pos:end].decode('utf-8', errors='ignore')
                                if ':' in block_id:
                                    found_blocks.append(block_id)
                                
                                start = end
                    
                    if found_blocks:
                        unique_blocks = list(set(found_blocks))
                        print(f"  📦 Znalezione bloki w {file_name}:")
                        for block in unique_blocks:
                            print(f"    - {block}")
                        return unique_blocks
                        
                except Exception as e:
                    print(f"  ⚠️  Błąd odczytu {file_name}: {e}")
    
    print(f"  ⚠️  Nie znaleziono bloków z naszym namespace")
    return []

def main():
    """Główna funkcja migracji"""
    print("🌍 MIGRACJA NAMESPACE W ŚWIECIE MINECRAFT")
    print("=" * 60)
    print(f"Zmiana z: {OLD_NAMESPACE} → {NEW_NAMESPACE}")
    print()
    
    # Sprawdź argumenty
    if len(sys.argv) != 2:
        print("❌ Błąd: Podaj ścieżkę do świata jako argument")
        print(f"Użycie: python3 {sys.argv[0]} <ścieżka_do_świata>")
        print(f"Przykład: python3 {sys.argv[0]} ~/Library/Application\\ Support/mcpelauncher/games/com.mojang/minecraftWorlds/mqKp4KnQBc8=")
        return
    
    world_path = sys.argv[1]
    
    # Sprawdź czy ścieżka jest poprawna
    if not validate_world_path(world_path):
        return
    
    print(f"📁 Świat: {world_path}")
    print(f"📁 Nazwa: {os.path.basename(world_path)}")
    print()
    
    # Sprawdź istniejące bloki
    existing_blocks = check_existing_blocks(world_path)
    print()
    
    print("⚠️  UWAGA: Przed migracją zamknij Minecraft!")
    print("⚠️  Ta operacja może uszkodzić światy - upewnij się, że masz kopię zapasową!")
    print()
    
    response = input("Czy chcesz kontynuować? (tak/nie): ").lower().strip()
    if response not in ["tak", "yes", "y"]:
        print("❌ Migracja anulowana")
        return
    
    print()
    
    # Migruj świat
    world_name = os.path.basename(world_path)
    print(f"🌍 Migracja świata: {world_name}")
    
    # Migruj level.dat
    level_success = migrate_world_level_dat(world_path)
    
    # Migruj chunki
    chunks_success = migrate_chunk_files(world_path)
    
    print()
    print("=" * 60)
    print(f"📊 PODSUMOWANIE:")
    print(f"   🌍 Świat: {world_name}")
    print(f"   📦 Bloki przed migracją: {len(existing_blocks)}")
    print(f"   ✅ level.dat: {'Tak' if level_success else 'Nie'}")
    print(f"   ✅ chunki: {'Tak' if chunks_success else 'Nie'}")
    
    if level_success or chunks_success:
        print()
        print("🎉 Migracja zakończona!")
        print("Uruchom Minecraft i sprawdź czy bloki działają poprawnie")
    else:
        print()
        print("❌ Migracja nie powiodła się")
        print("Sprawdź czy w świecie są bloki z namespace 'jct'")

if __name__ == "__main__":
    main() 