#!/usr/bin/env python3
"""
Script to create a minimal RNAmigos2 inference package.

This script copies all necessary files from the full repository to create
a minimal distribution containing only what's needed for inference.

Usage:
    python create_minimal.py [source_dir] [target_dir]
    
    source_dir: Path to the full RNAmigos2 repository (default: parent directory)
    target_dir: Path where minimal package will be created (default: rnamigos2_minimal)
"""

import os
import shutil
import sys
from pathlib import Path


def create_directory_structure(target_dir):
    """Create all required directories."""
    directories = [
        "rnamigos/learning",
        "rnamigos/utils",
        "data/map_files",
        "data/sample_files",
        "inputs/structures",
        "inputs/ligands",
        "outputs",
        "results/trained_models/is_native/native_42",
        "results/trained_models/dock/dock_42",
    ]
    
    for dir_path in directories:
        full_path = target_dir / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {full_path}")


def copy_file(source, target, description=""):
    """Copy a file and print status."""
    try:
        shutil.copy2(source, target)
        print(f"Copied: {source} -> {target} {description}")
        return True
    except FileNotFoundError:
        print(f"WARNING: File not found: {source}")
        return False
    except Exception as e:
        print(f"ERROR copying {source}: {e}")
        return False


def create_init_files(target_dir):
    """Create __init__.py files for package structure."""
    init_files = [
        "rnamigos/__init__.py",
        "rnamigos/learning/__init__.py",
        "rnamigos/utils/__init__.py",
    ]
    
    for init_file in init_files:
        file_path = target_dir / init_file
        file_path.touch()
        print(f"Created: {file_path}")


def main(source_dir=None, target_dir=None):
    """Main function to create minimal package."""
    
    # Determine source directory (parent of script location by default)
    if source_dir is None:
        script_dir = Path(__file__).parent.absolute()
        # Assume source is the parent directory
        source_dir = script_dir.parent
    
    source_dir = Path(source_dir).resolve()
    if not source_dir.exists():
        print(f"ERROR: Source directory does not exist: {source_dir}")
        sys.exit(1)
    
    # Determine target directory
    if target_dir is None:
        target_dir = source_dir.parent / "rnamigos2_minimal"
    else:
        target_dir = Path(target_dir).resolve()
    
    print(f"Creating minimal package from: {source_dir}")
    print(f"Target directory: {target_dir}")
    print()
    
    # Create directory structure
    create_directory_structure(target_dir)
    print()
    
    # Copy Python modules
    python_files = [
        ("rnamigos/inference.py", "rnamigos/inference.py"),
        ("rnamigos/learning/models.py", "rnamigos/learning/models.py"),
        ("rnamigos/learning/dataset.py", "rnamigos/learning/dataset.py"),
        ("rnamigos/learning/ligand_encoding.py", "rnamigos/learning/ligand_encoding.py"),
        ("rnamigos/utils/graph_utils.py", "rnamigos/utils/graph_utils.py"),
        ("rnamigos/utils/mixing_utils.py", "rnamigos/utils/mixing_utils.py"),
        ("rnamigos/utils/virtual_screen.py", "rnamigos/utils/virtual_screen.py"),
    ]
    
    print("Copying Python modules...")
    for source_rel, target_rel in python_files:
        source = source_dir / source_rel
        target = target_dir / target_rel
        copy_file(source, target)
    print()
    
    # Copy data files
    data_files = [
        ("data/map_files/edges_and_nodes_map.pickle", "data/map_files/edges_and_nodes_map.pickle"),
        ("data/sample_files/3ox0.cif", "data/sample_files/3ox0.cif"),
        ("data/sample_files/test_smiles.txt", "data/sample_files/test_smiles.txt"),
    ]
    
    print("Copying data files...")
    for source_rel, target_rel in data_files:
        source = source_dir / source_rel
        target = target_dir / target_rel
        copy_file(source, target)
    print()
    
    # Copy model checkpoints
    model_files = [
        ("results/trained_models/is_native/native_42/config.yaml", 
         "results/trained_models/is_native/native_42/config.yaml"),
        ("results/trained_models/is_native/native_42/model.pth", 
         "results/trained_models/is_native/native_42/model.pth"),
        ("results/trained_models/dock/dock_42/config.yaml", 
         "results/trained_models/dock/dock_42/config.yaml"),
        ("results/trained_models/dock/dock_42/model.pth", 
         "results/trained_models/dock/dock_42/model.pth"),
    ]
    
    print("Copying model checkpoints...")
    for source_rel, target_rel in model_files:
        source = source_dir / source_rel
        target = target_dir / target_rel
        copy_file(source, target)
    print()
    
    # Create __init__.py files
    print("Creating __init__.py files...")
    create_init_files(target_dir)
    print()
    
    # Create requirements_minimal.txt (already exists if script is in minimal dir)
    # This is just a placeholder - the actual file should be created manually
    # or copied from a template
    
    print("=" * 60)
    print("Minimal package structure created successfully!")
    print(f"Location: {target_dir}")
    print()
    print("Next steps:")
    print("1. Review the copied files")
    print("2. Install dependencies: pip install -r requirements_minimal.txt")
    print("3. Test with: python -c \"from rnamigos.inference import do_inference\"")
    print("=" * 60)


if __name__ == "__main__":
    source_dir = sys.argv[1] if len(sys.argv) > 1 else None
    target_dir = sys.argv[2] if len(sys.argv) > 2 else None
    main(source_dir, target_dir)
