"""
Gov-OS Benefit Module Configuration - v6.1

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY
"""

MODULE_ID = "benefit"
MODULE_PRIORITY = 0  # P0 - Critical
RECEIPT_TYPES = ["benefit_disburse", "beneficiary_verification", "fraud_compress"]

# v6.1: ZK ENABLED - Required: Contains beneficiary PII
ZK_ENABLED = True
