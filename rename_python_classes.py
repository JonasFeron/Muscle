import os
import re
from pathlib import Path

# Define the root directory of your project
PROJECT_ROOT = Path("c:/Users/Jonas/Documents/GitHub/Muscle")
MUSCLE_PY_DIR = PROJECT_ROOT / "src" / "MusclePy"
TESTS_DIR = PROJECT_ROOT / "tests" / "MusclePyTests"

# Class name mappings
CLASS_MAPPINGS = {
    "FEM_Nodes": "PyNodes",
    "FEM_Elements": "PyElements",
    "FEM_Structure": "PyTruss",
    "SVDResults": "PyResultsSVD",
    "DR_Structure": "PyTrussDR",
    "DR_Nodes": "PyNodesDR",
    "DR_Elements": "PyElementsDR",
    "DRconfig": "PyConfigDR"

}

# Module name mappings
MODULE_MAPPINGS = {
    "fem_nodes": "pynodes",
    "fem_elements": "pyelements",
    "fem_structure": "pytruss",
    "svd_results": "py_results_svd",
    "dr_structure": "py_truss_dr",
    "dr_nodes": "py_nodes_dr",
    "dr_elements": "py_elements_dr",
    "dr_config": "py_config_dr"
}

# File name mappings
FILE_MAPPINGS = {
    "dr_structure.py": "py_truss_dr.py",
    "dr_nodes.py": "py_nodes_dr.py",
    "dr_elements.py": "py_elements_dr.py",
    "dr_config.py": "py_config_dr.py",
    "svd_results.py": "py_results_svd.py"
}

# Test file mappings
TEST_FILE_MAPPINGS = {
    "test_fem_nodes.py": "test_pynodes.py",
    "test_fem_elements.py": "test_pyelements.py"
}

# Test class mappings
TEST_CLASS_MAPPINGS = {
    "TestFEMNodes": "TestPyNodes",
    "TestFEMElements": "TestPyElements"
}

def update_file_content(file_path):
    """Update class names and import statements in a file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Replace class names
    for old_class, new_class in CLASS_MAPPINGS.items():
        # Use word boundary to ensure we only replace whole words
        content = re.sub(r'\b' + old_class + r'\b', new_class, content)
    
    # Replace test class names
    for old_class, new_class in TEST_CLASS_MAPPINGS.items():
        # Use word boundary to ensure we only replace whole words
        content = re.sub(r'\b' + old_class + r'\b', new_class, content)
    
    # Update import statements for module mappings
    for old_module, new_module in MODULE_MAPPINGS.items():
        # Various import patterns
        patterns = [
            rf'from MusclePy\.femodel\.{old_module} import',
            rf'from MusclePy\.femodel import {old_module}',
            rf'import MusclePy\.femodel\.{old_module}',
            rf'from MusclePy\.solvers\.dr\.{old_module} import',
            rf'from MusclePy\.solvers\.dr import {old_module}',
            rf'import MusclePy\.solvers\.dr\.{old_module}',
            rf'from MusclePy\.solvers\.svd\.{old_module} import',
            rf'from MusclePy\.solvers\.svd import {old_module}',
            rf'import MusclePy\.solvers\.svd\.{old_module}',
            rf'from \.{old_module} import',
            rf'import \.{old_module}'
        ]
        replacements = [
            f'from MusclePy.femodel.{new_module} import',
            f'from MusclePy.femodel import {new_module}',
            f'import MusclePy.femodel.{new_module}',
            f'from MusclePy.solvers.dr.{new_module} import',
            f'from MusclePy.solvers.dr import {new_module}',
            f'import MusclePy.solvers.dr.{new_module}',
            f'from MusclePy.solvers.svd.{new_module} import',
            f'from MusclePy.solvers.svd import {new_module}',
            f'import MusclePy.solvers.svd.{new_module}',
            f'from .{new_module} import',
            f'import .{new_module}'
        ]
        
        for pattern, replacement in zip(patterns, replacements):
            content = re.sub(pattern, replacement, content)
    
    # Only write if content has changed
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated: {file_path}")
    else:
        print(f"No changes needed: {file_path}")

def rename_file_if_needed(file_path):
    """Rename file if it matches any of the mappings"""
    file_name = os.path.basename(file_path)
    
    # Check test file mappings
    if file_name in TEST_FILE_MAPPINGS:
        new_file_name = TEST_FILE_MAPPINGS[file_name]
        new_file_path = os.path.join(os.path.dirname(file_path), new_file_name)
        if not os.path.exists(new_file_path):
            os.rename(file_path, new_file_path)
            print(f"Renamed: {file_name} → {new_file_name}")
            return new_file_path
    
    # Check regular file mappings
    if file_name in FILE_MAPPINGS:
        new_file_name = FILE_MAPPINGS[file_name]
        new_file_path = os.path.join(os.path.dirname(file_path), new_file_name)
        if not os.path.exists(new_file_path):
            os.rename(file_path, new_file_path)
            print(f"Renamed: {file_name} → {new_file_name}")
            return new_file_path
    
    return file_path

def process_directory(directory):
    """Process all Python files in a directory recursively"""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                # First update the content
                update_file_content(file_path)
                
                # Then rename if needed
                file_path = rename_file_if_needed(file_path)

def main():
    # Process MusclePy directory
    print("Processing MusclePy directory...")
    process_directory(MUSCLE_PY_DIR)
    
    # Process MusclePyTests directory
    print("\nProcessing MusclePyTests directory...")
    process_directory(TESTS_DIR)
    
    print("\nRenaming process completed!")
    print("\nReminder: You may need to manually check for:")
    print("1. References in string literals or dynamically constructed names")
    print("2. Any remaining references to old class names in C# interop code")
    print("3. Run your tests to ensure everything works correctly")

if __name__ == "__main__":
    main()
