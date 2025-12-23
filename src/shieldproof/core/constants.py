"""
SHIELDPROOF v2.1 Core Constants - Universal Constants for All Modules

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY
"""

from pathlib import Path

# =============================================================================
# VERSION & IDENTITY
# =============================================================================
VERSION = "2.1.0"
TENANT_ID = "shieldproof"
DISCLAIMER = "THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY"

# =============================================================================
# RECEIPT TYPES (3 core, plus anomaly)
# =============================================================================
RECEIPT_TYPES = ["contract", "milestone", "payment", "anomaly", "variance", "dashboard", "anchor"]

# =============================================================================
# MILESTONE STATES
# =============================================================================
MILESTONE_STATES = ["PENDING", "DELIVERED", "VERIFIED", "PAID", "DISPUTED"]

# =============================================================================
# VARIANCE THRESHOLDS
# =============================================================================
VARIANCE_THRESHOLD = 0.05  # 5% variance triggers alert
VARIANCE_CRITICAL = 0.15   # 15% variance = critical

# =============================================================================
# ANCHORING
# =============================================================================
ANCHOR_BATCH_SIZE = 1000  # Receipts per Merkle batch

# =============================================================================
# GATE TIMELINES
# =============================================================================
GATE_T2H_SECONDS = 7200     # 2-hour challenge window
GATE_T24H_SECONDS = 86400   # 24-hour validation
GATE_T48H_SECONDS = 172800  # 48-hour finalization

# =============================================================================
# HASHING
# =============================================================================
HASH_ALGORITHM_PRIMARY = "SHA256"
HASH_ALGORITHM_SECONDARY = "BLAKE3"
HASH_FORMAT = "{sha256}:{blake3}"

# =============================================================================
# STORAGE
# =============================================================================
RECEIPT_STORAGE = "receipts.jsonl"
LEDGER_PATH = Path(__file__).parent.parent.parent.parent / "shieldproof_receipts.jsonl"

# =============================================================================
# SLO THRESHOLDS (realistic, not microsecond)
# =============================================================================
SLO_CONTRACT_REGISTER_MS = 100   # Contract registration <= 100ms
SLO_PAYMENT_RELEASE_MS = 200     # Payment release <= 200ms
SLO_DASHBOARD_EXPORT_MS = 2000   # Dashboard export <= 2s
SLO_MILESTONE_VERIFY_MS = 150    # Milestone verification <= 150ms

# Legacy SLO names (v2.0 compatibility)
RECEIPT_LATENCY_MS = 10.0       # Receipt emission
VERIFY_LATENCY_MS = 50.0        # Verification
DASHBOARD_REFRESH_S = 60.0      # Dashboard refresh

# =============================================================================
# MODULE IDS
# =============================================================================
MODULE_ID_CORE = "core"
MODULE_ID_CONTRACT = "contract"
MODULE_ID_MILESTONE = "milestone"
MODULE_ID_PAYMENT = "payment"
MODULE_ID_RECONCILE = "reconcile"
MODULE_ID_DASHBOARD = "dashboard"
MODULE_ID_SCENARIOS = "scenarios"
