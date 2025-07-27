#!/usr/bin/env python3
"""
Comprehensive verification script for Minecraft Bedrock Addon
Verifies project structure, files, textures, and build readiness
"""

import os
import json
import sys
from pathlib import Path
from console_utils import ConsoleStyle, print_if_not_quiet

def print_header(title):
    """Print formatted header"""
    print(f"\n{ConsoleStyle.header(title)}")
    print("=" * 60)

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
            print(f"✅ Found: {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            errors.append(f"Missing required file: {file_path}")
    
    # Check required directories
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ Found: {dir_path}/")
        else:
            print(f"❌ Missing: {dir_path}/")
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
                    print(f"✅ {pack_type} version: {'.'.join(map(str, version))}")
            
            print(f"✅ {pack_type} manifest is valid JSON")
            
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
            print(f"✅ Namespace: {namespace}")
            
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
        
        print("✅ config.json is valid JSON")
        
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
    
    print(f"✅ Found {block_count} block files")
    
    if block_count == 0:
        warnings.append("No block files found")
    
    return errors, warnings

def verify_textures():
    """Verify texture files and mappings"""
    print_header("🎨 VERIFYING TEXTURES")
    
    errors = []
    warnings = []
    
    # Check terrain_texture.json
    terrain_texture_path = "RP/textures/terrain_texture.json"
    if os.path.exists(terrain_texture_path):
        try:
            with open(terrain_texture_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            texture_data = data.get('texture_data', {})
            print(f"✅ Found {len(texture_data)} texture mappings")
            
            # Check if texture files exist
            missing_textures = []
            for texture_id, texture_info in texture_data.items():
                if 'textures' in texture_info:
                    texture_path = texture_info['textures']
                    full_path = f"RP/{texture_path}"
                    if not os.path.exists(full_path):
                        missing_textures.append(f"{texture_id} -> {full_path}")
            
            if missing_textures:
                for missing in missing_textures:
                    errors.append(f"Missing texture file: {missing}")
            
        except json.JSONDecodeError as e:
            errors.append(f"terrain_texture.json is invalid JSON: {e}")
        except Exception as e:
            errors.append(f"Error reading terrain_texture.json: {e}")
    else:
        errors.append("Missing terrain_texture.json")
    
    # Count texture files
    texture_count = 0
    for root, dirs, files in os.walk("RP/textures"):
        for file in files:
            if file.endswith(('.png', '.jpg', '.jpeg')):
                texture_count += 1
    
    print(f"✅ Found {texture_count} texture files")
    
    if texture_count == 0:
        warnings.append("No texture files found")
    
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
                print(f"✅ Found {len(language_files)} language files")
                
                # Check if language files exist
                for lang_file in language_files:
                    lang_path = f"RP/texts/{lang_file}.lang"
                    if os.path.exists(lang_path):
                        print(f"✅ Found: {lang_file}.lang")
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
            print("✅ build.py is valid Python")
            
            # Check if main function exists
            if hasattr(build, 'main'):
                print("✅ build.py has main function")
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
    print(f"📦 Total files: {total_files}")
    
    for directory, count in sorted(stats.items()):
        if count > 0:
            print(f"  📁 {directory}/: {count} files")
    
    return stats

def main():
    """Main verification function"""
    print("🔍 COMPREHENSIVE PROJECT VERIFICATION")
    print("=" * 60)
    
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
        print(f"❌ Found {len(all_errors)} errors:")
        for error in all_errors:
            print(f"  • {error}")
    else:
        print("✅ No errors found!")
    
    if all_warnings:
        print(f"⚠️ Found {len(all_warnings)} warnings:")
        for warning in all_warnings:
            print(f"  • {warning}")
    else:
        print("✅ No warnings found!")
    
    # Exit with appropriate code
    if all_errors:
        print(f"\n❌ Verification failed with {len(all_errors)} errors")
        sys.exit(1)
    else:
        print(f"\n✅ Verification passed! Project is ready for building.")
        sys.exit(0)

if __name__ == "__main__":
    main() 