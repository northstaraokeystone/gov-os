"""
Gov-OS Spend Module Configuration - v6.2

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

v6.2 Changes:
- Added USAID_LINKAGE for cross-reference with aid module
- Added cross-module links for round-trip detection
"""

MODULE_ID = "spend"
MODULE_PRIORITY = 0  # P0 - Critical
RECEIPT_TYPES = ["spend_proof", "budget_verification", "audit_compress"]

# v6.1: ZK disabled - public spending data, no PII
ZK_ENABLED = False

# v6.2: USAID cross-reference configuration
USAID_LINKAGE = True  # Enable USAID cross-reference with aid module

# v6.2: Cross-domain links
CROSS_MODULE_LINKS = ["aid", "graft", "origin"]

DISCLAIMER = "THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY"
