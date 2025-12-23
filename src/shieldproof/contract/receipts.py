"""
SHIELDPROOF v2.1 Contract Receipts - Contract Receipt Emission

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY
"""

from ..core import emit_receipt, TENANT_ID


def emit_contract_receipt(contract: dict) -> dict:
    """
    Emit contract_receipt using core/receipt.py.

    Args:
        contract: Contract data dict

    Returns:
        Contract receipt

    contract_receipt Schema:
    {
        "receipt_type": "contract",
        "ts": str,
        "tenant_id": str,
        "payload_hash": str,
        "contract_id": str,
        "contractor_name": str,
        "contract_type": str,
        "total_value_usd": float,
        "milestone_count": int,
        "start_date": str,
        "end_date": str
    }
    """
    return emit_receipt("contract", {
        "tenant_id": contract.get("tenant_id", TENANT_ID),
        "contract_id": contract.get("contract_id"),
        "contractor": contract.get("contractor"),
        "contractor_name": contract.get("contractor_name", contract.get("contractor")),
        "contract_type": contract.get("contract_type", "fixed-price"),
        "amount_fixed": contract.get("amount_fixed", contract.get("total_value_usd")),
        "total_value_usd": contract.get("total_value_usd", contract.get("amount_fixed")),
        "milestones": contract.get("milestones", []),
        "milestone_count": contract.get("milestone_count", len(contract.get("milestones", []))),
        "terms_hash": contract.get("terms_hash"),
        "start_date": contract.get("start_date"),
        "end_date": contract.get("end_date"),
    })
