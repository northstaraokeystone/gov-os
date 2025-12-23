"""
SHIELDPROOF v2.1 Reconcile Receipts - Variance Receipt Emission

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY
"""

from ..core import emit_receipt, TENANT_ID


def emit_variance_receipt(variance_data: dict) -> dict:
    """
    Emit variance_receipt using core/receipt.py.

    Args:
        variance_data: Variance data dict

    Returns:
        Variance receipt

    variance_receipt Schema:
    {
        "receipt_type": "variance",
        "ts": str,
        "tenant_id": str,
        "payload_hash": str,
        "contract_id": str,
        "expected_spend_usd": float,
        "actual_spend_usd": float,
        "variance_pct": float,
        "threshold_pct": float,
        "severity": str  # "warning" | "critical"
    }
    """
    return emit_receipt("variance", {
        "tenant_id": variance_data.get("tenant_id", TENANT_ID),
        "contract_id": variance_data.get("contract_id"),
        "expected_spend_usd": variance_data.get("expected_spend_usd"),
        "actual_spend_usd": variance_data.get("actual_spend_usd"),
        "variance_pct": variance_data.get("variance_pct"),
        "threshold_pct": variance_data.get("threshold_pct"),
        "severity": variance_data.get("severity", "warning"),
    })
