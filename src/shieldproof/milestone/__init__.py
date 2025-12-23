"""
SHIELDPROOF v2.1 Milestone Module - Deliverable Milestone Verification

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

Track milestone delivery and verification.
Per Grok: "Automated reconciliation" - verify deliverables before payment.

"One receipt. One milestone. One truth."
"""

from .config import (
    MODULE_ID,
    MILESTONE_STATES,
)

from .verify import (
    submit_milestone,
    submit_deliverable,
    verify_milestone,
    get_milestone,
    list_milestones,
    list_pending,
    list_verified,
    list_disputed,
)

from .receipts import (
    emit_milestone_receipt,
)

__all__ = [
    # Config
    "MODULE_ID",
    "MILESTONE_STATES",
    # Verify
    "submit_milestone",
    "submit_deliverable",
    "verify_milestone",
    "get_milestone",
    "list_milestones",
    "list_pending",
    "list_verified",
    "list_disputed",
    # Receipts
    "emit_milestone_receipt",
]
