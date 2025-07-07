# CrossSim - Simple Environment Editor

A quick setup guide for the CrossSim interactive environment creation toolkit.

## Quick Start

1. **Check dependencies:**
   ```bash
   cd /home/benpkessler/CrossSim
   python3 check_dependencies.py
   ```

2. **Test core functionality:**
   ```bash
   python3 test_save_functionality.py
   ```

3. **Launch the simple environment editor:**
   ```bash
   # Easy launch (recommended)
   ./launch_simple_editor.sh
   
   # Or manual launch
   PYTHONPATH=/home/benpkessler/CrossSim python3 crosssim/gui/simple_editor.py
   ```

## Fixed Issues

✅ **File Extension**: The save dialog now automatically adds `.yaml` extension if not provided  
✅ **PGM File Creation**: Both YAML and PGM files are now properly created  
✅ **ROS2 Compatibility**: Output files follow ROS2 Nav2 conventions exactly  

## Simple Environment Editor Features

### Current Features:
- **Map Setup**: Configure map size, resolution, and origin
- **Static Layer Editing**: Draw rectangular obstacles by clicking and dragging  
- **Interactive Editing**: Select, move, and delete obstacles
- **ROS2 Nav2 Export**: Save maps in ROS2 Nav2 format (.yaml + .pgm files)
- **Automatic File Extensions**: No need to manually add `.yaml` extension

### How to Use:

1. **Create New Environment**:
   - Launch the application
   - Set your desired map dimensions and resolution
   - Click "OK" to create the environment

2. **Draw Obstacles**:
   - Click the "Draw Obstacles" button to enter drawing mode
   - Click and drag to create rectangular obstacles
   - Click the button again to exit drawing mode

3. **Edit Obstacles**:
   - In selection mode, click on obstacles to select them
   - Selected obstacles can be moved by dragging
   - Press Delete key to remove selected obstacles

4. **Save Your Map**:
   - Use "File" → "Save as ROS2 Map" or click "Save ROS2 Map" button
   - Choose a filename (e.g., "my_map.yaml")
   - The system will create both .yaml and .pgm files for ROS2 Nav2

### File Format Compatibility:
The exported files are fully compatible with ROS2 Nav2 navigation stack:
- `.yaml` file contains map metadata
- `.pgm` file contains the occupancy grid image
- Free space appears white, obstacles appear black

## Development Notes

This is a focused implementation for creating 2D occupancy grid environments. The current version includes:

- Simple obstacle drawing with rectangles
- ROS2 Nav2 compatible export format
- Grid-based editing with metric units
- Configurable map resolution and dimensions

Future enhancements will include:
- Additional layer types
- More complex obstacle shapes
- Agent/robot placement
- Export to multiple simulator formats

## Dependencies

- PyQt5 (GUI framework)
- NumPy (numerical operations)
- PyYAML (YAML file handling)
- Pillow (image processing)

## File Structure

```
crosssim/
├── core/                 # Core data structures
│   ├── scenario.py      # Scenario management
│   ├── environment.py   # Environment representation
│   └── agent.py         # Agent/robot definitions
├── gui/                 # GUI components
│   ├── simple_editor.py # Simple 2D environment editor
│   ├── main_window.py   # Full GUI (placeholder)
│   └── main.py          # GUI entry point
└── cli/                 # Command line interface
    └── main.py          # CLI entry point
```
