"""
Main entry point for the CrossSim GUI application.

This module provides the main function to launch the interactive environment
creation GUI.
"""

import sys
import argparse
from typing import Optional
from PyQt5.QtWidgets import QApplication
from crosssim.gui.main_window import MainWindow
from crosssim.gui.simple_editor import SimpleEnvironmentEditor


def main(args: Optional[list] = None) -> int:
    """
    Main entry point for the CrossSim GUI application.
    
    Args:
        args: Command line arguments (optional)
        
    Returns:
        Exit code
    """
    if args is None:
        args = sys.argv
    
    # Parse arguments for GUI mode selection
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--simple', action='store_true', 
                       help='Launch simple 2D environment editor')
    parsed_args, remaining = parser.parse_known_args(args[1:])
    
    app = QApplication([args[0]] + remaining)
    app.setApplicationName("CrossSim")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("CrossSim")
    
    # Create and show the appropriate window
    if parsed_args.simple:
        window = SimpleEnvironmentEditor()
    else:
        window = MainWindow()
    
    window.show()
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
