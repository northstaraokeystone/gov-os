"""
Gov-OS DOGE Module - DOGE Efficiency Claims Verification

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

v6.1: "Receipts for DOGE" - Cryptographic validation of efficiency claims
using real USASpending data integration.
"""

from .config import (
    MODULE_ID,
    MODULE_PRIORITY,
    RECEIPT_TYPES,
    ZK_ENABLED,
    DOGE_CLAIM_SOURCES,
    DOGE_FRAUD_TARGETS,
    DOGE_DATA_COHORTS,
)

__all__ = [
    "MODULE_ID",
    "MODULE_PRIORITY",
    "RECEIPT_TYPES",
    "ZK_ENABLED",
    "DOGE_CLAIM_SOURCES",
    "DOGE_FRAUD_TARGETS",
    "DOGE_DATA_COHORTS",
]
