"""
WarrantProof Shipyard Receipts - 8 Shipbuilding-Specific Receipt Types

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

Per CLAUDEME: Every receipt type = SCHEMA + EMIT + TEST + STOPRULE

Receipt Types:
1. keel_receipt - Keel laying ceremony and coordinates
2. block_receipt - Block assembly with weld tracking
3. additive_receipt - 3D printed section validation
4. iteration_receipt - SpaceX-style rapid iteration
5. milestone_receipt - Program milestone tracking
6. procurement_receipt - Contract and change orders
7. propulsion_receipt - Nuclear reactor installation
8. delivery_receipt - Final ship delivery

LAW_1 = "No receipt -> not real"
"""

import json
import time
from datetime import datetime
from typing import Any, Optional

from src.core import dual_hash, emit_receipt, StopRuleException

from .constants import (
    SHIPYARD_TENANT_ID,
    SHIPYARD_DISCLAIMER,
)

# === RECEIPT SCHEMAS ===

RECEIPT_SCHEMA = {
    "keel_receipt": {
        "description": "Keel laying ceremony marking construction start",
        "required_fields": ["ship_id", "yard_id", "ts", "coordinates"],
        "optional_fields": ["material_hash", "ceremony_attendees"],
        "emitted_by": "lifecycle.py",
    },
    "block_receipt": {
        "description": "Block assembly with weld count and quality tracking",
        "required_fields": ["block_id", "ship_id", "weld_count", "inspector_id"],
        "optional_fields": ["pass_rate", "weld_hashes"],
        "emitted_by": "assembly.py",
    },
    "additive_receipt": {
        "description": "3D printed section with layer validation",
        "required_fields": ["part_id", "printer_id", "material_kg", "print_hours"],
        "optional_fields": ["qa_hash", "layer_count", "layer_hashes"],
        "emitted_by": "additive.py",
    },
    "iteration_receipt": {
        "description": "SpaceX-style rapid iteration cycle",
        "required_fields": ["cycle_id", "ship_id", "changes_count", "time_delta_days"],
        "optional_fields": ["change_descriptions", "parallel_factor"],
        "emitted_by": "iterate.py",
    },
    "milestone_receipt": {
        "description": "Program milestone completion",
        "required_fields": ["milestone_id", "ship_id", "completion_pct"],
        "optional_fields": ["variance_days", "phase", "blocker_receipts"],
        "emitted_by": "lifecycle.py",
    },
    "procurement_receipt": {
        "description": "Contract creation or modification",
        "required_fields": ["contract_id", "vendor_id", "amount_usd", "contract_type"],
        "optional_fields": ["change_order_count", "cumulative_variance"],
        "emitted_by": "procurement.py",
    },
    "propulsion_receipt": {
        "description": "Nuclear reactor installation and testing",
        "required_fields": ["reactor_id", "ship_id", "power_mwe"],
        "optional_fields": ["test_hash", "nrc_cert_chain"],
        "emitted_by": "nuclear.py",
    },
    "delivery_receipt": {
        "description": "Final ship delivery with cost summary",
        "required_fields": ["ship_id", "yard_id", "final_cost_usd", "total_days"],
        "optional_fields": ["overrun_pct", "receipt_merkle_root"],
        "emitted_by": "lifecycle.py",
    },
}


# === EMIT FUNCTIONS ===

def emit_keel_receipt(
    ship_id: str,
    yard_id: str,
    ts: str,
    coordinates: Optional[dict] = None,
    material_hash: Optional[str] = None,
    to_stdout: bool = False
) -> dict:
    """
    Emit keel laying receipt marking construction start.

    Args:
        ship_id: Unique ship identifier
        yard_id: Shipyard identifier
        ts: ISO8601 timestamp of keel laying
        coordinates: Optional GPS coordinates of keel location
        material_hash: Optional hash of keel materials
        to_stdout: Whether to print to stdout

    Returns:
        keel_receipt dict
    """
    if coordinates is None:
        coordinates = {"lat": 0.0, "lon": 0.0}

    data = {
        "tenant_id": SHIPYARD_TENANT_ID,
        "ship_id": ship_id,
        "yard_id": yard_id,
        "keel_ts": ts,
        "coordinates": coordinates,
        "simulation_flag": SHIPYARD_DISCLAIMER,
    }

    if material_hash:
        data["material_hash"] = material_hash

    receipt = emit_receipt("keel", data, to_stdout=to_stdout)
    return receipt


def emit_block_receipt(
    block_id: str,
    ship_id: str,
    weld_count: int,
    inspector_id: str,
    pass_rate: float = 1.0,
    weld_hashes: Optional[list] = None,
    to_stdout: bool = False
) -> dict:
    """
    Emit block assembly receipt with weld tracking.

    Args:
        block_id: Unique block identifier
        ship_id: Ship this block belongs to
        weld_count: Number of welds in this block
        inspector_id: Inspector who certified the block
        pass_rate: Fraction of welds passing inspection
        weld_hashes: Optional list of individual weld hashes
        to_stdout: Whether to print to stdout

    Returns:
        block_receipt dict
    """
    data = {
        "tenant_id": SHIPYARD_TENANT_ID,
        "block_id": block_id,
        "ship_id": ship_id,
        "weld_count": weld_count,
        "inspector_id": inspector_id,
        "pass_rate": pass_rate,
        "simulation_flag": SHIPYARD_DISCLAIMER,
    }

    if weld_hashes:
        data["weld_hashes"] = weld_hashes
        data["weld_merkle_root"] = dual_hash(json.dumps(weld_hashes, sort_keys=True))

    receipt = emit_receipt("block", data, to_stdout=to_stdout)
    return receipt


def emit_additive_receipt(
    part_id: str,
    printer_id: str,
    material_kg: float,
    print_hours: float,
    material_type: str = "HDPE",
    qa_hash: Optional[str] = None,
    layer_count: int = 0,
    layer_hashes: Optional[list] = None,
    to_stdout: bool = False
) -> dict:
    """
    Emit 3D printing receipt with layer validation.

    Args:
        part_id: Unique part identifier
        printer_id: Printer identifier
        material_kg: Material used in kg
        print_hours: Print duration in hours
        material_type: Type of material (must be marine certified)
        qa_hash: QA validation hash
        layer_count: Number of printed layers
        layer_hashes: Per-layer validation hashes
        to_stdout: Whether to print to stdout

    Returns:
        additive_receipt dict
    """
    data = {
        "tenant_id": SHIPYARD_TENANT_ID,
        "part_id": part_id,
        "printer_id": printer_id,
        "material_kg": material_kg,
        "print_hours": print_hours,
        "material_type": material_type,
        "simulation_flag": SHIPYARD_DISCLAIMER,
    }

    if qa_hash:
        data["qa_hash"] = qa_hash

    if layer_count > 0:
        data["layer_count"] = layer_count

    if layer_hashes:
        data["layer_hashes"] = layer_hashes
        # Merkle root of all layer hashes
        data["part_merkle_root"] = dual_hash(json.dumps(layer_hashes, sort_keys=True))

    receipt = emit_receipt("additive", data, to_stdout=to_stdout)
    return receipt


def emit_iteration_receipt(
    cycle_id: str,
    ship_id: str,
    changes_count: int,
    time_delta_days: float,
    change_descriptions: Optional[list] = None,
    parallel_factor: float = 1.0,
    to_stdout: bool = False
) -> dict:
    """
    Emit iteration cycle receipt for SpaceX-style rapid iteration.

    Args:
        cycle_id: Unique iteration cycle identifier
        ship_id: Ship being iterated
        changes_count: Number of changes in this cycle
        time_delta_days: Days since last iteration
        change_descriptions: Optional list of change descriptions
        parallel_factor: Parallelization multiplier (1.0 = serial)
        to_stdout: Whether to print to stdout

    Returns:
        iteration_receipt dict
    """
    # Calculate cadence (iterations per month)
    cadence = 30.0 / time_delta_days if time_delta_days > 0 else 0.0

    data = {
        "tenant_id": SHIPYARD_TENANT_ID,
        "cycle_id": cycle_id,
        "ship_id": ship_id,
        "changes_count": changes_count,
        "time_delta_days": time_delta_days,
        "cadence_per_month": round(cadence, 2),
        "parallel_factor": parallel_factor,
        "simulation_flag": SHIPYARD_DISCLAIMER,
    }

    if change_descriptions:
        data["change_descriptions"] = change_descriptions

    receipt = emit_receipt("iteration", data, to_stdout=to_stdout)
    return receipt


def emit_milestone_receipt(
    milestone_id: str,
    ship_id: str,
    completion_pct: float,
    phase: str,
    variance_days: int = 0,
    blocker_receipts: Optional[list] = None,
    to_stdout: bool = False
) -> dict:
    """
    Emit milestone completion receipt.

    Args:
        milestone_id: Unique milestone identifier
        ship_id: Ship achieving milestone
        completion_pct: Percentage complete (0-100)
        phase: Current lifecycle phase
        variance_days: Days ahead/behind schedule
        blocker_receipts: Receipt IDs blocking progress
        to_stdout: Whether to print to stdout

    Returns:
        milestone_receipt dict
    """
    data = {
        "tenant_id": SHIPYARD_TENANT_ID,
        "milestone_id": milestone_id,
        "ship_id": ship_id,
        "completion_pct": completion_pct,
        "phase": phase,
        "variance_days": variance_days,
        "on_schedule": variance_days <= 0,
        "simulation_flag": SHIPYARD_DISCLAIMER,
    }

    if blocker_receipts:
        data["blocker_receipts"] = blocker_receipts

    receipt = emit_receipt("milestone", data, to_stdout=to_stdout)
    return receipt


def emit_procurement_receipt(
    contract_id: str,
    vendor_id: str,
    amount_usd: float,
    contract_type: str,
    change_order_count: int = 0,
    cumulative_variance: float = 0.0,
    to_stdout: bool = False
) -> dict:
    """
    Emit procurement/contract receipt.

    Args:
        contract_id: Unique contract identifier
        vendor_id: Vendor/contractor identifier
        amount_usd: Contract amount in USD
        contract_type: "fixed_price", "cost_plus", or "hybrid"
        change_order_count: Number of change orders
        cumulative_variance: Cumulative cost variance percentage
        to_stdout: Whether to print to stdout

    Returns:
        procurement_receipt dict
    """
    # Calculate entropy direction based on contract type
    entropy_direction = {
        "fixed_price": "shedding",
        "cost_plus": "accumulating",
        "hybrid": "neutral",
    }.get(contract_type, "unknown")

    data = {
        "tenant_id": SHIPYARD_TENANT_ID,
        "contract_id": contract_id,
        "vendor_id": vendor_id,
        "amount_usd": amount_usd,
        "contract_type": contract_type,
        "change_order_count": change_order_count,
        "cumulative_variance_pct": cumulative_variance,
        "entropy_direction": entropy_direction,
        "simulation_flag": SHIPYARD_DISCLAIMER,
    }

    receipt = emit_receipt("procurement", data, to_stdout=to_stdout)
    return receipt


def emit_propulsion_receipt(
    reactor_id: str,
    ship_id: str,
    power_mwe: float,
    test_hash: Optional[str] = None,
    nrc_cert_chain: Optional[list] = None,
    to_stdout: bool = False
) -> dict:
    """
    Emit nuclear reactor installation receipt.

    Args:
        reactor_id: Unique reactor identifier
        ship_id: Ship receiving reactor
        power_mwe: Reactor power output in MWe
        test_hash: Hash of power test results
        nrc_cert_chain: NRC certification chain receipts
        to_stdout: Whether to print to stdout

    Returns:
        propulsion_receipt dict
    """
    data = {
        "tenant_id": SHIPYARD_TENANT_ID,
        "reactor_id": reactor_id,
        "ship_id": ship_id,
        "power_mwe": power_mwe,
        "propulsion_type": "nuclear_smr",
        "simulation_flag": SHIPYARD_DISCLAIMER,
    }

    if test_hash:
        data["test_hash"] = test_hash

    if nrc_cert_chain:
        data["nrc_cert_chain"] = nrc_cert_chain
        data["cert_complete"] = len(nrc_cert_chain) >= 3  # Minimum cert steps

    receipt = emit_receipt("propulsion", data, to_stdout=to_stdout)
    return receipt


def emit_delivery_receipt(
    ship_id: str,
    yard_id: str,
    final_cost_usd: float,
    total_days: int,
    baseline_cost_usd: float,
    baseline_days: int,
    receipt_merkle_root: Optional[str] = None,
    to_stdout: bool = False
) -> dict:
    """
    Emit final ship delivery receipt with cost summary.

    Args:
        ship_id: Ship being delivered
        yard_id: Delivering shipyard
        final_cost_usd: Final total cost
        total_days: Total construction days
        baseline_cost_usd: Original baseline cost
        baseline_days: Original baseline schedule
        receipt_merkle_root: Merkle root of all ship receipts
        to_stdout: Whether to print to stdout

    Returns:
        delivery_receipt dict
    """
    # Calculate overruns
    cost_overrun_pct = ((final_cost_usd - baseline_cost_usd) / baseline_cost_usd) * 100 if baseline_cost_usd > 0 else 0
    schedule_overrun_pct = ((total_days - baseline_days) / baseline_days) * 100 if baseline_days > 0 else 0

    data = {
        "tenant_id": SHIPYARD_TENANT_ID,
        "ship_id": ship_id,
        "yard_id": yard_id,
        "final_cost_usd": final_cost_usd,
        "total_days": total_days,
        "baseline_cost_usd": baseline_cost_usd,
        "baseline_days": baseline_days,
        "cost_overrun_pct": round(cost_overrun_pct, 2),
        "schedule_overrun_pct": round(schedule_overrun_pct, 2),
        "simulation_flag": SHIPYARD_DISCLAIMER,
    }

    if receipt_merkle_root:
        data["receipt_merkle_root"] = receipt_merkle_root

    receipt = emit_receipt("delivery", data, to_stdout=to_stdout)
    return receipt


# === TEST FUNCTIONS ===

def test_keel_receipt_slo() -> bool:
    """Test keel_receipt emission latency."""
    t0 = time.time()
    r = emit_keel_receipt("TEST-001", "YARD-001", datetime.utcnow().isoformat() + "Z")
    latency_ms = (time.time() - t0) * 1000
    assert latency_ms <= 50, f"Latency {latency_ms}ms > 50ms SLO"
    assert "tenant_id" in r, "Missing tenant_id"
    assert r["tenant_id"] == SHIPYARD_TENANT_ID
    return True


def test_block_receipt_slo() -> bool:
    """Test block_receipt emission latency."""
    t0 = time.time()
    r = emit_block_receipt("BLK-001", "SHIP-001", 100, "INSP-001")
    latency_ms = (time.time() - t0) * 1000
    assert latency_ms <= 50, f"Latency {latency_ms}ms > 50ms SLO"
    assert "tenant_id" in r
    assert "weld_count" in r
    return True


def test_additive_receipt_slo() -> bool:
    """Test additive_receipt emission latency."""
    t0 = time.time()
    r = emit_additive_receipt("PART-001", "PRINTER-001", 500.0, 24.0)
    latency_ms = (time.time() - t0) * 1000
    assert latency_ms <= 50, f"Latency {latency_ms}ms > 50ms SLO"
    assert "tenant_id" in r
    assert "material_kg" in r
    return True


def test_iteration_receipt_slo() -> bool:
    """Test iteration_receipt emission latency."""
    t0 = time.time()
    r = emit_iteration_receipt("ITER-001", "SHIP-001", 5, 7.0)
    latency_ms = (time.time() - t0) * 1000
    assert latency_ms <= 50, f"Latency {latency_ms}ms > 50ms SLO"
    assert "tenant_id" in r
    assert "cadence_per_month" in r
    return True


def test_all_receipt_types() -> bool:
    """Test all 8 receipt types emit valid JSON."""
    receipts = [
        emit_keel_receipt("T1", "Y1", "2025-01-01T00:00:00Z"),
        emit_block_receipt("B1", "S1", 50, "I1"),
        emit_additive_receipt("P1", "PR1", 100.0, 10.0),
        emit_iteration_receipt("IT1", "S1", 3, 7.0),
        emit_milestone_receipt("M1", "S1", 50.0, "BLOCK_ASSEMBLY"),
        emit_procurement_receipt("C1", "V1", 1000000.0, "fixed_price"),
        emit_propulsion_receipt("R1", "S1", 77.0),
        emit_delivery_receipt("S1", "Y1", 10000000000.0, 1095, 9000000000.0, 1000),
    ]

    for r in receipts:
        assert "receipt_type" in r, f"Missing receipt_type: {r}"
        assert "ts" in r, f"Missing ts: {r}"
        assert "tenant_id" in r, f"Missing tenant_id: {r}"
        assert "payload_hash" in r, f"Missing payload_hash: {r}"
        assert ":" in r["payload_hash"], "payload_hash must be dual-hash format"

    return True


# === STOPRULES ===

def stoprule_keel_missing(ship_id: str) -> None:
    """Stoprule: Ship construction started without keel receipt."""
    emit_receipt("anomaly", {
        "metric": "keel_missing",
        "ship_id": ship_id,
        "delta": -1,
        "action": "halt",
        "classification": "violation",
        "simulation_flag": SHIPYARD_DISCLAIMER,
    })
    raise StopRuleException(f"Ship {ship_id} has no keel_receipt - construction cannot proceed")


def stoprule_block_inspection_failed(block_id: str, pass_rate: float) -> None:
    """Stoprule: Block failed inspection threshold."""
    emit_receipt("anomaly", {
        "metric": "block_inspection_failed",
        "block_id": block_id,
        "pass_rate": pass_rate,
        "delta": pass_rate - 0.95,  # 95% threshold
        "action": "halt",
        "classification": "violation",
        "simulation_flag": SHIPYARD_DISCLAIMER,
    })
    raise StopRuleException(f"Block {block_id} failed inspection: pass_rate={pass_rate} < 0.95")


def stoprule_additive_layer_mismatch(part_id: str, expected_hash: str, actual_hash: str) -> None:
    """Stoprule: Additive layer hash mismatch - potential quality issue."""
    emit_receipt("anomaly", {
        "metric": "additive_layer_mismatch",
        "part_id": part_id,
        "expected_hash": expected_hash[:16],
        "actual_hash": actual_hash[:16],
        "delta": -1,
        "action": "halt",
        "classification": "violation",
        "simulation_flag": SHIPYARD_DISCLAIMER,
    })
    raise StopRuleException(f"Part {part_id} layer hash mismatch - quality validation failed")


def stoprule_procurement_overrun(contract_id: str, overrun_pct: float) -> None:
    """Stoprule: Contract exceeded overrun threshold."""
    emit_receipt("anomaly", {
        "metric": "procurement_overrun",
        "contract_id": contract_id,
        "overrun_pct": overrun_pct,
        "delta": overrun_pct - 0.12,  # 12% threshold
        "action": "escalate",
        "classification": "cost_cascade",
        "simulation_flag": SHIPYARD_DISCLAIMER,
    })
    raise StopRuleException(f"Contract {contract_id} overrun {overrun_pct}% exceeds 12% threshold")


# === MODULE SELF-TEST ===

if __name__ == "__main__":
    print("# WarrantProof Shipyard Receipts Self-Test", file=sys.stderr)
    print(f"# {SHIPYARD_DISCLAIMER}", file=sys.stderr)

    # Run all SLO tests
    assert test_keel_receipt_slo(), "keel_receipt SLO failed"
    assert test_block_receipt_slo(), "block_receipt SLO failed"
    assert test_additive_receipt_slo(), "additive_receipt SLO failed"
    assert test_iteration_receipt_slo(), "iteration_receipt SLO failed"
    assert test_all_receipt_types(), "Receipt type validation failed"

    print("# PASS: All 8 receipt types validated", file=sys.stderr)
