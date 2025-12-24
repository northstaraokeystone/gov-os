"""
Gov-OS AidProof Module Configuration - v6.3

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

AidProof: Foreign aid accountability module for USAID, State, MCC, UN agencies
Priority: P1 (Important)

Political Hook:
Tests Musk's claim that "most USAID funding went to far left
political causes... including money coming back to fund the left
in America."

v6.3 Changes:
- Added UN agencies to AGENCIES list
- Added UN_PATHWAY_ENABLED, UN_VOLUNTARY_AGENCIES, UN_ROUND_TRIP_PATHWAY
- Added un_round_trip_receipt to RECEIPT_TYPES
"""

# === MODULE IDENTITY ===

MODULE_ID = "aid"
MODULE_PRIORITY = 1  # P1 - Important

# === ZK CONFIGURATION ===

ZK_ENABLED = False  # Public foreign aid data, no PII

# === RECEIPT TYPES ===

RECEIPT_TYPES = [
    "aid_ingest_receipt",
    "partner_ingest_receipt",
    "aid_verification_receipt",
    "round_trip_receipt",
    "un_round_trip_receipt",  # v6.3: UN pathway round-trip
    "overhead_receipt",
    "country_allocation_receipt",
    "aid_anomaly_receipt",
    "cross_reference_receipt",
]

# === DATA SOURCES ===

DATA_SOURCES = {
    "usaspending": "https://api.usaspending.gov/api/v2/",
    "foreignassistance": "https://api.foreignassistance.gov/v1/",
    "fec": "https://api.open.fec.gov/v1/",
    "propublica_990": "https://projects.propublica.org/nonprofits/api/v2/",
}

# === SUPPORTED AGENCIES ===

AGENCIES = [
    # Bilateral (v6.2)
    "USAID",
    "STATE",
    "MCC",
    "PEACE_CORPS",
    "TDA",
    "USTDA",
    # UN Agencies (v6.3 NEW)
    "UN_REGULAR",
    "UN_PEACEKEEPING",
    "UNICEF",
    "UNDP",
    "WFP",
    "UNHCR",
    "WHO",
    "UNFPA",
    "UNRWA",
]

# === v6.3 UN PATHWAY CONFIGURATION ===

UN_PATHWAY_ENABLED = True  # Enable UN→NGO round-trip detection
UN_VOLUNTARY_AGENCIES = [
    "UNICEF",
    "UNDP",
    "WFP",
    "UNHCR",
    "WHO",
    "UNFPA",
    "UNRWA",
]
UN_ROUND_TRIP_PATHWAY = "US_GOV → UN_AGENCY → US_NGO → FEC"  # Documentation of pathway

# === THRESHOLDS ===

# Compression threshold for NGO grants
IMPLEMENTING_PARTNER_THRESHOLD = 0.50

# Donation/award ratio flag threshold for round-trip detection
ROUND_TRIP_THRESHOLD = 0.10

# Overhead ratio threshold for admin cost flagging
OVERHEAD_RATIO_THRESHOLD = 0.40  # Flag if admin costs > 40% of total

# Temporal correlation window for round-trip detection
TEMPORAL_CORRELATION_DAYS = 90

# === CROSS-MODULE LINKS ===

CROSS_MODULE_LINKS = ["spend", "graft", "origin"]

# === CLAIM TYPES ===

CLAIM_TYPES = [
    "waste",        # Check compression ratios against baseline
    "round_trip",   # Check FEC correlation
    "overhead",     # Check admin cost ratios
    "country_allocation",  # Check country-level patterns
]

# === SIMULATION DISCLAIMER ===

DISCLAIMER = "THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY"
