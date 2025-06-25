"""
Scenario data structure for CrossSim.

This module provides the main Scenario class that represents a complete
simulation scenario including environment, agents, and configuration.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import json
import yaml
from pathlib import Path


@dataclass
class ScenarioMetadata:
    """Metadata for a simulation scenario."""
    name: str = "Untitled Scenario"
    description: str = ""
    author: str = ""
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    created_at: Optional[str] = None
    modified_at: Optional[str] = None


@dataclass
class EnvironmentConfig:
    """Environment configuration settings."""
    size: Dict[str, float] = field(default_factory=lambda: {"width": 10.0, "height": 10.0})
    resolution: float = 0.05  # meters per pixel
    origin: Dict[str, float] = field(default_factory=lambda: {"x": 0.0, "y": 0.0})


@dataclass
class SimulationConfig:
    """Simulation runtime configuration."""
    time_step: float = 0.1  # seconds
    duration: float = 60.0  # seconds
    real_time_factor: float = 1.0
    record_data: bool = True
    output_format: str = "json"


class Scenario:
    """
    Main scenario class representing a complete simulation setup.
    
    A scenario contains all the information needed to run a simulation,
    including the environment layout, agent configurations, and simulation
    parameters.
    """
    
    def __init__(self, name: str = "New Scenario"):
        """
        Initialize a new scenario.
        
        Args:
            name: Name of the scenario
        """
        self.metadata = ScenarioMetadata(name=name)
        self.environment_config = EnvironmentConfig()
        self.simulation_config = SimulationConfig()
        
        # Scenario data
        self.environment_data = {}
        self.agents = {}
        self.robots = {}
        self.static_objects = {}
        self.goals = {}
        
        # File path (when loaded/saved)
        self._file_path: Optional[Path] = None
        self._modified = False
    
    @property
    def name(self) -> str:
        """Get scenario name."""
        return self.metadata.name
    
    @name.setter
    def name(self, value: str) -> None:
        """Set scenario name."""
        self.metadata.name = value
        self._modified = True
    
    @property
    def description(self) -> str:
        """Get scenario description."""
        return self.metadata.description
    
    @description.setter
    def description(self, value: str) -> None:
        """Set scenario description."""
        self.metadata.description = value
        self._modified = True
    
    @property
    def is_modified(self) -> bool:
        """Check if scenario has been modified."""
        return self._modified
    
    @property
    def file_path(self) -> Optional[Path]:
        """Get the file path where scenario is saved."""
        return self._file_path
    
    def add_agent(self, agent_id: str, agent_data: Dict[str, Any]) -> None:
        """
        Add an agent to the scenario.
        
        Args:
            agent_id: Unique identifier for the agent
            agent_data: Agent configuration data
        """
        self.agents[agent_id] = agent_data.copy()
        self._modified = True
    
    def remove_agent(self, agent_id: str) -> bool:
        """
        Remove an agent from the scenario.
        
        Args:
            agent_id: Unique identifier for the agent
            
        Returns:
            True if agent was removed, False if not found
        """
        if agent_id in self.agents:
            del self.agents[agent_id]
            self._modified = True
            return True
        return False
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get agent data by ID.
        
        Args:
            agent_id: Unique identifier for the agent
            
        Returns:
            Agent data dictionary or None if not found
        """
        return self.agents.get(agent_id)
    
    def add_robot(self, robot_id: str, robot_data: Dict[str, Any]) -> None:
        """
        Add a robot to the scenario.
        
        Args:
            robot_id: Unique identifier for the robot
            robot_data: Robot configuration data
        """
        self.robots[robot_id] = robot_data.copy()
        self._modified = True
    
    def remove_robot(self, robot_id: str) -> bool:
        """
        Remove a robot from the scenario.
        
        Args:
            robot_id: Unique identifier for the robot
            
        Returns:
            True if robot was removed, False if not found
        """
        if robot_id in self.robots:
            del self.robots[robot_id]
            self._modified = True
            return True
        return False
    
    def get_robot(self, robot_id: str) -> Optional[Dict[str, Any]]:
        """
        Get robot data by ID.
        
        Args:
            robot_id: Unique identifier for the robot
            
        Returns:
            Robot data dictionary or None if not found
        """
        return self.robots.get(robot_id)
    
    def set_environment_data(self, environment_data: Dict[str, Any]) -> None:
        """
        Set the environment data.
        
        Args:
            environment_data: Environment layout and configuration
        """
        self.environment_data = environment_data.copy()
        self._modified = True
    
    def get_environment_data(self) -> Dict[str, Any]:
        """
        Get the environment data.
        
        Returns:
            Environment data dictionary
        """
        return self.environment_data.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert scenario to dictionary format.
        
        Returns:
            Scenario data as dictionary
        """
        return {
            "metadata": {
                "name": self.metadata.name,
                "description": self.metadata.description,
                "author": self.metadata.author,
                "version": self.metadata.version,
                "tags": self.metadata.tags,
                "created_at": self.metadata.created_at,
                "modified_at": self.metadata.modified_at,
            },
            "environment_config": {
                "size": self.environment_config.size,
                "resolution": self.environment_config.resolution,
                "origin": self.environment_config.origin,
            },
            "simulation_config": {
                "time_step": self.simulation_config.time_step,
                "duration": self.simulation_config.duration,
                "real_time_factor": self.simulation_config.real_time_factor,
                "record_data": self.simulation_config.record_data,
                "output_format": self.simulation_config.output_format,
            },
            "environment_data": self.environment_data,
            "agents": self.agents,
            "robots": self.robots,
            "static_objects": self.static_objects,
            "goals": self.goals,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Scenario":
        """
        Create scenario from dictionary data.
        
        Args:
            data: Scenario data dictionary
            
        Returns:
            New Scenario instance
        """
        scenario = cls()
        
        # Load metadata
        metadata = data.get("metadata", {})
        scenario.metadata.name = metadata.get("name", "Untitled Scenario")
        scenario.metadata.description = metadata.get("description", "")
        scenario.metadata.author = metadata.get("author", "")
        scenario.metadata.version = metadata.get("version", "1.0.0")
        scenario.metadata.tags = metadata.get("tags", [])
        scenario.metadata.created_at = metadata.get("created_at")
        scenario.metadata.modified_at = metadata.get("modified_at")
        
        # Load environment config
        env_config = data.get("environment_config", {})
        scenario.environment_config.size = env_config.get("size", {"width": 10.0, "height": 10.0})
        scenario.environment_config.resolution = env_config.get("resolution", 0.05)
        scenario.environment_config.origin = env_config.get("origin", {"x": 0.0, "y": 0.0})
        
        # Load simulation config
        sim_config = data.get("simulation_config", {})
        scenario.simulation_config.time_step = sim_config.get("time_step", 0.1)
        scenario.simulation_config.duration = sim_config.get("duration", 60.0)
        scenario.simulation_config.real_time_factor = sim_config.get("real_time_factor", 1.0)
        scenario.simulation_config.record_data = sim_config.get("record_data", True)
        scenario.simulation_config.output_format = sim_config.get("output_format", "json")
        
        # Load scenario data
        scenario.environment_data = data.get("environment_data", {})
        scenario.agents = data.get("agents", {})
        scenario.robots = data.get("robots", {})
        scenario.static_objects = data.get("static_objects", {})
        scenario.goals = data.get("goals", {})
        
        scenario._modified = False
        return scenario
    
    def save_to_file(self, file_path: Path, file_format: str = "yaml") -> None:
        """
        Save scenario to file.
        
        Args:
            file_path: Path to save the scenario
            file_format: File format ("yaml" or "json")
        """
        data = self.to_dict()
        
        if file_format.lower() == "json":
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        
        self._file_path = Path(file_path)
        self._modified = False
    
    @classmethod
    def load_from_file(cls, file_path: Path) -> "Scenario":
        """
        Load scenario from file.
        
        Args:
            file_path: Path to the scenario file
            
        Returns:
            Loaded Scenario instance
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.suffix.lower() == '.json':
                data = json.load(f)
            else:
                data = yaml.safe_load(f)
        
        scenario = cls.from_dict(data)
        scenario._file_path = Path(file_path)
        scenario._modified = False
        
        return scenario
    
    def validate(self) -> List[str]:
        """
        Validate the scenario data.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check required fields
        if not self.metadata.name.strip():
            errors.append("Scenario name is required")
        
        # Validate environment config
        if self.environment_config.size["width"] <= 0:
            errors.append("Environment width must be positive")
        if self.environment_config.size["height"] <= 0:
            errors.append("Environment height must be positive")
        if self.environment_config.resolution <= 0:
            errors.append("Environment resolution must be positive")
        
        # Validate simulation config
        if self.simulation_config.time_step <= 0:
            errors.append("Time step must be positive")
        if self.simulation_config.duration <= 0:
            errors.append("Simulation duration must be positive")
        
        return errors
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the scenario.
        
        Returns:
            Summary information dictionary
        """
        return {
            "name": self.metadata.name,
            "description": self.metadata.description,
            "agent_count": len(self.agents),
            "robot_count": len(self.robots),
            "static_object_count": len(self.static_objects),
            "goal_count": len(self.goals),
            "environment_size": f"{self.environment_config.size['width']}x{self.environment_config.size['height']}m",
            "simulation_duration": f"{self.simulation_config.duration}s",
            "is_modified": self._modified,
            "file_path": str(self._file_path) if self._file_path else None,
        }
