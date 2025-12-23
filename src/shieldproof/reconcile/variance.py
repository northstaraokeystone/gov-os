"""
SHIELDPROOF v2.1 Reconcile Variance - Variance Detection Functions

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY
"""

from typing import Optional

from ..core import emit_receipt, query_receipts
from ..contract import get_contract, get_contract_milestones
from ..payment import total_paid, list_payments
from .config import VARIANCE_THRESHOLD, VARIANCE_CRITICAL
from .receipts import emit_variance_receipt


def check_variance(contract_id: str) -> dict:
    """
    Compare actual spend vs fixed-price baseline.
    Return variance calculation.
    Emit variance_receipt if threshold exceeded.

    Args:
        contract_id: Contract identifier

    Returns:
        Variance calculation dict
    """
    contract = get_contract(contract_id)
    if not contract:
        return {"contract_id": contract_id, "error": "Contract not found", "variance": 0.0}

    milestones = get_contract_milestones(contract_id)
    paid = total_paid(contract_id)
    contract_total = contract.get("amount_fixed", contract.get("total_value_usd", 0))

    # Calculate milestone progress (0.0 to 1.0)
    verified_milestones = [m for m in milestones if m.get("status") in ["VERIFIED", "PAID", "verified"]]
    milestone_progress = len(verified_milestones) / len(milestones) if milestones else 0.0

    # Calculate expected spend based on milestone progress
    expected_spend = contract_total * milestone_progress
    actual_spend = paid

    # Calculate variance
    if expected_spend > 0:
        variance = (actual_spend - expected_spend) / expected_spend
    else:
        variance = 0.0

    result = {
        "contract_id": contract_id,
        "variance": variance,
        "expected_spend_usd": expected_spend,
        "actual_spend_usd": actual_spend,
        "milestone_progress": milestone_progress,
        "threshold_pct": VARIANCE_THRESHOLD,
    }

    # Emit variance_receipt if threshold exceeded
    if abs(variance) > VARIANCE_THRESHOLD:
        severity = "critical" if abs(variance) > VARIANCE_CRITICAL else "warning"
        emit_variance_receipt({
            "contract_id": contract_id,
            "expected_spend_usd": expected_spend,
            "actual_spend_usd": actual_spend,
            "variance_pct": variance,
            "threshold_pct": VARIANCE_THRESHOLD,
            "severity": severity,
        })
        result["severity"] = severity

    return result


def variance_report() -> dict:
    """
    Generate full variance report for all contracts.

    Returns:
        Variance report dict
    """
    contracts = query_receipts("contract")
    seen_contracts = set()
    results = []

    for contract in contracts:
        contract_id = contract.get("contract_id")
        if contract_id in seen_contracts:
            continue
        seen_contracts.add(contract_id)

        result = check_variance(contract_id)
        results.append(result)

    return {
        "total_contracts": len(results),
        "contracts_over_threshold": len([r for r in results if abs(r.get("variance", 0)) > VARIANCE_THRESHOLD]),
        "contracts": results,
    }


def flag_contracts(threshold: float = VARIANCE_THRESHOLD) -> list:
    """
    Return contracts exceeding threshold.

    Args:
        threshold: Variance threshold (default: 5%)

    Returns:
        List of contracts exceeding threshold
    """
    contracts = query_receipts("contract")
    seen_contracts = set()
    flagged = []

    for contract in contracts:
        contract_id = contract.get("contract_id")
        if contract_id in seen_contracts:
            continue
        seen_contracts.add(contract_id)

        result = check_variance(contract_id)
        if abs(result.get("variance", 0)) > threshold:
            flagged.append(result)

    return flagged


def reconcile_contract(contract_id: str) -> dict:
    """
    Reconcile a single contract - compare paid vs verified milestones (v2.0 API).

    Args:
        contract_id: Contract identifier

    Returns:
        Reconciliation report dict
    """
    contract = get_contract(contract_id)
    if not contract:
        return {
            "contract_id": contract_id,
            "error": "Contract not found",
            "status": "ERROR",
        }

    contractor = contract.get("contractor", "Unknown")
    amount_fixed = contract.get("amount_fixed", contract.get("total_value_usd", 0))
    milestones = get_contract_milestones(contract_id)
    payments = list_payments(contract_id)

    # Count milestone states
    milestones_pending = sum(1 for m in milestones if m.get("status") == "PENDING")
    milestones_delivered = sum(1 for m in milestones if m.get("status") in ["DELIVERED", "submitted"])
    milestones_verified = sum(1 for m in milestones if m.get("status") in ["VERIFIED", "verified"])
    milestones_paid = sum(1 for m in milestones if m.get("status") == "PAID")
    milestones_disputed = sum(1 for m in milestones if m.get("status") in ["DISPUTED", "rejected"])

    # Calculate amounts
    amount_paid = total_paid(contract_id)
    amount_verified = sum(
        m.get("amount", 0) for m in milestones
        if m.get("status") in ["VERIFIED", "PAID", "verified"]
    )

    # Determine status and discrepancy
    discrepancy = 0.0
    status = "ON_TRACK"
    anomalies = []

    # Check for overpayment
    if amount_paid > amount_verified:
        discrepancy = amount_paid - amount_verified
        status = "OVERPAID"
        anomalies.append(_emit_overpayment_anomaly(contract_id, amount_paid, amount_verified))

    # Check for unverified payments
    for payment in payments:
        milestone_id = payment.get("milestone_id")
        milestone = next((m for m in milestones if m["id"] == milestone_id), None)
        if milestone and milestone.get("status") not in ["VERIFIED", "PAID", "verified"]:
            status = "UNVERIFIED_PAYMENT"
            anomalies.append(_emit_unverified_payment_anomaly(
                contract_id,
                milestone_id,
                payment.get("amount", payment.get("amount_usd", 0))
            ))

    # Check for disputes
    if milestones_disputed > 0:
        status = "DISPUTED"

    return {
        "contract_id": contract_id,
        "contractor": contractor,
        "amount_fixed": amount_fixed,
        "amount_paid": amount_paid,
        "amount_verified": amount_verified,
        "milestones_total": len(milestones),
        "milestones_pending": milestones_pending,
        "milestones_delivered": milestones_delivered,
        "milestones_verified": milestones_verified,
        "milestones_paid": milestones_paid,
        "milestones_disputed": milestones_disputed,
        "status": status,
        "discrepancy": discrepancy,
        "anomalies": len(anomalies),
    }


def reconcile_all() -> list:
    """
    Run reconciliation across all contracts (v2.0 API).

    Returns:
        List of reconciliation reports
    """
    contracts = query_receipts("contract")
    reports = []
    seen_contracts = set()

    for contract in contracts:
        contract_id = contract.get("contract_id")
        if contract_id in seen_contracts:
            continue
        seen_contracts.add(contract_id)

        report = reconcile_contract(contract_id)
        reports.append(report)

    return reports


def flag_anomaly(contract_id: str, reason: str) -> dict:
    """
    Manually flag an anomaly for a contract.

    Args:
        contract_id: Contract identifier
        reason: Reason for flagging

    Returns:
        anomaly_receipt
    """
    return emit_receipt("anomaly", {
        "metric": "manual_flag",
        "contract_id": contract_id,
        "reason": reason,
        "delta": -1,
        "action": "investigate",
        "classification": "suspicious",
    })


def get_waste_summary() -> dict:
    """
    Get aggregate waste summary across all contracts.

    Returns:
        Summary dict with waste metrics
    """
    reports = reconcile_all()

    total_contracts = len(reports)
    total_committed = sum(r.get("amount_fixed", 0) for r in reports)
    total_paid_amount = sum(r.get("amount_paid", 0) for r in reports)
    total_verified = sum(r.get("amount_verified", 0) for r in reports)

    # Waste = paid without verification
    waste_identified = total_paid_amount - total_verified if total_paid_amount > total_verified else 0

    # Count milestone states
    milestones_pending = sum(r.get("milestones_pending", 0) for r in reports)
    milestones_disputed = sum(r.get("milestones_disputed", 0) for r in reports)

    contracts_on_track = sum(1 for r in reports if r.get("status") == "ON_TRACK")
    contracts_overpaid = sum(1 for r in reports if r.get("status") == "OVERPAID")
    contracts_unverified = sum(1 for r in reports if r.get("status") == "UNVERIFIED_PAYMENT")
    contracts_disputed = sum(1 for r in reports if r.get("status") == "DISPUTED")

    return {
        "total_contracts": total_contracts,
        "total_committed": total_committed,
        "total_paid": total_paid_amount,
        "total_verified": total_verified,
        "waste_identified": waste_identified,
        "milestones_pending": milestones_pending,
        "milestones_disputed": milestones_disputed,
        "contracts_on_track": contracts_on_track,
        "contracts_overpaid": contracts_overpaid,
        "contracts_unverified": contracts_unverified,
        "contracts_disputed": contracts_disputed,
    }


# === ANOMALY HELPERS ===

def _emit_overpayment_anomaly(contract_id: str, paid: float, verified: float) -> dict:
    """Emit anomaly receipt for overpayment."""
    return emit_receipt("anomaly", {
        "metric": "overpayment",
        "contract_id": contract_id,
        "amount_paid": paid,
        "amount_verified": verified,
        "delta": paid - verified,
        "action": "investigate",
        "classification": "violation",
    })


def _emit_unverified_payment_anomaly(contract_id: str, milestone_id: str, amount: float) -> dict:
    """Emit anomaly receipt for payment without verification."""
    return emit_receipt("anomaly", {
        "metric": "unverified_payment",
        "contract_id": contract_id,
        "milestone_id": milestone_id,
        "amount": amount,
        "delta": -1,
        "action": "investigate",
        "classification": "violation",
    })
