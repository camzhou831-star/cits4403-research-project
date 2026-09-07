"""Discrete-time stochastic ABM: M1 baseline.

Daily order (model-specification section 13):
  1 management update  2 movement  3 transmission snapshot  4 transmission draws
  5 recovery draws     6 synchronous commit  7 record  8 stopping check

In the M1 baseline the movement stage is a no-op (transfer_rate == 0) and the management stage never
activates a quarantine (strategy == "none"). Both stages exist so that M2 slots in without reordering.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from typing import Any

from turtlefarm.config import SimulationConfig
from turtlefarm.entities import Agent, Tank, S, I, R, OPEN
from turtlefarm.rng import epidemic_streams

STATUS_COMPLETED = "completed"
STATUS_CENSORED = "censored_max_days"
STATUS_FAILED = "failed"


class InvariantError(RuntimeError):
    """A required invariant (validation-plan V001-V012) was violated during a run."""


@dataclass
class DailyRecord:
    day: int
    S: int
    I: int
    R: int
    new_infections: int
    recoveries: int
    attempted_transfers: int
    accepted_transfers: int
    blocked_transfers: int
    affected_tanks_now: int  # tanks with at least one I agent at end of day
    affected_tanks_ever: int
    tanks: list[dict[str, Any]]  # per-tank occupancy / S / I / R / management_state


@dataclass
class RunRecord:
    config: dict[str, Any]
    status: str
    stop_reason: str
    error: str | None
    seeds: dict[str, int | None]
    initial_infected_agents: list[int]
    initial_infected_tanks: list[int]
    selected_tanks: list[int]
    intervention_start_day: int | None
    intervention_cost: int
    daily: list[DailyRecord]
    metrics: dict[str, Any]
    code_commit: str | None
    transitions: list[tuple[int, int, str, str]] = field(default_factory=list)  # (day, agent, from, to)


def _git_commit() -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=5, check=False
        )
        return out.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


class Simulation:
    def __init__(self, config: SimulationConfig, record_transitions: bool = False) -> None:
        self.cfg = config
        self.streams = epidemic_streams(config.epidemic_seed)
        self.record_transitions = record_transitions
        self.day = 0
        self.agents: list[Agent] = []
        self.tanks: list[Tank] = []
        self.ever_affected: set[int] = set()
        self.daily: list[DailyRecord] = []
        self.transitions: list[tuple[int, int, str, str]] = []
        self.initial_infected_agents: list[int] = []
        self._initialise()

    # ------------------------------------------------------------------ initialisation (section 6)
    def _initialise(self) -> None:
        cfg = self.cfg
        per_region = cfg.tanks_per_region
        self.tanks = [
            Tank(tank_id=t, region_id=t // per_region, capacity=cfg.capacity) for t in range(cfg.n_tanks)
        ]
        # Fixed initial placement: agent a starts in tank a // initial_per_tank (10 per tank).
        self.agents = [Agent(agent_id=a, tank_id=a // cfg.initial_per_tank) for a in range(cfg.n_agents)]
        for ag in self.agents:
            self.tanks[ag.tank_id].members.add(ag.agent_id)

        # Initial infected chosen uniformly from all agents with the initialisation stream.
        chosen = self.streams.initialisation.choice(cfg.n_agents, size=cfg.initial_infected, replace=False)
        self.initial_infected_agents = sorted(int(x) for x in chosen)
        for a in self.initial_infected_agents:
            ag = self.agents[a]
            ag.disease_state = I
            ag.ever_infected = True
            ag.state_entered_day = 0
            self.ever_affected.add(ag.tank_id)

        self._check_invariants()
        self._record(new_infections=0, recoveries=0, attempted=0, accepted=0, blocked=0)

    # ------------------------------------------------------------------ daily stages
    def _management_update(self) -> None:
        """Stage 1. Baseline: strategy 'none' never selects tanks. Releases are generic."""
        for tank in self.tanks:
            if tank.quarantine_end_day is not None and self.day >= tank.quarantine_end_day:
                tank.management_state = OPEN
                tank.quarantine_start_day = None
                tank.quarantine_end_day = None

    def _movement_stage(self) -> tuple[int, int, int]:
        """Stage 2. Baseline: transfer_rate == 0, so no agent attempts to move."""
        return 0, 0, 0  # attempted, accepted, blocked

    def _transmission_and_recovery(self) -> tuple[list[int], list[int]]:
        """Stages 3-5. Draws are made against a frozen snapshot; nothing is committed here."""
        cfg = self.cfg
        # Stage 3: snapshot of infectious counts per tank and the set of agents infectious today.
        infectious_by_tank = [0] * cfg.n_tanks
        infectious_today: list[int] = []
        for ag in self.agents:
            if ag.disease_state == I:
                infectious_by_tank[ag.tank_id] += 1
                infectious_today.append(ag.agent_id)

        # Stage 4: independent per-agent infection chance, P = 1 - (1 - beta)^I_j.
        pending_infections: list[int] = []
        for ag in self.agents:
            if ag.disease_state != S:
                continue
            i_j = infectious_by_tank[ag.tank_id]
            if i_j == 0:
                continue
            p = 1.0 - (1.0 - cfg.beta) ** i_j
            if self.streams.transmission.random() < p:
                pending_infections.append(ag.agent_id)

        # Stage 5: recovery only for agents already infectious at the snapshot.
        pending_recoveries: list[int] = []
        for a in infectious_today:
            if self.streams.recovery.random() < cfg.gamma:
                pending_recoveries.append(a)

        return pending_infections, pending_recoveries

    def _commit(self, infections: list[int], recoveries: list[int]) -> None:
        """Stage 6: synchronous commit. An agent cannot be in both lists by construction."""
        for a in recoveries:
            ag = self.agents[a]
            if ag.disease_state != I:
                raise InvariantError(f"day {self.day}: recovery drawn for non-infectious agent {a}")
            self._transition(ag, R)
        for a in infections:
            ag = self.agents[a]
            if ag.disease_state != S:
                raise InvariantError(f"day {self.day}: infection drawn for non-susceptible agent {a}")
            self._transition(ag, I)
            ag.ever_infected = True
            self.ever_affected.add(ag.tank_id)

    def _transition(self, ag: Agent, new_state: str) -> None:
        if self.record_transitions:
            self.transitions.append((self.day, ag.agent_id, ag.disease_state, new_state))
        ag.disease_state = new_state
        ag.state_entered_day = self.day

    # ------------------------------------------------------------------ recording and checks
    def _counts(self) -> tuple[int, int, int]:
        s = i = r = 0
        for ag in self.agents:
            if ag.disease_state == S:
                s += 1
            elif ag.disease_state == I:
                i += 1
            else:
                r += 1
        return s, i, r

    def _record(self, *, new_infections: int, recoveries: int, attempted: int, accepted: int, blocked: int) -> None:
        s, i, r = self._counts()
        tank_rows = []
        affected_now = 0
        for tank in self.tanks:
            ts = ti = tr = 0
            for a in tank.members:
                st = self.agents[a].disease_state
                if st == S:
                    ts += 1
                elif st == I:
                    ti += 1
                else:
                    tr += 1
            if ti > 0:
                affected_now += 1
            tank_rows.append(
                {
                    "tank_id": tank.tank_id,
                    "region_id": tank.region_id,
                    "occupancy": tank.occupancy,
                    "S": ts,
                    "I": ti,
                    "R": tr,
                    "management_state": tank.management_state,
                }
            )
        self.daily.append(
            DailyRecord(
                day=self.day,
                S=s,
                I=i,
                R=r,
                new_infections=new_infections,
                recoveries=recoveries,
                attempted_transfers=attempted,
                accepted_transfers=accepted,
                blocked_transfers=blocked,
                affected_tanks_now=affected_now,
                affected_tanks_ever=len(self.ever_affected),
                tanks=tank_rows,
            )
        )

    def _check_invariants(self) -> None:
        cfg = self.cfg
        if len(self.agents) != cfg.n_agents:  # V001
            raise InvariantError(f"agent count {len(self.agents)} != {cfg.n_agents}")
        seen: set[int] = set()
        for tank in self.tanks:
            if tank.occupancy > tank.capacity:  # V006
                raise InvariantError(f"tank {tank.tank_id} occupancy {tank.occupancy} > capacity {tank.capacity}")
            for a in tank.members:
                if a in seen:  # V002
                    raise InvariantError(f"agent {a} listed in more than one tank")
                seen.add(a)
                if self.agents[a].tank_id != tank.tank_id:
                    raise InvariantError(f"agent {a} tank_id mismatch")
        if len(seen) != cfg.n_agents:
            raise InvariantError("some agents are not in any tank")
        s, i, r = self._counts()
        if s + i + r != cfg.n_agents:  # V004 (V003 is enforced by _transition/_commit)
            raise InvariantError(f"S+I+R = {s + i + r} != {cfg.n_agents}")

    # ------------------------------------------------------------------ run loop
    def step(self) -> None:
        """Advance from state at `day` to state at `day + 1`."""
        self.day += 1
        self._management_update()
        attempted, accepted, blocked = self._movement_stage()
        infections, recoveries = self._transmission_and_recovery()
        self._commit(infections, recoveries)
        self._check_invariants()
        self._record(
            new_infections=len(infections),
            recoveries=len(recoveries),
            attempted=attempted,
            accepted=accepted,
            blocked=blocked,
        )

    def run(self) -> RunRecord:
        cfg = self.cfg
        status, stop_reason, error = STATUS_COMPLETED, "", None
        try:
            if self.daily[-1].I == 0:
                stop_reason = "no infectious agents at t=0"
            else:
                while True:
                    self.step()
                    if self.daily[-1].I == 0:
                        stop_reason = f"extinction on day {self.day}"
                        break
                    if self.day >= cfg.max_days:
                        status, stop_reason = STATUS_CENSORED, f"infection present at max_days={cfg.max_days}"
                        break
        except InvariantError as exc:
            status, stop_reason, error = STATUS_FAILED, "invariant failure", str(exc)

        return RunRecord(
            config=cfg.to_dict(),
            status=status,
            stop_reason=stop_reason,
            error=error,
            seeds={
                "network_seed": cfg.network_seed,
                "epidemic_seed": cfg.epidemic_seed,
                "policy_seed": cfg.policy_seed,
            },
            initial_infected_agents=list(self.initial_infected_agents),
            initial_infected_tanks=sorted({self.agents[a].tank_id for a in self.initial_infected_agents}),
            selected_tanks=[],
            intervention_start_day=None,
            intervention_cost=0,
            daily=list(self.daily),
            metrics=compute_metrics(self.agents, self.daily, status, cfg),
            code_commit=_git_commit(),
            transitions=list(self.transitions),
        )


def compute_metrics(agents: list[Agent], daily: list[DailyRecord], status: str, cfg: SimulationConfig) -> dict[str, Any]:
    """Metrics of model-specification section 15.3. Censored runs get time_to_extinction = None."""
    ever = sum(1 for ag in agents if ag.ever_infected)
    peak = max(d.I for d in daily)
    time_to_peak = next(d.day for d in daily if d.I == peak)
    extinction = next((d.day for d in daily if d.I == 0), None)
    if status != STATUS_COMPLETED:
        extinction = None
    return {
        "final_attack_rate": ever / cfg.n_agents,
        "ever_infected": ever,
        "affected_tanks": daily[-1].affected_tanks_ever,
        "peak_infected": peak,
        "time_to_peak": time_to_peak,
        "time_to_extinction": extinction,
        "days_simulated": daily[-1].day,
        "intervention_cost": 0 if cfg.strategy == "none" else cfg.k * cfg.quarantine_duration,
    }


def run_baseline(config: SimulationConfig, record_transitions: bool = False) -> RunRecord:
    return Simulation(config, record_transitions=record_transitions).run()
