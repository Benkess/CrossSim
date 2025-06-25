"""
Main entry point for the CrossSim CLI application.

This module provides command line interface for creating and managing scenarios.
"""

import sys
import argparse
from typing import Optional


def main(args: Optional[list] = None) -> int:
    """
    Main entry point for the CrossSim CLI.
    
    Args:
        args: Command line arguments (optional)
        
    Returns:
        Exit code
    """
    if args is None:
        args = sys.argv[1:]
    
    parser = argparse.ArgumentParser(
        description="CrossSim - Cross-Simulator Scenario Generation Toolkit"
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version="CrossSim 0.1.0"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create scenario command
    create_parser = subparsers.add_parser("create", help="Create a new scenario")
    create_parser.add_argument("name", help="Name of the scenario")
    create_parser.add_argument("--output", "-o", help="Output file path")
    
    # Validate scenario command
    validate_parser = subparsers.add_parser("validate", help="Validate a scenario")
    validate_parser.add_argument("scenario", help="Path to scenario file")
    
    # Convert scenario command
    convert_parser = subparsers.add_parser("convert", help="Convert scenario format")
    convert_parser.add_argument("input", help="Input scenario file")
    convert_parser.add_argument("output", help="Output file path")
    convert_parser.add_argument("--format", choices=["yaml", "json"], default="yaml")
    
    # List scenarios command
    list_parser = subparsers.add_parser("list", help="List scenarios in directory")
    list_parser.add_argument("directory", nargs="?", default=".", help="Directory to search")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show scenario information")
    info_parser.add_argument("scenario", help="Path to scenario file")
    
    parsed_args = parser.parse_args(args)
    
    if not parsed_args.command:
        parser.print_help()
        return 1
    
    try:
        if parsed_args.command == "create":
            return _create_scenario(parsed_args)
        elif parsed_args.command == "validate":
            return _validate_scenario(parsed_args)
        elif parsed_args.command == "convert":
            return _convert_scenario(parsed_args)
        elif parsed_args.command == "list":
            return _list_scenarios(parsed_args)
        elif parsed_args.command == "info":
            return _show_scenario_info(parsed_args)
        else:
            print(f"Unknown command: {parsed_args.command}")
            return 1
    
    except Exception as e:
        print(f"Error: {e}")
        return 1


def _create_scenario(args) -> int:
    """Create a new scenario."""
    from crosssim.core.scenario import Scenario
    from pathlib import Path
    
    scenario = Scenario(args.name)
    
    # Set output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path(f"{args.name.lower().replace(' ', '_')}.yaml")
    
    # Save scenario
    scenario.save_to_file(output_path)
    
    print(f"Created scenario '{args.name}' at {output_path}")
    return 0


def _validate_scenario(args) -> int:
    """Validate a scenario file."""
    from crosssim.core.scenario import Scenario
    from pathlib import Path
    
    scenario_path = Path(args.scenario)
    
    if not scenario_path.exists():
        print(f"Scenario file not found: {scenario_path}")
        return 1
    
    try:
        scenario = Scenario.load_from_file(scenario_path)
        errors = scenario.validate()
        
        if errors:
            print(f"Validation failed for {scenario_path}:")
            for error in errors:
                print(f"  - {error}")
            return 1
        else:
            print(f"Scenario {scenario_path} is valid")
            return 0
    
    except Exception as e:
        print(f"Failed to load scenario: {e}")
        return 1


def _convert_scenario(args) -> int:
    """Convert scenario between formats."""
    from crosssim.core.scenario import Scenario
    from pathlib import Path
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        return 1
    
    try:
        scenario = Scenario.load_from_file(input_path)
        scenario.save_to_file(output_path, args.format)
        
        print(f"Converted {input_path} to {output_path} ({args.format} format)")
        return 0
    
    except Exception as e:
        print(f"Conversion failed: {e}")
        return 1


def _list_scenarios(args) -> int:
    """List scenarios in directory."""
    from pathlib import Path
    
    directory = Path(args.directory)
    
    if not directory.exists():
        print(f"Directory not found: {directory}")
        return 1
    
    # Find scenario files
    scenario_files = []
    for pattern in ["*.yaml", "*.yml", "*.json"]:
        scenario_files.extend(directory.glob(pattern))
    
    if not scenario_files:
        print(f"No scenario files found in {directory}")
        return 0
    
    print(f"Scenarios in {directory}:")
    for file_path in sorted(scenario_files):
        try:
            from crosssim.core.scenario import Scenario
            scenario = Scenario.load_from_file(file_path)
            summary = scenario.get_summary()
            
            print(f"  {file_path.name}")
            print(f"    Name: {summary['name']}")
            print(f"    Agents: {summary['agent_count']}, Robots: {summary['robot_count']}")
            print(f"    Size: {summary['environment_size']}")
            print()
        
        except Exception as e:
            print(f"  {file_path.name} (failed to load: {e})")
    
    return 0


def _show_scenario_info(args) -> int:
    """Show detailed scenario information."""
    from crosssim.core.scenario import Scenario
    from pathlib import Path
    
    scenario_path = Path(args.scenario)
    
    if not scenario_path.exists():
        print(f"Scenario file not found: {scenario_path}")
        return 1
    
    try:
        scenario = Scenario.load_from_file(scenario_path)
        summary = scenario.get_summary()
        
        print(f"Scenario Information: {scenario_path}")
        print("=" * 50)
        print(f"Name: {summary['name']}")
        print(f"Description: {scenario.description}")
        print(f"Author: {scenario.metadata.author}")
        print(f"Version: {scenario.metadata.version}")
        print(f"Tags: {', '.join(scenario.metadata.tags) if scenario.metadata.tags else 'None'}")
        print()
        print("Environment:")
        print(f"  Size: {summary['environment_size']}")
        print(f"  Resolution: {scenario.environment_config.resolution} m/px")
        print()
        print("Entities:")
        print(f"  Agents: {summary['agent_count']}")
        print(f"  Robots: {summary['robot_count']}")
        print(f"  Static Objects: {summary['static_object_count']}")
        print(f"  Goals: {summary['goal_count']}")
        print()
        print("Simulation:")
        print(f"  Duration: {summary['simulation_duration']}")
        print(f"  Time Step: {scenario.simulation_config.time_step}s")
        print(f"  Real-time Factor: {scenario.simulation_config.real_time_factor}")
        print()
        print(f"Modified: {'Yes' if summary['is_modified'] else 'No'}")
        
        return 0
    
    except Exception as e:
        print(f"Failed to load scenario: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
