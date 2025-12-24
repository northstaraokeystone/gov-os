"""
Gov-OS Spend Module Configuration - v6.1

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY
"""

MODULE_ID = "spend"
MODULE_PRIORITY = 0  # P0 - Critical
RECEIPT_TYPES = ["spend_proof", "budget_verification", "audit_compress"]

# v6.1: ZK disabled - public spending data, no PII
ZK_ENABLED = False
