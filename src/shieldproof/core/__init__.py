"""
SHIELDPROOF v2.1 Core Module - Shared Infrastructure

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

This module provides the foundation for all SHIELDPROOF operations:
- constants: Universal constants for all modules
- utils: Core utility functions (dual_hash, merkle, StopRule)
- receipt: Receipt emission and validation
- ledger: Receipt storage and Merkle batching
- anchor: Dual-hash anchoring operations
- gate: T+2h/24h/48h gate logic

"One receipt. One milestone. One truth."
"""

from .constants import (
    TENANT_ID,
    VERSION,
    DISCLAIMER,
    RECEIPT_TYPES,
    MILESTONE_STATES,
    VARIANCE_THRESHOLD,
    VARIANCE_CRITICAL,
    ANCHOR_BATCH_SIZE,
    GATE_T2H_SECONDS,
    GATE_T24H_SECONDS,
    GATE_T48H_SECONDS,
    HASH_ALGORITHM_PRIMARY,
    HASH_ALGORITHM_SECONDARY,
    HASH_FORMAT,
    RECEIPT_STORAGE,
    LEDGER_PATH,
    SLO_CONTRACT_REGISTER_MS,
    SLO_PAYMENT_RELEASE_MS,
    SLO_DASHBOARD_EXPORT_MS,
    SLO_MILESTONE_VERIFY_MS,
    MODULE_ID_CORE,
    MODULE_ID_CONTRACT,
    MODULE_ID_MILESTONE,
    MODULE_ID_PAYMENT,
    MODULE_ID_RECONCILE,
    MODULE_ID_DASHBOARD,
    MODULE_ID_SCENARIOS,
)

from .utils import (
    dual_hash,
    merkle,
    StopRule,
    StopRuleException,
    validate_hash,
    timestamp_iso,
    generate_id,
)

from .receipt import (
    emit_receipt,
    validate_receipt,
    load_receipts,
    append_receipt,
)

from .ledger import (
    load_ledger,
    query_receipts,
    clear_ledger,
    get_ledger,
    add_to_ledger,
    anchor_batch,
    get_by_type,
    get_by_id,
)

from .anchor import (
    anchor_receipt,
    anchor_chain,
    verify_anchor,
)

from .gate import (
    check_t2h,
    check_t24h,
    check_t48h,
    gate_status,
)

__all__ = [
    # Constants
    "TENANT_ID",
    "VERSION",
    "DISCLAIMER",
    "RECEIPT_TYPES",
    "MILESTONE_STATES",
    "VARIANCE_THRESHOLD",
    "VARIANCE_CRITICAL",
    "ANCHOR_BATCH_SIZE",
    "GATE_T2H_SECONDS",
    "GATE_T24H_SECONDS",
    "GATE_T48H_SECONDS",
    "HASH_ALGORITHM_PRIMARY",
    "HASH_ALGORITHM_SECONDARY",
    "HASH_FORMAT",
    "RECEIPT_STORAGE",
    "LEDGER_PATH",
    "SLO_CONTRACT_REGISTER_MS",
    "SLO_PAYMENT_RELEASE_MS",
    "SLO_DASHBOARD_EXPORT_MS",
    "SLO_MILESTONE_VERIFY_MS",
    "MODULE_ID_CORE",
    "MODULE_ID_CONTRACT",
    "MODULE_ID_MILESTONE",
    "MODULE_ID_PAYMENT",
    "MODULE_ID_RECONCILE",
    "MODULE_ID_DASHBOARD",
    "MODULE_ID_SCENARIOS",
    # Utils
    "dual_hash",
    "merkle",
    "StopRule",
    "StopRuleException",
    "validate_hash",
    "timestamp_iso",
    "generate_id",
    # Receipt
    "emit_receipt",
    "validate_receipt",
    "load_receipts",
    "append_receipt",
    # Ledger
    "load_ledger",
    "query_receipts",
    "clear_ledger",
    "get_ledger",
    "add_to_ledger",
    "anchor_batch",
    "get_by_type",
    "get_by_id",
    # Anchor
    "anchor_receipt",
    "anchor_chain",
    "verify_anchor",
    # Gate
    "check_t2h",
    "check_t24h",
    "check_t48h",
    "gate_status",
]
