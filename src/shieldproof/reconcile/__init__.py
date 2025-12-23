"""
SHIELDPROOF v2.1 Reconcile Module - Variance Detection (Cost-Plus Drift)

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

Automated reconciliation of spending vs deliverables.
Per Grok: "Automated reconciliation" - detect waste before it happens.

"One receipt. One milestone. One truth."
"""

from .config import (
    MODULE_ID,
    VARIANCE_THRESHOLD,
    VARIANCE_CRITICAL,
)

from .variance import (
    check_variance,
    variance_report,
    flag_contracts,
    reconcile_contract,
    reconcile_all,
    flag_anomaly,
    get_waste_summary,
)

from .receipts import (
    emit_variance_receipt,
)

__all__ = [
    # Config
    "MODULE_ID",
    "VARIANCE_THRESHOLD",
    "VARIANCE_CRITICAL",
    # Variance
    "check_variance",
    "variance_report",
    "flag_contracts",
    "reconcile_contract",
    "reconcile_all",
    "flag_anomaly",
    "get_waste_summary",
    # Receipts
    "emit_variance_receipt",
]
