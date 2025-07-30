#!/usr/bin/env python3
"""
Comprehensive verification script for Minecraft Bedrock Addon
Verifies project structure, files, textures, and build readiness
"""

import os
import json
import sys
import glob
import re
from pathlib import Path
from console_utils import ConsoleStyle, print_if_not_quiet


def load_json_file(file_path):
    """Load JSON file and return its content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print_if_not_quiet(ConsoleStyle.error(f"Error loading [{file_path}]: {e}"))
        return None


def extract_texture_from_block(block_data):
    """Extract texture name from block data"""
    try:
        material_instances = block_data.get('minecraft:block', {}).get('components', {}).get(
            'minecraft:material_instances', {})
        for instance_name, instance_data in material_instances.items():
            if instance_name == 'up':
                return instance_data.get('texture')
            elif instance_name == '*' and 'up' not in material_instances:
                # If no 'up', use '*' as fallback
                return instance_data.get('texture')
        return None
    except Exception as e:
        print_if_not_quiet(ConsoleStyle.error(f"Error extracting texture: {e}"))
        return None


def check_texture_exists(texture_name, texture_dir, terrain_texture_file):
    """Check if texture file exists"""
    if not texture_name:
        return False

    # Check mapping in terrain_texture.json
    terrain_data = load_json_file(terrain_texture_file)
    if terrain_data:
        texture_mappings = terrain_data.get('texture_data', {})
        if texture_name in texture_mappings:
            texture_path = texture_mappings[texture_name].get('textures', '')
            if texture_path:
                # Remove "textures/blocks/" prefix
                actual_texture_name = texture_path.replace('textures/blocks/', '')
                full_path = os.path.join(texture_dir, actual_texture_name)
                if os.path.exists(full_path):
                    return True

    # Check various possible extensions (fallback)
    for ext in ['.png', '.jpg', '.jpeg']:
        texture_path = os.path.join(texture_dir, f"{texture_name}{ext}")
        if os.path.exists(texture_path):
            return True

    return False


def verify_project_structure():
    """Verify basic project structure"""
    ConsoleStyle.print_section("🔍 VERIFYING PROJECT STRUCTURE")

    required_files = [
        'config.json',
        'BP/manifest.json',
        'RP/manifest.json',
        'build.py'
    ]

    required_dirs = [
        'BP',
        'BP/blocks',
        'RP',
        'RP/textures',
        'RP/models',
        'RP/texts'
    ]

    errors = []
    warnings = []

    # Check required files
    for file_path in required_files:
        if os.path.exists(file_path):
            print_if_not_quiet(ConsoleStyle.success(f"Found: {file_path}"))
        else:
            print_if_not_quiet(ConsoleStyle.error(f"Missing: {file_path}"))
            errors.append(f"Missing required file: {file_path}")

    # Check required directories
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print_if_not_quiet(ConsoleStyle.success(f"Found: {dir_path}/"))
        else:
            print_if_not_quiet(ConsoleStyle.error(f"Missing: {dir_path}/"))
            errors.append(f"Missing required directory: {dir_path}")

    return errors, warnings


def verify_manifests():
    """Weryfikuj pliki manifestów"""
    ConsoleStyle.print_section("📋 MANIFESTS VERIFICATION")

    errors = []
    warnings = []

    manifest_files = [
        ("BP/manifest.json", "Behavior Pack"),
        ("RP/manifest.json", "Resource Pack")
    ]

    for file_path, pack_type in manifest_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Check required fields
            required_fields = ['format_version', 'header']
            for field in required_fields:
                if field not in data:
                    errors.append(f"{pack_type} missing required field: {field}")
                    continue

            if 'header' in data:
                header = data['header']
                header_fields = ['name', 'description', 'uuid', 'version', 'min_engine_version']
                for field in header_fields:
                    if field not in header:
                        errors.append(f"{pack_type} header missing required field: {field}")

            # Check a version format
            if 'header' in data and 'version' in data['header']:
                version = data['header']['version']
                if not isinstance(version, list) or len(version) != 3:
                    errors.append(f"{pack_type} version must be [major, minor, patch]")
                else:
                    print_if_not_quiet(ConsoleStyle.success(f"{pack_type} version: {'.'.join(map(str, version))}"))

            print_if_not_quiet(ConsoleStyle.success(f"{pack_type} manifest is valid JSON"))

        except json.JSONDecodeError as e:
            errors.append(f"{pack_type} manifest is invalid JSON: {e}")
        except Exception as e:
            errors.append(f"Error reading {pack_type} manifest: {e}")

    if errors:
        print_if_not_quiet(ConsoleStyle.error(f"Found {len(errors)} manifest errors:"))
        for error in errors:
            print_if_not_quiet(f"  • {error}")
    else:
        print_if_not_quiet(ConsoleStyle.success("All manifests are valid!"))

    if warnings:
        print_if_not_quiet(ConsoleStyle.warning(f"Found {len(warnings)} manifest warnings:"))
        for warning in warnings:
            print_if_not_quiet(f"  • {warning}")

    return errors, warnings


def verify_config():
    """Weryfikuj plik config.json"""
    ConsoleStyle.print_section("⚙️ CONFIG VERIFICATION")

    errors = []
    warnings = []

    config_path = "config.json"
    if not os.path.exists(config_path):
        print_if_not_quiet(ConsoleStyle.info("config.json not found - skipping config verification"))
        return errors, warnings

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Check required fields
        required_fields = ['type', 'name', 'namespace', 'targetVersion']
        for field in required_fields:
            if field not in data:
                errors.append(f"config.json missing required field: {field}")

        # Check namespace consistency
        if 'namespace' in data:
            namespace = data['namespace']
            print_if_not_quiet(ConsoleStyle.success(f"Namespace: {namespace}"))

            # Check if namespace is used in block files
            namespace_used = False
            for root, dirs, files in os.walk("BP/blocks"):
                for file in files:
                    if file.endswith('.block.json'):
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            block_data = json.load(f)
                            if 'minecraft:block' in block_data:
                                identifier = block_data['minecraft:block']['description'].get('identifier', '')
                                if identifier.startswith(f"{namespace}:"):
                                    namespace_used = True
                                    break
                if namespace_used:
                    break

            if not namespace_used:
                warnings.append(f"Namespace '{namespace}' not found in block identifiers")

        print_if_not_quiet(ConsoleStyle.success("config.json is valid JSON"))

    except json.JSONDecodeError as e:
        errors.append(f"config.json is invalid JSON: {e}")
    except Exception as e:
        errors.append(f"Error reading config.json: {e}")

    if errors:
        print_if_not_quiet(ConsoleStyle.error(f"Found {len(errors)} config errors:"))
        for error in errors:
            print_if_not_quiet(f"  • {error}")
    else:
        print_if_not_quiet(ConsoleStyle.success("Config is valid!"))

    if warnings:
        print_if_not_quiet(ConsoleStyle.warning(f"Found {len(warnings)} config warnings:"))
        for warning in warnings:
            print_if_not_quiet(f"  • {warning}")

    return errors, warnings


def count_project_files():
    """Count files in project"""
    stats = {}

    # Count files by directory
    for root, dirs, files in os.walk("."):
        # Skip git and cache directories
        if any(skip in root for skip in ['.git', '.idea', '__pycache__', 'venv', 'dist']):
            continue

        rel_path = os.path.relpath(root, ".")
        if rel_path == ".":
            rel_path = ""

        stats[f"📁 {rel_path}/"] = len(files)

    # Print statistics
    total_files = sum(stats.values())
    ConsoleStyle.print_stats(stats, f"📦 Total files: {total_files}")

    return [], []


def verify_translations():
    """Verify localization files"""
    ConsoleStyle.print_section("🌐 TRANSLATIONS")

    errors = []
    warnings = []

    # Check languages.json
    languages_path = "RP/texts/languages.json"
    if os.path.exists(languages_path):
        try:
            with open(languages_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # languages.json is a list, not an object
            if isinstance(data, list):
                language_files = data
                print_if_not_quiet(ConsoleStyle.success(f"Found {len(language_files)} language files"))

                # Check if language files exist
                for lang_name in language_files:
                    lang_path = f"RP/texts/{lang_name}.lang"
                    if os.path.exists(lang_path):
                        # Wczytaj plik językowy
                        file_block_translations = set()
                        file_category_translations = set()
                        stats = {}
                        try:
                            with open(lang_path, 'r', encoding='utf-8') as f:
                                for line in f:
                                    line = line.strip()
                                    if line and '=' in line:
                                        key = line.split('=', 1)[0].strip()
                                        if key.startswith('tile.jct:') and key.endswith('.name'):
                                            block_name = key.replace('tile.jct:', '').replace('.name', '')
                                            file_block_translations.add(block_name)
                                        elif key.startswith('jct:'):
                                            # Kategorie mają format `jct:category_name`
                                            category_name = key.replace('jct:', '')
                                            file_category_translations.add(category_name)

                            # Wczytaj crafting catalog
                            project_category_translations = set()
                            try:
                                with open('BP/item_catalog/crafting_item_catalog.json', 'r', encoding='utf-8') as f:
                                    catalog_data = json.load(f)
                                    for category in catalog_data['minecraft:crafting_items_catalog']['categories']:
                                        for group in category.get('groups', []):
                                            if 'group_identifier' in group and 'name' in group['group_identifier']:
                                                name = group['group_identifier']['name']
                                                if name.startswith('jct:'):
                                                    category_name = name.replace('jct:', '')
                                                    project_category_translations.add(category_name)
                            except Exception as e:
                                print_if_not_quiet(ConsoleStyle.error(f"Error reading crafting catalog: {e}"))
                                warnings.append(f"Error reading crafting catalog: {e}")

                            # Wczytaj bloki
                            project_block_translations = set()
                            for root, dirs, files in os.walk("BP/blocks"):
                                for file in files:
                                    if file.endswith('.block.json'):
                                        file_path = os.path.join(root, file)
                                        try:
                                            with open(file_path, 'r', encoding='utf-8') as f:
                                                block_data = json.load(f)
                                                block_name = block_data['minecraft:block']['description']['identifier']
                                                project_block_translations.add(block_name.replace('jct:', ''))
                                        except Exception as e:
                                            print_if_not_quiet(
                                                ConsoleStyle.error(f"Error reading block data file [{file}]: {e}"))
                                            warnings.append(f"Error reading block data file [{file}]: {e}")

                            # Porównaj znaki
                            stats[ConsoleStyle.info(
                                "In lang file")] = f'{len(file_category_translations) + len(file_block_translations)}'
                            stats["   crafting catalog in file"] = len(file_block_translations)
                            file_extra_categories = file_category_translations - project_category_translations
                            if file_extra_categories:
                                warnings.append(f"Extra [{len(file_extra_categories)}] categories in [{lang_name}]")
                                stats[
                                    "   extra categories in lang file"] = f'[{len(file_extra_categories)}] ({', '.join([f'{name}' for name in sorted(file_extra_categories)])})'
                            stats["   blocks in file"] = len(project_block_translations)
                            file_extra_blocks = file_block_translations - project_block_translations
                            if file_extra_blocks:
                                warnings.append(f"Extra [{len(file_extra_blocks)}] blocks in [{lang_name}]")
                                stats[
                                    "   extra blocks in lang file"] = f'[{len(file_extra_blocks)}] ({', '.join([f'{name}' for name in sorted(file_extra_blocks)])})'

                            stats[ConsoleStyle.info("In project")] = len(project_category_translations) + len(
                                project_block_translations)
                            stats["   blocks in project"] = len(project_block_translations)
                            stats["   crafting catalog in project"] = len(project_category_translations)
                            file_missing_categories = project_category_translations - file_category_translations
                            if file_missing_categories:
                                warnings.append(
                                    f"Missing [{len(file_missing_categories)}] categories from crafting catalog in [{lang_name}]")
                                stats[
                                    "   missing categories from crafting catalog"] = f'[{len(file_missing_categories)}] ({', '.join([f'{name}' for name in sorted(file_missing_categories)])})'
                            file_missing_blocks = project_block_translations - file_block_translations
                            if file_missing_blocks:
                                warnings.append(
                                    f"Missing [{len(file_missing_blocks)}] blocks from crafting catalog in [{lang_name}]")
                                stats[
                                    "   missing blocks from files"] = f'[{len(file_missing_blocks)}] ({', '.join([f'{name}' for name in sorted(file_missing_blocks)])})'

                            ConsoleStyle.print_stats(stats, f"{lang_name}", '-')

                        except Exception as e:
                            print_if_not_quiet(ConsoleStyle.error(f"Error reading [{lang_path}]: {e}"))
                            errors.append(f"Error reading [{lang_path}]")

                            continue
                    else:
                        errors.append(f"Missing language file [{lang_name}.lang]")
            else:
                errors.append("languages.json should be a list of language codes")

        except json.JSONDecodeError as e:
            errors.append(f"languages.json is invalid JSON: {e}")
        except Exception as e:
            errors.append(f"Error reading languages.json: {e}")
    else:
        errors.append("Missing languages.json")

    return errors, warnings


def verify_blocks():
    """Verify all block files are valid and have required fields"""
    ConsoleStyle.print_section("⏹️ VERIFYING BLOCKS")

    errors = []
    warnings = []
    block_count = 0

    for root, dirs, files in os.walk("BP/blocks"):
        for file in files:
            if file.endswith('.block.json'):
                block_count += 1
                file_path = os.path.join(root, file)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # Check required structure
                    if 'minecraft:block' not in data:
                        errors.append(f"{file}: Missing 'minecraft:block' section")
                        continue

                    block_data = data['minecraft:block']

                    # Check description
                    if 'description' not in block_data:
                        errors.append(f"{file}: Missing 'description' section")
                        continue

                    description = block_data['description']

                    # Check identifier
                    if 'identifier' not in description:
                        errors.append(f"{file}: Missing 'identifier' field")
                    else:
                        identifier = description['identifier']
                        if ':' not in identifier:
                            errors.append(f"{file}: Invalid identifier format (should be 'namespace:name')")

                    # Check components
                    if 'components' not in block_data:
                        errors.append(f"{file}: Missing 'components' section")

                except json.JSONDecodeError as e:
                    errors.append(f"{file}: Invalid JSON - {e}")
                except Exception as e:
                    errors.append(f"{file}: Error reading file - {e}")

    print_if_not_quiet(ConsoleStyle.success(f"Found {block_count} block files"))

    if block_count == 0:
        warnings.append("No block files found")

    return errors, warnings


def verify_textures():
    """Verify texture files and mappings with detailed analysis"""
    ConsoleStyle.print_section("🎨 VERIFYING TEXTURES")

    errors = []
    warnings = []

    texture_dir = "RP/textures/blocks"
    terrain_texture_file = "RP/textures/terrain_texture.json"

    # Check if directories exist
    if not os.path.exists(texture_dir):
        errors.append(f"Texture directory does not exist: {texture_dir}")
        return errors, warnings

    if not os.path.exists(terrain_texture_file):
        errors.append(f"terrain_texture.json does not exist: {terrain_texture_file}")
        return errors, warnings

    # Detailed texture verification from verify_textures.py
    ConsoleStyle.print_section("🔍 VERIFYING TERRAIN_TEXTURE.JSON MAPPING")

    terrain_data = load_json_file(terrain_texture_file)
    if terrain_data:
        texture_mappings = terrain_data.get('texture_data', {})

        missing_textures = []
        valid_textures = []

        for texture_id, texture_info in texture_mappings.items():
            texture_path = texture_info.get('textures')
            if texture_path:
                # Remove "textures/blocks/" prefix
                texture_name = texture_path.replace('textures/blocks/', '')
                full_path = os.path.join(texture_dir, texture_name)

                if os.path.exists(full_path):
                    valid_textures.append(texture_id)
                    print_if_not_quiet(ConsoleStyle.success(f"{texture_id} -> {texture_name}"))
                else:
                    missing_textures.append((texture_id, texture_name))
                    print_if_not_quiet(ConsoleStyle.error(f"{texture_id} -> {texture_name} (MISSING FILE)"))

        ConsoleStyle.print_stats({
            "✅ Valid mappings": len(valid_textures),
            "❌ Missing textures": len(missing_textures),
        }, f"📊 MAPPING SUMMARY")

        if missing_textures:
            print_if_not_quiet(f"\n❌ MISSING TEXTURES:")
            for texture_id, texture_name in missing_textures:
                print_if_not_quiet(f"   - {texture_id}: {texture_name}")
                errors.append(f"Missing texture: {texture_id} -> {texture_name}")

    # Verify block textures
    ConsoleStyle.print_section("🔍 VERIFYING BLOCKS AND TEXTURES")

    blocks_dir = "BP/blocks"
    block_files = glob.glob(os.path.join(blocks_dir, "**/*.block.json"), recursive=True)

    valid_blocks = []
    invalid_blocks = []
    missing_textures = []

    for block_file in sorted(block_files):
        block_data = load_json_file(block_file)
        if not block_data:
            continue

        # Extract block identifier
        identifier = block_data.get('minecraft:block', {}).get('description', {}).get('identifier', 'UNKNOWN')

        # Extract texture
        texture_name = extract_texture_from_block(block_data)

        if texture_name:
            if check_texture_exists(texture_name, texture_dir, terrain_texture_file):
                valid_blocks.append((identifier, texture_name))
                print_if_not_quiet(ConsoleStyle.success(f"{identifier} -> {texture_name}"))
            else:
                invalid_blocks.append((identifier, texture_name))
                missing_textures.append(texture_name)
                print_if_not_quiet(ConsoleStyle.error(f"{identifier} -> {texture_name} (MISSING TEXTURE)"))
                errors.append(f"Block {identifier} references missing texture: {texture_name}")
        else:
            print_if_not_quiet(ConsoleStyle.warning(f"{identifier} -> NO TEXTURE"))
            warnings.append(f"Block {identifier} has no texture defined")

    ConsoleStyle.print_stats({
        "✅ Valid blocks": len(valid_blocks),
        "❌ Invalid blocks": len(invalid_blocks),
    }, f"📊 BLOCK SUMMARY")

    if invalid_blocks:
        print_if_not_quiet(f"\n❌ BLOCKS WITH MISSING TEXTURES:")
        for identifier, texture_name in invalid_blocks:
            print_if_not_quiet(f"   - {identifier}: {texture_name}")

    # Check unused textures
    ConsoleStyle.print_section("🔍 VERIFYING UNUSED TEXTURES")

    # Get all texture files
    texture_files = []
    for ext in ['*.png', '*.jpg', '*.jpeg']:
        texture_files.extend(glob.glob(os.path.join(texture_dir, ext)))

    # Get used textures from terrain_texture.json
    terrain_data = load_json_file(terrain_texture_file)
    used_textures = set()

    if terrain_data:
        texture_mappings = terrain_data.get('texture_data', {})
        for texture_info in texture_mappings.values():
            texture_path = texture_info.get('textures', '')
            if texture_path:
                texture_name = texture_path.replace('textures/blocks/', '')
                used_textures.add(texture_name)

    # Check unused textures
    unused_textures = []
    for texture_file in texture_files:
        texture_name = os.path.basename(texture_file)
        if texture_name not in used_textures:
            unused_textures.append(texture_name)
            warnings.append(f"Unused texture: {texture_name}")

    ConsoleStyle.print_stats({
        "📁Total textures": f"[{len(texture_files)}]",
        "✅ Used textures": f"[{len(used_textures)}]",
        "🗑Unused textures": f"[{len(unused_textures)}] ({', '.join([f'{name}' for name in sorted(unused_textures)])})" if unused_textures else "0",
    }, f"📊 TEXTURE SUMMARY")

    return errors, warnings


def main():
    """Main verification function"""
    ConsoleStyle.print_section("🔍 COMPREHENSIVE PROJECT VERIFICATION")

    all_errors = []
    all_warnings = []

    # Run all verification functions
    verifications = [
        verify_manifests,
        verify_config,
        verify_project_structure,
        verify_translations,
        verify_blocks,
        verify_textures,
        count_project_files,
    ]

    for verify_func in verifications:
        try:
            errors, warnings = verify_func()
            all_errors.extend(errors)
            all_warnings.extend(warnings)
        except Exception as e:
            all_errors.append(f"Error in {verify_func.__name__}: {e}")

    # Print summary
    ConsoleStyle.print_section("📋 VERIFICATION SUMMARY")

    if all_errors:
        print_if_not_quiet(ConsoleStyle.error(f"Found {len(all_errors)} errors:"))
        for error in all_errors:
            print_if_not_quiet(f"  • {error}")
    else:
        print_if_not_quiet(ConsoleStyle.success("No errors found!"))

    if all_warnings:
        print_if_not_quiet(ConsoleStyle.warning(f"Found {len(all_warnings)} warnings:"))
        for warning in all_warnings:
            print_if_not_quiet(f"  • {warning}")
    else:
        print_if_not_quiet(ConsoleStyle.success("No warnings found!"))

    # Exit with the appropriate code
    if all_errors:
        print_if_not_quiet(ConsoleStyle.error(f"Verification failed with {len(all_errors)} errors"))
        sys.exit(1)
    else:
        print_if_not_quiet(ConsoleStyle.success("Verification passed! Project is ready for building."))
        sys.exit(0)


if __name__ == "__main__":
    main()
