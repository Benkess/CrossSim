#!/usr/bin/env python3
"""
Test script to verify CrossSim installation and launch the simple editor.
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported."""
    try:
        import crosssim
        print(f"✓ CrossSim version {crosssim.__version__} imported successfully")
        
        from crosssim.core.scenario import Scenario
        print("✓ Core scenario module imported")
        
        from crosssim.core.environment import Environment
        print("✓ Core environment module imported")
        
        from crosssim.core.agent import Agent, Robot
        print("✓ Core agent modules imported")
        
        from crosssim.gui.simple_editor import SimpleEnvironmentEditor
        print("✓ Simple editor GUI imported")
        
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_dependencies():
    """Test if all required dependencies are available."""
    try:
        import PyQt5
        print("✓ PyQt5 available")
        
        import numpy
        print("✓ NumPy available")
        
        import yaml
        print("✓ PyYAML available")
        
        return True
    except ImportError as e:
        print(f"✗ Dependency missing: {e}")
        return False

def main():
    """Main test function."""
    print("CrossSim Installation Test")
    print("=" * 30)
    
    # Test dependencies
    print("\nTesting dependencies...")
    deps_ok = test_dependencies()
    
    # Test imports
    print("\nTesting imports...")
    imports_ok = test_imports()
    
    if deps_ok and imports_ok:
        print("\n✓ All tests passed!")
        
        # Ask if user wants to launch the simple editor
        response = input("\nWould you like to launch the simple environment editor? (y/N): ")
        if response.lower() in ['y', 'yes']:
            print("Launching simple environment editor...")
            from crosssim.gui.simple_editor import main as launch_editor
            return launch_editor()
        else:
            print("Test completed successfully. You can launch the editor with:")
            print("  python -m crosssim.gui.simple_editor")
            print("  or: crosssim-simple (if installed)")
            return 0
    else:
        print("\n✗ Some tests failed. Please check the installation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
