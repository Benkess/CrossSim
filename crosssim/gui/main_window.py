"""
Main window for the CrossSim GUI application.

This module provides the primary user interface for the interactive environment
creation toolkit.
"""

from typing import Optional
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QMenuBar, QMenu, QAction, QStatusBar, QSplitter,
    QDockWidget, QTabWidget, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence

from crosssim.gui.map_editor import MapEditor
from crosssim.gui.agent_editor import AgentEditor
from crosssim.gui.scenario_panel import ScenarioPanel
from crosssim.gui.properties_panel import PropertiesPanel


class MainWindow(QMainWindow):
    """
    Main window for the CrossSim GUI application.
    
    Provides the primary interface for creating and editing robotic simulation
    scenarios, including map editing, agent placement, and scenario configuration.
    """
    
    # Signals
    scenario_changed = pyqtSignal()
    selection_changed = pyqtSignal(object)
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the main window.
        
        Args:
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        
        self.setWindowTitle("CrossSim - Environment Creation Toolkit")
        self.setMinimumSize(1200, 800)
        
        # Initialize components
        self._setup_ui()
        self._setup_menus()
        self._setup_toolbars()
        self._setup_status_bar()
        self._connect_signals()
        
        # Center the window
        self._center_window()
    
    def _setup_ui(self) -> None:
        """Set up the main user interface layout."""
        # Create central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Main horizontal splitter
        main_splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(main_splitter)
        
        # Left panel - Scenario and properties
        left_panel = self._create_left_panel()
        main_splitter.addWidget(left_panel)
        
        # Center panel - Map editor (main workspace)
        self.map_editor = MapEditor()
        main_splitter.addWidget(self.map_editor)
        
        # Right panel - Agent editor and tools
        right_panel = self._create_right_panel()
        main_splitter.addWidget(right_panel)
        
        # Set initial splitter sizes (25%, 50%, 25%)
        main_splitter.setSizes([300, 600, 300])
    
    def _create_left_panel(self) -> QWidget:
        """
        Create the left panel containing scenario management and properties.
        
        Returns:
            Left panel widget
        """
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        panel.setMinimumWidth(250)
        
        layout = QVBoxLayout(panel)
        
        # Scenario panel
        self.scenario_panel = ScenarioPanel()
        layout.addWidget(self.scenario_panel)
        
        # Properties panel
        self.properties_panel = PropertiesPanel()
        layout.addWidget(self.properties_panel)
        
        return panel
    
    def _create_right_panel(self) -> QWidget:
        """
        Create the right panel containing agent editor and tools.
        
        Returns:
            Right panel widget
        """
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        panel.setMinimumWidth(250)
        
        layout = QVBoxLayout(panel)
        
        # Agent editor
        self.agent_editor = AgentEditor()
        layout.addWidget(self.agent_editor)
        
        return panel
    
    def _setup_menus(self) -> None:
        """Set up the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        # New scenario
        new_action = QAction("&New Scenario", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.setStatusTip("Create a new scenario")
        file_menu.addAction(new_action)
        
        # Open scenario
        open_action = QAction("&Open Scenario", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.setStatusTip("Open an existing scenario")
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # Save scenario
        save_action = QAction("&Save Scenario", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.setStatusTip("Save the current scenario")
        file_menu.addAction(save_action)
        
        # Save as
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.setStatusTip("Save the scenario with a new name")
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        # Export menu
        export_menu = file_menu.addMenu("&Export")
        
        # Gazebo export
        gazebo_action = QAction("Export to &Gazebo", self)
        gazebo_action.setStatusTip("Export scenario to Gazebo format")
        export_menu.addAction(gazebo_action)
        
        # Isaac Sim export
        isaac_action = QAction("Export to &Isaac Sim", self)
        isaac_action.setStatusTip("Export scenario to Isaac Sim format")
        export_menu.addAction(isaac_action)
        
        # Nav2 export
        nav2_action = QAction("Export to &Nav2", self)
        nav2_action.setStatusTip("Export scenario to Nav2 format")
        export_menu.addAction(nav2_action)
        
        file_menu.addSeparator()
        
        # Exit
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.Undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.Redo)
        edit_menu.addAction(redo_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About CrossSim", self)
        about_action.setStatusTip("About CrossSim")
        help_menu.addAction(about_action)
    
    def _setup_toolbars(self) -> None:
        """Set up application toolbars."""
        # Main toolbar will be added here
        pass
    
    def _setup_status_bar(self) -> None:
        """Set up the status bar."""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready", 2000)
    
    def _connect_signals(self) -> None:
        """Connect signals between components."""
        # Connect map editor signals
        # self.map_editor.selection_changed.connect(self.selection_changed)
        
        # Connect scenario panel signals
        # self.scenario_panel.scenario_changed.connect(self.scenario_changed)
        pass
    
    def _center_window(self) -> None:
        """Center the window on the screen."""
        from PyQt5.QtWidgets import QDesktopWidget
        
        screen = QDesktopWidget().screenGeometry()
        window = self.geometry()
        self.move(
            (screen.width() - window.width()) // 2,
            (screen.height() - window.height()) // 2
        )
