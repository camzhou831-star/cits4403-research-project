"""Stylised explanatory agent-based model of disease spread in a modular captive-turtle housing system.

Implementation follows docs/model-specification.md. The package currently provides S/I/R agents,
within-tank transmission, recovery, a fixed modular transfer network, network-constrained movement and
stopping rules. Quarantine strategies and the experiment runner remain M2 work.
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
