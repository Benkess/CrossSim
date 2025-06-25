"""
Agent and robot data structures for CrossSim.

This module provides classes for representing dynamic entities in the simulation,
including pedestrians, robots, and other moving agents.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid


class AgentType(Enum):
    """Types of agents in the simulation."""
    PEDESTRIAN = "pedestrian"
    ROBOT = "robot"
    VEHICLE = "vehicle"
    STATIC_OBJECT = "static_object"


class BehaviorType(Enum):
    """Types of agent behaviors."""
    STATIC = "static"
    RANDOM_WALK = "random_walk"
    WAYPOINT_FOLLOWING = "waypoint_following"
    SOCIAL_FORCE = "social_force"
    ORCA = "orca"
    CUSTOM = "custom"


@dataclass
class Position:
    """2D position with orientation."""
    x: float = 0.0
    y: float = 0.0
    theta: float = 0.0  # orientation in radians


@dataclass
class Velocity:
    """2D velocity."""
    vx: float = 0.0
    vy: float = 0.0
    angular: float = 0.0  # angular velocity in rad/s


@dataclass
class Size:
    """Physical size of an agent."""
    width: float = 0.5
    height: float = 0.5
    radius: Optional[float] = None  # for circular agents


@dataclass
class Goal:
    """Navigation goal for an agent."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    position: Position = field(default_factory=Position)
    radius: float = 0.5
    priority: int = 1
    reached: bool = False


@dataclass
class SpeedLimits:
    """Speed limits for an agent."""
    min_speed: float = 0.0
    max_speed: float = 2.0
    preferred_speed: float = 1.0
    max_acceleration: float = 1.0
    max_deceleration: float = 2.0


class Agent:
    """
    Base class for dynamic agents in the simulation.
    
    Represents any moving entity including pedestrians, robots, vehicles, etc.
    """
    
    def __init__(self, agent_id: str = None, agent_type: AgentType = AgentType.PEDESTRIAN):
        """
        Initialize agent.
        
        Args:
            agent_id: Unique identifier (generated if None)
            agent_type: Type of agent
        """
        self.id = agent_id or str(uuid.uuid4())
        self.type = agent_type
        self.name = f"{agent_type.value}_{self.id[:8]}"
        
        # Physical properties
        self.position = Position()
        self.velocity = Velocity()
        self.size = Size()
        self.mass = 70.0  # kg
        
        # Behavior properties
        self.behavior_type = BehaviorType.STATIC
        self.speed_limits = SpeedLimits()
        self.personal_space = 0.5  # meters
        
        # Navigation
        self.goals: List[Goal] = []
        self.current_goal_index = 0
        
        # Visual properties
        self.color = "blue"
        self.visible = True
        
        # State
        self.is_active = True
        self.metadata = {}
    
    @property
    def current_goal(self) -> Optional[Goal]:
        """Get the current navigation goal."""
        if 0 <= self.current_goal_index < len(self.goals):
            return self.goals[self.current_goal_index]
        return None
    
    def add_goal(self, position: Tuple[float, float], radius: float = 0.5,
                 priority: int = 1) -> str:
        """
        Add a navigation goal.
        
        Args:
            position: Goal position (x, y) in meters
            radius: Goal radius in meters
            priority: Goal priority (higher is more important)
            
        Returns:
            Goal ID
        """
        goal = Goal(
            position=Position(x=position[0], y=position[1]),
            radius=radius,
            priority=priority
        )
        self.goals.append(goal)
        
        # Sort goals by priority (highest first)
        self.goals.sort(key=lambda g: g.priority, reverse=True)
        
        return goal.id
    
    def remove_goal(self, goal_id: str) -> bool:
        """
        Remove a navigation goal.
        
        Args:
            goal_id: ID of goal to remove
            
        Returns:
            True if goal was removed, False if not found
        """
        for i, goal in enumerate(self.goals):
            if goal.id == goal_id:
                del self.goals[i]
                # Adjust current goal index if necessary
                if self.current_goal_index >= len(self.goals):
                    self.current_goal_index = max(0, len(self.goals) - 1)
                return True
        return False
    
    def set_position(self, x: float, y: float, theta: float = None) -> None:
        """
        Set agent position.
        
        Args:
            x: X coordinate in meters
            y: Y coordinate in meters
            theta: Orientation in radians (optional)
        """
        self.position.x = x
        self.position.y = y
        if theta is not None:
            self.position.theta = theta
    
    def set_velocity(self, vx: float, vy: float, angular: float = 0.0) -> None:
        """
        Set agent velocity.
        
        Args:
            vx: X velocity in m/s
            vy: Y velocity in m/s
            angular: Angular velocity in rad/s
        """
        self.velocity.vx = vx
        self.velocity.vy = vy
        self.velocity.angular = angular
    
    def get_distance_to_goal(self) -> Optional[float]:
        """
        Get distance to current goal.
        
        Returns:
            Distance in meters or None if no current goal
        """
        if self.current_goal:
            dx = self.current_goal.position.x - self.position.x
            dy = self.current_goal.position.y - self.position.y
            return (dx * dx + dy * dy) ** 0.5
        return None
    
    def is_at_goal(self) -> bool:
        """
        Check if agent is at current goal.
        
        Returns:
            True if agent is within goal radius
        """
        if self.current_goal:
            distance = self.get_distance_to_goal()
            return distance is not None and distance <= self.current_goal.radius
        return False
    
    def advance_to_next_goal(self) -> bool:
        """
        Advance to the next goal in the list.
        
        Returns:
            True if advanced to next goal, False if no more goals
        """
        if self.current_goal:
            self.current_goal.reached = True
        
        if self.current_goal_index + 1 < len(self.goals):
            self.current_goal_index += 1
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert agent to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "id": self.id,
            "type": self.type.value,
            "name": self.name,
            "position": {
                "x": self.position.x,
                "y": self.position.y,
                "theta": self.position.theta
            },
            "velocity": {
                "vx": self.velocity.vx,
                "vy": self.velocity.vy,
                "angular": self.velocity.angular
            },
            "size": {
                "width": self.size.width,
                "height": self.size.height,
                "radius": self.size.radius
            },
            "mass": self.mass,
            "behavior_type": self.behavior_type.value,
            "speed_limits": {
                "min_speed": self.speed_limits.min_speed,
                "max_speed": self.speed_limits.max_speed,
                "preferred_speed": self.speed_limits.preferred_speed,
                "max_acceleration": self.speed_limits.max_acceleration,
                "max_deceleration": self.speed_limits.max_deceleration
            },
            "personal_space": self.personal_space,
            "goals": [
                {
                    "id": goal.id,
                    "position": {
                        "x": goal.position.x,
                        "y": goal.position.y,
                        "theta": goal.position.theta
                    },
                    "radius": goal.radius,
                    "priority": goal.priority,
                    "reached": goal.reached
                }
                for goal in self.goals
            ],
            "current_goal_index": self.current_goal_index,
            "color": self.color,
            "visible": self.visible,
            "is_active": self.is_active,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Agent":
        """
        Create agent from dictionary.
        
        Args:
            data: Dictionary representation
            
        Returns:
            Agent instance
        """
        # Create agent with ID and type
        agent_type = AgentType(data.get("type", "pedestrian"))
        agent = cls(data.get("id"), agent_type)
        
        # Load basic properties
        agent.name = data.get("name", agent.name)
        
        # Load position
        pos_data = data.get("position", {})
        agent.position = Position(
            x=pos_data.get("x", 0.0),
            y=pos_data.get("y", 0.0),
            theta=pos_data.get("theta", 0.0)
        )
        
        # Load velocity
        vel_data = data.get("velocity", {})
        agent.velocity = Velocity(
            vx=vel_data.get("vx", 0.0),
            vy=vel_data.get("vy", 0.0),
            angular=vel_data.get("angular", 0.0)
        )
        
        # Load size
        size_data = data.get("size", {})
        agent.size = Size(
            width=size_data.get("width", 0.5),
            height=size_data.get("height", 0.5),
            radius=size_data.get("radius")
        )
        
        # Load other properties
        agent.mass = data.get("mass", 70.0)
        agent.behavior_type = BehaviorType(data.get("behavior_type", "static"))
        
        # Load speed limits
        speed_data = data.get("speed_limits", {})
        agent.speed_limits = SpeedLimits(
            min_speed=speed_data.get("min_speed", 0.0),
            max_speed=speed_data.get("max_speed", 2.0),
            preferred_speed=speed_data.get("preferred_speed", 1.0),
            max_acceleration=speed_data.get("max_acceleration", 1.0),
            max_deceleration=speed_data.get("max_deceleration", 2.0)
        )
        
        agent.personal_space = data.get("personal_space", 0.5)
        
        # Load goals
        agent.goals = []
        for goal_data in data.get("goals", []):
            goal_pos_data = goal_data.get("position", {})
            goal = Goal(
                id=goal_data.get("id", str(uuid.uuid4())),
                position=Position(
                    x=goal_pos_data.get("x", 0.0),
                    y=goal_pos_data.get("y", 0.0),
                    theta=goal_pos_data.get("theta", 0.0)
                ),
                radius=goal_data.get("radius", 0.5),
                priority=goal_data.get("priority", 1),
                reached=goal_data.get("reached", False)
            )
            agent.goals.append(goal)
        
        agent.current_goal_index = data.get("current_goal_index", 0)
        
        # Load visual and state properties
        agent.color = data.get("color", "blue")
        agent.visible = data.get("visible", True)
        agent.is_active = data.get("is_active", True)
        agent.metadata = data.get("metadata", {})
        
        return agent


class Robot(Agent):
    """
    Robot agent with additional robot-specific properties.
    
    Extends the base Agent class with robot-specific capabilities like
    sensors, actuators, and control interfaces.
    """
    
    def __init__(self, robot_id: str = None):
        """
        Initialize robot.
        
        Args:
            robot_id: Unique identifier (generated if None)
        """
        super().__init__(robot_id, AgentType.ROBOT)
        
        # Robot-specific properties
        self.robot_model = "generic"
        self.sensors = {}
        self.actuators = {}
        self.control_mode = "manual"  # manual, autonomous, teleop
        
        # Navigation capabilities
        self.has_mapping = True
        self.has_localization = True
        self.has_path_planning = True
        
        # Safety properties
        self.emergency_stop = False
        self.safety_radius = 0.3  # meters
        self.max_safe_speed = 1.0  # m/s
    
    def add_sensor(self, sensor_id: str, sensor_type: str, 
                   properties: Dict[str, Any] = None) -> None:
        """
        Add a sensor to the robot.
        
        Args:
            sensor_id: Unique sensor identifier
            sensor_type: Type of sensor (lidar, camera, imu, etc.)
            properties: Sensor-specific properties
        """
        if properties is None:
            properties = {}
        
        self.sensors[sensor_id] = {
            "type": sensor_type,
            "properties": properties,
            "active": True
        }
    
    def add_actuator(self, actuator_id: str, actuator_type: str,
                    properties: Dict[str, Any] = None) -> None:
        """
        Add an actuator to the robot.
        
        Args:
            actuator_id: Unique actuator identifier
            actuator_type: Type of actuator (wheels, arm, gripper, etc.)
            properties: Actuator-specific properties
        """
        if properties is None:
            properties = {}
        
        self.actuators[actuator_id] = {
            "type": actuator_type,
            "properties": properties,
            "active": True
        }
    
    def set_control_mode(self, mode: str) -> None:
        """
        Set robot control mode.
        
        Args:
            mode: Control mode ("manual", "autonomous", "teleop")
        """
        valid_modes = ["manual", "autonomous", "teleop"]
        if mode in valid_modes:
            self.control_mode = mode
        else:
            raise ValueError(f"Invalid control mode. Must be one of: {valid_modes}")
    
    def emergency_stop_activate(self) -> None:
        """Activate emergency stop."""
        self.emergency_stop = True
        self.set_velocity(0.0, 0.0, 0.0)
    
    def emergency_stop_deactivate(self) -> None:
        """Deactivate emergency stop."""
        self.emergency_stop = False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert robot to dictionary.
        
        Returns:
            Dictionary representation
        """
        base_dict = super().to_dict()
        
        # Add robot-specific properties
        base_dict.update({
            "robot_model": self.robot_model,
            "sensors": self.sensors,
            "actuators": self.actuators,
            "control_mode": self.control_mode,
            "has_mapping": self.has_mapping,
            "has_localization": self.has_localization,
            "has_path_planning": self.has_path_planning,
            "emergency_stop": self.emergency_stop,
            "safety_radius": self.safety_radius,
            "max_safe_speed": self.max_safe_speed
        })
        
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Robot":
        """
        Create robot from dictionary.
        
        Args:
            data: Dictionary representation
            
        Returns:
            Robot instance
        """
        # Create base agent
        robot = cls(data.get("id"))
        
        # Load base agent properties
        agent_data = Agent.from_dict(data)
        robot.name = agent_data.name
        robot.position = agent_data.position
        robot.velocity = agent_data.velocity
        robot.size = agent_data.size
        robot.mass = agent_data.mass
        robot.behavior_type = agent_data.behavior_type
        robot.speed_limits = agent_data.speed_limits
        robot.personal_space = agent_data.personal_space
        robot.goals = agent_data.goals
        robot.current_goal_index = agent_data.current_goal_index
        robot.color = agent_data.color
        robot.visible = agent_data.visible
        robot.is_active = agent_data.is_active
        robot.metadata = agent_data.metadata
        
        # Load robot-specific properties
        robot.robot_model = data.get("robot_model", "generic")
        robot.sensors = data.get("sensors", {})
        robot.actuators = data.get("actuators", {})
        robot.control_mode = data.get("control_mode", "manual")
        robot.has_mapping = data.get("has_mapping", True)
        robot.has_localization = data.get("has_localization", True)
        robot.has_path_planning = data.get("has_path_planning", True)
        robot.emergency_stop = data.get("emergency_stop", False)
        robot.safety_radius = data.get("safety_radius", 0.3)
        robot.max_safe_speed = data.get("max_safe_speed", 1.0)
        
        return robot
