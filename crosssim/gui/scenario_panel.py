"""
Scenario panel widget for the CrossSim GUI.

This module provides the interface for managing scenarios, including creating,
loading, saving, and configuring scenario metadata.
"""

from typing import Optional, Dict, Any
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QPushButton,
    QFormLayout, QComboBox, QListWidget, QListWidgetItem,
    QFrame, QSplitter
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class ScenarioPanel(QWidget):
    """
    Scenario management panel.
    
    Provides interface for managing scenario metadata, settings, and
    overall scenario configuration.
    """
    
    # Signals
    scenario_created = pyqtSignal(dict)
    scenario_loaded = pyqtSignal(dict)
    scenario_saved = pyqtSignal(dict)
    scenario_modified = pyqtSignal(dict)
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the scenario panel.
        
        Args:
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        
        self.current_scenario = {
            "name": "New Scenario",
            "description": "",
            "author": "",
            "version": "1.0",
            "tags": [],
            "environment": {
                "size": {"width": 10.0, "height": 10.0},
                "resolution": 0.05,
                "origin": {"x": 0.0, "y": 0.0}
            },
            "simulation": {
                "time_step": 0.1,
                "duration": 60.0,
                "real_time_factor": 1.0
            }
        }
        
        self._setup_ui()
        self._connect_signals()
        self._load_scenario_data()
    
    def _setup_ui(self) -> None:
        """Set up the user interface layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Scenario info section
        info_group = QGroupBox("Scenario Information")
        info_layout = QFormLayout(info_group)
        
        # Scenario name
        self.name_edit = QLineEdit()
        info_layout.addRow("Name:", self.name_edit)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(60)
        info_layout.addRow("Description:", self.description_edit)
        
        # Author
        self.author_edit = QLineEdit()
        info_layout.addRow("Author:", self.author_edit)
        
        # Version
        self.version_edit = QLineEdit()
        info_layout.addRow("Version:", self.version_edit)
        
        layout.addWidget(info_group)
        
        # Environment settings section
        env_group = QGroupBox("Environment Settings")
        env_layout = QFormLayout(env_group)
        
        # Environment size
        size_layout = QHBoxLayout()
        self.width_spin = QDoubleSpinBox()
        self.width_spin.setRange(1.0, 100.0)
        self.width_spin.setSuffix(" m")
        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(1.0, 100.0)
        self.height_spin.setSuffix(" m")
        size_layout.addWidget(QLabel("W:"))
        size_layout.addWidget(self.width_spin)
        size_layout.addWidget(QLabel("H:"))
        size_layout.addWidget(self.height_spin)
        env_layout.addRow("Size:", size_layout)
        
        # Resolution
        self.resolution_spin = QDoubleSpinBox()
        self.resolution_spin.setRange(0.01, 1.0)
        self.resolution_spin.setDecimals(3)
        self.resolution_spin.setSuffix(" m/px")
        env_layout.addRow("Resolution:", self.resolution_spin)
        
        # Origin
        origin_layout = QHBoxLayout()
        self.origin_x_spin = QDoubleSpinBox()
        self.origin_x_spin.setRange(-50.0, 50.0)
        self.origin_x_spin.setSuffix(" m")
        self.origin_y_spin = QDoubleSpinBox()
        self.origin_y_spin.setRange(-50.0, 50.0)
        self.origin_y_spin.setSuffix(" m")
        origin_layout.addWidget(QLabel("X:"))
        origin_layout.addWidget(self.origin_x_spin)
        origin_layout.addWidget(QLabel("Y:"))
        origin_layout.addWidget(self.origin_y_spin)
        env_layout.addRow("Origin:", origin_layout)
        
        layout.addWidget(env_group)
        
        # Simulation settings section
        sim_group = QGroupBox("Simulation Settings")
        sim_layout = QFormLayout(sim_group)
        
        # Time step
        self.time_step_spin = QDoubleSpinBox()
        self.time_step_spin.setRange(0.01, 1.0)
        self.time_step_spin.setDecimals(3)
        self.time_step_spin.setSuffix(" s")
        sim_layout.addRow("Time Step:", self.time_step_spin)
        
        # Duration
        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(1.0, 3600.0)
        self.duration_spin.setSuffix(" s")
        sim_layout.addRow("Duration:", self.duration_spin)
        
        # Real-time factor
        self.rtf_spin = QDoubleSpinBox()
        self.rtf_spin.setRange(0.1, 10.0)
        self.rtf_spin.setDecimals(1)
        sim_layout.addRow("Real-time Factor:", self.rtf_spin)
        
        layout.addWidget(sim_group)
        
        # Tags section
        tags_group = QGroupBox("Tags")
        tags_layout = QVBoxLayout(tags_group)
        
        # Tags input
        tags_input_layout = QHBoxLayout()
        self.tag_edit = QLineEdit()
        self.tag_edit.setPlaceholderText("Enter tag and press Add")
        self.add_tag_btn = QPushButton("Add")
        tags_input_layout.addWidget(self.tag_edit)
        tags_input_layout.addWidget(self.add_tag_btn)
        tags_layout.addLayout(tags_input_layout)
        
        # Tags list
        self.tags_list = QListWidget()
        self.tags_list.setMaximumHeight(80)
        tags_layout.addWidget(self.tags_list)
        
        # Tag management buttons
        tag_buttons_layout = QHBoxLayout()
        self.remove_tag_btn = QPushButton("Remove")
        self.clear_tags_btn = QPushButton("Clear All")
        tag_buttons_layout.addWidget(self.remove_tag_btn)
        tag_buttons_layout.addWidget(self.clear_tags_btn)
        tags_layout.addLayout(tag_buttons_layout)
        
        layout.addWidget(tags_group)
        
        # Action buttons
        action_layout = QHBoxLayout()
        self.new_btn = QPushButton("New")
        self.load_btn = QPushButton("Load")
        self.save_btn = QPushButton("Save")
        self.save_as_btn = QPushButton("Save As...")
        
        action_layout.addWidget(self.new_btn)
        action_layout.addWidget(self.load_btn)
        action_layout.addWidget(self.save_btn)
        action_layout.addWidget(self.save_as_btn)
        
        layout.addLayout(action_layout)
        layout.addStretch()
    
    def _connect_signals(self) -> None:
        """Connect widget signals."""
        # Scenario info changes
        self.name_edit.textChanged.connect(self._on_name_changed)
        self.description_edit.textChanged.connect(self._on_description_changed)
        self.author_edit.textChanged.connect(self._on_author_changed)
        self.version_edit.textChanged.connect(self._on_version_changed)
        
        # Environment settings changes
        self.width_spin.valueChanged.connect(self._on_environment_changed)
        self.height_spin.valueChanged.connect(self._on_environment_changed)
        self.resolution_spin.valueChanged.connect(self._on_environment_changed)
        self.origin_x_spin.valueChanged.connect(self._on_environment_changed)
        self.origin_y_spin.valueChanged.connect(self._on_environment_changed)
        
        # Simulation settings changes
        self.time_step_spin.valueChanged.connect(self._on_simulation_changed)
        self.duration_spin.valueChanged.connect(self._on_simulation_changed)
        self.rtf_spin.valueChanged.connect(self._on_simulation_changed)
        
        # Tag management
        self.add_tag_btn.clicked.connect(self._add_tag)
        self.remove_tag_btn.clicked.connect(self._remove_tag)
        self.clear_tags_btn.clicked.connect(self._clear_tags)
        self.tag_edit.returnPressed.connect(self._add_tag)
        
        # Action buttons
        self.new_btn.clicked.connect(self._new_scenario)
        self.load_btn.clicked.connect(self._load_scenario)
        self.save_btn.clicked.connect(self._save_scenario)
        self.save_as_btn.clicked.connect(self._save_as_scenario)
    
    def _load_scenario_data(self) -> None:
        """Load current scenario data into the UI."""
        # Scenario info
        self.name_edit.setText(self.current_scenario["name"])
        self.description_edit.setPlainText(self.current_scenario["description"])
        self.author_edit.setText(self.current_scenario["author"])
        self.version_edit.setText(self.current_scenario["version"])
        
        # Environment settings
        env = self.current_scenario["environment"]
        self.width_spin.setValue(env["size"]["width"])
        self.height_spin.setValue(env["size"]["height"])
        self.resolution_spin.setValue(env["resolution"])
        self.origin_x_spin.setValue(env["origin"]["x"])
        self.origin_y_spin.setValue(env["origin"]["y"])
        
        # Simulation settings
        sim = self.current_scenario["simulation"]
        self.time_step_spin.setValue(sim["time_step"])
        self.duration_spin.setValue(sim["duration"])
        self.rtf_spin.setValue(sim["real_time_factor"])
        
        # Tags
        self.tags_list.clear()
        for tag in self.current_scenario["tags"]:
            self.tags_list.addItem(tag)
    
    def _on_name_changed(self, text: str) -> None:
        """Handle scenario name changes."""
        self.current_scenario["name"] = text
        self.scenario_modified.emit(self.current_scenario)
    
    def _on_description_changed(self) -> None:
        """Handle scenario description changes."""
        self.current_scenario["description"] = self.description_edit.toPlainText()
        self.scenario_modified.emit(self.current_scenario)
    
    def _on_author_changed(self, text: str) -> None:
        """Handle author changes."""
        self.current_scenario["author"] = text
        self.scenario_modified.emit(self.current_scenario)
    
    def _on_version_changed(self, text: str) -> None:
        """Handle version changes."""
        self.current_scenario["version"] = text
        self.scenario_modified.emit(self.current_scenario)
    
    def _on_environment_changed(self) -> None:
        """Handle environment settings changes."""
        env = self.current_scenario["environment"]
        env["size"]["width"] = self.width_spin.value()
        env["size"]["height"] = self.height_spin.value()
        env["resolution"] = self.resolution_spin.value()
        env["origin"]["x"] = self.origin_x_spin.value()
        env["origin"]["y"] = self.origin_y_spin.value()
        self.scenario_modified.emit(self.current_scenario)
    
    def _on_simulation_changed(self) -> None:
        """Handle simulation settings changes."""
        sim = self.current_scenario["simulation"]
        sim["time_step"] = self.time_step_spin.value()
        sim["duration"] = self.duration_spin.value()
        sim["real_time_factor"] = self.rtf_spin.value()
        self.scenario_modified.emit(self.current_scenario)
    
    def _add_tag(self) -> None:
        """Add a new tag."""
        tag_text = self.tag_edit.text().strip()
        if tag_text and tag_text not in self.current_scenario["tags"]:
            self.current_scenario["tags"].append(tag_text)
            self.tags_list.addItem(tag_text)
            self.tag_edit.clear()
            self.scenario_modified.emit(self.current_scenario)
    
    def _remove_tag(self) -> None:
        """Remove the selected tag."""
        current_item = self.tags_list.currentItem()
        if current_item:
            tag_text = current_item.text()
            if tag_text in self.current_scenario["tags"]:
                self.current_scenario["tags"].remove(tag_text)
            row = self.tags_list.row(current_item)
            self.tags_list.takeItem(row)
            self.scenario_modified.emit(self.current_scenario)
    
    def _clear_tags(self) -> None:
        """Clear all tags."""
        self.current_scenario["tags"].clear()
        self.tags_list.clear()
        self.scenario_modified.emit(self.current_scenario)
    
    def _new_scenario(self) -> None:
        """Create a new scenario."""
        # Reset to default scenario
        self.current_scenario = {
            "name": "New Scenario",
            "description": "",
            "author": "",
            "version": "1.0",
            "tags": [],
            "environment": {
                "size": {"width": 10.0, "height": 10.0},
                "resolution": 0.05,
                "origin": {"x": 0.0, "y": 0.0}
            },
            "simulation": {
                "time_step": 0.1,
                "duration": 60.0,
                "real_time_factor": 1.0
            }
        }
        self._load_scenario_data()
        self.scenario_created.emit(self.current_scenario)
    
    def _load_scenario(self) -> None:
        """Load a scenario from file."""
        # This will be implemented with file dialog
        # For now, just emit the signal
        self.scenario_loaded.emit(self.current_scenario)
    
    def _save_scenario(self) -> None:
        """Save the current scenario."""
        # This will be implemented with file operations
        # For now, just emit the signal
        self.scenario_saved.emit(self.current_scenario)
    
    def _save_as_scenario(self) -> None:
        """Save the scenario with a new name."""
        # This will be implemented with file dialog
        # For now, just emit the signal
        self.scenario_saved.emit(self.current_scenario)
    
    def get_scenario_data(self) -> Dict[str, Any]:
        """
        Get the current scenario data.
        
        Returns:
            Current scenario dictionary
        """
        return self.current_scenario.copy()
    
    def set_scenario_data(self, scenario_data: Dict[str, Any]) -> None:
        """
        Set the scenario data.
        
        Args:
            scenario_data: Scenario data dictionary
        """
        self.current_scenario = scenario_data.copy()
        self._load_scenario_data()
        self.scenario_loaded.emit(self.current_scenario)
