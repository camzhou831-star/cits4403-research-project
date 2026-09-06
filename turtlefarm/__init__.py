"""Stylised explanatory agent-based model of disease spread in a modular captive-turtle housing system.

Implementation follows docs/model-specification.md. This package is the M1 baseline:
S/I/R agents in fixed tanks with within-tank transmission, recovery and stopping rules.
Cross-tank movement, the transfer network and quarantine strategies are M2 work.
"""

from turtlefarm.config import SimulationConfig
from turtlefarm.model import Simulation, RunRecord

__all__ = ["SimulationConfig", "Simulation", "RunRecord"]
