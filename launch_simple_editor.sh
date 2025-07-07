#!/bin/bash
# Launch script for CrossSim Simple Environment Editor

echo "CrossSim Simple Environment Editor"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "crosssim/gui/simple_editor.py" ]; then
    echo "Error: Please run this script from the CrossSim project directory"
    echo "Usage: cd /home/benpkessler/CrossSim && ./launch_simple_editor.sh"
    exit 1
fi

# Set Python path and launch
echo "Starting simple environment editor..."
echo "Close the GUI window when you're done testing."
echo ""

export PYTHONPATH="/home/benpkessler/CrossSim:$PYTHONPATH"
python3 crosssim/gui/simple_editor.py

echo ""
echo "Simple editor closed."
