"""Seed management (data/methods/model.md#16-random-number-and-seed-management).

Epidemic randomness is **event-keyed**: the uniform draw consulted for (process, day, agent) is a pure
function of (epidemic_seed, process, day, agent_id). It does not depend on how many other agents were
exposed that day or on what happened on earlier days, so two strategies run under the same epidemic seed
see identical draws for every agent-day they both consult. This is what makes the paired comparison
across strategies meaningful: a strategy that prevents one exposure does not shift every later draw.

Streams:
  initialisation  one Generator, used once to pick the initial case (main design only)
  movement, movement_destination, transmission, recovery  event-keyed uniforms
  policy          one Generator per policy seed, random tank selection only (M2)
"""

from __future__ import annotations

from typing import Protocol

import numpy as np

PROCESSES = ("movement", "movement_destination", "transmission", "recovery")
_INITIALISATION_KEY = 0
_PROCESS_KEY = {name: index + 1 for index, name in enumerate(PROCESSES)}


class DrawSource(Protocol):
    def uniform(self, process: str, day: int, agent_id: int) -> float:
        """Uniform[0, 1) draw for one process / day / agent. Deterministic for a fixed source."""


class MissingDrawError(KeyError):
    """A hand-trace table was asked for a draw it does not contain (see TableDraws)."""


class EventKeyedDraws:
    """Draws derived from ``epidemic_seed`` and keyed by (process, day, agent_id).

    Each (process, day) pair seeds its own PCG64 generator via ``SeedSequence(seed, spawn_key=(process,
    day))`` and yields one uniform per agent; agent ``a`` reads position ``a``. Only the arrays for the
    current and previous day are cached, so memory is O(n_agents) regardless of horizon.
    """

    def __init__(self, epidemic_seed: int, n_agents: int) -> None:
        self.epidemic_seed = int(epidemic_seed)
        self.n_agents = int(n_agents)
        self._cache: dict[tuple[str, int], np.ndarray] = {}

    def _day_array(self, process: str, day: int) -> np.ndarray:
        key = (process, day)
        arr = self._cache.get(key)
        if arr is None:
            seq = np.random.SeedSequence(self.epidemic_seed, spawn_key=(_PROCESS_KEY[process], day))
            arr = np.random.Generator(np.random.PCG64(seq)).random(self.n_agents)
            self._cache = {k: v for k, v in self._cache.items() if k[1] >= day - 1}
            self._cache[key] = arr
        return arr

    def uniform(self, process: str, day: int, agent_id: int) -> float:
        if not 0 <= agent_id < self.n_agents:
            raise IndexError(f"agent_id {agent_id} outside [0, {self.n_agents})")
        return float(self._day_array(process, day)[agent_id])


class TableDraws:
    """Explicit draws for hand traces (data/methods/validation.md#hand-trace).

    Consulting a draw that is not in the table raises ``MissingDrawError``. That is deliberate: a trace
    proves a draw was *not* consulted (for example no recovery draw for an agent infected today) by
    leaving it out of the table. ``consulted`` records every lookup in order.
    """

    def __init__(self, table: dict[tuple[str, int, int], float]) -> None:
        for key, value in table.items():
            process, _day, _agent = key
            if process not in PROCESSES:
                raise ValueError(f"unknown process {process!r} in draw table")
            if not 0.0 <= value < 1.0:
                raise ValueError(f"draw {key} = {value} is not in [0, 1)")
        self.table = dict(table)
        self.consulted: list[tuple[str, int, int]] = []

    def uniform(self, process: str, day: int, agent_id: int) -> float:
        key = (process, day, agent_id)
        if key not in self.table:
            raise MissingDrawError(key)
        self.consulted.append(key)
        return self.table[key]


def initialisation_stream(epidemic_seed: int) -> np.random.Generator:
    """Generator used only to choose the initial infected agent (data/methods/model.md#61-population-and-initial-infection)."""
    seq = np.random.SeedSequence(int(epidemic_seed), spawn_key=(_INITIALISATION_KEY,))
    return np.random.Generator(np.random.PCG64(seq))


def policy_stream(policy_seed: int) -> np.random.Generator:
    """Stream used only for random tank selection (M2)."""
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(int(policy_seed))))
