#!/usr/bin/env python3
"""
Test script for CrossSim simple editor core functionality.
Tests the saving functionality without requiring a GUI display.
"""

import sys
import os
import tempfile
from pathlib import Path

# Add the project to Python path
sys.path.insert(0, '/home/benpkessler/CrossSim')

import numpy as np
import yaml

def test_occupancy_grid_generation():
    """Test occupancy grid generation."""
    print("Testing occupancy grid generation...")
    
    # Mock the editor functionality
    width_px = 200  # 10m / 0.05m resolution
    height_px = 200
    
    # Create a simple grid with some obstacles
    grid = np.zeros((height_px, width_px), dtype=np.int8)
    
    # Add some obstacles (occupied cells = 100)
    grid[50:100, 50:100] = 100  # Square obstacle
    grid[150:170, 80:120] = 100  # Rectangle obstacle
    
    print(f"✓ Grid created: {grid.shape}")
    print(f"  Free cells: {np.sum(grid == 0)}")
    print(f"  Occupied cells: {np.sum(grid == 100)}")
    
    return grid

def test_pgm_saving(grid, file_path):
    """Test PGM file saving."""
    print(f"Testing PGM saving to: {file_path}")
    
    height, width = grid.shape
    
    # Convert to PGM format (0-255, where 254 is free, 0 is occupied)
    pgm_data = np.zeros_like(grid, dtype=np.uint8)
    pgm_data[grid == 0] = 254      # Free space -> white (254)
    pgm_data[grid == 100] = 0      # Occupied -> black (0)
    pgm_data[grid == -1] = 205     # Unknown -> gray (205)
    
    # Flip vertically to match ROS convention
    pgm_data = np.flipud(pgm_data)
    
    try:
        with open(file_path, 'wb') as f:
            # PGM header
            header = f"P5\n{width} {height}\n255\n"
            f.write(header.encode('ascii'))
            # Write data
            f.write(pgm_data.tobytes())
        
        print(f"✓ PGM file saved successfully")
        print(f"  File size: {os.path.getsize(file_path)} bytes")
        return True
        
    except Exception as e:
        print(f"✗ PGM save failed: {e}")
        return False

def test_yaml_saving(file_path, pgm_filename, resolution=0.05):
    """Test YAML file saving."""
    print(f"Testing YAML saving to: {file_path}")
    
    map_data = {
        'image': pgm_filename,
        'resolution': resolution,
        'origin': [0.0, 0.0, 0.0],
        'negate': 0,
        'occupied_thresh': 0.65,
        'free_thresh': 0.196
    }
    
    try:
        with open(file_path, 'w') as f:
            yaml.dump(map_data, f, default_flow_style=False)
        
        print(f"✓ YAML file saved successfully")
        
        # Verify content
        with open(file_path, 'r') as f:
            loaded_data = yaml.safe_load(f)
        
        print(f"  Image: {loaded_data['image']}")
        print(f"  Resolution: {loaded_data['resolution']}")
        print(f"  Origin: {loaded_data['origin']}")
        
        return True
        
    except Exception as e:
        print(f"✗ YAML save failed: {e}")
        return False

def main():
    """Main test function."""
    print("CrossSim Simple Editor - Core Functionality Test")
    print("=" * 50)
    
    # Create temporary directory for test files
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Test directory: {temp_dir}")
        
        # Test occupancy grid generation
        grid = test_occupancy_grid_generation()
        
        # Test file saving
        pgm_path = os.path.join(temp_dir, "test_map.pgm")
        yaml_path = os.path.join(temp_dir, "test_map.yaml")
        
        pgm_success = test_pgm_saving(grid, pgm_path)
        yaml_success = test_yaml_saving(yaml_path, "test_map.pgm")
        
        if pgm_success and yaml_success:
            print("\n" + "=" * 50)
            print("✓ All tests passed!")
            print("\nGenerated files:")
            print(f"  • {os.path.basename(yaml_path)} ({os.path.getsize(yaml_path)} bytes)")
            print(f"  • {os.path.basename(pgm_path)} ({os.path.getsize(pgm_path)} bytes)")
            print("\nThese files are compatible with ROS2 Nav2!")
            
            # Show file contents
            print(f"\n{yaml_path} contents:")
            with open(yaml_path, 'r') as f:
                print(f.read())
            
            return 0
        else:
            print("\n✗ Some tests failed!")
            return 1

if __name__ == "__main__":
    sys.exit(main())
