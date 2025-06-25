"""
Agent editor widget for the CrossSim GUI.

This module provides tools for creating, editing, and managing agents and robots
in the simulation scenario.
"""

from typing import Optional, List, Dict, Any
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QGroupBox, QLabel, QSpinBox, QDoubleSpinBox,
    QComboBox, QLineEdit, QTextEdit, QTabWidget, QFormLayout,
    QCheckBox, QSlider, QColorDialog, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor


class AgentEditor(QWidget):
    """
    Agent editor widget for managing robots and dynamic agents.
    
    Provides interface for creating, configuring, and managing agents
    including robots, pedestrians, and other dynamic entities.
    """
    
    # Signals
    agent_added = pyqtSignal(dict)
    agent_removed = pyqtSignal(str)
    agent_modified = pyqtSignal(str, dict)
    selection_changed = pyqtSignal(str)
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the agent editor.
        
        Args:
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        
        self.agents = {}  # Dictionary of agent_id -> agent_data
        self.current_agent_id = None
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self) -> None:
        """Set up the user interface layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Agent list section
        agent_list_group = QGroupBox("Agents & Robots")
        agent_list_layout = QVBoxLayout(agent_list_group)
        
        # Agent list
        self.agent_list = QListWidget()
        self.agent_list.setMaximumHeight(150)
        agent_list_layout.addWidget(self.agent_list)
        
        # Agent list buttons
        list_buttons_layout = QHBoxLayout()
        
        self.add_robot_btn = QPushButton("Add Robot")
        self.add_agent_btn = QPushButton("Add Agent")
        self.remove_btn = QPushButton("Remove")
        self.remove_btn.setEnabled(False)
        
        list_buttons_layout.addWidget(self.add_robot_btn)
        list_buttons_layout.addWidget(self.add_agent_btn)
        list_buttons_layout.addWidget(self.remove_btn)
        
        agent_list_layout.addLayout(list_buttons_layout)
        layout.addWidget(agent_list_group)
        
        # Agent properties section
        self.properties_group = QGroupBox("Properties")
        self.properties_group.setEnabled(False)
        layout.addWidget(self.properties_group)
        
        # Create tabbed interface for agent properties
        self._setup_properties_tabs()
        
        layout.addStretch()
    
    def _setup_properties_tabs(self) -> None:
        """Set up the tabbed interface for agent properties."""
        properties_layout = QVBoxLayout(self.properties_group)
        
        self.properties_tabs = QTabWidget()
        properties_layout.addWidget(self.properties_tabs)
        
        # Basic properties tab
        basic_tab = self._create_basic_properties_tab()
        self.properties_tabs.addTab(basic_tab, "Basic")
        
        # Physical properties tab
        physical_tab = self._create_physical_properties_tab()
        self.properties_tabs.addTab(physical_tab, "Physical")
        
        # Behavior tab
        behavior_tab = self._create_behavior_properties_tab()
        self.properties_tabs.addTab(behavior_tab, "Behavior")
        
        # Goals tab
        goals_tab = self._create_goals_properties_tab()
        self.properties_tabs.addTab(goals_tab, "Goals")
    
    def _create_basic_properties_tab(self) -> QWidget:
        """
        Create the basic properties tab.
        
        Returns:
            Basic properties widget
        """
        tab = QWidget()
        layout = QFormLayout(tab)
        
        # Name
        self.name_edit = QLineEdit()
        layout.addRow("Name:", self.name_edit)
        
        # Type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Robot", "Pedestrian", "Vehicle", "Static Object"])
        layout.addRow("Type:", self.type_combo)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(60)
        layout.addRow("Description:", self.description_edit)
        
        # Color
        color_layout = QHBoxLayout()
        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(30, 30)
        self.color_btn.setStyleSheet("background-color: blue;")
        self.color_btn.clicked.connect(self._choose_color)
        color_layout.addWidget(self.color_btn)
        color_layout.addStretch()
        layout.addRow("Color:", color_layout)
        
        return tab
    
    def _create_physical_properties_tab(self) -> QWidget:
        """
        Create the physical properties tab.
        
        Returns:
            Physical properties widget
        """
        tab = QWidget()
        layout = QFormLayout(tab)
        
        # Position
        position_layout = QHBoxLayout()
        self.pos_x_spin = QDoubleSpinBox()
        self.pos_x_spin.setRange(-100, 100)
        self.pos_x_spin.setSuffix(" m")
        self.pos_y_spin = QDoubleSpinBox()
        self.pos_y_spin.setRange(-100, 100)
        self.pos_y_spin.setSuffix(" m")
        position_layout.addWidget(QLabel("X:"))
        position_layout.addWidget(self.pos_x_spin)
        position_layout.addWidget(QLabel("Y:"))
        position_layout.addWidget(self.pos_y_spin)
        layout.addRow("Position:", position_layout)
        
        # Orientation
        self.orientation_spin = QDoubleSpinBox()
        self.orientation_spin.setRange(-180, 180)
        self.orientation_spin.setSuffix("°")
        layout.addRow("Orientation:", self.orientation_spin)
        
        # Size
        size_layout = QHBoxLayout()
        self.width_spin = QDoubleSpinBox()
        self.width_spin.setRange(0.1, 5.0)
        self.width_spin.setValue(0.5)
        self.width_spin.setSuffix(" m")
        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(0.1, 5.0)
        self.height_spin.setValue(0.5)
        self.height_spin.setSuffix(" m")
        size_layout.addWidget(QLabel("W:"))
        size_layout.addWidget(self.width_spin)
        size_layout.addWidget(QLabel("H:"))
        size_layout.addWidget(self.height_spin)
        layout.addRow("Size:", size_layout)
        
        # Mass (for dynamic objects)
        self.mass_spin = QDoubleSpinBox()
        self.mass_spin.setRange(0.1, 1000.0)
        self.mass_spin.setValue(70.0)
        self.mass_spin.setSuffix(" kg")
        layout.addRow("Mass:", self.mass_spin)
        
        return tab
    
    def _create_behavior_properties_tab(self) -> QWidget:
        """
        Create the behavior properties tab.
        
        Returns:
            Behavior properties widget
        """
        tab = QWidget()
        layout = QFormLayout(tab)
        
        # Behavior type
        self.behavior_combo = QComboBox()
        self.behavior_combo.addItems([
            "Static", "Random Walk", "Waypoint Following", 
            "Social Force", "ORCA", "Custom"
        ])
        layout.addRow("Behavior:", self.behavior_combo)
        
        # Speed
        speed_layout = QHBoxLayout()
        self.min_speed_spin = QDoubleSpinBox()
        self.min_speed_spin.setRange(0.0, 10.0)
        self.min_speed_spin.setValue(0.5)
        self.min_speed_spin.setSuffix(" m/s")
        self.max_speed_spin = QDoubleSpinBox()
        self.max_speed_spin.setRange(0.0, 10.0)
        self.max_speed_spin.setValue(1.5)
        self.max_speed_spin.setSuffix(" m/s")
        speed_layout.addWidget(QLabel("Min:"))
        speed_layout.addWidget(self.min_speed_spin)
        speed_layout.addWidget(QLabel("Max:"))
        speed_layout.addWidget(self.max_speed_spin)
        layout.addRow("Speed:", speed_layout)
        
        # Preferred speed
        self.pref_speed_spin = QDoubleSpinBox()
        self.pref_speed_spin.setRange(0.0, 10.0)
        self.pref_speed_spin.setValue(1.0)
        self.pref_speed_spin.setSuffix(" m/s")
        layout.addRow("Preferred Speed:", self.pref_speed_spin)
        
        # Acceleration
        self.acceleration_spin = QDoubleSpinBox()
        self.acceleration_spin.setRange(0.1, 5.0)
        self.acceleration_spin.setValue(1.0)
        self.acceleration_spin.setSuffix(" m/s²")
        layout.addRow("Max Acceleration:", self.acceleration_spin)
        
        # Social parameters
        layout.addRow(QLabel(""))  # Spacer
        layout.addRow(QLabel("Social Parameters:"))
        
        # Personal space
        self.personal_space_spin = QDoubleSpinBox()
        self.personal_space_spin.setRange(0.1, 2.0)
        self.personal_space_spin.setValue(0.5)
        self.personal_space_spin.setSuffix(" m")
        layout.addRow("Personal Space:", self.personal_space_spin)
        
        return tab
    
    def _create_goals_properties_tab(self) -> QWidget:
        """
        Create the goals properties tab.
        
        Returns:
            Goals properties widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Goal management
        goals_group = QGroupBox("Navigation Goals")
        goals_layout = QVBoxLayout(goals_group)
        
        # Goals list
        self.goals_list = QListWidget()
        self.goals_list.setMaximumHeight(100)
        goals_layout.addWidget(self.goals_list)
        
        # Goal buttons
        goal_buttons_layout = QHBoxLayout()
        self.add_goal_btn = QPushButton("Add Goal")
        self.remove_goal_btn = QPushButton("Remove Goal")
        goal_buttons_layout.addWidget(self.add_goal_btn)
        goal_buttons_layout.addWidget(self.remove_goal_btn)
        goals_layout.addLayout(goal_buttons_layout)
        
        layout.addWidget(goals_group)
        
        # Goal properties
        goal_props_group = QGroupBox("Goal Properties")
        goal_props_layout = QFormLayout(goal_props_group)
        
        # Goal position
        goal_pos_layout = QHBoxLayout()
        self.goal_x_spin = QDoubleSpinBox()
        self.goal_x_spin.setRange(-100, 100)
        self.goal_x_spin.setSuffix(" m")
        self.goal_y_spin = QDoubleSpinBox()
        self.goal_y_spin.setRange(-100, 100)
        self.goal_y_spin.setSuffix(" m")
        goal_pos_layout.addWidget(QLabel("X:"))
        goal_pos_layout.addWidget(self.goal_x_spin)
        goal_pos_layout.addWidget(QLabel("Y:"))
        goal_pos_layout.addWidget(self.goal_y_spin)
        goal_props_layout.addRow("Position:", goal_pos_layout)
        
        # Goal radius
        self.goal_radius_spin = QDoubleSpinBox()
        self.goal_radius_spin.setRange(0.1, 5.0)
        self.goal_radius_spin.setValue(0.5)
        self.goal_radius_spin.setSuffix(" m")
        goal_props_layout.addRow("Radius:", self.goal_radius_spin)
        
        # Goal priority
        self.goal_priority_spin = QSpinBox()
        self.goal_priority_spin.setRange(1, 10)
        self.goal_priority_spin.setValue(1)
        goal_props_layout.addRow("Priority:", self.goal_priority_spin)
        
        layout.addWidget(goal_props_group)
        layout.addStretch()
        
        return tab
    
    def _connect_signals(self) -> None:
        """Connect widget signals."""
        # Agent list selection
        self.agent_list.currentItemChanged.connect(self._on_agent_selected)
        
        # Buttons
        self.add_robot_btn.clicked.connect(lambda: self._add_agent("Robot"))
        self.add_agent_btn.clicked.connect(lambda: self._add_agent("Pedestrian"))
        self.remove_btn.clicked.connect(self._remove_agent)
        
        # Properties change signals
        self.name_edit.textChanged.connect(self._on_property_changed)
        self.type_combo.currentTextChanged.connect(self._on_property_changed)
        # Add more property change connections as needed
    
    def _add_agent(self, agent_type: str) -> None:
        """
        Add a new agent to the list.
        
        Args:
            agent_type: Type of agent to add ("Robot", "Pedestrian", etc.)
        """
        # Generate unique ID
        agent_id = f"{agent_type.lower()}_{len(self.agents) + 1}"
        
        # Create agent data
        agent_data = {
            "id": agent_id,
            "name": f"{agent_type} {len(self.agents) + 1}",
            "type": agent_type,
            "position": {"x": 0.0, "y": 0.0},
            "orientation": 0.0,
            "size": {"width": 0.5, "height": 0.5},
            "mass": 70.0,
            "behavior": "Static",
            "speed": {"min": 0.5, "max": 1.5, "preferred": 1.0},
            "acceleration": 1.0,
            "personal_space": 0.5,
            "color": "blue",
            "goals": []
        }
        
        # Add to agents dictionary
        self.agents[agent_id] = agent_data
        
        # Add to list widget
        item = QListWidgetItem(agent_data["name"])
        item.setData(Qt.UserRole, agent_id)
        self.agent_list.addItem(item)
        
        # Select the new agent
        self.agent_list.setCurrentItem(item)
        
        # Emit signal
        self.agent_added.emit(agent_data)
    
    def _remove_agent(self) -> None:
        """Remove the currently selected agent."""
        current_item = self.agent_list.currentItem()
        if current_item is None:
            return
        
        agent_id = current_item.data(Qt.UserRole)
        
        # Remove from agents dictionary
        if agent_id in self.agents:
            del self.agents[agent_id]
        
        # Remove from list widget
        row = self.agent_list.row(current_item)
        self.agent_list.takeItem(row)
        
        # Update UI state
        self.current_agent_id = None
        self.properties_group.setEnabled(False)
        self.remove_btn.setEnabled(False)
        
        # Emit signal
        self.agent_removed.emit(agent_id)
    
    def _on_agent_selected(self, current: QListWidgetItem, previous: QListWidgetItem) -> None:
        """
        Handle agent selection changes.
        
        Args:
            current: Currently selected item
            previous: Previously selected item
        """
        if current is None:
            self.current_agent_id = None
            self.properties_group.setEnabled(False)
            self.remove_btn.setEnabled(False)
            return
        
        agent_id = current.data(Qt.UserRole)
        self.current_agent_id = agent_id
        
        # Enable properties panel
        self.properties_group.setEnabled(True)
        self.remove_btn.setEnabled(True)
        
        # Load agent properties
        self._load_agent_properties(agent_id)
        
        # Emit selection change signal
        self.selection_changed.emit(agent_id)
    
    def _load_agent_properties(self, agent_id: str) -> None:
        """
        Load agent properties into the UI.
        
        Args:
            agent_id: ID of the agent to load
        """
        if agent_id not in self.agents:
            return
        
        agent_data = self.agents[agent_id]
        
        # Basic properties
        self.name_edit.setText(agent_data["name"])
        self.type_combo.setCurrentText(agent_data["type"])
        # Set color button color
        self.color_btn.setStyleSheet(f"background-color: {agent_data['color']};")
        
        # Physical properties
        self.pos_x_spin.setValue(agent_data["position"]["x"])
        self.pos_y_spin.setValue(agent_data["position"]["y"])
        self.orientation_spin.setValue(agent_data["orientation"])
        self.width_spin.setValue(agent_data["size"]["width"])
        self.height_spin.setValue(agent_data["size"]["height"])
        self.mass_spin.setValue(agent_data["mass"])
        
        # Behavior properties
        self.behavior_combo.setCurrentText(agent_data["behavior"])
        self.min_speed_spin.setValue(agent_data["speed"]["min"])
        self.max_speed_spin.setValue(agent_data["speed"]["max"])
        self.pref_speed_spin.setValue(agent_data["speed"]["preferred"])
        self.acceleration_spin.setValue(agent_data["acceleration"])
        self.personal_space_spin.setValue(agent_data["personal_space"])
    
    def _on_property_changed(self) -> None:
        """Handle property changes."""
        if self.current_agent_id is None:
            return
        
        # Update agent data and emit signal
        # Implementation depends on which property changed
        pass
    
    def _choose_color(self) -> None:
        """Open color dialog for agent color selection."""
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_btn.setStyleSheet(f"background-color: {color.name()};")
            if self.current_agent_id:
                self.agents[self.current_agent_id]["color"] = color.name()
                self.agent_modified.emit(self.current_agent_id, self.agents[self.current_agent_id])
    
    def get_agents(self) -> Dict[str, Any]:
        """
        Get all agents data.
        
        Returns:
            Dictionary of all agents
        """
        return self.agents.copy()
    
    def clear_agents(self) -> None:
        """Clear all agents."""
        self.agents.clear()
        self.agent_list.clear()
        self.current_agent_id = None
        self.properties_group.setEnabled(False)
        self.remove_btn.setEnabled(False)
