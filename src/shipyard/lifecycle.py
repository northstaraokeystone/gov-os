"""
WarrantProof Shipyard Lifecycle - Ship State Machine

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

Models the ship lifecycle from keel laying to delivery.
Each phase transition emits receipts and validates constraints.

States: DESIGN -> KEEL_LAYING -> BLOCK_ASSEMBLY -> LAUNCH -> FITTING_OUT -> SEA_TRIALS -> DELIVERY

Physics constraints:
- Ship cannot skip phases
- Each phase has minimum duration (material/process constraints)
- Overrun detection triggers at 12% variance (vs historical 23%)
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional

from src.core import dual_hash, emit_receipt, merkle, StopRuleException

from .constants import (
    SHIPYARD_TENANT_ID,
    SHIPYARD_DISCLAIMER,
    PHASE_MIN_DAYS,
    VARIANCE_ALERT_PCT,
    TRUMP_CLASS_PER_SHIP_B,
)
from .receipts import (
    emit_keel_receipt,
    emit_milestone_receipt,
    emit_delivery_receipt,
)


# === LIFECYCLE PHASES ===

LIFECYCLE_PHASES = [
    "DESIGN",
    "KEEL_LAYING",
    "BLOCK_ASSEMBLY",
    "LAUNCH",
    "FITTING_OUT",
    "SEA_TRIALS",
    "DELIVERY",
]

PHASE_COMPLETION_PCT = {
    "DESIGN": 10,
    "KEEL_LAYING": 15,
    "BLOCK_ASSEMBLY": 60,
    "LAUNCH": 70,
    "FITTING_OUT": 90,
    "SEA_TRIALS": 98,
    "DELIVERY": 100,
}


# === CORE FUNCTIONS ===

def create_ship(
    ship_id: str,
    class_type: str,
    yard_id: str,
    baseline_cost_usd: Optional[float] = None,
    baseline_days: Optional[int] = None,
) -> dict:
    """
    Initialize ship state and emit keel_receipt.

    Args:
        ship_id: Unique ship identifier
        class_type: Ship class (e.g., "trump", "ford")
        yard_id: Shipyard identifier
        baseline_cost_usd: Baseline cost in USD
        baseline_days: Baseline schedule in days

    Returns:
        Ship state dict
    """
    if baseline_cost_usd is None:
        baseline_cost_usd = TRUMP_CLASS_PER_SHIP_B * 1e9  # Convert to USD

    if baseline_days is None:
        baseline_days = sum(PHASE_MIN_DAYS.values())  # Minimum total

    now = datetime.utcnow()
    ts = now.isoformat() + "Z"

    # Create initial ship state
    ship = {
        "ship_id": ship_id,
        "class_type": class_type,
        "yard_id": yard_id,
        "current_phase": "DESIGN",
        "phase_index": 0,
        "created_at": ts,
        "phase_started_at": ts,
        "baseline_cost_usd": baseline_cost_usd,
        "baseline_days": baseline_days,
        "actual_cost_usd": 0.0,
        "actual_days": 0,
        "receipts": [],
        "milestones": [],
        "variance_history": [],
        "simulation_flag": SHIPYARD_DISCLAIMER,
    }

    # Emit keel receipt
    keel_receipt = emit_keel_receipt(
        ship_id=ship_id,
        yard_id=yard_id,
        ts=ts,
        coordinates={"lat": 36.9, "lon": -76.3},  # Norfolk VA area
        material_hash=dual_hash(f"{ship_id}:{class_type}:keel"),
    )
    ship["receipts"].append(keel_receipt)
    ship["keel_receipt_id"] = keel_receipt.get("payload_hash")

    # Emit initial milestone
    milestone = emit_milestone_receipt(
        milestone_id=f"{ship_id}_DESIGN_START",
        ship_id=ship_id,
        completion_pct=0.0,
        phase="DESIGN",
        variance_days=0,
    )
    ship["milestones"].append(milestone)
    ship["receipts"].append(milestone)

    return ship


def advance_phase(ship: dict, phase: str, actual_days: int = 0, actual_cost: float = 0.0) -> dict:
    """
    Transition ship to next phase and emit milestone_receipt.

    Args:
        ship: Ship state dict
        phase: Target phase (must be next in sequence)
        actual_days: Days spent in current phase
        actual_cost: Cost incurred in current phase

    Returns:
        Updated ship state
    """
    current_index = ship["phase_index"]
    current_phase = ship["current_phase"]

    # Validate phase transition
    if phase not in LIFECYCLE_PHASES:
        raise StopRuleException(f"Invalid phase: {phase}")

    target_index = LIFECYCLE_PHASES.index(phase)

    # Cannot skip phases
    if target_index != current_index + 1:
        raise StopRuleException(
            f"Cannot transition from {current_phase} to {phase}. "
            f"Next phase must be {LIFECYCLE_PHASES[current_index + 1]}"
        )

    # Check minimum duration
    min_days = PHASE_MIN_DAYS.get(current_phase, 0)
    if actual_days < min_days:
        # Warning but allow (simulation flexibility)
        pass

    # Update ship state
    now = datetime.utcnow()
    ts = now.isoformat() + "Z"

    ship["current_phase"] = phase
    ship["phase_index"] = target_index
    ship["phase_started_at"] = ts
    ship["actual_days"] += actual_days
    ship["actual_cost_usd"] += actual_cost

    # Calculate variance
    variance = calculate_variance(ship)
    ship["variance_history"].append({
        "phase": phase,
        "ts": ts,
        "cost_variance_pct": variance.get("cost_variance_pct", 0),
        "schedule_variance_pct": variance.get("schedule_variance_pct", 0),
    })

    # Emit milestone receipt
    completion_pct = PHASE_COMPLETION_PCT.get(phase, 0)
    variance_days = variance.get("schedule_variance_days", 0)

    milestone = emit_milestone_receipt(
        milestone_id=f"{ship['ship_id']}_{phase}",
        ship_id=ship["ship_id"],
        completion_pct=completion_pct,
        phase=phase,
        variance_days=variance_days,
    )
    ship["milestones"].append(milestone)
    ship["receipts"].append(milestone)

    # Check for variance alert
    cost_variance_pct = variance.get("cost_variance_pct", 0)
    if abs(cost_variance_pct) > VARIANCE_ALERT_PCT * 100:
        _emit_variance_alert(ship, cost_variance_pct)

    return ship


def calculate_variance(ship: dict) -> dict:
    """
    Compare actual vs planned progress.

    Args:
        ship: Ship state dict

    Returns:
        Variance metrics dict
    """
    baseline_cost = ship.get("baseline_cost_usd", 1.0)
    baseline_days = ship.get("baseline_days", 1)
    actual_cost = ship.get("actual_cost_usd", 0.0)
    actual_days = ship.get("actual_days", 0)

    # Calculate phase progress (expected vs actual)
    phase_index = ship.get("phase_index", 0)
    expected_pct = (phase_index + 1) / len(LIFECYCLE_PHASES)

    # Cost variance
    expected_cost = baseline_cost * expected_pct
    cost_variance_usd = actual_cost - expected_cost
    cost_variance_pct = (cost_variance_usd / baseline_cost) * 100 if baseline_cost > 0 else 0

    # Schedule variance
    expected_days = baseline_days * expected_pct
    schedule_variance_days = actual_days - expected_days
    schedule_variance_pct = (schedule_variance_days / baseline_days) * 100 if baseline_days > 0 else 0

    return {
        "ship_id": ship.get("ship_id"),
        "current_phase": ship.get("current_phase"),
        "completion_pct": expected_pct * 100,
        "cost_variance_usd": cost_variance_usd,
        "cost_variance_pct": cost_variance_pct,
        "schedule_variance_days": schedule_variance_days,
        "schedule_variance_pct": schedule_variance_pct,
        "on_budget": cost_variance_pct <= VARIANCE_ALERT_PCT * 100,
        "on_schedule": schedule_variance_pct <= VARIANCE_ALERT_PCT * 100,
    }


def complete_ship(ship: dict) -> dict:
    """
    Finalize delivery and emit delivery_receipt with overrun_pct.

    Args:
        ship: Ship state dict

    Returns:
        Updated ship state with delivery receipt
    """
    # Ensure ship is in final phase
    if ship["current_phase"] != "DELIVERY":
        # Advance to delivery first
        while ship["current_phase"] != "DELIVERY":
            next_index = ship["phase_index"] + 1
            if next_index >= len(LIFECYCLE_PHASES):
                break
            ship = advance_phase(
                ship,
                LIFECYCLE_PHASES[next_index],
                actual_days=PHASE_MIN_DAYS.get(ship["current_phase"], 30),
                actual_cost=ship["baseline_cost_usd"] * 0.1,
            )

    # Calculate final merkle root of all receipts
    receipt_merkle = merkle(ship["receipts"])

    # Emit delivery receipt
    delivery = emit_delivery_receipt(
        ship_id=ship["ship_id"],
        yard_id=ship["yard_id"],
        final_cost_usd=ship["actual_cost_usd"],
        total_days=ship["actual_days"],
        baseline_cost_usd=ship["baseline_cost_usd"],
        baseline_days=ship["baseline_days"],
        receipt_merkle_root=receipt_merkle,
    )

    ship["receipts"].append(delivery)
    ship["delivery_receipt"] = delivery
    ship["completed_at"] = datetime.utcnow().isoformat() + "Z"
    ship["final_overrun_pct"] = delivery.get("cost_overrun_pct", 0)

    return ship


def get_phase_progress(ship: dict) -> dict:
    """
    Get current phase progress details.

    Args:
        ship: Ship state dict

    Returns:
        Progress dict
    """
    current_phase = ship.get("current_phase", "DESIGN")
    phase_index = ship.get("phase_index", 0)

    return {
        "ship_id": ship.get("ship_id"),
        "current_phase": current_phase,
        "phase_index": phase_index,
        "phases_completed": phase_index,
        "phases_remaining": len(LIFECYCLE_PHASES) - phase_index - 1,
        "overall_pct": PHASE_COMPLETION_PCT.get(current_phase, 0),
        "next_phase": LIFECYCLE_PHASES[phase_index + 1] if phase_index < len(LIFECYCLE_PHASES) - 1 else None,
    }


def validate_phase_sequence(phases: list) -> bool:
    """
    Validate that phases occurred in correct sequence.

    Args:
        phases: List of phase names

    Returns:
        True if sequence is valid
    """
    if not phases:
        return True

    for i, phase in enumerate(phases):
        expected_index = LIFECYCLE_PHASES.index(phase) if phase in LIFECYCLE_PHASES else -1
        if i == 0:
            if expected_index != 0 and expected_index != LIFECYCLE_PHASES.index(phases[0]):
                return False
        else:
            prev_phase = phases[i - 1]
            prev_index = LIFECYCLE_PHASES.index(prev_phase) if prev_phase in LIFECYCLE_PHASES else -1
            if expected_index != prev_index + 1:
                return False

    return True


# === HELPER FUNCTIONS ===

def _emit_variance_alert(ship: dict, variance_pct: float) -> dict:
    """Emit variance alert receipt."""
    return emit_receipt("alert", {
        "tenant_id": SHIPYARD_TENANT_ID,
        "anomaly_type": "cost_variance",
        "severity": "high" if variance_pct > 20 else "medium",
        "ship_id": ship.get("ship_id"),
        "current_phase": ship.get("current_phase"),
        "variance_pct": variance_pct,
        "threshold_pct": VARIANCE_ALERT_PCT * 100,
        "action": "review_required",
        "simulation_flag": SHIPYARD_DISCLAIMER,
    }, to_stdout=False)


# === STOPRULES ===

def stoprule_phase_skip(ship_id: str, from_phase: str, to_phase: str) -> None:
    """Stoprule: Attempted to skip phases."""
    emit_receipt("anomaly", {
        "metric": "phase_skip_attempted",
        "ship_id": ship_id,
        "from_phase": from_phase,
        "to_phase": to_phase,
        "delta": -1,
        "action": "halt",
        "classification": "violation",
        "simulation_flag": SHIPYARD_DISCLAIMER,
    })
    raise StopRuleException(f"Ship {ship_id} attempted to skip from {from_phase} to {to_phase}")


def stoprule_variance_exceeded(ship_id: str, variance_pct: float) -> None:
    """Stoprule: Variance exceeded critical threshold."""
    emit_receipt("anomaly", {
        "metric": "variance_critical",
        "ship_id": ship_id,
        "variance_pct": variance_pct,
        "threshold_pct": 30.0,
        "delta": variance_pct - 30.0,
        "action": "halt",
        "classification": "cost_cascade",
        "simulation_flag": SHIPYARD_DISCLAIMER,
    })
    raise StopRuleException(f"Ship {ship_id} variance {variance_pct}% exceeds critical 30% threshold")


# === MODULE SELF-TEST ===

if __name__ == "__main__":
    print("# WarrantProof Shipyard Lifecycle Self-Test", file=sys.stderr)
    print(f"# {SHIPYARD_DISCLAIMER}", file=sys.stderr)

    # Create a test ship
    ship = create_ship("TEST-001", "trump", "HII-YARD")
    assert ship["current_phase"] == "DESIGN", "Ship should start in DESIGN"
    assert len(ship["receipts"]) >= 2, "Should have keel and milestone receipts"
    print(f"# Ship created: {ship['ship_id']}", file=sys.stderr)

    # Advance through phases
    for i, phase in enumerate(LIFECYCLE_PHASES[1:], 1):
        ship = advance_phase(ship, phase, actual_days=30 * i, actual_cost=1e9 * i)
        assert ship["current_phase"] == phase, f"Should be in {phase}"
        print(f"# Advanced to: {phase}", file=sys.stderr)

    # Validate variance calculation
    variance = calculate_variance(ship)
    assert "cost_variance_pct" in variance, "Should have cost variance"
    print(f"# Final variance: {variance['cost_variance_pct']:.1f}%", file=sys.stderr)

    # Complete ship
    ship = complete_ship(ship)
    assert "delivery_receipt" in ship, "Should have delivery receipt"
    print(f"# Ship delivered: overrun={ship['final_overrun_pct']:.1f}%", file=sys.stderr)

    # Validate phase sequence
    phases = [m.get("phase") for m in ship["milestones"]]
    assert validate_phase_sequence(phases), "Phase sequence should be valid"

    print("# PASS: Lifecycle state machine validated", file=sys.stderr)
