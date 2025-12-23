"""
SHIELDPROOF v2.1 - Defense Contract Accountability System

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

The paradigm: Fixed-price contracts with receipts-native accountability.
No receipt -> not real. No verified milestone -> no payment.

v2.1 Changes:
- Modular directory structure (src/shieldproof/core/, contract/, milestone/, etc.)
- Added scenarios/ for cross-module integration tests
- Added variance receipt type for cost-plus drift detection
- Added dashboard receipt for audit trail generation
- Backward compatible with v2.0 API

Components (3, not 20):
1. Immutable Receipts (contract, milestone, payment)
2. Automated Reconciliation
3. Public Audit Trail

"One receipt. One milestone. One truth."
"""

__version__ = "2.1.0"

# === CORE MODULE (v2.1 modular structure) ===
from .core import (
    # Constants
    TENANT_ID,
    VERSION,
    DISCLAIMER,
    RECEIPT_TYPES,
    MILESTONE_STATES,
    VARIANCE_THRESHOLD,
    LEDGER_PATH,
    # Utils
    dual_hash,
    merkle,
    StopRule,
    StopRuleException,
    validate_hash,
    timestamp_iso,
    generate_id,
    # Receipt
    emit_receipt,
    validate_receipt,
    load_receipts,
    append_receipt,
    # Ledger
    load_ledger,
    query_receipts,
    clear_ledger,
    get_ledger,
    add_to_ledger,
    anchor_batch,
    get_by_type,
    get_by_id,
    # Anchor
    anchor_receipt,
    anchor_chain,
    verify_anchor,
    # Gate
    check_t2h,
    check_t24h,
    check_t48h,
    gate_status,
)

# === CONTRACT MODULE ===
from .contract import (
    register_contract,
    get_contract,
    list_contracts,
    get_contract_milestones,
    update_contract,
    emit_contract_receipt,
)

# === MILESTONE MODULE ===
from .milestone import (
    submit_milestone,
    submit_deliverable,
    verify_milestone,
    get_milestone,
    list_milestones,
    list_pending,
    list_verified,
    list_disputed,
    emit_milestone_receipt,
)

# === PAYMENT MODULE ===
from .payment import (
    request_payment,
    release_payment,
    get_payment,
    get_payments,
    list_payments,
    total_paid,
    total_outstanding,
    emit_payment_receipt,
)

# === RECONCILE MODULE ===
from .reconcile import (
    check_variance,
    variance_report,
    flag_contracts,
    reconcile_contract,
    reconcile_all,
    flag_anomaly,
    get_waste_summary,
    emit_variance_receipt,
)

# === DASHBOARD MODULE ===
from .dashboard import (
    export_dashboard,
    dashboard_summary,
    contracts_by_status,
    generate_summary,
    contract_status,
    export_csv,
    export_json,
    format_currency,
    print_dashboard,
    serve,
    check,
    emit_dashboard_receipt,
)

# === SCENARIOS MODULE ===
from .scenarios import (
    run_baseline_scenario,
    run_stress_scenario,
)

__all__ = [
    # Version
    "__version__",
    # Core Constants
    "TENANT_ID",
    "VERSION",
    "DISCLAIMER",
    "RECEIPT_TYPES",
    "MILESTONE_STATES",
    "VARIANCE_THRESHOLD",
    "LEDGER_PATH",
    # Core Utils
    "dual_hash",
    "merkle",
    "StopRule",
    "StopRuleException",
    "validate_hash",
    "timestamp_iso",
    "generate_id",
    # Core Receipt
    "emit_receipt",
    "validate_receipt",
    "load_receipts",
    "append_receipt",
    # Core Ledger
    "load_ledger",
    "query_receipts",
    "clear_ledger",
    "get_ledger",
    "add_to_ledger",
    "anchor_batch",
    "get_by_type",
    "get_by_id",
    # Core Anchor
    "anchor_receipt",
    "anchor_chain",
    "verify_anchor",
    # Core Gate
    "check_t2h",
    "check_t24h",
    "check_t48h",
    "gate_status",
    # Contract
    "register_contract",
    "get_contract",
    "list_contracts",
    "get_contract_milestones",
    "update_contract",
    "emit_contract_receipt",
    # Milestone
    "submit_milestone",
    "submit_deliverable",
    "verify_milestone",
    "get_milestone",
    "list_milestones",
    "list_pending",
    "list_verified",
    "list_disputed",
    "emit_milestone_receipt",
    # Payment
    "request_payment",
    "release_payment",
    "get_payment",
    "get_payments",
    "list_payments",
    "total_paid",
    "total_outstanding",
    "emit_payment_receipt",
    # Reconcile
    "check_variance",
    "variance_report",
    "flag_contracts",
    "reconcile_contract",
    "reconcile_all",
    "flag_anomaly",
    "get_waste_summary",
    "emit_variance_receipt",
    # Dashboard
    "export_dashboard",
    "dashboard_summary",
    "contracts_by_status",
    "generate_summary",
    "contract_status",
    "export_csv",
    "export_json",
    "format_currency",
    "print_dashboard",
    "serve",
    "check",
    "emit_dashboard_receipt",
    # Scenarios
    "run_baseline_scenario",
    "run_stress_scenario",
]
