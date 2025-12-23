"""
SHIELDPROOF v2.1 Dashboard Module - Public Audit Trail Generation

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

Public audit trail. Spending vs deliverables, redacted for OPSEC.
Per Grok: "Open audit trail" - transparency that doesn't compromise security.

"One receipt. One milestone. One truth."
"""

from .config import (
    MODULE_ID,
    EXPORT_FORMATS,
)

from .export import (
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
)

from .receipts import (
    emit_dashboard_receipt,
)

__all__ = [
    # Config
    "MODULE_ID",
    "EXPORT_FORMATS",
    # Export
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
    # Receipts
    "emit_dashboard_receipt",
]
