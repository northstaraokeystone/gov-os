"""
SHIELDPROOF v2.1 Contract Register - Contract Registration Functions

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY
"""

import json
import uuid
from typing import Optional

from ..core import dual_hash, query_receipts, StopRule
from .receipts import emit_contract_receipt


def register_contract(
    contractor: str,
    amount: float,
    milestones: list,
    terms: dict,
    contract_id: Optional[str] = None,
    contract_type: str = "fixed-price",
) -> dict:
    """
    Register a fixed-price contract with milestone definitions.

    Args:
        contractor: Name of contractor
        amount: Total fixed-price amount
        milestones: List of milestone dicts with id, description, amount, due_date
        terms: Contract terms dict (will be hashed)
        contract_id: Optional contract ID (generated if not provided)
        contract_type: Contract type (default: fixed-price)

    Returns:
        contract_receipt

    Stoprules:
        - stoprule_duplicate_contract: If contract_id already exists
        - stoprule_invalid_amount: If amount <= 0 or milestones don't sum to amount
    """
    if contract_id is None:
        contract_id = f"C-{uuid.uuid4().hex[:12].upper()}"

    # Stoprule: Check for duplicate
    existing = query_receipts("contract", contract_id=contract_id)
    if existing:
        _stoprule_duplicate_contract(contract_id)

    # Stoprule: Validate amount
    if amount <= 0:
        _stoprule_invalid_amount(contract_id, "Amount must be positive")

    # Stoprule: Validate milestones sum to amount
    milestone_sum = sum(m.get("amount", 0) for m in milestones)
    if abs(milestone_sum - amount) > 0.01:  # Allow for floating point tolerance
        _stoprule_invalid_amount(
            contract_id,
            f"Milestone sum ({milestone_sum}) does not equal contract amount ({amount})"
        )

    # Normalize milestones with PENDING status
    normalized_milestones = []
    for m in milestones:
        normalized_milestones.append({
            "id": m.get("id", f"M{len(normalized_milestones)+1}"),
            "description": m.get("description", ""),
            "amount": m.get("amount", 0),
            "due_date": m.get("due_date"),
            "status": "PENDING",
        })

    # Create contract receipt
    receipt = emit_contract_receipt({
        "contract_id": contract_id,
        "contractor": contractor,
        "contractor_name": contractor,  # v2.1 field name
        "contract_type": contract_type,
        "amount_fixed": amount,
        "total_value_usd": amount,  # v2.1 field name
        "milestones": normalized_milestones,
        "milestone_count": len(normalized_milestones),
        "terms_hash": dual_hash(json.dumps(terms, sort_keys=True)),
        "start_date": terms.get("start_date"),
        "end_date": terms.get("end_date"),
    })

    return receipt


def get_contract(contract_id: str) -> Optional[dict]:
    """
    Retrieve contract by ID.

    Args:
        contract_id: Contract identifier

    Returns:
        Contract receipt or None if not found
    """
    contracts = query_receipts("contract", contract_id=contract_id)
    if not contracts:
        return None
    # Return the most recent contract receipt (in case of updates)
    return contracts[-1]


def list_contracts(status: Optional[str] = None, contract_type: Optional[str] = None) -> list:
    """
    List all contracts, optionally filtered by milestone status or contract type.

    Args:
        status: Optional milestone status filter
        contract_type: Optional contract type filter

    Returns:
        List of contract receipts
    """
    contracts = query_receipts("contract")

    if contract_type is not None:
        contracts = [c for c in contracts if c.get("contract_type") == contract_type]

    if status is None:
        return contracts

    # Filter by contracts that have at least one milestone with the given status
    filtered = []
    for contract in contracts:
        milestones = contract.get("milestones", [])
        if any(m.get("status") == status for m in milestones):
            filtered.append(contract)

    return filtered


def get_contract_milestones(contract_id: str) -> list:
    """
    Get current milestone states for a contract.
    Merges original contract milestones with any milestone receipts.

    Args:
        contract_id: Contract identifier

    Returns:
        List of milestone dicts with current status
    """
    contract = get_contract(contract_id)
    if not contract:
        return []

    # Start with contract milestones
    milestones = {m["id"]: m.copy() for m in contract.get("milestones", [])}

    # Update with milestone receipts
    milestone_receipts = query_receipts("milestone", contract_id=contract_id)
    for mr in milestone_receipts:
        mid = mr.get("milestone_id")
        if mid in milestones:
            milestones[mid]["status"] = mr.get("status", milestones[mid]["status"])
            if mr.get("deliverable_hash"):
                milestones[mid]["deliverable_hash"] = mr["deliverable_hash"]
            if mr.get("verifier_id"):
                milestones[mid]["verifier_id"] = mr["verifier_id"]
            if mr.get("verification_ts"):
                milestones[mid]["verification_ts"] = mr["verification_ts"]

    return list(milestones.values())


def update_contract(contract_id: str, updates: dict) -> dict:
    """
    Update contract (emits new receipt with updates).

    Args:
        contract_id: Contract identifier
        updates: Fields to update

    Returns:
        Updated contract receipt
    """
    contract = get_contract(contract_id)
    if not contract:
        _stoprule_unknown_contract(contract_id)

    # Merge updates
    updated = {**contract, **updates, "contract_id": contract_id}

    # Emit new receipt
    receipt = emit_contract_receipt(updated)
    return receipt


# === STOPRULES ===

def _stoprule_duplicate_contract(contract_id: str) -> None:
    """Emit anomaly receipt for duplicate contract."""
    from ..core import emit_receipt
    emit_receipt("anomaly", {
        "metric": "duplicate_contract",
        "contract_id": contract_id,
        "delta": -1,
        "action": "reject",
        "classification": "violation",
    })
    raise StopRule(f"Duplicate contract: {contract_id} already exists")


def _stoprule_invalid_amount(contract_id: str, reason: str) -> None:
    """Emit anomaly receipt for invalid amount."""
    from ..core import emit_receipt
    emit_receipt("anomaly", {
        "metric": "invalid_amount",
        "contract_id": contract_id,
        "reason": reason,
        "delta": -1,
        "action": "reject",
        "classification": "violation",
    })
    raise StopRule(f"Invalid amount for {contract_id}: {reason}")


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
