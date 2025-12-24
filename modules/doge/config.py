"""
Gov-OS DOGE Module Configuration - v6.1

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

v6.1 Changes:
- Added DOGE_CLAIM_SOURCES for official savings claims
- Added DOGE_FRAUD_TARGETS for target fraud categories
- Added DOGE_DATA_COHORTS for validation cohorts
- ZK_ENABLED = False (public spending data, no PII)
"""

# === MODULE IDENTITY ===

MODULE_ID = "doge"
MODULE_PRIORITY = 0  # P0 - Critical
RECEIPT_TYPES = [
    "doge_proof",
    "doge_validation",
    "doge_claim",
    "efficiency_claim",
]

# === v6.1 ZK CONFIGURATION ===

ZK_ENABLED = False  # No PII in this module - public spending data

# === v6.1 DOGE CLAIM SOURCES ===
# Official DOGE savings claims for validation

DOGE_CLAIM_SOURCES = {
    "160B_savings_2025": {
        "claimed_amount": 160_000_000_000,  # $160B
        "claimed_cost_savings": 135_000_000_000,  # $135B in actual cuts
        "source": "Elon Musk X post, Nov 2024",
        "categories": ["medicaid", "real_estate", "dod_contracts"],
        "date": "2024-11-12",
        "url": "https://x.com/elonmusk",
    },
    "100B_medicaid_2024": {
        "claimed_amount": 100_000_000_000,  # $100B
        "claimed_cost_savings": 100_000_000_000,
        "source": "GAO High-Risk Series / DOGE analysis",
        "categories": ["medicaid"],
        "date": "2024",
        "url": "https://www.gao.gov/highrisk",
    },
    "7B_real_estate_2024": {
        "claimed_amount": 7_400_000_000,  # $7.4B
        "claimed_cost_savings": 7_400_000_000,
        "source": "GSA Federal Real Property Profile 2024",
        "categories": ["real_estate"],
        "date": "2024",
        "url": "https://www.gsa.gov",
    },
    # v6.2: USAID waste claim for round-trip detection
    "usaid_waste": {
        "claimed_amount": "unspecified",
        "source": "Elon Musk X post, Dec 2024",
        "claim": "Most USAID funding went to far left political causes, including money coming back to fund the left in America",
        "categories": ["foreign_aid", "round_trip"],
        "date": "2024-12",
        "url": "https://x.com/elonmusk",
        "testable_hypothesis": "Round-trip funding detectable via FEC cross-reference",
        "methodology": "implementing_partner_fec_correlation",
    },
}

# === v6.1 DOGE FRAUD TARGETS ===
# Target fraud categories with estimated annual exposure

DOGE_FRAUD_TARGETS = {
    "medicaid_improper": {
        "estimated_annual": 100_000_000_000,  # $100B
        "source": "GAO-24-106541",
        "cohort": "doge_medicaid",
        "description": "Medicaid improper payments including fraud, waste, abuse",
    },
    "federal_real_estate": {
        "estimated_annual": 7_400_000_000,  # $7.4B
        "source": "GSA occupancy report 2024",
        "occupancy_rate": 0.12,  # 12% average occupancy
        "cohort": "federal_real_estate",
        "description": "Underutilized federal real estate leases",
    },
    "dod_sole_source": {
        "estimated_annual": 5_000_000_000,  # $5B
        "source": "DoD IG Report 2024",
        "cohort": "dod_transdigm",
        "description": "DoD sole-source contract overpricing (TransDigm pattern)",
    },
    "navy_husbanding": {
        "estimated_annual": 500_000_000,  # $500M
        "source": "DOJ Fat Leonard prosecution",
        "cohort": "fat_leonard",
        "description": "Navy husbanding contract fraud pattern",
    },
}

# === v6.1 DOGE DATA COHORTS ===
# Which cohorts to use for claim validation

DOGE_DATA_COHORTS = [
    "doge_medicaid",
    "dod_transdigm",
    "fat_leonard",
    "federal_real_estate",
    "dod_shipbuilding",
    # v6.2: USAID cohorts for round-trip detection
    "usaid_implementing_partners",
    "usaid_direct_country",
    "state_dept_foreign_assistance",
]

# === SIMULATION DISCLAIMER ===

DISCLAIMER = "THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY"
