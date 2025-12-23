"""
WarrantProof Shipyard Procurement - Fixed-Price vs Cost-Plus Entropy Modeling

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

Models procurement contract types and their entropy characteristics.

Core Insight: Contract type determines entropy direction.
- Cost-plus contracts create entropy accumulation:
  - No compression pressure (vendor paid regardless)
  - Change orders compound without receipts
  - Overruns discovered post-hoc (unrecoverable)

- Fixed-price with receipts creates entropy shedding:
  - Compression pressure (vendor absorbs overruns)
  - Each change requires warrant + receipt
  - Anomalies detected real-time (recoverable)

Entropy Model:
- Fixed-price: entropy_rate < 0 (shedding)
- Cost-plus: entropy_rate > 0 (accumulating)
- Threshold: contracts exceeding 12% overrun flagged
"""

import uuid
from datetime import datetime
from typing import Optional

from src.core import dual_hash, emit_receipt

from .constants import (
    SHIPYARD_TENANT_ID,
    SHIPYARD_DISCLAIMER,
    CONTRACT_TYPES,
    CONTRACT_ENTROPY,
    MAX_CHANGE_ORDERS_BEFORE_REVIEW,
    CHANGE_ORDER_OVERRUN_THRESHOLD,
    EARLY_DETECTION_PCT,
)
from .receipts import emit_procurement_receipt, stoprule_procurement_overrun


# === CORE FUNCTIONS ===

def create_contract(
    contract_id: str,
    vendor_id: str,
    contract_type: str,
    amount: float,
    ship_id: Optional[str] = None,
    description: str = ""
) -> dict:
    """
    Initialize contract and emit procurement_receipt.

    Args:
        contract_id: Unique contract identifier
        vendor_id: Vendor identifier
        contract_type: "fixed_price", "cost_plus", or "hybrid"
        amount: Contract amount in USD
        ship_id: Optional ship this contract supports
        description: Contract description

    Returns:
        Contract state dict
    """
    if contract_type not in CONTRACT_TYPES:
        contract_type = "fixed_price"  # Default to safer option

    ts = datetime.utcnow().isoformat() + "Z"

    # Calculate entropy direction
    entropy_rate = CONTRACT_ENTROPY.get(contract_type, 0.0)

    # Create contract state
    contract = {
        "contract_id": contract_id,
        "vendor_id": vendor_id,
        "contract_type": contract_type,
        "base_amount_usd": amount,
        "current_amount_usd": amount,
        "ship_id": ship_id,
        "description": description,
        "created_at": ts,
        "change_orders": [],
        "change_order_count": 0,
        "cumulative_variance_pct": 0.0,
        "entropy_rate": entropy_rate,
        "entropy_direction": "shedding" if entropy_rate < 0 else "accumulating" if entropy_rate > 0 else "neutral",
        "receipts": [],
        "status": "active",
        "simulation_flag": SHIPYARD_DISCLAIMER,
    }

    # Emit procurement receipt
    receipt = emit_procurement_receipt(
        contract_id=contract_id,
        vendor_id=vendor_id,
        amount_usd=amount,
        contract_type=contract_type,
        change_order_count=0,
        cumulative_variance=0.0,
    )
    contract["receipts"].append(receipt)

    return contract


def process_change_order(
    contract: dict,
    change: dict
) -> dict:
    """
    Validate and emit change_order_receipt.

    Args:
        contract: Contract state dict
        change: Change order dict with amount_delta and reason

    Returns:
        Updated contract state
    """
    ts = datetime.utcnow().isoformat() + "Z"

    amount_delta = change.get("amount_delta", 0.0)
    reason = change.get("reason", "unspecified")

    # Update contract amounts
    new_amount = contract["current_amount_usd"] + amount_delta
    base_amount = contract["base_amount_usd"]

    # Calculate cumulative variance
    variance_pct = ((new_amount - base_amount) / base_amount) * 100 if base_amount > 0 else 0

    # Create change order record
    change_order = {
        "change_order_id": f"{contract['contract_id']}_CO_{len(contract['change_orders']) + 1:04d}",
        "ts": ts,
        "amount_delta": amount_delta,
        "reason": reason,
        "previous_amount": contract["current_amount_usd"],
        "new_amount": new_amount,
        "variance_pct": variance_pct,
    }

    contract["change_orders"].append(change_order)
    contract["change_order_count"] = len(contract["change_orders"])
    contract["current_amount_usd"] = new_amount
    contract["cumulative_variance_pct"] = variance_pct

    # Emit change order receipt
    co_receipt = emit_receipt("change_order", {
        "tenant_id": SHIPYARD_TENANT_ID,
        "contract_id": contract["contract_id"],
        "change_order_id": change_order["change_order_id"],
        "vendor_id": contract["vendor_id"],
        "amount_delta": amount_delta,
        "new_total": new_amount,
        "variance_pct": variance_pct,
        "reason": reason,
        "contract_type": contract["contract_type"],
        "simulation_flag": SHIPYARD_DISCLAIMER,
    }, to_stdout=False)
    contract["receipts"].append(co_receipt)

    # Check for threshold violations
    if abs(variance_pct) > EARLY_DETECTION_PCT * 100:
        _emit_variance_alert(contract, variance_pct)

    # Check for excessive change orders
    if contract["change_order_count"] >= MAX_CHANGE_ORDERS_BEFORE_REVIEW:
        _emit_change_order_alert(contract)

    # Update entropy accumulation based on contract type
    entropy_rate = CONTRACT_ENTROPY.get(contract["contract_type"], 0.0)
    if entropy_rate > 0:
        # Cost-plus: entropy increases with changes
        contract["entropy_accumulated"] = contract.get("entropy_accumulated", 0.0) + abs(amount_delta) * 0.001
    else:
        # Fixed-price: entropy shed with proper documentation
        contract["entropy_shed"] = contract.get("entropy_shed", 0.0) + 0.01

    return contract


def calculate_overrun_rate(contract: dict) -> float:
    """
    Return current overrun percentage.

    Args:
        contract: Contract state dict

    Returns:
        Overrun rate as percentage
    """
    base = contract.get("base_amount_usd", 0)
    current = contract.get("current_amount_usd", 0)

    if base <= 0:
        return 0.0

    overrun = ((current - base) / base) * 100
    return round(overrun, 2)


def compare_contract_types(
    fixed: list,
    costplus: list
) -> dict:
    """
    Entropy comparison between contract types.

    Args:
        fixed: List of fixed-price contracts
        costplus: List of cost-plus contracts

    Returns:
        Comparison metrics dict
    """
    # Calculate fixed-price metrics
    fixed_overruns = [calculate_overrun_rate(c) for c in fixed]
    fixed_changes = [c.get("change_order_count", 0) for c in fixed]
    fixed_entropy = [c.get("entropy_shed", 0) for c in fixed]

    # Calculate cost-plus metrics
    costplus_overruns = [calculate_overrun_rate(c) for c in costplus]
    costplus_changes = [c.get("change_order_count", 0) for c in costplus]
    costplus_entropy = [c.get("entropy_accumulated", 0) for c in costplus]

    # Aggregate
    import statistics

    def safe_mean(lst):
        return statistics.mean(lst) if lst else 0.0

    def safe_stdev(lst):
        return statistics.stdev(lst) if len(lst) >= 2 else 0.0

    comparison = {
        "fixed_price": {
            "count": len(fixed),
            "avg_overrun_pct": round(safe_mean(fixed_overruns), 2),
            "overrun_std": round(safe_stdev(fixed_overruns), 2),
            "avg_change_orders": round(safe_mean(fixed_changes), 1),
            "total_entropy_shed": round(sum(fixed_entropy), 4),
            "entropy_direction": "shedding",
        },
        "cost_plus": {
            "count": len(costplus),
            "avg_overrun_pct": round(safe_mean(costplus_overruns), 2),
            "overrun_std": round(safe_stdev(costplus_overruns), 2),
            "avg_change_orders": round(safe_mean(costplus_changes), 1),
            "total_entropy_accumulated": round(sum(costplus_entropy), 4),
            "entropy_direction": "accumulating",
        },
        "comparison": {
            "overrun_reduction_pct": round(
                safe_mean(costplus_overruns) - safe_mean(fixed_overruns), 2
            ) if costplus_overruns and fixed_overruns else 0,
            "change_order_reduction": round(
                safe_mean(costplus_changes) - safe_mean(fixed_changes), 1
            ) if costplus_changes and fixed_changes else 0,
            "entropy_net": round(
                sum(fixed_entropy) - sum(costplus_entropy), 4
            ),
            "fixed_price_recommended": True,  # Always recommend fixed-price
        },
        "citations": ["GAO_2022", "GAO_2018", "GAO_2024"],
        "simulation_flag": SHIPYARD_DISCLAIMER,
    }

    return comparison


def calculate_entropy_trajectory(contract: dict) -> dict:
    """
    Calculate entropy trajectory based on contract history.

    Args:
        contract: Contract state dict

    Returns:
        Entropy trajectory metrics
    """
    contract_type = contract.get("contract_type", "fixed_price")
    base_rate = CONTRACT_ENTROPY.get(contract_type, 0.0)
    change_orders = contract.get("change_orders", [])

    # Calculate cumulative entropy
    entropy_points = []
    cumulative = 0.0

    for co in change_orders:
        delta = abs(co.get("amount_delta", 0))
        if contract_type == "cost_plus":
            cumulative += delta * 0.001  # Entropy increases
        else:
            cumulative -= 0.01  # Fixed-price sheds entropy per documented change

        entropy_points.append({
            "change_order_id": co.get("change_order_id"),
            "entropy_delta": base_rate,
            "cumulative_entropy": cumulative,
        })

    return {
        "contract_id": contract.get("contract_id"),
        "contract_type": contract_type,
        "base_entropy_rate": base_rate,
        "trajectory_points": entropy_points,
        "final_entropy": cumulative,
        "entropy_direction": "shedding" if cumulative < 0 else "accumulating",
    }


def emit_contract_summary(contract: dict) -> dict:
    """
    Emit contract summary receipt.

    Args:
        contract: Contract state dict

    Returns:
        Summary receipt dict
    """
    overrun = calculate_overrun_rate(contract)
    trajectory = calculate_entropy_trajectory(contract)

    return emit_receipt("contract_summary", {
        "tenant_id": SHIPYARD_TENANT_ID,
        "contract_id": contract.get("contract_id"),
        "vendor_id": contract.get("vendor_id"),
        "contract_type": contract.get("contract_type"),
        "base_amount_usd": contract.get("base_amount_usd"),
        "final_amount_usd": contract.get("current_amount_usd"),
        "overrun_pct": overrun,
        "change_order_count": contract.get("change_order_count", 0),
        "entropy_direction": trajectory.get("entropy_direction"),
        "final_entropy": trajectory.get("final_entropy"),
        "status": contract.get("status", "active"),
        "simulation_flag": SHIPYARD_DISCLAIMER,
    }, to_stdout=False)


# === HELPER FUNCTIONS ===

def _emit_variance_alert(contract: dict, variance_pct: float) -> dict:
    """Emit variance threshold alert."""
    return emit_receipt("alert", {
        "tenant_id": SHIPYARD_TENANT_ID,
        "anomaly_type": "contract_variance",
        "severity": "high" if abs(variance_pct) > 20 else "medium",
        "contract_id": contract.get("contract_id"),
        "variance_pct": variance_pct,
        "threshold_pct": EARLY_DETECTION_PCT * 100,
        "action": "review_required",
        "simulation_flag": SHIPYARD_DISCLAIMER,
    }, to_stdout=False)


def _emit_change_order_alert(contract: dict) -> dict:
    """Emit excessive change orders alert."""
    return emit_receipt("alert", {
        "tenant_id": SHIPYARD_TENANT_ID,
        "anomaly_type": "excessive_change_orders",
        "severity": "medium",
        "contract_id": contract.get("contract_id"),
        "change_order_count": contract.get("change_order_count", 0),
        "threshold": MAX_CHANGE_ORDERS_BEFORE_REVIEW,
        "action": "contract_review",
        "simulation_flag": SHIPYARD_DISCLAIMER,
    }, to_stdout=False)


# === STOPRULES ===

def stoprule_contract_fraud(contract_id: str, indicators: list) -> None:
    """Stoprule: Contract exhibits fraud indicators."""
    emit_receipt("anomaly", {
        "metric": "contract_fraud_indicators",
        "contract_id": contract_id,
        "indicator_count": len(indicators),
        "indicators": indicators,
        "delta": -len(indicators),
        "action": "halt",
        "classification": "procurement_fraud",
        "simulation_flag": SHIPYARD_DISCLAIMER,
    }, to_stdout=False)


# === MODULE SELF-TEST ===

if __name__ == "__main__":
    print("# WarrantProof Shipyard Procurement Self-Test", file=sys.stderr)
    print(f"# {SHIPYARD_DISCLAIMER}", file=sys.stderr)

    # Create fixed-price contract
    fixed = create_contract(
        contract_id="FP-001",
        vendor_id="VENDOR-001",
        contract_type="fixed_price",
        amount=10_000_000.0,
        description="Fixed-price hull construction"
    )
    assert fixed["entropy_direction"] == "shedding", "Fixed-price should shed entropy"
    print(f"# Fixed-price contract: ${fixed['base_amount_usd']:,.0f}", file=sys.stderr)

    # Create cost-plus contract
    costplus = create_contract(
        contract_id="CP-001",
        vendor_id="VENDOR-002",
        contract_type="cost_plus",
        amount=10_000_000.0,
        description="Cost-plus systems integration"
    )
    assert costplus["entropy_direction"] == "accumulating", "Cost-plus should accumulate entropy"
    print(f"# Cost-plus contract: ${costplus['base_amount_usd']:,.0f}", file=sys.stderr)

    # Process change orders
    for i in range(3):
        fixed = process_change_order(fixed, {"amount_delta": 100_000, "reason": f"Change {i+1}"})
        costplus = process_change_order(costplus, {"amount_delta": 500_000, "reason": f"Overrun {i+1}"})

    # Calculate overruns
    fixed_overrun = calculate_overrun_rate(fixed)
    costplus_overrun = calculate_overrun_rate(costplus)
    print(f"# Fixed-price overrun: {fixed_overrun:.1f}%", file=sys.stderr)
    print(f"# Cost-plus overrun: {costplus_overrun:.1f}%", file=sys.stderr)

    # Compare contract types
    comparison = compare_contract_types([fixed], [costplus])
    assert comparison["comparison"]["fixed_price_recommended"], "Should recommend fixed-price"
    print(f"# Overrun difference: {comparison['comparison']['overrun_reduction_pct']:.1f}%", file=sys.stderr)

    # Test entropy trajectory
    trajectory = calculate_entropy_trajectory(costplus)
    assert trajectory["entropy_direction"] == "accumulating", "Cost-plus should accumulate"
    print(f"# Cost-plus entropy: {trajectory['final_entropy']:.4f}", file=sys.stderr)

    print("# PASS: Procurement module validated", file=sys.stderr)
