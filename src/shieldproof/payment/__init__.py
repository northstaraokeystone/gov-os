"""
SHIELDPROOF v2.1 Payment Module - Payment Release with Stoprule Enforcement

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

Release payment ONLY on verified milestone.
Per Grok: "On-chain payment release" - payment follows verification, never before.

"One receipt. One milestone. One truth."
"""

from .config import (
    MODULE_ID,
    REQUIRE_VERIFIED_MILESTONE,
)

from .release import (
    request_payment,
    release_payment,
    get_payment,
    get_payments,
    list_payments,
    total_paid,
    total_outstanding,
)

from .receipts import (
    emit_payment_receipt,
)

__all__ = [
    # Config
    "MODULE_ID",
    "REQUIRE_VERIFIED_MILESTONE",
    # Release
    "request_payment",
    "release_payment",
    "get_payment",
    "get_payments",
    "list_payments",
    "total_paid",
    "total_outstanding",
    # Receipts
    "emit_payment_receipt",
]
