"""Compact, deterministic Checkpoint 2 demonstration.

This script demonstrates implemented model behaviour under one fixed seed block. It is a functionality
check, not an experiment and not evidence for the research hypotheses.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from turtlefarm import SimulationConfig
from turtlefarm.model import RunRecord, run_baseline


NETWORK_SEED = 0
EPIDEMIC_SEED = 7
POLICY_SEED = 3
TRANSFER_RATE = 0.02
BETA = 0.15
GAMMA = 0.10
RESPONSE_DELAY = 2
QUARANTINE_DURATION = 7
K = 2


def run_strategy(strategy: str) -> RunRecord:
    kwargs = dict(
        strategy=strategy,
        network_seed=NETWORK_SEED,
        epidemic_seed=EPIDEMIC_SEED,
        transfer_rate=TRANSFER_RATE,
        beta=BETA,
        gamma=GAMMA,
        response_delay=RESPONSE_DELAY,
        quarantine_duration=QUARANTINE_DURATION,
        k=K,
        max_days=365,
        label="checkpoint-2-functionality-demo",
    )
    if strategy == "random":
        kwargs["policy_seed"] = POLICY_SEED
    return run_baseline(SimulationConfig(**kwargs))


def intervention_window_counts(record: RunRecord) -> tuple[int, int]:
    start = RESPONSE_DELAY
    end = start + QUARANTINE_DURATION
    rows = [day for day in record.daily if start <= day.day < end]
    return (
        sum(day.accepted_transfers for day in rows),
        sum(day.blocked_transfers for day in rows),
    )


def selected_text(record: RunRecord) -> str:
    return "-" if not record.selected_tanks else ",".join(str(tank) for tank in record.selected_tanks)


def print_network_summary(records: dict[str, RunRecord]) -> None:
    network = records["none"].network
    assert network is not None
    assert len({record.network["network_hash"] for record in records.values()}) == 1
    print("CHECKPOINT 2 FUNCTIONALITY DEMONSTRATION")
    print("========================================")
    print(f"Network: seed={NETWORK_SEED}, hash={network['network_hash']}, "
          f"edges={network['metrics']['n_edges']}, inter-region edges={network['metrics']['n_inter_edges']}")
    print(f"Highest-betweenness tanks: {network['ranking'][:K]}")
    print(f"Paired epidemic seed: {EPIDEMIC_SEED}")
    print(
        f"Parameters: mu={TRANSFER_RATE}, beta={BETA}, gamma={GAMMA}, "
        f"delay={RESPONSE_DELAY}, duration={QUARANTINE_DURATION}, k={K}"
    )


def print_strategy_comparison(records: dict[str, RunRecord]) -> None:
    print("\nPAIRED STRATEGY COMPARISON")
    print("--------------------------")
    print(
        f"{'strategy':<13} {'selected':<10} {'start':>5} {'cost':>5} "
        f"{'accepted*':>10} {'blocked*':>9} {'affected':>9} {'attack':>8} {'status':>10}"
    )
    for strategy, record in records.items():
        accepted, blocked = intervention_window_counts(record)
        start = "-" if record.intervention_start_day is None else str(record.intervention_start_day)
        print(
            f"{strategy:<13} {selected_text(record):<10} {start:>5} {record.intervention_cost:>5} "
            f"{accepted:>10} {blocked:>9} {record.metrics['affected_tanks']:>9} "
            f"{record.metrics['final_attack_rate']:>7.1%} {record.status:>10}"
        )
    print(f"* accepted/blocked counts are restricted to days {RESPONSE_DELAY}-{RESPONSE_DELAY + QUARANTINE_DURATION - 1}.")


def print_targeted_timeline(record: RunRecord) -> None:
    print("\nBETWEENNESS QUARANTINE TIMELINE")
    print("--------------------------------")
    print(f"Selected tanks: {record.selected_tanks}; equal-budget cost: {record.intervention_cost} tank-days")
    for day_number in range(0, RESPONSE_DELAY + QUARANTINE_DURATION + 1):
        day = record.daily[day_number]
        states = {tank["tank_id"]: tank["management_state"] for tank in day.tanks
                  if tank["tank_id"] in record.selected_tanks}
        print(
            f"day {day.day:>2}: {states}; accepted={day.accepted_transfers:>2}; "
            f"blocked={day.blocked_transfers:>2}"
        )


def verify_demo(records: dict[str, RunRecord]) -> None:
    assert all(record.status == "completed" for record in records.values())
    assert records["none"].intervention_cost == 0
    assert records["random"].intervention_cost == records["betweenness"].intervention_cost == K * QUARANTINE_DURATION
    assert records["betweenness"].selected_tanks == records["betweenness"].network["ranking"][:K]
    assert all(len(records[strategy].selected_tanks) == K for strategy in ("random", "betweenness"))


def main() -> None:
    records = {strategy: run_strategy(strategy) for strategy in ("none", "random", "betweenness")}
    verify_demo(records)
    print_network_summary(records)
    print_strategy_comparison(records)
    print_targeted_timeline(records["betweenness"])
    print("\nInterpretation: this run proves that network movement, policy selection, quarantine timing,")
    print("movement blocking, equal budgets and result recording work together. It is not a scientific result.")


if __name__ == "__main__":
    main()
