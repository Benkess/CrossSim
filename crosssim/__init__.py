"""
CrossSim - Cross-Simulator Scenario Generation Toolkit for Robotic Navigation

A modular, extensible set of tools for generating, editing, and exporting 
robotic simulation environments and navigation scenarios.
"""

__version__ = "0.1.0"
__author__ = "CrossSim Contributors"
__email__ = ""
__description__ = "Cross-Simulator Scenario Generation Toolkit for Robotic Navigation"

from crosssim.core.scenario import Scenario
from crosssim.core.environment import Environment
from crosssim.core.agent import Agent, Robot

__all__ = [
    "Scenario",
    "Environment", 
    "Agent",
    "Robot",
]
