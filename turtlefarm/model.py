"""Discrete-time stochastic ABM with network-constrained movement.

Daily order (model-specification section 13):
  1 management update  2 movement  3 transmission snapshot  4 transmission draws
  5 recovery draws     6 synchronous commit  7 record  8 stopping check

The management stage does not yet activate quarantine (strategy == "none"). It remains a separate stage
so that intervention logic can be added without changing the frozen daily update order.
"""

from __future__ import annotations

import subprocess
import traceback
from dataclasses import dataclass, field
from typing import Any

from turtlefarm.config import ConfigError, SimulationConfig
from turtlefarm.entities import Agent, Tank, S, I, R, OPEN, DISEASE_STATES
from turtlefarm.network import TransferNetwork, generate_network
from turtlefarm.rng import DrawSource, EventKeyedDraws, initialisation_stream
from turtlefarm.scenario import Layout

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
    network: dict[str, Any] | None = None  # spec 15.2: attempt index, adjacency, centralities, hash
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
    """One run. Construct, then call ``run()``; initialisation happens inside ``run()`` so that a failure
    at any point yields a ``failed`` RunRecord instead of an exception (model-specification section 14).

    ``layout`` builds an explicit small scenario (config ``design="scenario"``) and ``draws`` replaces the
    seed-derived event-keyed draws, e.g. with a ``TableDraws`` hand-trace table. Both are validation-only.
    """

    def __init__(
        self,
        config: SimulationConfig,
        record_transitions: bool = False,
        *,
        layout: Layout | None = None,
        draws: DrawSource | None = None,
    ) -> None:
        if (config.design == "scenario") != (layout is not None):
            raise ConfigError('design="scenario" requires a Layout, and a Layout requires design="scenario"')
        if layout is not None and (layout.n_agents != config.n_agents or layout.n_tanks != config.n_tanks):
            raise ConfigError(
                f"layout has {layout.n_agents} agents / {layout.n_tanks} tanks but config says "
                f"{config.n_agents} / {config.n_tanks}"
            )
        self.cfg = config
        self.layout = layout
        self.n_agents = config.n_agents
        self.n_tanks = config.n_tanks
        self.draws: DrawSource = draws if draws is not None else EventKeyedDraws(config.epidemic_seed, self.n_agents)
        self.record_transitions = record_transitions
        self.day = 0
        self.agents: list[Agent] = []
        self.tanks: list[Tank] = []
        self.ever_affected: set[int] = set()
        self.daily: list[DailyRecord] = []
        self.transitions: list[tuple[int, int, str, str]] = []
        self.initial_infected_agents: list[int] = []
        self.initial_infected_tanks: list[int] = []
        self.network: TransferNetwork | None = None
        self.initialised = False

    # ------------------------------------------------------------------ initialisation (section 6)
    def _initialise(self) -> None:
        if self.initialised:
            return
        cfg = self.cfg
        if self.layout is None:
            # Pre-outbreak transfer network (spec section 3). Generated before any epidemic draw and never
            # modified afterwards; M1 does not move agents but records it for provenance (section 15.2).
            self.network = generate_network(
                network_seed=cfg.network_seed,
                p_in=cfg.p_in,
                p_out=cfg.p_out,
                n_tanks=cfg.n_tanks,
                n_regions=cfg.n_regions,
                max_attempts=cfg.network_max_attempts,
            )
            per_region = cfg.tanks_per_region
            self.tanks = [
                Tank(tank_id=t, region_id=t // per_region, capacity=cfg.capacity) for t in range(cfg.n_tanks)
            ]
            # Fixed initial placement: agent a starts in tank a // initial_per_tank (10 per tank).
            self.agents = [Agent(agent_id=a, tank_id=a // cfg.initial_per_tank) for a in range(cfg.n_agents)]
            # Initial infected chosen uniformly from all agents with the initialisation stream.
            chosen = initialisation_stream(cfg.epidemic_seed).choice(
                cfg.n_agents, size=cfg.initial_infected, replace=False
            )
            self.initial_infected_agents = sorted(int(x) for x in chosen)
        else:
            self.tanks = [Tank(tank_id=t.tank_id, region_id=t.region_id, capacity=t.capacity) for t in self.layout.tanks]
            self.agents = [Agent(agent_id=a.agent_id, tank_id=a.tank_id) for a in self.layout.agents]
            for spec, ag in zip(self.layout.agents, self.agents):
                if spec.disease_state == R:
                    ag.disease_state = R
                    ag.ever_infected = True
            self.initial_infected_agents = [a.agent_id for a in self.layout.agents if a.disease_state == I]

        for ag in self.agents:
            self.tanks[ag.tank_id].members.add(ag.agent_id)
        for a in self.initial_infected_agents:
            ag = self.agents[a]
            ag.disease_state = I
            ag.ever_infected = True
            ag.state_entered_day = 0
            self.ever_affected.add(ag.tank_id)
        self.initial_infected_tanks = sorted(self.ever_affected)

        self.initialised = True
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
        """Stage 2: randomized asynchronous movement over the fixed transfer network.

        The event-keyed ``movement`` draw serves as both the per-agent random priority and the
        probability draw for attempting movement. Reusing that keyed value avoids an additional random
        stream while keeping every agent-day stable across paired strategies. A successful move updates
        both tank memberships immediately, so later agents observe current capacity.
        """
        if self.cfg.transfer_rate == 0.0:
            return 0, 0, 0
        if self.network is None:
            raise InvariantError("non-zero transfer_rate requires a transfer network")

        movement_draws = {
            ag.agent_id: self.draws.uniform("movement", self.day, ag.agent_id) for ag in self.agents
        }
        processing_order = sorted(movement_draws, key=lambda agent_id: (movement_draws[agent_id], agent_id))

        attempted = accepted = blocked = 0
        for agent_id in processing_order:
            if movement_draws[agent_id] >= self.cfg.transfer_rate:
                continue

            attempted += 1
            agent = self.agents[agent_id]
            origin = self.tanks[agent.tank_id]
            if origin.management_state != OPEN:
                blocked += 1
                continue

            destinations = [
                tank_id
                for tank_id in self.network.neighbours(origin.tank_id)
                if self.tanks[tank_id].management_state == OPEN
                and self.tanks[tank_id].occupancy < self.tanks[tank_id].capacity
            ]
            if not destinations:
                blocked += 1
                continue

            destination_draw = self.draws.uniform("movement_destination", self.day, agent_id)
            destination_id = destinations[int(destination_draw * len(destinations))]
            destination = self.tanks[destination_id]

            origin.members.remove(agent_id)
            destination.members.add(agent_id)
            agent.tank_id = destination_id
            if agent.disease_state == I:
                self.ever_affected.add(destination_id)
            accepted += 1

        return attempted, accepted, blocked

    def _transmission_and_recovery(self) -> tuple[list[int], list[int]]:
        """Stages 3-5. Draws are made against a frozen snapshot; nothing is committed here."""
        cfg = self.cfg
        # Stage 3: snapshot of infectious counts per tank and the set of agents infectious today.
        infectious_by_tank = [0] * self.n_tanks
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
            if self.draws.uniform("transmission", self.day, ag.agent_id) < p:
                pending_infections.append(ag.agent_id)

        # Stage 5: recovery only for agents already infectious at the snapshot. Agents infected today are
        # not in ``infectious_today``, so no recovery draw is consulted for them.
        pending_recoveries: list[int] = []
        for a in infectious_today:
            if self.draws.uniform("recovery", self.day, a) < cfg.gamma:
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

    _ALLOWED_TRANSITIONS = frozenset({(S, I), (I, R)})

    def _transition(self, ag: Agent, new_state: str) -> None:
        """Only S -> I and I -> R exist (spec section 5). In particular R -> I is impossible (V005)."""
        if (ag.disease_state, new_state) not in self._ALLOWED_TRANSITIONS:
            raise InvariantError(
                f"day {self.day}: illegal transition {ag.disease_state} -> {new_state} for agent {ag.agent_id}"
            )
        if self.record_transitions:
            self.transitions.append((self.day, ag.agent_id, ag.disease_state, new_state))
        ag.disease_state = new_state
        ag.state_entered_day = self.day

    # ------------------------------------------------------------------ recording and checks
    def _counts(self) -> tuple[int, int, int]:
        s = i = r = 0
        for ag in self.agents:
            st = ag.disease_state
            if st == S:
                s += 1
            elif st == I:
                i += 1
            elif st == R:
                r += 1
            else:  # V003: never fold an unknown state into R
                raise InvariantError(f"agent {ag.agent_id} has disease_state {st!r}, expected one of {DISEASE_STATES}")
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
        n = self.n_agents
        if len(self.agents) != n:  # V001
            raise InvariantError(f"agent count {len(self.agents)} != {n}")
        for ag in self.agents:  # V003 / V005 per-agent domain checks
            if ag.disease_state not in DISEASE_STATES:
                raise InvariantError(f"agent {ag.agent_id} has disease_state {ag.disease_state!r}")
            if ag.disease_state != S and not ag.ever_infected:
                raise InvariantError(f"agent {ag.agent_id} is {ag.disease_state} but ever_infected is False")
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
        if len(seen) != n:
            raise InvariantError("some agents are not in any tank")
        s, i, r = self._counts()  # raises on unknown state (V003)
        if s + i + r != n:  # V004
            raise InvariantError(f"S+I+R = {s + i + r} != {n}")

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
        """Run to extinction, horizon or failure. Every run ends with an explicit status and stop reason
        (V012). Any exception other than KeyboardInterrupt/SystemExit becomes a ``failed`` record that
        keeps the configuration, seeds, error type and traceback (spec section 14/15)."""
        cfg = self.cfg
        status, stop_reason, error = STATUS_COMPLETED, "", None
        try:
            self._initialise()
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
            status, stop_reason, error = STATUS_FAILED, "invariant failure", f"InvariantError: {exc}"
        except Exception as exc:  # noqa: BLE001 - deliberate: runs must not die without a record
            status, stop_reason = STATUS_FAILED, "runtime error"
            error = f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"

        metrics = compute_metrics(self.agents, self.daily, status) if self.daily else {}
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
            initial_infected_tanks=list(self.initial_infected_tanks),
            selected_tanks=[],
            intervention_start_day=None,
            intervention_cost=0,
            daily=list(self.daily),
            metrics=metrics,
            code_commit=_git_commit(),
            transitions=list(self.transitions),
            network=self.network.to_dict() if self.network is not None else None,
        )


def compute_metrics(agents: list[Agent], daily: list[DailyRecord], status: str) -> dict[str, Any]:
    """Metrics of model-specification section 15.3. Censored runs get time_to_extinction = None."""
    ever = sum(1 for ag in agents if ag.ever_infected)
    peak = max(d.I for d in daily)
    time_to_peak = next(d.day for d in daily if d.I == peak)
    extinction = next((d.day for d in daily if d.I == 0), None)
    if status != STATUS_COMPLETED:
        extinction = None
    return {
        "final_attack_rate": ever / len(agents),
        "ever_infected": ever,
        "affected_tanks": daily[-1].affected_tanks_ever,
        "peak_infected": peak,
        "time_to_peak": time_to_peak,
        "time_to_extinction": extinction,
        "days_simulated": daily[-1].day,
        "intervention_cost": 0,  # M1: strategy is always "none"
    }


def run_baseline(
    config: SimulationConfig,
    record_transitions: bool = False,
    *,
    layout: Layout | None = None,
    draws: DrawSource | None = None,
) -> RunRecord:
    return Simulation(config, record_transitions=record_transitions, layout=layout, draws=draws).run()
