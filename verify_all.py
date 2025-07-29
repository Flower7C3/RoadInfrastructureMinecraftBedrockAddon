#!/usr/bin/env python3
"""
Comprehensive verification script for Minecraft Bedrock Addon
Verifies project structure, files, textures, and build readiness
"""

import os
import json
import sys
import glob
from pathlib import Path
from console_utils import ConsoleStyle, print_if_not_quiet, print_header

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
        material_instances = block_data.get('minecraft:block', {}).get('components', {}).get('minecraft:material_instances', {})
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
    print_header("🔍 VERIFYING PROJECT STRUCTURE")
    
    required_files = [
        "config.json",
        "BP/manifest.json", 
        "RP/manifest.json",
        "build.py"
    ]
    
    required_dirs = [
        "BP",
        "RP",
        "BP/blocks",
        "RP/textures",
        "RP/texts"
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
    """Verify manifest files are valid JSON and have required fields"""
    print_header("📋 VERIFYING MANIFESTS")
    
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
            
            # Check version format
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
    
    return errors, warnings

def verify_config():
    """Verify config.json is valid and has required fields"""
    print_header("⚙️ VERIFYING CONFIG")
    
    errors = []
    warnings = []
    
    try:
        with open("config.json", 'r', encoding='utf-8') as f:
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
                        try:
                            with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                                block_data = json.load(f)
                                if 'minecraft:block' in block_data:
                                    identifier = block_data['minecraft:block']['description'].get('identifier', '')
                                    if identifier.startswith(f"{namespace}:"):
                                        namespace_used = True
                                        break
                        except:
                            continue
                if namespace_used:
                    break
            
            if not namespace_used:
                warnings.append(f"Namespace '{namespace}' not found in block identifiers")
        
        print_if_not_quiet(ConsoleStyle.success("config.json is valid JSON"))
        
    except json.JSONDecodeError as e:
        errors.append(f"config.json is invalid JSON: {e}")
    except Exception as e:
        errors.append(f"Error reading config.json: {e}")
    
    return errors, warnings

def verify_blocks():
    """Verify all block files are valid and have required fields"""
    print_header("⏹️ VERIFYING BLOCKS")
    
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
    print_header("🎨 VERIFYING TEXTURES")
    
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
    print_if_not_quiet("\n🔍 VERIFYING TERRAIN_TEXTURE.JSON MAPPING")
    print_if_not_quiet("=" * 60)
    
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
        
        print_if_not_quiet(f"\n📊 MAPPING SUMMARY:")
        print_if_not_quiet(f"   ✅ Valid mappings: {len(valid_textures)}")
        print_if_not_quiet(f"   ❌ Missing textures: {len(missing_textures)}")
        
        if missing_textures:
            print_if_not_quiet(f"\n❌ MISSING TEXTURES:")
            for texture_id, texture_name in missing_textures:
                print_if_not_quiet(f"   - {texture_id}: {texture_name}")
                errors.append(f"Missing texture: {texture_id} -> {texture_name}")
    
    # Verify block textures
    print_if_not_quiet("\n🔍 VERIFYING BLOCKS AND TEXTURES")
    print_if_not_quiet("=" * 60)
    
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
    
    print_if_not_quiet(f"\n📊 BLOCK SUMMARY:")
    print_if_not_quiet(f"   ✅ Valid blocks: {len(valid_blocks)}")
    print_if_not_quiet(f"   ❌ Invalid blocks: {len(invalid_blocks)}")
    
    if invalid_blocks:
        print_if_not_quiet(f"\n❌ BLOCKS WITH MISSING TEXTURES:")
        for identifier, texture_name in invalid_blocks:
            print_if_not_quiet(f"   - {identifier}: {texture_name}")
    
    # Check unused textures
    print_if_not_quiet("\n🔍 VERIFYING UNUSED TEXTURES")
    print_if_not_quiet("=" * 60)
    
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
    
    print_if_not_quiet(f"📊 TEXTURE SUMMARY:")
    print_if_not_quiet(f"   📁 Total textures: {len(texture_files)}")
    print_if_not_quiet(f"   ✅ Used textures: {len(used_textures)}")
    print_if_not_quiet(f"   🗑️  Unused textures: {len(unused_textures)}")
    
    if unused_textures:
        print_if_not_quiet(f"\n🗑️  UNUSED TEXTURES:")
        for texture_name in sorted(unused_textures):
            print_if_not_quiet(f"   - {texture_name}")
            warnings.append(f"Unused texture: {texture_name}")
    
    return errors, warnings

def verify_localization():
    """Verify localization files"""
    print_header("🌐 VERIFYING LOCALIZATION")
    
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
                for lang_file in language_files:
                    lang_path = f"RP/texts/{lang_file}.lang"
                    if os.path.exists(lang_path):
                        print_if_not_quiet(ConsoleStyle.success(f"Found: {lang_file}.lang"))
                    else:
                        errors.append(f"Missing language file: {lang_file}.lang")
            else:
                errors.append("languages.json should be a list of language codes")
            
        except json.JSONDecodeError as e:
            errors.append(f"languages.json is invalid JSON: {e}")
        except Exception as e:
            errors.append(f"Error reading languages.json: {e}")
    else:
        errors.append("Missing languages.json")
    
    return errors, warnings

def verify_build_script():
    """Verify build script is valid Python"""
    print_header("🔨 VERIFYING BUILD SCRIPT")
    
    errors = []
    warnings = []
    
    if os.path.exists("build.py"):
        try:
            # Try to import the build script
            import build
            print_if_not_quiet(ConsoleStyle.success("build.py is valid Python"))
            
            # Check if main function exists
            if hasattr(build, 'main'):
                print_if_not_quiet(ConsoleStyle.success("build.py has main function"))
            else:
                warnings.append("build.py missing main function")
            
        except ImportError as e:
            errors.append(f"build.py import error: {e}")
        except Exception as e:
            errors.append(f"Error testing build.py: {e}")
    else:
        errors.append("Missing build.py")
    
    return errors, warnings

def count_project_files():
    """Count files in project"""
    print_header("📊 PROJECT STATISTICS")
    
    stats = {}
    
    # Count files by directory
    for root, dirs, files in os.walk("."):
        # Skip git and cache directories
        if any(skip in root for skip in ['.git', '__pycache__', 'venv', 'dist']):
            continue
        
        rel_path = os.path.relpath(root, ".")
        if rel_path == ".":
            rel_path = "root"
        
        stats[rel_path] = len(files)
    
    # Print statistics
    total_files = sum(stats.values())
    print_if_not_quiet(f"📦 Total files: {total_files}")
    
    for directory, count in sorted(stats.items()):
        if count > 0:
            print_if_not_quiet(f"  📁 {directory}/: {count} files")
    
    return stats

def main():
    """Main verification function"""
    print_if_not_quiet("🔍 COMPREHENSIVE PROJECT VERIFICATION")
    print_if_not_quiet("=" * 60)
    
    all_errors = []
    all_warnings = []
    
    # Run all verification functions
    verifications = [
        verify_project_structure,
        verify_manifests,
        verify_config,
        verify_blocks,
        verify_textures,
        verify_localization,
        verify_build_script
    ]
    
    for verify_func in verifications:
        try:
            errors, warnings = verify_func()
            all_errors.extend(errors)
            all_warnings.extend(warnings)
        except Exception as e:
            all_errors.append(f"Error in {verify_func.__name__}: {e}")
    
    # Count files
    stats = count_project_files()
    
    # Print summary
    print_header("📋 VERIFICATION SUMMARY")
    
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
    
    # Exit with appropriate code
    if all_errors:
        print_if_not_quiet(ConsoleStyle.error(f"Verification failed with {len(all_errors)} errors"))
        sys.exit(1)
    else:
        print_if_not_quiet(ConsoleStyle.success("Verification passed! Project is ready for building."))
        sys.exit(0)

if __name__ == "__main__":
    main() 