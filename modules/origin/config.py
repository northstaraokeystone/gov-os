"""
Gov-OS Origin Module Configuration - v6.2

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

v6.2 Changes:
- Added IMPLEMENTING_PARTNER_TRACKING for NGO supply chain tracking
- Added cross-module links for round-trip detection
"""

MODULE_ID = "origin"
MODULE_PRIORITY = 1  # P1 - Important
RECEIPT_TYPES = [
    "origin_chain",
    "supply_chain_verification",
    "counterfeit_detection",
    "implementing_partner_receipt",  # v6.2: NGO partner tracking
]

# v6.1: ZK disabled - supply chain metadata
ZK_ENABLED = False

# v6.2: Implementing partner tracking
IMPLEMENTING_PARTNER_TRACKING = True  # Track NGO implementing partner supply chains

# v6.2: Cross-domain links
CROSS_MODULE_LINKS = ["aid", "spend", "graft"]

DISCLAIMER = "THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY"
