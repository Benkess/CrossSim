#!/usr/bin/env python3
"""
Check dependencies and setup for CrossSim Simple Editor.
"""

import sys
import subprocess

def check_dependency(module_name, package_name=None, import_name=None):
    """Check if a dependency is available."""
    if import_name is None:
        import_name = module_name
    if package_name is None:
        package_name = module_name
    
    try:
        __import__(import_name)
        print(f"✓ {module_name} is available")
        return True
    except ImportError:
        print(f"✗ {module_name} is missing")
        print(f"  Install with: pip install {package_name}")
        return False

def main():
    """Check all dependencies."""
    print("CrossSim Simple Editor - Dependency Check")
    print("=" * 45)
    
    dependencies = [
        ("PyQt5", "PyQt5", "PyQt5.QtWidgets"),
        ("NumPy", "numpy", "numpy"),
        ("PyYAML", "pyyaml", "yaml"),
    ]
    
    all_ok = True
    
    for module_name, package_name, import_name in dependencies:
        if not check_dependency(module_name, package_name, import_name):
            all_ok = False
    
    print()
    
    if all_ok:
        print("✓ All dependencies are available!")
        print("\nYou can now run the simple editor:")
        print("  cd /home/benpkessler/CrossSim")
        print("  PYTHONPATH=/home/benpkessler/CrossSim python3 crosssim/gui/simple_editor.py")
        return 0
    else:
        print("✗ Some dependencies are missing.")
        print("\nInstall missing dependencies with:")
        print("  pip install PyQt5 numpy pyyaml")
        return 1

if __name__ == "__main__":
    sys.exit(main())
