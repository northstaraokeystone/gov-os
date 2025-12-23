"""
SHIELDPROOF v2.1 Payment Receipts - Payment Receipt Emission

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY
"""

from ..core import emit_receipt, TENANT_ID


def emit_payment_receipt(payment: dict) -> dict:
    """
    Emit payment_receipt using core/receipt.py.

    Args:
        payment: Payment data dict

    Returns:
        Payment receipt

    payment_receipt Schema:
    {
        "receipt_type": "payment",
        "ts": str,
        "tenant_id": str,
        "payload_hash": str,
        "payment_id": str,
        "contract_id": str,
        "milestone_id": str,
        "amount_usd": float,
        "requestor_id": str,
        "total_paid_usd": float,  # Running total for contract
        "remaining_usd": float    # Contract total - total paid
    }
    """
    return emit_receipt("payment", {
        "tenant_id": payment.get("tenant_id", TENANT_ID),
        "contract_id": payment.get("contract_id"),
        "milestone_id": payment.get("milestone_id"),
        "amount": payment.get("amount", payment.get("amount_usd")),
        "amount_usd": payment.get("amount_usd", payment.get("amount")),
        "payment_hash": payment.get("payment_hash"),
        "released_at": payment.get("released_at"),
        "requestor_id": payment.get("requestor_id"),
        "total_paid_usd": payment.get("total_paid_usd"),
        "remaining_usd": payment.get("remaining_usd"),
    })
