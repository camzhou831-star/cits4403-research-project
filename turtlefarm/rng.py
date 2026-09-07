"""Seed management (model-specification section 16).

The epidemic seed is split into independent, deterministically derived substreams so that a strategy
that consumes one fewer draw in one stage does not shift every later random sequence.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

EPIDEMIC_STREAMS = ("initialisation", "movement", "transmission", "recovery")


@dataclass(frozen=True)
class EpidemicStreams:
    initialisation: np.random.Generator
    movement: np.random.Generator
    transmission: np.random.Generator
    recovery: np.random.Generator


def epidemic_streams(epidemic_seed: int) -> EpidemicStreams:
    """Derive the four epidemic substreams from one seed. Same seed -> identical streams."""
    children = np.random.SeedSequence(epidemic_seed).spawn(len(EPIDEMIC_STREAMS))
    gens = [np.random.Generator(np.random.PCG64(c)) for c in children]
    return EpidemicStreams(*gens)


def policy_stream(policy_seed: int) -> np.random.Generator:
    """Stream used only for random tank selection (M2)."""
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(policy_seed)))
