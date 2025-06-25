"""
Core module for CrossSim data structures and base classes.

This module provides the fundamental data structures used throughout
the CrossSim toolkit.
"""

from crosssim.core.scenario import Scenario
from crosssim.core.environment import Environment
from crosssim.core.agent import Agent, Robot

__all__ = [
    "Scenario",
    "Environment",
    "Agent", 
    "Robot",
]
