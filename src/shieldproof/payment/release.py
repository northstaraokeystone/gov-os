"""
SHIELDPROOF v2.1 Payment Release - Payment Release Functions

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY
"""

import json
from datetime import datetime
from typing import Optional

from ..core import dual_hash, query_receipts, emit_receipt, StopRule
from ..contract import get_contract
from ..milestone import get_milestone
from .config import REQUIRE_VERIFIED_MILESTONE
from .receipts import emit_payment_receipt


def request_payment(
    contract_id: str,
    milestone_id: str,
    amount_usd: float,
    requestor_id: str,
) -> dict:
    """
    Request payment (v2.1 API).
    STOPRULE: If milestone not verified, raise StopRule and emit anomaly_receipt.
    If verified, emit payment_receipt and return.

    Args:
        contract_id: Contract identifier
        milestone_id: Milestone identifier
        amount_usd: Payment amount in USD
        requestor_id: ID of requestor

    Returns:
        payment_receipt

    Stoprules:
        - stoprule_unverified_milestone: HALT if attempting payment on non-VERIFIED
    """
    milestone = get_milestone(contract_id, milestone_id)

    if milestone is None or milestone.get("status") not in ["VERIFIED", "verified"]:
        emit_receipt("anomaly", {
            "reason": "payment_without_verification",
            "contract_id": contract_id,
            "milestone_id": milestone_id,
            "amount_usd": amount_usd,
            "delta": -1,
            "action": "halt",
            "classification": "violation",
        })
        raise StopRule(f"Payment blocked: milestone {milestone_id} not verified")

    # Check for existing payment
    existing_payments = query_receipts("payment", contract_id=contract_id, milestone_id=milestone_id)
    if existing_payments:
        _stoprule_already_paid(contract_id, milestone_id)

    released_at = datetime.utcnow().isoformat() + "Z"
    contract = get_contract(contract_id)
    total = total_paid(contract_id)
    contract_total = contract.get("amount_fixed", contract.get("total_value_usd", 0)) if contract else 0

    return emit_payment_receipt({
        "contract_id": contract_id,
        "milestone_id": milestone_id,
        "amount_usd": amount_usd,
        "amount": amount_usd,
        "requestor_id": requestor_id,
        "released_at": released_at,
        "total_paid_usd": total + amount_usd,
        "remaining_usd": contract_total - total - amount_usd,
    })


def release_payment(contract_id: str, milestone_id: str) -> dict:
    """
    Release payment for a verified milestone (v2.0 compatible API).
    Creates payment_receipt and updates milestone to PAID.

    Args:
        contract_id: Contract identifier
        milestone_id: Milestone identifier

    Returns:
        payment_receipt

    Stoprules:
        - stoprule_unverified_milestone: HALT if attempting payment on non-VERIFIED
        - stoprule_already_paid: If milestone already PAID
    """
    # Get milestone status
    milestone = get_milestone(contract_id, milestone_id)
    if not milestone:
        _stoprule_unverified_milestone(contract_id, milestone_id, "Milestone not found")

    # Check for existing payment FIRST (before status check)
    existing_payments = query_receipts("payment", contract_id=contract_id, milestone_id=milestone_id)
    if existing_payments:
        _stoprule_already_paid(contract_id, milestone_id)

    # Stoprule: Check milestone is verified
    if REQUIRE_VERIFIED_MILESTONE and milestone.get("status") not in ["VERIFIED", "verified"]:
        _stoprule_unverified_milestone(
            contract_id,
            milestone_id,
            f"Status is {milestone.get('status')}, not VERIFIED"
        )

    amount = milestone.get("amount", 0)
    released_at = datetime.utcnow().isoformat() + "Z"

    # Create payment data for hashing
    payment_data = {
        "contract_id": contract_id,
        "milestone_id": milestone_id,
        "amount": amount,
        "released_at": released_at,
    }
    payment_hash = dual_hash(json.dumps(payment_data, sort_keys=True))

    # Create payment receipt
    receipt = emit_payment_receipt({
        "contract_id": contract_id,
        "milestone_id": milestone_id,
        "amount": amount,
        "amount_usd": amount,
        "payment_hash": payment_hash,
        "released_at": released_at,
    })

    # Emit milestone receipt to update status to PAID
    emit_receipt("milestone", {
        "contract_id": contract_id,
        "milestone_id": milestone_id,
        "status": "PAID",
        "deliverable_hash": milestone.get("deliverable_hash"),
        "verifier_id": milestone.get("verifier_id"),
        "verification_ts": milestone.get("verification_ts"),
    })

    return receipt


def get_payment(contract_id: str, milestone_id: str) -> Optional[dict]:
    """
    Retrieve payment status for a milestone.

    Args:
        contract_id: Contract identifier
        milestone_id: Milestone identifier

    Returns:
        Payment receipt or None if not paid
    """
    payments = query_receipts("payment", contract_id=contract_id, milestone_id=milestone_id)
    if not payments:
        return None
    return payments[-1]


def get_payments(contract_id: str) -> list:
    """
    List all payments for contract (v2.1 API).

    Args:
        contract_id: Contract identifier

    Returns:
        List of payment receipts
    """
    return query_receipts("payment", contract_id=contract_id)


def list_payments(contract_id: Optional[str] = None) -> list:
    """
    List all payment receipts, optionally filtered by contract (v2.0 API).

    Args:
        contract_id: Optional contract filter

    Returns:
        List of payment receipts
    """
    if contract_id:
        return query_receipts("payment", contract_id=contract_id)
    return query_receipts("payment")


def total_paid(contract_id: str) -> float:
    """
    Sum of released payments for a contract.

    Args:
        contract_id: Contract identifier

    Returns:
        Total amount paid
    """
    payments = query_receipts("payment", contract_id=contract_id)
    return sum(p.get("amount", p.get("amount_usd", 0)) for p in payments)


def total_outstanding(contract_id: str) -> float:
    """
    Remaining unpaid amount for a contract.

    Args:
        contract_id: Contract identifier

    Returns:
        Outstanding amount
    """
    contract = get_contract(contract_id)
    if not contract:
        return 0.0

    total_amount = contract.get("amount_fixed", contract.get("total_value_usd", 0))
    paid = total_paid(contract_id)
    return total_amount - paid


# === STOPRULES ===

def _stoprule_unverified_milestone(contract_id: str, milestone_id: str, reason: str) -> None:
    """Emit anomaly receipt and HALT for unverified milestone payment attempt."""
    emit_receipt("anomaly", {
        "metric": "unverified_milestone",
        "contract_id": contract_id,
        "milestone_id": milestone_id,
        "reason": reason,
        "delta": -1,
        "action": "halt",
        "classification": "violation",
    })
    raise StopRule(f"HALT: Cannot pay unverified milestone {milestone_id} in {contract_id}: {reason}")


def _stoprule_already_paid(contract_id: str, milestone_id: str) -> None:
    """Emit anomaly receipt for already paid milestone."""
    emit_receipt("anomaly", {
        "metric": "already_paid",
        "contract_id": contract_id,
        "milestone_id": milestone_id,
        "delta": -1,
        "action": "reject",
        "classification": "violation",
    })
    raise StopRule(f"Milestone already paid: {milestone_id} in contract {contract_id}")
