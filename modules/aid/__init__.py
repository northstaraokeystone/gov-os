"""
Gov-OS AidProof Module - Foreign Aid Accountability

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

v6.2 New Module:
- USAID, State Dept, MCC foreign aid accountability
- Round-trip funding detection (FEC cross-reference)
- Implementing partner analysis
- Country allocation pattern detection

Political Hook:
Tests Musk's claim that "most USAID funding went to far left
political causes... including money coming back to fund the left
in America."

The system is agnostic. The math is not.
"""

from .config import (
    MODULE_ID,
    MODULE_PRIORITY,
    ZK_ENABLED,
    RECEIPT_TYPES,
    DATA_SOURCES,
    AGENCIES,
    IMPLEMENTING_PARTNER_THRESHOLD,
    ROUND_TRIP_THRESHOLD,
    CROSS_MODULE_LINKS,
)

from .ingest import (
    ingest,
    ingest_usaid_awards,
    ingest_implementing_partners,
    ingest_country_allocations,
)

from .verify import (
    verify,
    verify_aid_claim,
    detect_round_trip,
    calculate_overhead_ratio,
    compare_to_baseline,
)

from .receipts import (
    AidIngestReceipt,
    PartnerIngestReceipt,
    AidVerificationReceipt,
    RoundTripReceipt,
    OverheadReceipt,
    CountryAllocationReceipt,
    AidAnomalyReceipt,
    CrossReferenceReceipt,
)

from .data import (
    AidAward,
    ImplementingPartner,
    RoundTripEvidence,
)

from .scenario import (
    run_aid_scenario,
    SCENARIOS,
)

__all__ = [
    # Config
    "MODULE_ID",
    "MODULE_PRIORITY",
    "ZK_ENABLED",
    "RECEIPT_TYPES",
    "DATA_SOURCES",
    "AGENCIES",
    "IMPLEMENTING_PARTNER_THRESHOLD",
    "ROUND_TRIP_THRESHOLD",
    "CROSS_MODULE_LINKS",
    # Ingest
    "ingest",
    "ingest_usaid_awards",
    "ingest_implementing_partners",
    "ingest_country_allocations",
    # Verify
    "verify",
    "verify_aid_claim",
    "detect_round_trip",
    "calculate_overhead_ratio",
    "compare_to_baseline",
    # Receipts
    "AidIngestReceipt",
    "PartnerIngestReceipt",
    "AidVerificationReceipt",
    "RoundTripReceipt",
    "OverheadReceipt",
    "CountryAllocationReceipt",
    "AidAnomalyReceipt",
    "CrossReferenceReceipt",
    # Data
    "AidAward",
    "ImplementingPartner",
    "RoundTripEvidence",
    # Scenario
    "run_aid_scenario",
    "SCENARIOS",
]
