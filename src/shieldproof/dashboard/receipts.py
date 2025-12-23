"""
SHIELDPROOF v2.1 Dashboard Receipts - Dashboard Receipt Emission

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY
"""

from ..core import emit_receipt, TENANT_ID


def emit_dashboard_receipt(export: dict) -> dict:
    """
    Emit dashboard_receipt using core/receipt.py.

    Args:
        export: Export data dict

    Returns:
        Dashboard receipt

    dashboard_receipt Schema:
    {
        "receipt_type": "dashboard",
        "ts": str,
        "tenant_id": str,
        "payload_hash": str,
        "export_format": str,
        "output_path": str,
        "contract_count": int,
        "total_value_usd": float,
        "total_paid_usd": float,
        "contracts_over_variance": int
    }
    """
    return emit_receipt("dashboard", {
        "tenant_id": export.get("tenant_id", TENANT_ID),
        "export_format": export.get("export_format"),
        "output_path": export.get("output_path"),
        "contract_count": export.get("contract_count", 0),
        "total_value_usd": export.get("total_value_usd", 0),
        "total_paid_usd": export.get("total_paid_usd", 0),
        "contracts_over_variance": export.get("contracts_over_variance", 0),
    })
