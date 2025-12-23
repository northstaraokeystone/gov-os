"""
SHIELDPROOF v2.1 Milestone Verify - Milestone Verification Functions

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY
"""

from datetime import datetime
from typing import Optional, Union

from ..core import dual_hash, query_receipts, StopRule
from ..contract import get_contract, get_contract_milestones
from .receipts import emit_milestone_receipt


def submit_milestone(
    contract_id: str,
    milestone_id: str,
    deliverable_hash: str,
    metadata: Optional[dict] = None,
) -> dict:
    """
    Submit milestone for verification (v2.1 API).

    Args:
        contract_id: Contract identifier
        milestone_id: Milestone identifier
        deliverable_hash: Hash of deliverable
        metadata: Optional metadata dict

    Returns:
        milestone_receipt with status="submitted"
    """
    # Validate contract exists
    contract = get_contract(contract_id)
    if not contract:
        _stoprule_unknown_contract(contract_id)

    # Validate milestone exists in contract
    milestones = get_contract_milestones(contract_id)
    milestone = next((m for m in milestones if m["id"] == milestone_id), None)
    if not milestone:
        _stoprule_unknown_milestone(contract_id, milestone_id)

    return emit_milestone_receipt({
        "contract_id": contract_id,
        "milestone_id": milestone_id,
        "deliverable_hash": deliverable_hash,
        "status": "submitted",
        "verifier_id": None,
        "metadata": metadata or {},
    })


def submit_deliverable(
    contract_id: str,
    milestone_id: str,
    deliverable: Union[bytes, str],
) -> dict:
    """
    Submit a deliverable for a milestone (v2.0 compatible API).
    Changes status to DELIVERED.

    Args:
        contract_id: Contract identifier
        milestone_id: Milestone identifier
        deliverable: Deliverable content (bytes or string, will be hashed)

    Returns:
        milestone_receipt with status=DELIVERED
    """
    # Validate contract exists
    contract = get_contract(contract_id)
    if not contract:
        _stoprule_unknown_contract(contract_id)

    # Validate milestone exists in contract
    milestones = get_contract_milestones(contract_id)
    milestone = next((m for m in milestones if m["id"] == milestone_id), None)
    if not milestone:
        _stoprule_unknown_milestone(contract_id, milestone_id)

    # Hash the deliverable
    if isinstance(deliverable, str):
        deliverable = deliverable.encode('utf-8')
    deliverable_hash = dual_hash(deliverable)

    return emit_milestone_receipt({
        "contract_id": contract_id,
        "milestone_id": milestone_id,
        "deliverable_hash": deliverable_hash,
        "status": "DELIVERED",
        "verifier_id": None,
        "verification_ts": None,
    })


def verify_milestone(
    contract_id_or_milestone_id: str,
    milestone_id_or_verifier_id: str,
    verifier_id: Optional[str] = None,
    passed: bool = True,
) -> dict:
    """
    Verify a milestone deliverable.
    Supports both v2.0 API (contract_id, milestone_id, verifier_id, passed)
    and v2.1 API (milestone_id, verifier_id).

    Args:
        contract_id_or_milestone_id: Contract ID (v2.0) or Milestone ID (v2.1)
        milestone_id_or_verifier_id: Milestone ID (v2.0) or Verifier ID (v2.1)
        verifier_id: Verifier ID (v2.0 only)
        passed: Whether verification passed (v2.0 only)

    Returns:
        milestone_receipt with status=VERIFIED or REJECTED/DISPUTED
    """
    # Determine API version based on arguments
    if verifier_id is not None:
        # v2.0 API: (contract_id, milestone_id, verifier_id, passed)
        contract_id = contract_id_or_milestone_id
        milestone_id = milestone_id_or_verifier_id
        actual_verifier_id = verifier_id
    else:
        # Could be v2.1 API or v2.0 with keyword args
        # Try to find milestone by ID across all contracts
        contract_id = contract_id_or_milestone_id
        milestone_id = milestone_id_or_verifier_id
        actual_verifier_id = milestone_id_or_verifier_id
        # Default passed to True for v2.1

    # Validate contract exists
    contract = get_contract(contract_id)
    if not contract:
        _stoprule_unknown_contract(contract_id)

    # Validate milestone exists
    milestones = get_contract_milestones(contract_id)
    milestone = next((m for m in milestones if m["id"] == milestone_id), None)
    if not milestone:
        _stoprule_unknown_milestone(contract_id, milestone_id)

    # Check not already verified or paid
    if milestone.get("status") in ["VERIFIED", "PAID", "verified"]:
        _stoprule_already_verified(contract_id, milestone_id)

    new_status = "VERIFIED" if passed else "DISPUTED"
    verification_ts = datetime.utcnow().isoformat() + "Z"

    return emit_milestone_receipt({
        "contract_id": contract_id,
        "milestone_id": milestone_id,
        "deliverable_hash": milestone.get("deliverable_hash"),
        "status": new_status,
        "verifier_id": actual_verifier_id,
        "verification_ts": verification_ts,
    })


def get_milestone(contract_id: str, milestone_id: str) -> Optional[dict]:
    """
    Retrieve current milestone status.

    Args:
        contract_id: Contract identifier
        milestone_id: Milestone identifier

    Returns:
        Milestone dict with current status or None if not found
    """
    milestones = get_contract_milestones(contract_id)
    return next((m for m in milestones if m["id"] == milestone_id), None)


def list_milestones(contract_id: str) -> list:
    """
    List milestones for contract.

    Args:
        contract_id: Contract identifier

    Returns:
        List of milestone dicts
    """
    return get_contract_milestones(contract_id)


def list_pending() -> list:
    """
    List all milestones awaiting verification (status=DELIVERED or submitted).

    Returns:
        List of milestone dicts
    """
    pending = []
    contracts = query_receipts("contract")
    for contract in contracts:
        contract_id = contract.get("contract_id")
        milestones = get_contract_milestones(contract_id)
        for m in milestones:
            if m.get("status") in ["DELIVERED", "submitted"]:
                pending.append({
                    "contract_id": contract_id,
                    "contractor": contract.get("contractor"),
                    **m
                })
    return pending


def list_verified() -> list:
    """
    List all milestones that have been verified (status=VERIFIED or verified).

    Returns:
        List of milestone dicts
    """
    verified = []
    contracts = query_receipts("contract")
    for contract in contracts:
        contract_id = contract.get("contract_id")
        milestones = get_contract_milestones(contract_id)
        for m in milestones:
            if m.get("status") in ["VERIFIED", "verified"]:
                verified.append({
                    "contract_id": contract_id,
                    "contractor": contract.get("contractor"),
                    **m
                })
    return verified


def list_disputed() -> list:
    """
    List all disputed milestones (status=DISPUTED or rejected).

    Returns:
        List of milestone dicts
    """
    disputed = []
    contracts = query_receipts("contract")
    for contract in contracts:
        contract_id = contract.get("contract_id")
        milestones = get_contract_milestones(contract_id)
        for m in milestones:
            if m.get("status") in ["DISPUTED", "rejected"]:
                disputed.append({
                    "contract_id": contract_id,
                    "contractor": contract.get("contractor"),
                    **m
                })
    return disputed


# === STOPRULES ===

def _stoprule_unknown_contract(contract_id: str) -> None:
    """Emit anomaly receipt for unknown contract."""
    from ..core import emit_receipt
    emit_receipt("anomaly", {
        "metric": "unknown_contract",
        "contract_id": contract_id,
        "delta": -1,
        "action": "reject",
        "classification": "violation",
    })
    raise StopRule(f"Unknown contract: {contract_id}")


def _stoprule_unknown_milestone(contract_id: str, milestone_id: str) -> None:
    """Emit anomaly receipt for unknown milestone."""
    from ..core import emit_receipt
    emit_receipt("anomaly", {
        "metric": "unknown_milestone",
        "contract_id": contract_id,
        "milestone_id": milestone_id,
        "delta": -1,
        "action": "reject",
        "classification": "violation",
    })
    raise StopRule(f"Unknown milestone: {milestone_id} in contract {contract_id}")


def _stoprule_already_verified(contract_id: str, milestone_id: str) -> None:
    """Emit anomaly receipt for already verified milestone."""
    from ..core import emit_receipt
    emit_receipt("anomaly", {
        "metric": "already_verified",
        "contract_id": contract_id,
        "milestone_id": milestone_id,
        "delta": -1,
        "action": "reject",
        "classification": "violation",
    })
    raise StopRule(f"Milestone already verified: {milestone_id} in contract {contract_id}")
