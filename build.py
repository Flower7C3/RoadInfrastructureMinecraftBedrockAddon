#!/usr/bin/env python3
"""
Build Script for Road Infrastructure Addon
"""

import os
import json
import shutil
import zipfile
import sys
import argparse
from datetime import datetime
from pathlib import Path
from console_utils import ConsoleStyle, print_build_info, print_header, print_usage, print_installation_info

# Pack name constant
PACK_NAME = "RoadInfrastructure"

def get_minecraft_dir():
    """Try to auto-detect Minecraft com.mojang folder"""
    home = str(Path.home())
    # macOS
    mac_path = os.path.join(home, "Library/Application Support/minecraftpe")
    if os.path.exists(mac_path):
        return mac_path
    # mcpelauncher
    mcpelauncher_path = os.path.join(home, "Library/Application Support/mcpelauncher/games/com.mojang")
    if os.path.exists(mcpelauncher_path):
        return mcpelauncher_path
    # Windows
    win_path = os.path.join(home,
                            "AppData/Local/Packages/Microsoft.MinecraftUWP_8wekyb3d8bbwe/LocalState/games/com.mojang")
    if os.path.exists(win_path):
        return win_path
    # Linux/Android (user must specify)
    return None

def remove_existing_packs(mc_dir):
    """Remove existing RoadInfrastructure packs from the Minecraft directory"""
    bp_dir = os.path.join(mc_dir, 'behavior_packs', PACK_NAME)
    rp_dir = os.path.join(mc_dir, 'resource_packs', PACK_NAME)

    if os.path.exists(bp_dir):
        print(ConsoleStyle.warning(f"Removing existing behavior pack: {bp_dir}"))
        shutil.rmtree(bp_dir)

    if os.path.exists(rp_dir):
        print(ConsoleStyle.warning(f"Removing existing resource pack: {rp_dir}"))
        shutil.rmtree(rp_dir)

def install_mcaddon(mcaddon_path, clean_existing=True):
    """Install .mcaddon file to local Minecraft directory"""
    mc_dir = get_minecraft_dir()
    if not mc_dir:
        print(ConsoleStyle.error("Cannot auto-detect Minecraft com.mojang directory. Installation failed."))
        return False

    print(ConsoleStyle.info(f"Minecraft directory: {mc_dir}"))

    # Remove existing packs if requested
    if clean_existing:
        remove_existing_packs(mc_dir)

    # Install new packs
    print(ConsoleStyle.process("Installing new packs..."))
    file_count = 0
    
    with zipfile.ZipFile(mcaddon_path, 'r') as zf:
        for member in zf.namelist():
            if member.startswith('BP/'):
                out_dir = os.path.join(mc_dir, 'behavior_packs', PACK_NAME)
                rel_path = os.path.relpath(member, 'BP')
            elif member.startswith('RP/'):
                out_dir = os.path.join(mc_dir, 'resource_packs', PACK_NAME)
                rel_path = os.path.relpath(member, 'RP')
            else:
                continue
            target_path = os.path.join(out_dir, rel_path)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with zf.open(member) as src, open(target_path, 'wb') as dst:
                shutil.copyfileobj(src, dst)
            file_count += 1

    print(ConsoleStyle.success(f"Installed {file_count} files"))
    print_installation_info(PACK_NAME, mc_dir)
    return True

def read_manifest(file_path):
    """Read manifest file and return name and version"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['header']['name'], data['header']['version']

def bump_version(version):
    """Bump patch version"""
    version[2] += 1
    return version

def update_version(file_path, new_version):
    """Update version in manifest file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    data['header']['version'] = new_version
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def build_mcaddon(bp_version, rp_version, plugin_name, output_dir, timestamp):
    """Build .mcaddon package"""
    print(ConsoleStyle.process("Building .mcaddon package..."))
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Create mcaddon file
    mcaddon_filename = f"{plugin_name}_v{bp_version[0]}.{bp_version[1]}.{bp_version[2]}_{timestamp}.mcaddon"
    mcaddon_path = os.path.join(output_dir, mcaddon_filename)
    
    with zipfile.ZipFile(mcaddon_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add BP files
        bp_dir = "BP"
        for root, dirs, files in os.walk(bp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = file_path
                zf.write(file_path, arcname)
        
        # Add RP files
        rp_dir = "RP"
        for root, dirs, files in os.walk(rp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = file_path
                zf.write(file_path, arcname)
    
    # Get file size
    file_size = os.path.getsize(mcaddon_path) / (1024 * 1024)  # MB
    
    print(ConsoleStyle.success(f"Created: {mcaddon_path}"))
    print(ConsoleStyle.info(f"Size: {file_size:.2f} MB"))
    
    return mcaddon_path, file_size

def build_mcpack(bp_version, rp_version, bp_name, rp_name, output_dir, timestamp):
    """Build separate .mcpack files"""
    print(ConsoleStyle.process("Building .mcpack packages..."))
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Build BP mcpack
    bp_mcpack_filename = f"{bp_name}_v{bp_version[0]}.{bp_version[1]}.{bp_version[2]}_{timestamp}.mcpack"
    bp_mcpack_path = os.path.join(output_dir, bp_mcpack_filename)
    
    with zipfile.ZipFile(bp_mcpack_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        bp_dir = "BP"
        for root, dirs, files in os.walk(bp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, bp_dir)
                zf.write(file_path, arcname)
    
    # Build RP mcpack
    rp_mcpack_filename = f"{rp_name}_v{rp_version[0]}.{rp_version[1]}.{rp_version[2]}_{timestamp}.mcpack"
    rp_mcpack_path = os.path.join(output_dir, rp_mcpack_filename)
    
    with zipfile.ZipFile(rp_mcpack_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        rp_dir = "RP"
        for root, dirs, files in os.walk(rp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, rp_dir)
                zf.write(file_path, arcname)
    
    bp_size = os.path.getsize(bp_mcpack_path) / (1024 * 1024)
    rp_size = os.path.getsize(rp_mcpack_path) / (1024 * 1024)
    
    print(ConsoleStyle.success(f"Created: {bp_mcpack_path} ({bp_size:.2f} MB)"))
    print(ConsoleStyle.success(f"Created: {rp_mcpack_path} ({rp_size:.2f} MB)"))
    
    return bp_mcpack_path, rp_mcpack_path, bp_size, rp_size

def count_files():
    """Count total files in BP and RP directories"""
    file_count = 0
    for root, dirs, files in os.walk("BP"):
        file_count += len(files)
    for root, dirs, files in os.walk("RP"):
        file_count += len(files)
    return file_count

def main():
    """Main build function"""
    parser = argparse.ArgumentParser(description="Build Road Infrastructure Minecraft Addon")
    parser.add_argument("--mcaddon", action="store_true", help="Build .mcaddon package")
    parser.add_argument("--mcpack", action="store_true", help="Build separate .mcpack packages")
    parser.add_argument("--all", action="store_true", help="Build all package types")
    parser.add_argument("--no-bump", action="store_true", help="Don't bump version")
    parser.add_argument("--test-on-local", action="store_true", help="Install to local Minecraft after building")
    parser.add_argument("--output", default="dist", help="Output directory")
    
    args = parser.parse_args()
    
    if not any([args.mcaddon, args.mcpack, args.all]):
        print("Użycie: python3 build_enhanced.py [--mcaddon|--mcpack|--all] [--no-bump] [--test-on-local]")
        print("Przykłady:")
        print("  python3 build_enhanced.py --mcaddon")
        print("  python3 build_enhanced.py --all --test-on-local")
        print("  python3 build_enhanced.py --mcpack --no-bump")
        return
    
    print("🏗️ ROAD INFRASTRUCTURE BUILD SYSTEM")
    print("=" * 60)
    
    # Read current versions
    bp_name, bp_version = read_manifest("BP/manifest.json")
    rp_name, rp_version = read_manifest("RP/manifest.json")
    
    print(f"📦 BP: {bp_name} v{bp_version[0]}.{bp_version[1]}.{bp_version[2]}")
    print(f"📦 RP: {rp_name} v{rp_version[0]}.{rp_version[1]}.{rp_version[2]}")
    
    # Bump version if requested
    if not args.no_bump:
        print(ConsoleStyle.process("Bumping version..."))
        new_bp_version = bump_version(bp_version.copy())
        new_rp_version = bump_version(rp_version.copy())
        
        update_version("BP/manifest.json", new_bp_version)
        update_version("RP/manifest.json", new_rp_version)
        
        bp_version = new_bp_version
        rp_version = new_rp_version
        print(ConsoleStyle.success(f"Version bumped to {bp_version[0]}.{bp_version[1]}.{bp_version[2]}"))
    
    # Create timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Build packages
    mcaddon_path = None
    bp_mcpack_path = None
    rp_mcpack_path = None
    
    if args.mcaddon or args.all:
        mcaddon_path, mcaddon_size = build_mcaddon(bp_version, rp_version, PACK_NAME, args.output, timestamp)
    
    if args.mcpack or args.all:
        bp_mcpack_path, rp_mcpack_path, bp_size, rp_size = build_mcpack(
            bp_version, rp_version, f"{PACK_NAME}_BP", f"{PACK_NAME}_RP", args.output, timestamp
        )
    
    # Count files
    file_count = count_files()
    
    print("=" * 60)
    print(ConsoleStyle.info("BUILD SUMMARY"))
    print(f"📦 Total files: {file_count}")
    if mcaddon_path:
        print(f"📦 .mcaddon: {os.path.basename(mcaddon_path)}")
    if bp_mcpack_path and rp_mcpack_path:
        print(f"📦 .mcpack: {os.path.basename(bp_mcpack_path)}, {os.path.basename(rp_mcpack_path)}")
    
    # Install to local Minecraft if requested
    if args.test_on_local and mcaddon_path:
        print("=" * 60)
        print(ConsoleStyle.process("Installing to local Minecraft..."))
        if install_mcaddon(mcaddon_path):
            print(ConsoleStyle.success("Installation completed successfully!"))
        else:
            print(ConsoleStyle.error("Installation failed!"))
    
    print("=" * 60)
    print(ConsoleStyle.success("Build completed successfully!"))

if __name__ == "__main__":
    main() 