"""
SHIELDPROOF v2.1 Milestone Receipts - Milestone Receipt Emission

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY
"""

from ..core import emit_receipt, TENANT_ID


def emit_milestone_receipt(milestone: dict) -> dict:
    """
    Emit milestone_receipt using core/receipt.py.

    Args:
        milestone: Milestone data dict

    Returns:
        Milestone receipt

    milestone_receipt Schema:
    {
        "receipt_type": "milestone",
        "ts": str,
        "tenant_id": str,
        "payload_hash": str,
        "milestone_id": str,
        "contract_id": str,
        "deliverable_hash": str,
        "status": str,  # "submitted" | "verified" | "rejected" | "DELIVERED" | "VERIFIED" | "DISPUTED"
        "verifier_id": str | None,
        "metadata": dict
    }
    """
    return emit_receipt("milestone", {
        "tenant_id": milestone.get("tenant_id", TENANT_ID),
        "contract_id": milestone.get("contract_id"),
        "milestone_id": milestone.get("milestone_id"),
        "deliverable_hash": milestone.get("deliverable_hash"),
        "status": milestone.get("status"),
        "verifier_id": milestone.get("verifier_id"),
        "verification_ts": milestone.get("verification_ts"),
        "metadata": milestone.get("metadata", {}),
    })
