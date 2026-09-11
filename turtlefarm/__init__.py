"""Stylised explanatory agent-based model of disease spread in a modular captive-turtle housing system.

Implementation follows docs/model-specification.md. This package is the M1 baseline:
S/I/R agents in fixed tanks with within-tank transmission, recovery and stopping rules.
Cross-tank movement, the transfer network and quarantine strategies are M2 work.
"""

from turtlefarm.config import SimulationConfig
from turtlefarm.model import Simulation, RunRecord, run_baseline
from turtlefarm.rng import EventKeyedDraws, TableDraws
from turtlefarm.scenario import Layout, TankSpec, AgentSpec
from turtlefarm.network import TransferNetwork, generate_network

__all__ = [
    "SimulationConfig", "Simulation", "RunRecord", "run_baseline",
    "EventKeyedDraws", "TableDraws", "Layout", "TankSpec", "AgentSpec",
    "TransferNetwork", "generate_network",
]
