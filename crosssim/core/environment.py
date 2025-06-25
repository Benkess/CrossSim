"""
Environment data structure for CrossSim.

This module provides classes for representing simulation environments,
including maps, obstacles, and spatial layouts.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from enum import Enum


class CellType(Enum):
    """Types of cells in an occupancy grid."""
    FREE = 0
    OCCUPIED = 1
    UNKNOWN = 2


@dataclass
class MapInfo:
    """Information about a map."""
    resolution: float  # meters per pixel
    width: int  # pixels
    height: int  # pixels
    origin_x: float  # meters
    origin_y: float  # meters


class OccupancyGrid:
    """
    2D occupancy grid representation.
    
    Represents the environment as a grid where each cell can be free,
    occupied, or unknown.
    """
    
    def __init__(self, width: int, height: int, resolution: float = 0.05,
                 origin: Tuple[float, float] = (0.0, 0.0)):
        """
        Initialize occupancy grid.
        
        Args:
            width: Grid width in pixels
            height: Grid height in pixels
            resolution: Meters per pixel
            origin: Origin position in meters (x, y)
        """
        self.info = MapInfo(
            resolution=resolution,
            width=width,
            height=height,
            origin_x=origin[0],
            origin_y=origin[1]
        )
        
        # Initialize grid with unknown cells
        self.data = np.full((height, width), CellType.UNKNOWN.value, dtype=np.int8)
    
    def set_cell(self, x: int, y: int, cell_type: CellType) -> bool:
        """
        Set a cell value.
        
        Args:
            x: X coordinate in grid
            y: Y coordinate in grid
            cell_type: Type of cell
            
        Returns:
            True if cell was set, False if coordinates are invalid
        """
        if 0 <= x < self.info.width and 0 <= y < self.info.height:
            self.data[y, x] = cell_type.value
            return True
        return False
    
    def get_cell(self, x: int, y: int) -> Optional[CellType]:
        """
        Get a cell value.
        
        Args:
            x: X coordinate in grid
            y: Y coordinate in grid
            
        Returns:
            Cell type or None if coordinates are invalid
        """
        if 0 <= x < self.info.width and 0 <= y < self.info.height:
            return CellType(self.data[y, x])
        return None
    
    def world_to_grid(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """
        Convert world coordinates to grid coordinates.
        
        Args:
            world_x: X coordinate in meters
            world_y: Y coordinate in meters
            
        Returns:
            Grid coordinates (x, y)
        """
        grid_x = int((world_x - self.info.origin_x) / self.info.resolution)
        grid_y = int((world_y - self.info.origin_y) / self.info.resolution)
        return grid_x, grid_y
    
    def grid_to_world(self, grid_x: int, grid_y: int) -> Tuple[float, float]:
        """
        Convert grid coordinates to world coordinates.
        
        Args:
            grid_x: X coordinate in grid
            grid_y: Y coordinate in grid
            
        Returns:
            World coordinates (x, y) in meters
        """
        world_x = grid_x * self.info.resolution + self.info.origin_x
        world_y = grid_y * self.info.resolution + self.info.origin_y
        return world_x, world_y
    
    def set_line(self, start: Tuple[int, int], end: Tuple[int, int], 
                 cell_type: CellType) -> None:
        """
        Set a line of cells using Bresenham's algorithm.
        
        Args:
            start: Start coordinates (x, y)
            end: End coordinates (x, y)
            cell_type: Type of cells to set
        """
        x0, y0 = start
        x1, y1 = end
        
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        x, y = x0, y0
        
        while True:
            self.set_cell(x, y, cell_type)
            
            if x == x1 and y == y1:
                break
                
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
    
    def set_rectangle(self, top_left: Tuple[int, int], bottom_right: Tuple[int, int],
                     cell_type: CellType, filled: bool = True) -> None:
        """
        Set a rectangular region.
        
        Args:
            top_left: Top-left corner (x, y)
            bottom_right: Bottom-right corner (x, y)
            cell_type: Type of cells to set
            filled: Whether to fill the rectangle or just the border
        """
        x0, y0 = top_left
        x1, y1 = bottom_right
        
        if filled:
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for x in range(min(x0, x1), max(x0, x1) + 1):
                    self.set_cell(x, y, cell_type)
        else:
            # Draw border only
            for x in range(min(x0, x1), max(x0, x1) + 1):
                self.set_cell(x, y0, cell_type)
                self.set_cell(x, y1, cell_type)
            for y in range(min(y0, y1), max(y0, y1) + 1):
                self.set_cell(x0, y, cell_type)
                self.set_cell(x1, y, cell_type)
    
    def set_circle(self, center: Tuple[int, int], radius: int,
                   cell_type: CellType, filled: bool = True) -> None:
        """
        Set a circular region.
        
        Args:
            center: Center coordinates (x, y)
            radius: Radius in grid cells
            cell_type: Type of cells to set
            filled: Whether to fill the circle or just the border
        """
        cx, cy = center
        
        for y in range(cy - radius, cy + radius + 1):
            for x in range(cx - radius, cx + radius + 1):
                distance = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                
                if filled and distance <= radius:
                    self.set_cell(x, y, cell_type)
                elif not filled and abs(distance - radius) < 0.5:
                    self.set_cell(x, y, cell_type)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert occupancy grid to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "info": {
                "resolution": self.info.resolution,
                "width": self.info.width,
                "height": self.info.height,
                "origin_x": self.info.origin_x,
                "origin_y": self.info.origin_y,
            },
            "data": self.data.tolist()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OccupancyGrid":
        """
        Create occupancy grid from dictionary.
        
        Args:
            data: Dictionary representation
            
        Returns:
            OccupancyGrid instance
        """
        info = data["info"]
        grid = cls(
            width=info["width"],
            height=info["height"],
            resolution=info["resolution"],
            origin=(info["origin_x"], info["origin_y"])
        )
        grid.data = np.array(data["data"], dtype=np.int8)
        return grid


class Environment:
    """
    Environment representation containing maps, obstacles, and spatial layout.
    
    The Environment class manages the physical layout of the simulation world,
    including static obstacles, navigable areas, and other environmental features.
    """
    
    def __init__(self, name: str = "Environment"):
        """
        Initialize environment.
        
        Args:
            name: Name of the environment
        """
        self.name = name
        self.occupancy_grid: Optional[OccupancyGrid] = None
        self.static_obstacles = {}
        self.walls = {}
        self.landmarks = {}
        self.zones = {}  # Special areas (start zones, goal zones, etc.)
        
        # Environment properties
        self.properties = {
            "gravity": 9.81,
            "air_density": 1.225,
            "friction_coefficient": 0.1,
        }
    
    def create_occupancy_grid(self, width: int, height: int, 
                            resolution: float = 0.05,
                            origin: Tuple[float, float] = (0.0, 0.0)) -> None:
        """
        Create an occupancy grid for the environment.
        
        Args:
            width: Grid width in pixels
            height: Grid height in pixels
            resolution: Meters per pixel
            origin: Origin position in meters (x, y)
        """
        self.occupancy_grid = OccupancyGrid(width, height, resolution, origin)
    
    def add_wall(self, wall_id: str, start: Tuple[float, float], 
                 end: Tuple[float, float], thickness: float = 0.1) -> None:
        """
        Add a wall to the environment.
        
        Args:
            wall_id: Unique identifier for the wall
            start: Start position in meters (x, y)
            end: End position in meters (x, y)
            thickness: Wall thickness in meters
        """
        self.walls[wall_id] = {
            "start": {"x": start[0], "y": start[1]},
            "end": {"x": end[0], "y": end[1]},
            "thickness": thickness,
            "type": "wall"
        }
        
        # Update occupancy grid if available
        if self.occupancy_grid:
            start_grid = self.occupancy_grid.world_to_grid(start[0], start[1])
            end_grid = self.occupancy_grid.world_to_grid(end[0], end[1])
            self.occupancy_grid.set_line(start_grid, end_grid, CellType.OCCUPIED)
    
    def add_obstacle(self, obstacle_id: str, position: Tuple[float, float],
                    shape: str = "rectangle", size: Dict[str, float] = None,
                    is_static: bool = True) -> None:
        """
        Add an obstacle to the environment.
        
        Args:
            obstacle_id: Unique identifier for the obstacle
            position: Position in meters (x, y)
            shape: Shape type ("rectangle", "circle", "polygon")
            size: Size parameters (depends on shape)
            is_static: Whether the obstacle is static or dynamic
        """
        if size is None:
            size = {"width": 1.0, "height": 1.0}
        
        self.static_obstacles[obstacle_id] = {
            "position": {"x": position[0], "y": position[1]},
            "shape": shape,
            "size": size,
            "is_static": is_static,
            "type": "obstacle"
        }
        
        # Update occupancy grid if available
        if self.occupancy_grid and is_static:
            pos_grid = self.occupancy_grid.world_to_grid(position[0], position[1])
            
            if shape == "circle":
                radius_grid = int(size.get("radius", 0.5) / self.occupancy_grid.info.resolution)
                self.occupancy_grid.set_circle(pos_grid, radius_grid, CellType.OCCUPIED)
            else:  # rectangle or default
                width_grid = int(size.get("width", 1.0) / self.occupancy_grid.info.resolution)
                height_grid = int(size.get("height", 1.0) / self.occupancy_grid.info.resolution)
                top_left = (pos_grid[0] - width_grid // 2, pos_grid[1] - height_grid // 2)
                bottom_right = (pos_grid[0] + width_grid // 2, pos_grid[1] + height_grid // 2)
                self.occupancy_grid.set_rectangle(top_left, bottom_right, CellType.OCCUPIED)
    
    def add_zone(self, zone_id: str, zone_type: str, bounds: Dict[str, float],
                 properties: Dict[str, Any] = None) -> None:
        """
        Add a zone to the environment.
        
        Args:
            zone_id: Unique identifier for the zone
            zone_type: Type of zone ("start", "goal", "restricted", etc.)
            bounds: Zone boundaries {"x": x, "y": y, "width": w, "height": h}
            properties: Additional zone properties
        """
        if properties is None:
            properties = {}
        
        self.zones[zone_id] = {
            "type": zone_type,
            "bounds": bounds,
            "properties": properties
        }
    
    def get_free_space(self) -> List[Tuple[float, float]]:
        """
        Get list of free space coordinates.
        
        Returns:
            List of (x, y) coordinates in free space
        """
        free_spaces = []
        
        if self.occupancy_grid:
            for y in range(self.occupancy_grid.info.height):
                for x in range(self.occupancy_grid.info.width):
                    if self.occupancy_grid.get_cell(x, y) == CellType.FREE:
                        world_pos = self.occupancy_grid.grid_to_world(x, y)
                        free_spaces.append(world_pos)
        
        return free_spaces
    
    def is_position_free(self, position: Tuple[float, float], 
                        buffer_distance: float = 0.0) -> bool:
        """
        Check if a position is free of obstacles.
        
        Args:
            position: Position to check (x, y) in meters
            buffer_distance: Additional buffer distance in meters
            
        Returns:
            True if position is free, False otherwise
        """
        if not self.occupancy_grid:
            return True  # No occupancy grid means all positions are free
        
        grid_pos = self.occupancy_grid.world_to_grid(position[0], position[1])
        buffer_cells = int(buffer_distance / self.occupancy_grid.info.resolution)
        
        # Check the position and surrounding buffer area
        for dy in range(-buffer_cells, buffer_cells + 1):
            for dx in range(-buffer_cells, buffer_cells + 1):
                check_x = grid_pos[0] + dx
                check_y = grid_pos[1] + dy
                cell_type = self.occupancy_grid.get_cell(check_x, check_y)
                
                if cell_type == CellType.OCCUPIED:
                    return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert environment to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "name": self.name,
            "occupancy_grid": self.occupancy_grid.to_dict() if self.occupancy_grid else None,
            "static_obstacles": self.static_obstacles,
            "walls": self.walls,
            "landmarks": self.landmarks,
            "zones": self.zones,
            "properties": self.properties
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Environment":
        """
        Create environment from dictionary.
        
        Args:
            data: Dictionary representation
            
        Returns:
            Environment instance
        """
        env = cls(data.get("name", "Environment"))
        
        if data.get("occupancy_grid"):
            env.occupancy_grid = OccupancyGrid.from_dict(data["occupancy_grid"])
        
        env.static_obstacles = data.get("static_obstacles", {})
        env.walls = data.get("walls", {})
        env.landmarks = data.get("landmarks", {})
        env.zones = data.get("zones", {})
        env.properties = data.get("properties", {})
        
        return env
    
    def get_bounds(self) -> Dict[str, float]:
        """
        Get the bounds of the environment.
        
        Returns:
            Dictionary with min_x, max_x, min_y, max_y
        """
        if self.occupancy_grid:
            min_x = self.occupancy_grid.info.origin_x
            min_y = self.occupancy_grid.info.origin_y
            max_x = min_x + self.occupancy_grid.info.width * self.occupancy_grid.info.resolution
            max_y = min_y + self.occupancy_grid.info.height * self.occupancy_grid.info.resolution
            
            return {
                "min_x": min_x,
                "max_x": max_x,
                "min_y": min_y,
                "max_y": max_y
            }
        
        # If no occupancy grid, compute bounds from objects
        all_x = []
        all_y = []
        
        for wall in self.walls.values():
            all_x.extend([wall["start"]["x"], wall["end"]["x"]])
            all_y.extend([wall["start"]["y"], wall["end"]["y"]])
        
        for obstacle in self.static_obstacles.values():
            pos = obstacle["position"]
            size = obstacle["size"]
            all_x.extend([pos["x"] - size.get("width", 0)/2, pos["x"] + size.get("width", 0)/2])
            all_y.extend([pos["y"] - size.get("height", 0)/2, pos["y"] + size.get("height", 0)/2])
        
        if all_x and all_y:
            return {
                "min_x": min(all_x),
                "max_x": max(all_x),
                "min_y": min(all_y),
                "max_y": max(all_y)
            }
        
        # Default bounds
        return {"min_x": -5.0, "max_x": 5.0, "min_y": -5.0, "max_y": 5.0}
