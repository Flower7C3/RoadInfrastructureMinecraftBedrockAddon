#!/usr/bin/env python3
"""
GitHub Release Script for Road Infrastructure Addon
Automatically creates releases and uploads build artifacts
"""

import os
import json
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

def run_command(cmd, check=True):
    """Run shell command and return result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout.strip(), e.stderr.strip(), e.returncode

def get_latest_version():
    """Get latest version from manifest"""
    with open("BP/manifest.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    version = data['header']['version']
    return f"{version[0]}.{version[1]}.{version[2]}"

def get_release_notes():
    """Generate release notes from recent commits"""
    stdout, stderr, code = run_command("git log --oneline -10")
    if code != 0:
        return "Release notes unavailable"
    
    lines = stdout.split('\n')
    notes = "## Recent Changes\n\n"
    for line in lines:
        if line.strip():
            notes += f"- {line}\n"
    
    return notes

def create_github_release(version, release_notes, files):
    """Create GitHub release using gh CLI"""
    print(f"Creating GitHub release v{version}...")
    
    # Create release
    cmd = f'gh release create v{version} --title "Road Infrastructure v{version}" --notes "{release_notes}"'
    stdout, stderr, code = run_command(cmd)
    
    if code != 0:
        print(f"Error creating release: {stderr}")
        return False
    
    print(f"Release created: {stdout}")
    
    # Upload files
    for file_path in files:
        if os.path.exists(file_path):
            print(f"Uploading {os.path.basename(file_path)}...")
            cmd = f'gh release upload v{version} "{file_path}"'
            stdout, stderr, code = run_command(cmd)
            
            if code != 0:
                print(f"Error uploading {file_path}: {stderr}")
            else:
                print(f"Uploaded: {os.path.basename(file_path)}")
        else:
            print(f"Warning: File not found: {file_path}")
    
    return True

def check_gh_cli():
    """Check if GitHub CLI is installed and authenticated"""
    stdout, stderr, code = run_command("gh --version")
    if code != 0:
        print("Error: GitHub CLI (gh) is not installed")
        print("Install from: https://cli.github.com/")
        return False
    
    stdout, stderr, code = run_command("gh auth status")
    if code != 0:
        print("Error: GitHub CLI is not authenticated")
        print("Run: gh auth login")
        return False
    
    return True

def get_repository_info():
    """Get repository information"""
    stdout, stderr, code = run_command("git remote get-url origin")
    if code != 0:
        print("Error: Cannot get repository URL")
        return None
    
    url = stdout.strip()
    if url.endswith('.git'):
        url = url[:-4]
    
    # Extract owner/repo from URL
    if 'github.com' in url:
        parts = url.split('github.com/')
        if len(parts) > 1:
            return parts[1]
    
    return None

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Create GitHub release for Road Infrastructure Addon")
    parser.add_argument("--version", help="Version to release (default: auto-detect)")
    parser.add_argument("--files", nargs="+", help="Files to upload")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without doing it")
    parser.add_argument("--check", action="store_true", help="Check prerequisites only")
    
    args = parser.parse_args()
    
    print("🚀 GITHUB RELEASE SCRIPT")
    print("=" * 50)
    
    # Check prerequisites
    if not check_gh_cli():
        return
    
    repo_info = get_repository_info()
    if not repo_info:
        print("Error: Cannot determine repository information")
        return
    
    print(f"Repository: {repo_info}")
    
    if args.check:
        print("✅ All prerequisites met!")
        return
    
    # Get version
    version = args.version or get_latest_version()
    print(f"Version: {version}")
    
    # Get files to upload
    if args.files:
        files = args.files
    else:
        # Auto-detect files in dist/
        dist_dir = "dist"
        if os.path.exists(dist_dir):
            files = []
            for file in os.listdir(dist_dir):
                if file.endswith(('.mcaddon', '.mcpack')):
                    files.append(os.path.join(dist_dir, file))
        else:
            files = []
    
    print(f"Files to upload: {len(files)}")
    for file in files:
        print(f"  - {os.path.basename(file)}")
    
    # Generate release notes
    release_notes = get_release_notes()
    
    if args.dry_run:
        print("\n--- DRY RUN ---")
        print(f"Would create release: v{version}")
        print(f"Would upload {len(files)} files")
        print("Release notes preview:")
        print(release_notes[:200] + "..." if len(release_notes) > 200 else release_notes)
        return
    
    # Confirm action
    response = input(f"\nCreate GitHub release v{version}? (y/N): ")
    if response.lower() != 'y':
        print("Release cancelled")
        return
    
    # Create release
    if create_github_release(version, release_notes, files):
        print("\n✅ Release created successfully!")
        print(f"View at: https://github.com/{repo_info}/releases/tag/v{version}")
    else:
        print("\n❌ Release failed!")

if __name__ == "__main__":
    main() 