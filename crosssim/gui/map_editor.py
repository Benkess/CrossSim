"""
Map editor widget for the CrossSim GUI.

This module provides the interactive map editing interface where users can
draw maps, place obstacles, and define the environment layout.
"""

from typing import Optional, List, Tuple
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGraphicsView, QGraphicsScene,
    QGraphicsItem, QToolBar, QAction, QButtonGroup, QPushButton,
    QLabel, QSlider, QSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QRectF, QPointF
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter


class MapEditor(QWidget):
    """
    Interactive map editor widget.
    
    Provides tools for drawing and editing 2D maps, including walls, obstacles,
    free space, and other environmental features.
    """
    
    # Signals
    map_changed = pyqtSignal()
    selection_changed = pyqtSignal(object)
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the map editor.
        
        Args:
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        
        self.current_tool = "select"
        self.grid_size = 0.1  # meters
        self.map_resolution = 0.05  # meters per pixel
        
        self._setup_ui()
        self._setup_toolbar()
        self._setup_graphics_view()
    
    def _setup_ui(self) -> None:
        """Set up the user interface layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Toolbar
        self.toolbar = QToolBar("Map Tools")
        layout.addWidget(self.toolbar)
        
        # Graphics view
        self.graphics_view = QGraphicsView()
        self.graphics_scene = QGraphicsScene()
        self.graphics_view.setScene(self.graphics_scene)
        layout.addWidget(self.graphics_view)
        
        # Bottom controls
        controls_layout = QHBoxLayout()
        
        # Grid controls
        controls_layout.addWidget(QLabel("Grid:"))
        self.grid_size_spin = QSpinBox()
        self.grid_size_spin.setRange(1, 100)
        self.grid_size_spin.setValue(int(self.grid_size * 100))
        self.grid_size_spin.setSuffix(" cm")
        controls_layout.addWidget(self.grid_size_spin)
        
        controls_layout.addStretch()
        
        # Zoom controls
        controls_layout.addWidget(QLabel("Zoom:"))
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(10, 500)
        self.zoom_slider.setValue(100)
        controls_layout.addWidget(self.zoom_slider)
        
        layout.addLayout(controls_layout)
    
    def _setup_toolbar(self) -> None:
        """Set up the map editing toolbar."""
        # Tool selection buttons
        self.tool_group = QButtonGroup()
        
        # Select tool
        select_btn = QPushButton("Select")
        select_btn.setCheckable(True)
        select_btn.setChecked(True)
        select_btn.clicked.connect(lambda: self._set_tool("select"))
        self.toolbar.addWidget(select_btn)
        self.tool_group.addButton(select_btn)
        
        # Wall/obstacle drawing tool
        wall_btn = QPushButton("Wall")
        wall_btn.setCheckable(True)
        wall_btn.clicked.connect(lambda: self._set_tool("wall"))
        self.toolbar.addWidget(wall_btn)
        self.tool_group.addButton(wall_btn)
        
        # Free space tool
        free_btn = QPushButton("Free Space")
        free_btn.setCheckable(True)
        free_btn.clicked.connect(lambda: self._set_tool("free"))
        self.toolbar.addWidget(free_btn)
        self.tool_group.addButton(free_btn)
        
        # Robot placement tool
        robot_btn = QPushButton("Robot")
        robot_btn.setCheckable(True)
        robot_btn.clicked.connect(lambda: self._set_tool("robot"))
        self.toolbar.addWidget(robot_btn)
        self.tool_group.addButton(robot_btn)
        
        # Agent placement tool
        agent_btn = QPushButton("Agent")
        agent_btn.setCheckable(True)
        agent_btn.clicked.connect(lambda: self._set_tool("agent"))
        self.toolbar.addWidget(agent_btn)
        self.tool_group.addButton(agent_btn)
        
        self.toolbar.addSeparator()
        
        # Clear action
        clear_action = QAction("Clear", self)
        clear_action.triggered.connect(self._clear_map)
        self.toolbar.addAction(clear_action)
    
    def _setup_graphics_view(self) -> None:
        """Set up the graphics view for map editing."""
        # Configure graphics view
        self.graphics_view.setDragMode(QGraphicsView.RubberBandDrag)
        self.graphics_view.setRenderHint(QPainter.Antialiasing)
        
        # Set initial scene size (10m x 10m default)
        scene_size = 10.0 / self.map_resolution  # Convert to pixels
        self.graphics_scene.setSceneRect(-scene_size/2, -scene_size/2, 
                                       scene_size, scene_size)
        
        # Draw grid
        self._draw_grid()
        
        # Connect zoom slider
        self.zoom_slider.valueChanged.connect(self._on_zoom_changed)
    
    def _draw_grid(self) -> None:
        """Draw the grid lines on the scene."""
        scene_rect = self.graphics_scene.sceneRect()
        grid_spacing = self.grid_size / self.map_resolution
        
        pen = QPen(QColor(200, 200, 200), 0.5)
        
        # Vertical lines
        x = scene_rect.left()
        while x <= scene_rect.right():
            self.graphics_scene.addLine(x, scene_rect.top(), 
                                      x, scene_rect.bottom(), pen)
            x += grid_spacing
        
        # Horizontal lines
        y = scene_rect.top()
        while y <= scene_rect.bottom():
            self.graphics_scene.addLine(scene_rect.left(), y,
                                      scene_rect.right(), y, pen)
            y += grid_spacing
    
    def _set_tool(self, tool: str) -> None:
        """
        Set the current editing tool.
        
        Args:
            tool: Tool name ("select", "wall", "free", "robot", "agent")
        """
        self.current_tool = tool
        
        # Update cursor based on tool
        if tool == "select":
            self.graphics_view.setCursor(Qt.ArrowCursor)
        else:
            self.graphics_view.setCursor(Qt.CrossCursor)
    
    def _clear_map(self) -> None:
        """Clear all items from the map."""
        # Keep grid lines, remove other items
        items_to_remove = []
        for item in self.graphics_scene.items():
            if hasattr(item, 'item_type') and item.item_type != 'grid':
                items_to_remove.append(item)
        
        for item in items_to_remove:
            self.graphics_scene.removeItem(item)
        
        self.map_changed.emit()
    
    def _on_zoom_changed(self, value: int) -> None:
        """
        Handle zoom slider changes.
        
        Args:
            value: Zoom percentage (10-500)
        """
        scale_factor = value / 100.0
        transform = self.graphics_view.transform()
        transform.reset()
        transform.scale(scale_factor, scale_factor)
        self.graphics_view.setTransform(transform)
    
    def mousePressEvent(self, event) -> None:
        """Handle mouse press events for drawing."""
        # Map editor specific mouse handling will be implemented here
        super().mousePressEvent(event)
    
    def get_map_data(self) -> dict:
        """
        Get the current map data.
        
        Returns:
            Dictionary containing map information
        """
        return {
            "resolution": self.map_resolution,
            "grid_size": self.grid_size,
            "items": []  # Will be populated with actual map items
        }
    
    def load_map_data(self, data: dict) -> None:
        """
        Load map data into the editor.
        
        Args:
            data: Map data dictionary
        """
        # Implementation for loading map data
        pass
