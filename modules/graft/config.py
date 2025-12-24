"""
Gov-OS Graft Module Configuration - v6.3

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

v6.2 Changes:
- Added ROUND_TRIP_DETECTION for NGO round-trip funding detection
- Added FEC_CROSS_REFERENCE for political donation correlation
- Added round_trip_receipt to RECEIPT_TYPES

v6.3 Changes:
- Added TEMPORAL_CORRELATION_ENABLED for political timing pattern detection
- Added temporal_correlation_receipt to RECEIPT_TYPES
- Added event type weights for temporal analysis
"""

MODULE_ID = "graft"
MODULE_PRIORITY = 1  # P1 - Important
RECEIPT_TYPES = [
    "graft_proof",
    "case_chain",
    "corruption_detection",
    "round_trip_receipt",  # v6.2: Round-trip funding detection
    "temporal_correlation_receipt",  # v6.3: Political timing pattern detection
]

# v6.1: ZK disabled - public corruption data
ZK_ENABLED = False

# v6.2: Round-trip funding detection configuration
ROUND_TRIP_DETECTION = True  # Enable round-trip detection
FEC_CROSS_REFERENCE = True   # Enable FEC political donation cross-reference

# v6.2: Round-trip detection thresholds
ROUND_TRIP_THRESHOLD = 0.10  # Donation/award ratio threshold for flagging
TEMPORAL_CORRELATION_DAYS = 90  # Window for temporal correlation

# v6.2: Cross-domain links for round-trip detection
CROSS_MODULE_LINKS = ["aid", "spend", "origin"]

# v6.2: Data sources for graft detection
DATA_SOURCES = {
    "fec": "https://api.open.fec.gov/v1/",
    "fara": "https://efile.fara.gov/",
    "doj": "https://www.justice.gov/criminal/public-integrity",
}

# === v6.3 TEMPORAL CORRELATION CONFIGURATION ===

TEMPORAL_CORRELATION_ENABLED = True  # Enable temporal correlation analysis

# Event type weights for temporal analysis (v6.3)
# Higher weight = stronger signal
EVENT_TYPE_WEIGHTS = {
    "DOGE_RECOMMENDATION": 1.0,  # Highest weight
    "BUDGET_CUT": 0.8,
    "PERSONNEL_CHANGE": 0.6,
    "POLICY_ANNOUNCEMENT": 0.4,
    "OTHER": 0.2,
}

# Default correlation window
DEFAULT_TEMPORAL_WINDOW_DAYS = 90

# Minimum sample size for statistical significance
MIN_SAMPLE_SIZE = 10

DISCLAIMER = "THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY"
