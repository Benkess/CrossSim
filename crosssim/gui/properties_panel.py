"""
Properties panel widget for the CrossSim GUI.

This module provides a dynamic properties panel for displaying and editing
properties of selected objects in the scenario.
"""

from typing import Optional, Dict, Any, List
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox,
    QFormLayout, QFrame, QScrollArea, QPushButton, QTextEdit
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class PropertiesPanel(QWidget):
    """
    Dynamic properties panel for selected objects.
    
    Displays and allows editing of properties for the currently selected
    object in the scenario (map elements, agents, etc.).
    """
    
    # Signals
    property_changed = pyqtSignal(str, str, object)  # object_id, property_name, value
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the properties panel.
        
        Args:
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        
        self.current_object = None
        self.current_object_id = None
        self.property_widgets = {}
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the user interface layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Title
        title_layout = QHBoxLayout()
        title_label = QLabel("Properties")
        title_font = QFont()
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Scroll area for properties
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Properties widget (content of scroll area)
        self.properties_widget = QWidget()
        self.properties_layout = QVBoxLayout(self.properties_widget)
        self.properties_layout.setContentsMargins(0, 0, 0, 0)
        
        self.scroll_area.setWidget(self.properties_widget)
        layout.addWidget(self.scroll_area)
        
        # Initially show "No selection" message
        self._show_no_selection()
    
    def _show_no_selection(self) -> None:
        """Show message when no object is selected."""
        self._clear_properties()
        
        no_selection_label = QLabel("No object selected")
        no_selection_label.setAlignment(Qt.AlignCenter)
        no_selection_label.setStyleSheet("color: gray; font-style: italic;")
        self.properties_layout.addWidget(no_selection_label)
        self.properties_layout.addStretch()
    
    def _clear_properties(self) -> None:
        """Clear all property widgets."""
        # Remove all widgets from layout
        while self.properties_layout.count():
            child = self.properties_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        self.property_widgets = {}
    
    def set_object_properties(self, object_id: str, object_data: Dict[str, Any]) -> None:
        """
        Set the properties for the selected object.
        
        Args:
            object_id: Unique identifier for the object
            object_data: Dictionary containing object properties
        """
        self.current_object_id = object_id
        self.current_object = object_data
        
        self._clear_properties()
        self._create_property_widgets(object_data)
    
    def _create_property_widgets(self, object_data: Dict[str, Any]) -> None:
        """
        Create widgets for object properties.
        
        Args:
            object_data: Dictionary containing object properties
        """
        # Object type and ID
        info_group = QGroupBox("Object Information")
        info_layout = QFormLayout(info_group)
        
        # Object type
        type_label = QLabel(object_data.get("type", "Unknown"))
        type_label.setStyleSheet("font-weight: bold;")
        info_layout.addRow("Type:", type_label)
        
        # Object ID
        id_label = QLabel(self.current_object_id)
        id_label.setStyleSheet("font-family: monospace;")
        info_layout.addRow("ID:", id_label)
        
        self.properties_layout.addWidget(info_group)
        
        # Create property groups based on object type
        if object_data.get("type") == "Agent" or object_data.get("type") == "Robot":
            self._create_agent_properties(object_data)
        elif object_data.get("type") == "Wall":
            self._create_wall_properties(object_data)
        elif object_data.get("type") == "Obstacle":
            self._create_obstacle_properties(object_data)
        else:
            self._create_generic_properties(object_data)
        
        self.properties_layout.addStretch()
    
    def _create_agent_properties(self, object_data: Dict[str, Any]) -> None:
        """
        Create property widgets for agents/robots.
        
        Args:
            object_data: Agent/robot data
        """
        # Basic properties
        basic_group = QGroupBox("Basic Properties")
        basic_layout = QFormLayout(basic_group)
        
        # Name
        name_edit = QLineEdit(object_data.get("name", ""))
        name_edit.textChanged.connect(lambda text: self._on_property_changed("name", text))
        basic_layout.addRow("Name:", name_edit)
        self.property_widgets["name"] = name_edit
        
        # Description
        desc_edit = QTextEdit(object_data.get("description", ""))
        desc_edit.setMaximumHeight(60)
        desc_edit.textChanged.connect(lambda: self._on_property_changed("description", desc_edit.toPlainText()))
        basic_layout.addRow("Description:", desc_edit)
        self.property_widgets["description"] = desc_edit
        
        self.properties_layout.addWidget(basic_group)
        
        # Position properties
        pos_group = QGroupBox("Position & Orientation")
        pos_layout = QFormLayout(pos_group)
        
        # Position X
        pos_x_spin = QDoubleSpinBox()
        pos_x_spin.setRange(-100.0, 100.0)
        pos_x_spin.setValue(object_data.get("position", {}).get("x", 0.0))
        pos_x_spin.setSuffix(" m")
        pos_x_spin.valueChanged.connect(lambda val: self._on_position_changed("x", val))
        pos_layout.addRow("X Position:", pos_x_spin)
        self.property_widgets["pos_x"] = pos_x_spin
        
        # Position Y
        pos_y_spin = QDoubleSpinBox()
        pos_y_spin.setRange(-100.0, 100.0)
        pos_y_spin.setValue(object_data.get("position", {}).get("y", 0.0))
        pos_y_spin.setSuffix(" m")
        pos_y_spin.valueChanged.connect(lambda val: self._on_position_changed("y", val))
        pos_layout.addRow("Y Position:", pos_y_spin)
        self.property_widgets["pos_y"] = pos_y_spin
        
        # Orientation
        orient_spin = QDoubleSpinBox()
        orient_spin.setRange(-180.0, 180.0)
        orient_spin.setValue(object_data.get("orientation", 0.0))
        orient_spin.setSuffix("°")
        orient_spin.valueChanged.connect(lambda val: self._on_property_changed("orientation", val))
        pos_layout.addRow("Orientation:", orient_spin)
        self.property_widgets["orientation"] = orient_spin
        
        self.properties_layout.addWidget(pos_group)
        
        # Physical properties
        phys_group = QGroupBox("Physical Properties")
        phys_layout = QFormLayout(phys_group)
        
        # Width
        width_spin = QDoubleSpinBox()
        width_spin.setRange(0.1, 5.0)
        width_spin.setValue(object_data.get("size", {}).get("width", 0.5))
        width_spin.setSuffix(" m")
        width_spin.valueChanged.connect(lambda val: self._on_size_changed("width", val))
        phys_layout.addRow("Width:", width_spin)
        self.property_widgets["width"] = width_spin
        
        # Height
        height_spin = QDoubleSpinBox()
        height_spin.setRange(0.1, 5.0)
        height_spin.setValue(object_data.get("size", {}).get("height", 0.5))
        height_spin.setSuffix(" m")
        height_spin.valueChanged.connect(lambda val: self._on_size_changed("height", val))
        phys_layout.addRow("Height:", height_spin)
        self.property_widgets["height"] = height_spin
        
        # Mass
        mass_spin = QDoubleSpinBox()
        mass_spin.setRange(0.1, 1000.0)
        mass_spin.setValue(object_data.get("mass", 70.0))
        mass_spin.setSuffix(" kg")
        mass_spin.valueChanged.connect(lambda val: self._on_property_changed("mass", val))
        phys_layout.addRow("Mass:", mass_spin)
        self.property_widgets["mass"] = mass_spin
        
        self.properties_layout.addWidget(phys_group)
        
        # Behavior properties
        behavior_group = QGroupBox("Behavior Properties")
        behavior_layout = QFormLayout(behavior_group)
        
        # Behavior type
        behavior_combo = QComboBox()
        behavior_combo.addItems(["Static", "Random Walk", "Waypoint Following", "Social Force", "ORCA"])
        behavior_combo.setCurrentText(object_data.get("behavior", "Static"))
        behavior_combo.currentTextChanged.connect(lambda text: self._on_property_changed("behavior", text))
        behavior_layout.addRow("Behavior:", behavior_combo)
        self.property_widgets["behavior"] = behavior_combo
        
        # Speed
        speed_spin = QDoubleSpinBox()
        speed_spin.setRange(0.0, 10.0)
        speed_spin.setValue(object_data.get("speed", {}).get("preferred", 1.0))
        speed_spin.setSuffix(" m/s")
        speed_spin.valueChanged.connect(lambda val: self._on_speed_changed("preferred", val))
        behavior_layout.addRow("Preferred Speed:", speed_spin)
        self.property_widgets["speed"] = speed_spin
        
        self.properties_layout.addWidget(behavior_group)
    
    def _create_wall_properties(self, object_data: Dict[str, Any]) -> None:
        """
        Create property widgets for walls.
        
        Args:
            object_data: Wall data
        """
        # Wall properties
        wall_group = QGroupBox("Wall Properties")
        wall_layout = QFormLayout(wall_group)
        
        # Start point
        start_x_spin = QDoubleSpinBox()
        start_x_spin.setRange(-100.0, 100.0)
        start_x_spin.setValue(object_data.get("start", {}).get("x", 0.0))
        start_x_spin.setSuffix(" m")
        wall_layout.addRow("Start X:", start_x_spin)
        
        start_y_spin = QDoubleSpinBox()
        start_y_spin.setRange(-100.0, 100.0)
        start_y_spin.setValue(object_data.get("start", {}).get("y", 0.0))
        start_y_spin.setSuffix(" m")
        wall_layout.addRow("Start Y:", start_y_spin)
        
        # End point
        end_x_spin = QDoubleSpinBox()
        end_x_spin.setRange(-100.0, 100.0)
        end_x_spin.setValue(object_data.get("end", {}).get("x", 1.0))
        end_x_spin.setSuffix(" m")
        wall_layout.addRow("End X:", end_x_spin)
        
        end_y_spin = QDoubleSpinBox()
        end_y_spin.setRange(-100.0, 100.0)
        end_y_spin.setValue(object_data.get("end", {}).get("y", 0.0))
        end_y_spin.setSuffix(" m")
        wall_layout.addRow("End Y:", end_y_spin)
        
        # Thickness
        thickness_spin = QDoubleSpinBox()
        thickness_spin.setRange(0.01, 1.0)
        thickness_spin.setValue(object_data.get("thickness", 0.1))
        thickness_spin.setSuffix(" m")
        wall_layout.addRow("Thickness:", thickness_spin)
        
        self.properties_layout.addWidget(wall_group)
    
    def _create_obstacle_properties(self, object_data: Dict[str, Any]) -> None:
        """
        Create property widgets for obstacles.
        
        Args:
            object_data: Obstacle data
        """
        # Obstacle properties
        obstacle_group = QGroupBox("Obstacle Properties")
        obstacle_layout = QFormLayout(obstacle_group)
        
        # Shape
        shape_combo = QComboBox()
        shape_combo.addItems(["Rectangle", "Circle", "Polygon"])
        shape_combo.setCurrentText(object_data.get("shape", "Rectangle"))
        obstacle_layout.addRow("Shape:", shape_combo)
        
        # Size (for rectangle/circle)
        size_spin = QDoubleSpinBox()
        size_spin.setRange(0.1, 10.0)
        size_spin.setValue(object_data.get("size", 1.0))
        size_spin.setSuffix(" m")
        obstacle_layout.addRow("Size:", size_spin)
        
        # Static/Dynamic
        is_static_check = QCheckBox()
        is_static_check.setChecked(object_data.get("is_static", True))
        obstacle_layout.addRow("Static:", is_static_check)
        
        self.properties_layout.addWidget(obstacle_group)
    
    def _create_generic_properties(self, object_data: Dict[str, Any]) -> None:
        """
        Create generic property widgets for unknown object types.
        
        Args:
            object_data: Generic object data
        """
        # Generic properties
        props_group = QGroupBox("Properties")
        props_layout = QFormLayout(props_group)
        
        # Show all properties as text fields
        for key, value in object_data.items():
            if key not in ["type", "id"]:
                if isinstance(value, (int, float)):
                    spin = QDoubleSpinBox()
                    spin.setRange(-1000.0, 1000.0)
                    spin.setValue(float(value))
                    spin.valueChanged.connect(lambda val, k=key: self._on_property_changed(k, val))
                    props_layout.addRow(f"{key}:", spin)
                    self.property_widgets[key] = spin
                elif isinstance(value, str):
                    edit = QLineEdit(value)
                    edit.textChanged.connect(lambda text, k=key: self._on_property_changed(k, text))
                    props_layout.addRow(f"{key}:", edit)
                    self.property_widgets[key] = edit
                elif isinstance(value, bool):
                    check = QCheckBox()
                    check.setChecked(value)
                    check.toggled.connect(lambda checked, k=key: self._on_property_changed(k, checked))
                    props_layout.addRow(f"{key}:", check)
                    self.property_widgets[key] = check
        
        self.properties_layout.addWidget(props_group)
    
    def _on_property_changed(self, property_name: str, value: Any) -> None:
        """
        Handle property value changes.
        
        Args:
            property_name: Name of the property that changed
            value: New value
        """
        if self.current_object_id:
            self.property_changed.emit(self.current_object_id, property_name, value)
    
    def _on_position_changed(self, axis: str, value: float) -> None:
        """
        Handle position changes.
        
        Args:
            axis: Position axis ("x" or "y")
            value: New position value
        """
        if self.current_object_id:
            self.property_changed.emit(self.current_object_id, f"position_{axis}", value)
    
    def _on_size_changed(self, dimension: str, value: float) -> None:
        """
        Handle size changes.
        
        Args:
            dimension: Size dimension ("width" or "height")
            value: New size value
        """
        if self.current_object_id:
            self.property_changed.emit(self.current_object_id, f"size_{dimension}", value)
    
    def _on_speed_changed(self, speed_type: str, value: float) -> None:
        """
        Handle speed changes.
        
        Args:
            speed_type: Type of speed ("preferred", "min", "max")
            value: New speed value
        """
        if self.current_object_id:
            self.property_changed.emit(self.current_object_id, f"speed_{speed_type}", value)
    
    def clear_selection(self) -> None:
        """Clear the current selection and show no selection message."""
        self.current_object = None
        self.current_object_id = None
        self._show_no_selection()
    
    def get_current_properties(self) -> Optional[Dict[str, Any]]:
        """
        Get the current object properties.
        
        Returns:
            Current object properties or None if no selection
        """
        return self.current_object.copy() if self.current_object else None
