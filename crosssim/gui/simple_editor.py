"""
Simple 2D Environment Editor for CrossSim.

This module provides a focused GUI for creating 2D occupancy grid environments
with static obstacles that can be exported to ROS2 Nav2 format.
"""

import sys
import os
from typing import Optional, Tuple, List
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QToolBar,
    QPushButton, QSpinBox, QDoubleSpinBox, QLabel, QDialog,
    QDialogButtonBox, QFormLayout, QFileDialog, QMessageBox,
    QStatusBar, QAction, QMenuBar
)
from PyQt5.QtCore import Qt, QRectF, QPointF, pyqtSignal
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter, QPixmap
import numpy as np
import yaml


class MapSizeDialog(QDialog):
    """Dialog for setting up the initial map size and resolution."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Environment")
        self.setModal(True)
        
        layout = QFormLayout(self)
        
        # Map dimensions in meters
        self.width_spin = QDoubleSpinBox()
        self.width_spin.setRange(1.0, 100.0)
        self.width_spin.setValue(10.0)
        self.width_spin.setSuffix(" m")
        layout.addRow("Width:", self.width_spin)
        
        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(1.0, 100.0)
        self.height_spin.setValue(10.0)
        self.height_spin.setSuffix(" m")
        layout.addRow("Height:", self.height_spin)
        
        # Resolution (meters per pixel)
        self.resolution_spin = QDoubleSpinBox()
        self.resolution_spin.setRange(0.01, 1.0)
        self.resolution_spin.setValue(0.05)
        self.resolution_spin.setDecimals(3)
        self.resolution_spin.setSuffix(" m/px")
        layout.addRow("Resolution:", self.resolution_spin)
        
        # Origin position
        self.origin_x_spin = QDoubleSpinBox()
        self.origin_x_spin.setRange(-50.0, 50.0)
        self.origin_x_spin.setValue(0.0)
        self.origin_x_spin.setSuffix(" m")
        layout.addRow("Origin X:", self.origin_x_spin)
        
        self.origin_y_spin = QDoubleSpinBox()
        self.origin_y_spin.setRange(-50.0, 50.0)
        self.origin_y_spin.setValue(0.0)
        self.origin_y_spin.setSuffix(" m")
        layout.addRow("Origin Y:", self.origin_y_spin)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def get_map_config(self):
        """Get the map configuration from the dialog."""
        return {
            'width_m': self.width_spin.value(),
            'height_m': self.height_spin.value(),
            'resolution': self.resolution_spin.value(),
            'origin_x': self.origin_x_spin.value(),
            'origin_y': self.origin_y_spin.value()
        }


class ObstacleRectItem(QGraphicsRectItem):
    """Custom rectangle item representing a static obstacle."""
    
    def __init__(self, rect, parent=None):
        super().__init__(rect, parent)
        self.setPen(QPen(QColor(200, 50, 50), 2))
        self.setBrush(QBrush(QColor(200, 50, 50, 100)))
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsRectItem.ItemIsMovable, True)


class EnvironmentEditor(QGraphicsView):
    """Interactive 2D environment editor widget."""
    
    obstacle_added = pyqtSignal(QRectF)
    obstacle_removed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        # Map properties
        self.map_width_m = 10.0
        self.map_height_m = 10.0
        self.resolution = 0.05
        self.origin_x = 0.0
        self.origin_y = 0.0
        
        # Drawing state
        self.drawing_mode = False
        self.start_point = None
        self.current_rect = None
        
        # Obstacles list
        self.obstacles = []
        
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        
    def setup_map(self, config):
        """Setup the map with given configuration."""
        self.map_width_m = config['width_m']
        self.map_height_m = config['height_m']
        self.resolution = config['resolution']
        self.origin_x = config['origin_x']
        self.origin_y = config['origin_y']
        
        # Calculate pixel dimensions
        width_px = int(self.map_width_m / self.resolution)
        height_px = int(self.map_height_m / self.resolution)
        
        # Set scene size
        self.scene.setSceneRect(0, 0, width_px, height_px)
        
        # Clear existing items
        self.scene.clear()
        self.obstacles.clear()
        
        # Draw grid
        self._draw_grid()
        
        # Draw boundary
        self._draw_boundary()
        
        # Fit view
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
    
    def _draw_grid(self):
        """Draw grid lines on the scene."""
        grid_spacing_m = 1.0  # 1 meter grid
        grid_spacing_px = grid_spacing_m / self.resolution
        
        pen = QPen(QColor(220, 220, 220), 0.5)
        
        # Vertical lines
        x = 0
        while x <= self.scene.width():
            self.scene.addLine(x, 0, x, self.scene.height(), pen)
            x += grid_spacing_px
        
        # Horizontal lines
        y = 0
        while y <= self.scene.height():
            self.scene.addLine(0, y, self.scene.width(), y, pen)
            y += grid_spacing_px
    
    def _draw_boundary(self):
        """Draw the map boundary."""
        pen = QPen(QColor(100, 100, 100), 3)
        self.scene.addRect(self.scene.sceneRect(), pen)
    
    def set_drawing_mode(self, enabled):
        """Enable or disable drawing mode."""
        self.drawing_mode = enabled
        if enabled:
            self.setDragMode(QGraphicsView.NoDrag)
            self.setCursor(Qt.CrossCursor)
        else:
            self.setDragMode(QGraphicsView.RubberBandDrag)
            self.setCursor(Qt.ArrowCursor)
    
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if self.drawing_mode and event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            self.start_point = scene_pos
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events."""
        if self.drawing_mode and self.start_point:
            scene_pos = self.mapToScene(event.pos())
            
            # Remove previous temporary rectangle
            if self.current_rect:
                self.scene.removeItem(self.current_rect)
            
            # Create new temporary rectangle
            rect = QRectF(self.start_point, scene_pos).normalized()
            self.current_rect = QGraphicsRectItem(rect)
            self.current_rect.setPen(QPen(QColor(200, 50, 50), 2, Qt.DashLine))
            self.current_rect.setBrush(QBrush(QColor(200, 50, 50, 50)))
            self.scene.addItem(self.current_rect)
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        if self.drawing_mode and event.button() == Qt.LeftButton and self.start_point:
            scene_pos = self.mapToScene(event.pos())
            
            # Remove temporary rectangle
            if self.current_rect:
                self.scene.removeItem(self.current_rect)
                self.current_rect = None
            
            # Create final obstacle rectangle
            rect = QRectF(self.start_point, scene_pos).normalized()
            
            # Only create if rectangle has minimum size
            if rect.width() > 5 and rect.height() > 5:
                obstacle = ObstacleRectItem(rect)
                self.scene.addItem(obstacle)
                self.obstacles.append(obstacle)
                self.obstacle_added.emit(rect)
            
            self.start_point = None
        else:
            super().mouseReleaseEvent(event)
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Delete:
            self.delete_selected_obstacles()
        else:
            super().keyPressEvent(event)
    
    def delete_selected_obstacles(self):
        """Delete selected obstacles."""
        selected_items = self.scene.selectedItems()
        for item in selected_items:
            if isinstance(item, ObstacleRectItem):
                self.scene.removeItem(item)
                if item in self.obstacles:
                    self.obstacles.remove(item)
                self.obstacle_removed.emit()
    
    def clear_obstacles(self):
        """Clear all obstacles."""
        for obstacle in self.obstacles[:]:
            self.scene.removeItem(obstacle)
        self.obstacles.clear()
        self.obstacle_removed.emit()
    
    def get_occupancy_grid(self):
        """Generate occupancy grid from obstacles."""
        width_px = int(self.map_width_m / self.resolution)
        height_px = int(self.map_height_m / self.resolution)
        
        # Initialize grid (0 = free, 100 = occupied, -1 = unknown)
        grid = np.zeros((height_px, width_px), dtype=np.int8)
        
        # Fill obstacles
        for obstacle in self.obstacles:
            rect = obstacle.rect()
            
            # Convert to grid coordinates
            x1 = max(0, int(rect.left()))
            y1 = max(0, int(rect.top()))
            x2 = min(width_px, int(rect.right()))
            y2 = min(height_px, int(rect.bottom()))
            
            # Fill rectangle with occupied cells
            grid[y1:y2, x1:x2] = 100
        
        return grid
    
    def pixels_to_meters(self, px_x, px_y):
        """Convert pixel coordinates to meters."""
        m_x = px_x * self.resolution + self.origin_x
        m_y = px_y * self.resolution + self.origin_y
        return m_x, m_y
    
    def meters_to_pixels(self, m_x, m_y):
        """Convert meter coordinates to pixels."""
        px_x = (m_x - self.origin_x) / self.resolution
        px_y = (m_y - self.origin_y) / self.resolution
        return px_x, px_y


class SimpleEnvironmentEditor(QMainWindow):
    """Main application window for the simple environment editor."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CrossSim - Simple Environment Editor")
        self.setGeometry(100, 100, 1000, 700)
        
        # Initialize components
        self.editor = EnvironmentEditor()
        self.map_config = None
        
        self._setup_ui()
        self._setup_menus()
        self._setup_toolbar()
        self._setup_status_bar()
        self._connect_signals()
        
        # Start with new map dialog
        self.new_environment()
    
    def _setup_ui(self):
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.editor)
        
        # Status info
        info_layout = QHBoxLayout()
        self.info_label = QLabel("Ready")
        info_layout.addWidget(self.info_label)
        info_layout.addStretch()
        
        self.obstacle_count_label = QLabel("Obstacles: 0")
        info_layout.addWidget(self.obstacle_count_label)
        
        layout.addLayout(info_layout)
    
    def _setup_menus(self):
        """Setup menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New Environment", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_environment)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("Save as ROS2 Map", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_ros_map)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        clear_action = QAction("Clear All Obstacles", self)
        clear_action.triggered.connect(self.editor.clear_obstacles)
        edit_menu.addAction(clear_action)
        
        delete_action = QAction("Delete Selected", self)
        delete_action.setShortcut("Del")
        delete_action.triggered.connect(self.editor.delete_selected_obstacles)
        edit_menu.addAction(delete_action)
    
    def _setup_toolbar(self):
        """Setup toolbar."""
        toolbar = self.addToolBar("Tools")
        
        # Draw mode toggle
        self.draw_btn = QPushButton("Draw Obstacles")
        self.draw_btn.setCheckable(True)
        self.draw_btn.toggled.connect(self.editor.set_drawing_mode)
        toolbar.addWidget(self.draw_btn)
        
        toolbar.addSeparator()
        
        # Clear button
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.editor.clear_obstacles)
        toolbar.addWidget(clear_btn)
        
        toolbar.addSeparator()
        
        # Save button
        save_btn = QPushButton("Save ROS2 Map")
        save_btn.clicked.connect(self.save_ros_map)
        toolbar.addWidget(save_btn)
    
    def _setup_status_bar(self):
        """Setup status bar."""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready - Create a new environment to start")
    
    def _connect_signals(self):
        """Connect signals."""
        self.editor.obstacle_added.connect(self._update_obstacle_count)
        self.editor.obstacle_removed.connect(self._update_obstacle_count)
    
    def new_environment(self):
        """Create a new environment."""
        dialog = MapSizeDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.map_config = dialog.get_map_config()
            self.editor.setup_map(self.map_config)
            self._update_info()
            self.status_bar.showMessage("New environment created - Use Draw Obstacles to add static obstacles")
    
    def save_ros_map(self):
        """Save the environment as ROS2 Nav2 compatible map files."""
        if not self.map_config:
            QMessageBox.warning(self, "Warning", "No environment to save. Create a new environment first.")
            return
        
        # Get save location
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save ROS2 Map", "my_map.yaml", "YAML files (*.yaml)"
        )
        
        if not file_path:
            return
        
        # Ensure the file has .yaml extension
        if not file_path.endswith('.yaml'):
            file_path += '.yaml'
        
        try:
            # Generate occupancy grid
            occupancy_grid = self.editor.get_occupancy_grid()
            print(f"Generated occupancy grid: {occupancy_grid.shape}")
            print(f"Grid values - Free: {np.sum(occupancy_grid == 0)}, Occupied: {np.sum(occupancy_grid == 100)}")
            
            # Create PGM filename
            pgm_path = file_path.replace('.yaml', '.pgm')
            print(f"Saving files:\n  YAML: {file_path}\n  PGM: {pgm_path}")
            
            # Save PGM file (occupancy grid image)
            self._save_pgm(occupancy_grid, pgm_path)
            
            # Save YAML file (map metadata)
            map_data = {
                'image': os.path.basename(pgm_path),
                'resolution': self.map_config['resolution'],
                'origin': [
                    self.map_config['origin_x'],
                    self.map_config['origin_y'],
                    0.0
                ],
                'negate': 0,
                'occupied_thresh': 0.65,
                'free_thresh': 0.196
            }
            
            with open(file_path, 'w') as f:
                yaml.dump(map_data, f, default_flow_style=False)
            
            print(f"YAML file saved: {file_path}")
            
            QMessageBox.information(
                self, "Success", 
                f"Map saved successfully!\n\nFiles created:\n• {os.path.basename(file_path)}\n• {os.path.basename(pgm_path)}\n\nBoth files are ready for ROS2 Nav2!"
            )
            
            self.status_bar.showMessage(f"Map saved: {os.path.basename(file_path)}")
            
        except Exception as e:
            print(f"Save error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to save map: {str(e)}")
    
    def _save_pgm(self, grid, file_path):
        """Save occupancy grid as PGM file."""
        height, width = grid.shape
        
        # Convert to PGM format (0-255, where 254 is free, 0 is occupied)
        pgm_data = np.zeros_like(grid, dtype=np.uint8)
        pgm_data[grid == 0] = 254      # Free space -> white (254)
        pgm_data[grid == 100] = 0      # Occupied -> black (0)
        pgm_data[grid == -1] = 205     # Unknown -> gray (205)
        
        # Flip vertically to match ROS convention (origin at bottom-left)
        pgm_data = np.flipud(pgm_data)
        
        try:
            with open(file_path, 'wb') as f:
                # PGM header
                header = f"P5\n{width} {height}\n255\n"
                f.write(header.encode('ascii'))
                # Write data row by row
                f.write(pgm_data.tobytes())
            
            print(f"PGM file saved: {file_path} ({width}x{height})")
            
        except Exception as e:
            raise Exception(f"Failed to save PGM file: {str(e)}")
    
    def _update_obstacle_count(self):
        """Update obstacle count display."""
        count = len(self.editor.obstacles)
        self.obstacle_count_label.setText(f"Obstacles: {count}")
    
    def _update_info(self):
        """Update information display."""
        if self.map_config:
            info_text = (f"Size: {self.map_config['width_m']:.1f}x{self.map_config['height_m']:.1f}m | "
                        f"Resolution: {self.map_config['resolution']:.3f}m/px")
            self.info_label.setText(info_text)
    
    def closeEvent(self, event):
        """Handle close event."""
        reply = QMessageBox.question(
            self, "Exit", "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


def main():
    """Main entry point for the simple environment editor."""
    app = QApplication(sys.argv)
    app.setApplicationName("CrossSim Simple Environment Editor")
    
    # Create and show main window
    window = SimpleEnvironmentEditor()
    window.show()
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
