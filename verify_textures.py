#!/usr/bin/env python3
"""
Skrypt do weryfikacji tekstur w projekcie Minecraft CityBuildingKit
Sprawdza czy wszystkie bloki mają odpowiednie tekstury i czy wszystkie tekstury są używane
"""

import json
import os
import glob
from pathlib import Path

def load_json_file(file_path):
    """Ładuje plik JSON i zwraca jego zawartość"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Błąd ładowania {file_path}: {e}")
        return None

def extract_texture_from_block(block_data):
    """Wyciąga nazwę tekstury z danych bloku"""
    try:
        material_instances = block_data.get('minecraft:block', {}).get('components', {}).get('minecraft:material_instances', {})
        for instance_name, instance_data in material_instances.items():
            if instance_name == 'up':
                return instance_data.get('texture')
            elif instance_name == '*' and 'up' not in material_instances:
                # Jeśli nie ma 'up', użyj '*' jako fallback
                return instance_data.get('texture')
        return None
    except Exception as e:
        print(f"❌ Błąd wyciągania tekstury: {e}")
        return None

def check_texture_exists(texture_name, texture_dir, terrain_texture_file):
    """Sprawdza czy plik tekstury istnieje"""
    if not texture_name:
        return False
    
    # Sprawdź mapowanie w terrain_texture.json
    terrain_data = load_json_file(terrain_texture_file)
    if terrain_data:
        texture_mappings = terrain_data.get('texture_data', {})
        if texture_name in texture_mappings:
            texture_path = texture_mappings[texture_name].get('textures', '')
            if texture_path:
                # Usuń prefix "textures/blocks/"
                actual_texture_name = texture_path.replace('textures/blocks/', '')
                full_path = os.path.join(texture_dir, actual_texture_name)
                if os.path.exists(full_path):
                    return True
    
    # Sprawdź różne możliwe rozszerzenia (fallback)
    for ext in ['.png', '.jpg', '.jpeg']:
        texture_path = os.path.join(texture_dir, f"{texture_name}{ext}")
        if os.path.exists(texture_path):
            return True
    
    return False

def verify_terrain_texture_mapping(terrain_texture_file, texture_dir):
    """Sprawdza mapowanie w terrain_texture.json"""
    print("\n🔍 WERYFIKACJA MAPOWANIA TERRAIN_TEXTURE.JSON")
    print("=" * 60)
    
    terrain_data = load_json_file(terrain_texture_file)
    if not terrain_data:
        return
    
    texture_mappings = terrain_data.get('texture_data', {})
    
    missing_textures = []
    valid_textures = []
    
    for texture_id, texture_info in texture_mappings.items():
        texture_path = texture_info.get('textures')
        if texture_path:
            # Usuń prefix "textures/blocks/"
            texture_name = texture_path.replace('textures/blocks/', '')
            full_path = os.path.join(texture_dir, texture_name)
            
            if os.path.exists(full_path):
                valid_textures.append(texture_id)
                print(f"✅ {texture_id} -> {texture_name}")
            else:
                missing_textures.append((texture_id, texture_name))
                print(f"❌ {texture_id} -> {texture_name} (BRAK PLIKU)")
    
    print(f"\n📊 PODSUMOWANIE:")
    print(f"   ✅ Poprawne mapowania: {len(valid_textures)}")
    print(f"   ❌ Brakujące tekstury: {len(missing_textures)}")
    
    if missing_textures:
        print(f"\n❌ BRAKUJĄCE TEKSTURY:")
        for texture_id, texture_name in missing_textures:
            print(f"   - {texture_id}: {texture_name}")

def verify_block_textures(blocks_dir, texture_dir, terrain_texture_file):
    """Sprawdza wszystkie bloki i ich tekstury"""
    print("\n🔍 WERYFIKACJA BLOKÓW I TEKSTUR")
    print("=" * 60)
    
    block_files = glob.glob(os.path.join(blocks_dir, "**/*.block.json"), recursive=True)
    
    valid_blocks = []
    invalid_blocks = []
    missing_textures = []
    
    for block_file in sorted(block_files):
        block_data = load_json_file(block_file)
        if not block_data:
            continue
        
        # Wyciągnij identifier bloku
        identifier = block_data.get('minecraft:block', {}).get('description', {}).get('identifier', 'UNKNOWN')
        
        # Wyciągnij teksturę
        texture_name = extract_texture_from_block(block_data)
        
        if texture_name:
            if check_texture_exists(texture_name, texture_dir, terrain_texture_file):
                valid_blocks.append((identifier, texture_name))
                print(f"✅ {identifier} -> {texture_name}")
            else:
                invalid_blocks.append((identifier, texture_name))
                missing_textures.append(texture_name)
                print(f"❌ {identifier} -> {texture_name} (BRAK TEKSTURY)")
        else:
            print(f"⚠️  {identifier} -> BRAK TEKSTURY")
    
    print(f"\n📊 PODSUMOWANIE BLOKÓW:")
    print(f"   ✅ Poprawne bloki: {len(valid_blocks)}")
    print(f"   ❌ Błędne bloki: {len(invalid_blocks)}")
    
    if invalid_blocks:
        print(f"\n❌ BLOKI Z BRAKUJĄCYMI TEKSTURAMI:")
        for identifier, texture_name in invalid_blocks:
            print(f"   - {identifier}: {texture_name}")

def check_unused_textures(texture_dir, terrain_texture_file):
    """Sprawdza nieużywane tekstury"""
    print("\n🔍 WERYFIKACJA NIEUŻYWANYCH TEKSTUR")
    print("=" * 60)
    
    # Pobierz wszystkie pliki tekstur
    texture_files = []
    for ext in ['*.png', '*.jpg', '*.jpeg']:
        texture_files.extend(glob.glob(os.path.join(texture_dir, ext)))
    
    # Pobierz używane tekstury z terrain_texture.json
    terrain_data = load_json_file(terrain_texture_file)
    used_textures = set()
    
    if terrain_data:
        texture_mappings = terrain_data.get('texture_data', {})
        for texture_info in texture_mappings.values():
            texture_path = texture_info.get('textures', '')
            if texture_path:
                texture_name = texture_path.replace('textures/blocks/', '')
                used_textures.add(texture_name)
    
    # Sprawdź nieużywane tekstury
    unused_textures = []
    for texture_file in texture_files:
        texture_name = os.path.basename(texture_file)
        if texture_name not in used_textures:
            unused_textures.append(texture_name)
    
    print(f"📊 PODSUMOWANIE TEKSTUR:")
    print(f"   📁 Wszystkie tekstury: {len(texture_files)}")
    print(f"   ✅ Używane tekstury: {len(used_textures)}")
    print(f"   🗑️  Nieużywane tekstury: {len(unused_textures)}")
    
    if unused_textures:
        print(f"\n🗑️  NIEUŻYWANE TEKSTURY:")
        for texture_name in sorted(unused_textures):
            print(f"   - {texture_name}")

def main():
    """Główna funkcja weryfikacji"""
    print("🔍 WERYFIKACJA PROJEKTU CITYBUILDINGKIT")
    print("=" * 60)
    
    # Ścieżki
    blocks_dir = "BP/blocks"
    texture_dir = "RP/textures/blocks"
    terrain_texture_file = "RP/textures/terrain_texture.json"
    
    # Sprawdź czy katalogi istnieją
    if not os.path.exists(blocks_dir):
        print(f"❌ Katalog bloków nie istnieje: {blocks_dir}")
        return
    
    if not os.path.exists(texture_dir):
        print(f"❌ Katalog tekstur nie istnieje: {texture_dir}")
        return
    
    if not os.path.exists(terrain_texture_file):
        print(f"❌ Plik terrain_texture.json nie istnieje: {terrain_texture_file}")
        return
    
    # Wykonaj weryfikacje
    verify_terrain_texture_mapping(terrain_texture_file, texture_dir)
    verify_block_textures(blocks_dir, texture_dir, terrain_texture_file)
    check_unused_textures(texture_dir, terrain_texture_file)
    
    print("\n✅ WERYFIKACJA ZAKOŃCZONA")

if __name__ == "__main__":
    main() 