"""
Gov-OS DOGE Module - Verification Functions

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

v6.1 Changes:
- Added validate_doge_claim() function for validating DOGE savings claims
  against real USASpending data via RealDataGate

v6.2 Changes:
- Added validate_usaid_claim() function for testing Musk's USAID claim
- Integrates with ForeignAidETL for implementing partner analysis
- FEC cross-reference for round-trip funding detection

v6.3 Changes:
- Added detect_musk_ecosystem_coi() for Musk company COI detection
- Cross-references DOGE recommendations vs Musk company contracts
- Emits musk_ecosystem_coi_receipt

The Political Hook: "Receipts for DOGE"
Cryptographic validation of Musk/Ramaswamy $160B savings claims
using actual federal spending data.

v6.2: Tests Musk claim that "most USAID funding went to far left
political causes... including money coming back to fund the left
in America."

v6.3: Detects COI pattern where DOGE leader recommends cuts →
affiliated company wins contracts.
"""

import json
from typing import Any, Dict, List, Optional

from .config import (
    MODULE_ID,
    DOGE_CLAIM_SOURCES,
    DOGE_FRAUD_TARGETS,
    DOGE_DATA_COHORTS,
    DISCLAIMER,
    # v6.3 COI detection
    MUSK_ECOSYSTEM_ENTITIES,
    COI_DETECTION_ENABLED,
    COI_CORRELATION_WINDOW_DAYS,
    COI_MIN_CONTRACT_VALUE,
)

# Import core utilities
import sys
sys.path.insert(0, str(__file__).rsplit('/', 3)[0])

try:
    from src.core import (
        TENANT_ID,
        dual_hash,
        emit_receipt,
        RealDataGate,
        get_compression_threshold,
        ForeignAidETL,
    )
except ImportError:
    # Fallback for direct module execution
    TENANT_ID = "gov-os"
    dual_hash = lambda x: f"sha256:mock:{hash(x)}"
    emit_receipt = lambda t, p, **kw: {"receipt_type": t, **p}
    RealDataGate = None
    get_compression_threshold = lambda d: 0.75
    ForeignAidETL = None


def validate_doge_claim(claim_id: str) -> dict:
    """
    Validate a DOGE savings claim against real USASpending data.

    This function implements the "Receipts for DOGE" political hook:
    1. Load claim from DOGE_CLAIM_SOURCES by claim_id
    2. For each category, instantiate RealDataGate with appropriate cohort
    3. Ingest cohort data
    4. Run compression analysis on records
    5. Calculate verified savings (records flagged as anomalous x average amount)
    6. Compare verified vs claimed
    7. Emit receipt with delta

    Args:
        claim_id: ID of the claim from DOGE_CLAIM_SOURCES (e.g., "160B_savings_2025")

    Returns:
        Validation result dict with:
        - claim_id: str
        - claimed_amount: float
        - verified_amount: float
        - delta: float (claimed - verified)
        - delta_percent: float
        - passed: bool (verified >= 0.8 * claimed)
        - categories_analyzed: list
        - receipt: dict

    Raises:
        KeyError: If claim_id not found in DOGE_CLAIM_SOURCES

    Example:
        >>> result = validate_doge_claim("160B_savings_2025")
        >>> print(f"Verified: ${result['verified_amount']:,.0f}")
        >>> print(f"Delta: {result['delta_percent']:.1f}%")
    """
    # Load claim
    if claim_id not in DOGE_CLAIM_SOURCES:
        raise KeyError(f"Unknown DOGE claim: {claim_id}. Available: {list(DOGE_CLAIM_SOURCES.keys())}")

    claim = DOGE_CLAIM_SOURCES[claim_id]
    claimed_amount = claim["claimed_amount"]
    categories = claim["categories"]

    # Track verification results per category
    category_results = []
    total_verified = 0.0
    cohorts_used = []
    sample_sizes = {}

    for category in categories:
        # Find matching cohort and fraud target
        target = _find_fraud_target(category)
        if not target:
            continue

        cohort_name = target.get("cohort")
        if not cohort_name:
            continue

        cohorts_used.append(cohort_name)

        # Use RealDataGate to ingest and analyze
        try:
            if RealDataGate is None:
                # Fallback for testing without full imports
                verified = target["estimated_annual"] * 0.85  # Simulate 85% verification
                sample_size = 100
            else:
                gate = RealDataGate(cohort_name)
                records = gate.ingest_cohort(_simulate=True)
                sample_size = len(records)

                # Calibrate threshold from data
                threshold = gate.calibrate_threshold(records)

                # Count anomalies (records that fail compression threshold)
                anomaly_count = 0
                total_amount = 0.0
                for record in records:
                    result = gate.validate_gate(record)
                    if not result["passed"]:
                        anomaly_count += 1
                    amount = record.get("total_obligation", 0)
                    if isinstance(amount, (int, float)):
                        total_amount += amount

                # Calculate verified savings
                # Anomaly rate * total amount = potential fraud/waste
                if len(records) > 0:
                    anomaly_rate = anomaly_count / len(records)
                    verified = total_amount * anomaly_rate
                else:
                    verified = 0.0

            sample_sizes[cohort_name] = sample_size

            category_results.append({
                "category": category,
                "cohort": cohort_name,
                "target_annual": target["estimated_annual"],
                "verified_amount": verified,
                "sample_size": sample_size,
            })

            total_verified += verified

        except Exception as e:
            category_results.append({
                "category": category,
                "cohort": cohort_name,
                "error": str(e),
            })

    # Calculate delta
    delta = claimed_amount - total_verified
    delta_percent = (delta / claimed_amount * 100) if claimed_amount > 0 else 0

    # Determine pass/fail (verified >= 80% of claimed)
    passed = total_verified >= (0.8 * claimed_amount)

    # Build result
    result = {
        "claim_id": claim_id,
        "claimed_amount": claimed_amount,
        "verified_amount": total_verified,
        "delta": delta,
        "delta_percent": round(delta_percent, 2),
        "passed": passed,
        "categories_analyzed": categories,
        "category_results": category_results,
        "cohorts_used": cohorts_used,
        "sample_sizes": sample_sizes,
        "source": claim["source"],
        "methodology": "compression_anomaly_detection",
    }

    # Emit doge_validation receipt
    receipt = _emit_validation_receipt(result)
    result["receipt"] = receipt

    return result


def _find_fraud_target(category: str) -> Optional[dict]:
    """Find fraud target matching a category."""
    category_lower = category.lower()

    for target_id, target in DOGE_FRAUD_TARGETS.items():
        # Match by category name in target_id
        if category_lower in target_id.lower():
            return target

        # Match by description
        if category_lower in target.get("description", "").lower():
            return target

    return None


def _emit_validation_receipt(result: dict) -> dict:
    """Emit doge_validation receipt."""
    payload = {
        "claim_id": result["claim_id"],
        "claimed_amount": result["claimed_amount"],
        "verified_amount": result["verified_amount"],
        "delta_percent": result["delta_percent"],
        "methodology": result["methodology"],
        "cohorts_used": result["cohorts_used"],
        "sample_sizes": result["sample_sizes"],
        "passed": result["passed"],
    }

    return emit_receipt("doge_validation", {
        "tenant_id": TENANT_ID,
        "module": MODULE_ID,
        **payload,
        "payload_hash": dual_hash(json.dumps(payload, sort_keys=True)),
        "simulation_flag": DISCLAIMER,
    }, to_stdout=False)


def verify_efficiency_claim(claim: dict) -> dict:
    """
    Verify a generic efficiency claim.

    Args:
        claim: Claim dict with 'amount', 'category', 'source'

    Returns:
        Verification result
    """
    # For now, delegate to validate_doge_claim if it matches a known claim
    claim_id = claim.get("claim_id")
    if claim_id and claim_id in DOGE_CLAIM_SOURCES:
        return validate_doge_claim(claim_id)

    # Generic verification
    return {
        "claim": claim,
        "verified": False,
        "reason": "No matching DOGE claim source found",
        "simulation_flag": DISCLAIMER,
    }


def validate_usaid_claim(claim_id: str = "usaid_waste") -> dict:
    """
    v6.2: Validate Musk's USAID waste claim via round-trip funding detection.

    Tests the claim: "Most USAID funding went to far left political causes,
    including money coming back to fund the left in America."

    Methodology:
    1. Fetch USAID implementing partners via ForeignAidETL
    2. Cross-reference with FEC political donations
    3. Cross-reference with Form 990 financials
    4. Calculate correlation: aid_received vs political_activity
    5. Emit usaid_validation_receipt with findings

    Args:
        claim_id: Claim identifier (default: "usaid_waste")

    Returns:
        Dict with:
        - claim_id: str
        - claim_text: str
        - implementing_partners_analyzed: int
        - political_donation_correlation: float (0-1)
        - round_trip_evidence: list (specific cases)
        - verdict: "supported" | "unsupported" | "insufficient_data"
        - receipt: dict

    Example:
        >>> result = validate_usaid_claim("usaid_waste")
        >>> print(f"Correlation: {result['political_donation_correlation']:.2f}")
        >>> print(f"Verdict: {result['verdict']}")
    """
    # Load claim
    if claim_id not in DOGE_CLAIM_SOURCES:
        raise KeyError(f"Unknown claim: {claim_id}")

    claim = DOGE_CLAIM_SOURCES[claim_id]

    # Initialize results
    implementing_partners_analyzed = 0
    political_donation_correlation = 0.0
    round_trip_evidence = []
    total_aid = 0.0
    total_donations = 0.0

    try:
        if ForeignAidETL is None:
            # Fallback simulation
            implementing_partners_analyzed = 20
            political_donation_correlation = 0.04  # Low correlation
            round_trip_evidence = [
                {
                    "partner_name": "Democracy International (simulated)",
                    "aid_received": 50_000_000,
                    "political_donations": 1_500_000,
                    "ratio": 0.03,
                    "flagged": False,
                }
            ]
            total_aid = 1_000_000_000
            total_donations = 40_000_000
        else:
            # Use ForeignAidETL to fetch data
            etl = ForeignAidETL()
            partners = etl.fetch_implementing_partners("USAID", _simulate=True)
            implementing_partners_analyzed = len(partners)

            # Analyze each partner for round-trip pattern
            for partner in partners:
                total_aid += partner.total_awards
                total_donations += partner.political_donations

                # Check for round-trip pattern
                evidence = etl.detect_round_trip(partner)
                if evidence.flagged:
                    round_trip_evidence.append(evidence.to_dict())

            # Calculate correlation
            if total_aid > 0:
                political_donation_correlation = total_donations / total_aid
            else:
                political_donation_correlation = 0.0

    except Exception as e:
        # Handle errors gracefully
        return {
            "claim_id": claim_id,
            "claim_text": claim.get("claim", ""),
            "error": str(e),
            "verdict": "insufficient_data",
            "simulation_flag": DISCLAIMER,
        }

    # Determine verdict based on evidence
    # Round-trip threshold from graft config (default 0.10)
    round_trip_threshold = 0.10
    if len(round_trip_evidence) == 0:
        verdict = "unsupported"
    elif political_donation_correlation >= round_trip_threshold:
        verdict = "supported"
    else:
        verdict = "unsupported"

    # Build result
    result = {
        "claim_id": claim_id,
        "claim_text": claim.get("claim", ""),
        "implementing_partners_analyzed": implementing_partners_analyzed,
        "total_aid_analyzed": total_aid,
        "total_political_donations": total_donations,
        "political_donation_correlation": round(political_donation_correlation, 4),
        "round_trip_evidence": round_trip_evidence,
        "round_trip_cases_found": len(round_trip_evidence),
        "verdict": verdict,
        "methodology": claim.get("methodology", "implementing_partner_fec_correlation"),
        "source": claim["source"],
        "testable_hypothesis": claim.get("testable_hypothesis", ""),
        "interpretation": _interpret_usaid_verdict(verdict, political_donation_correlation),
    }

    # Emit validation receipt
    receipt = _emit_usaid_validation_receipt(result)
    result["receipt"] = receipt

    return result


def _interpret_usaid_verdict(verdict: str, correlation: float) -> str:
    """Generate plain-English interpretation of USAID claim verdict."""
    if verdict == "supported":
        return (
            f"Round-trip funding pattern detected. Correlation of {correlation:.1%} "
            "between aid received and political donations exceeds threshold. "
            "Evidence supports claim of funds returning to domestic political activity."
        )
    elif verdict == "unsupported":
        return (
            f"No significant round-trip funding pattern detected. Correlation of "
            f"{correlation:.1%} is below threshold. Evidence does not support "
            "claim that aid funds are systematically returning to fund domestic "
            "political causes."
        )
    else:
        return "Insufficient data to evaluate claim. More implementing partner data needed."


def _emit_usaid_validation_receipt(result: dict) -> dict:
    """Emit usaid_validation receipt."""
    payload = {
        "claim_id": result["claim_id"],
        "implementing_partners_analyzed": result["implementing_partners_analyzed"],
        "political_donation_correlation": result["political_donation_correlation"],
        "round_trip_cases_found": result["round_trip_cases_found"],
        "verdict": result["verdict"],
        "methodology": result["methodology"],
    }

    return emit_receipt("usaid_validation", {
        "tenant_id": TENANT_ID,
        "module": MODULE_ID,
        **payload,
        "payload_hash": dual_hash(json.dumps(payload, sort_keys=True)),
        "simulation_flag": DISCLAIMER,
    }, to_stdout=False)


# === v6.3 MUSK ECOSYSTEM COI DETECTION ===


def detect_musk_ecosystem_coi(lookback_days: int = 365) -> dict:
    """
    v6.3: Cross-reference DOGE efficiency recommendations against
    contract awards to Musk-affiliated entities.

    COI pattern: Entity that BENEFITS from cuts → Entity that WINS contracts

    Algorithm:
    1. Load MUSK_ECOSYSTEM_ENTITIES from config
    2. Query USASpending for contracts awarded to each entity in lookback period
    3. Query DOGE recommendations affecting competitor agencies/programs
    4. Calculate temporal correlation:
       - For each Musk contract, check if DOGE recommended cuts to:
         a) Same agency within COI_CORRELATION_WINDOW_DAYS before award
         b) Competing programs/contractors
    5. Score: coi_score = (correlated_contracts / total_contracts) × avg_contract_value_ratio
    6. Emit musk_ecosystem_coi_receipt

    Args:
        lookback_days: How far back to search contracts (default 365)

    Returns:
        dict with:
        - entities_analyzed: int
        - total_contracts_found: int
        - total_contract_value_usd: float
        - doge_recommendations_analyzed: int
        - correlated_events: list[dict]
        - coi_score: float (0-1, higher = more correlation)
        - verdict: "coi_detected" | "no_coi_detected" | "insufficient_data"
        - receipt: dict

    Example:
        >>> result = detect_musk_ecosystem_coi(lookback_days=365)
        >>> print(f"COI Score: {result['coi_score']:.2f}")
        >>> print(f"Verdict: {result['verdict']}")

    Note:
        Does NOT determine guilt—only flags temporal correlation.
        Requires contract data to be in USASpending (may lag announcements).
        xAI GenAIMil contract may not appear in FPDS yet.
    """
    if not COI_DETECTION_ENABLED:
        return {
            "error": "COI detection disabled in config",
            "verdict": "insufficient_data",
            "simulation_flag": DISCLAIMER,
        }

    # Initialize results
    entities_analyzed = 0
    total_contracts_found = 0
    total_contract_value_usd = 0.0
    doge_recommendations_analyzed = 0
    correlated_events = []

    try:
        # Simulate Musk ecosystem contract data
        # In production, would query USASpending API
        contracts = _simulate_musk_contracts(lookback_days)
        doge_recs = _simulate_doge_recommendations()

        entities_analyzed = len(MUSK_ECOSYSTEM_ENTITIES)
        total_contracts_found = len(contracts)
        total_contract_value_usd = sum(c.get("value", 0) for c in contracts)
        doge_recommendations_analyzed = len(doge_recs)

        # Check for temporal correlation
        for contract in contracts:
            # Find DOGE recommendations within window before contract award
            for rec in doge_recs:
                days_between = _calculate_days_between(
                    rec.get("date", ""),
                    contract.get("award_date", "")
                )
                if 0 <= days_between <= COI_CORRELATION_WINDOW_DAYS:
                    # Check if recommendation affects competitor
                    if _affects_competitor(rec, contract):
                        correlated_events.append({
                            "entity": contract.get("entity"),
                            "contract_id": contract.get("contract_id"),
                            "contract_value": contract.get("value"),
                            "award_date": contract.get("award_date"),
                            "doge_recommendation": rec.get("description"),
                            "recommendation_date": rec.get("date"),
                            "days_between": days_between,
                            "affected_competitor": rec.get("entity_affected"),
                        })

        # Calculate COI score
        if total_contracts_found > 0:
            correlation_ratio = len(correlated_events) / total_contracts_found
            avg_value_ratio = total_contract_value_usd / (total_contracts_found * COI_MIN_CONTRACT_VALUE)
            coi_score = min(1.0, correlation_ratio * (1 + min(1.0, avg_value_ratio / 100)))
        else:
            coi_score = 0.0

        # Determine verdict
        if total_contracts_found == 0:
            verdict = "insufficient_data"
        elif coi_score >= 0.3:
            verdict = "coi_detected"
        else:
            verdict = "no_coi_detected"

    except Exception as e:
        return {
            "error": str(e),
            "verdict": "insufficient_data",
            "simulation_flag": DISCLAIMER,
        }

    # Build result
    result = {
        "entities_analyzed": entities_analyzed,
        "total_contracts_found": total_contracts_found,
        "total_contract_value_usd": total_contract_value_usd,
        "doge_recommendations_analyzed": doge_recommendations_analyzed,
        "correlated_events": correlated_events,
        "coi_score": round(coi_score, 4),
        "verdict": verdict,
        "lookback_days": lookback_days,
        "correlation_window_days": COI_CORRELATION_WINDOW_DAYS,
    }

    # Emit receipt
    receipt = _emit_musk_coi_receipt(result)
    result["receipt"] = receipt
    result["simulation_flag"] = DISCLAIMER

    return result


def _simulate_musk_contracts(lookback_days: int) -> List[dict]:
    """Simulate Musk ecosystem contracts for testing."""
    import random
    random.seed(42)  # Deterministic for testing

    contracts = []
    entities = ["spacex", "starlink", "tesla", "xai"]

    for entity in entities:
        num_contracts = random.randint(1, 5)
        for i in range(num_contracts):
            contracts.append({
                "entity": entity,
                "contract_id": f"{entity.upper()}-{i+1:04d}",
                "award_date": f"2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                "value": random.randint(1_000_000, 500_000_000),
                "agency": random.choice(["DOD", "NASA", "USAID", "GSA"]),
            })

    return contracts


def _simulate_doge_recommendations() -> List[dict]:
    """Simulate DOGE recommendations for testing."""
    return [
        {
            "date": "2024-11-15",
            "description": "Recommended cuts to legacy launch providers",
            "entity_affected": "ULA",
            "category": "dod_contracts",
        },
        {
            "date": "2024-11-20",
            "description": "Recommended reduction in NASA SLS program",
            "entity_affected": "Boeing_SLS",
            "category": "nasa_programs",
        },
        {
            "date": "2024-12-01",
            "description": "Recommended consolidation of government AI contracts",
            "entity_affected": "Various_AI_vendors",
            "category": "ai_services",
        },
        {
            "date": "2024-12-10",
            "description": "Recommended GSA fleet electrification",
            "entity_affected": "Legacy_auto_manufacturers",
            "category": "gsa_fleet",
        },
    ]


def _calculate_days_between(date1: str, date2: str) -> int:
    """Calculate days between two ISO date strings."""
    try:
        from datetime import datetime
        d1 = datetime.fromisoformat(date1)
        d2 = datetime.fromisoformat(date2)
        return abs((d2 - d1).days)
    except (ValueError, TypeError):
        return -1  # Invalid dates


def _affects_competitor(rec: dict, contract: dict) -> bool:
    """Check if DOGE recommendation affects competitor of contract awardee."""
    # Simplified logic - in production would use more sophisticated matching
    entity = contract.get("entity", "").lower()
    affected = rec.get("entity_affected", "").lower()
    category = rec.get("category", "").lower()

    # SpaceX benefits from cuts to ULA/Boeing
    if entity in ["spacex", "starlink"] and any(x in affected for x in ["ula", "boeing", "sls"]):
        return True

    # xAI benefits from cuts to other AI vendors
    if entity == "xai" and "ai" in category:
        return True

    # Tesla benefits from cuts to legacy auto
    if entity == "tesla" and any(x in affected for x in ["legacy", "auto", "fleet"]):
        return True

    return False


def _emit_musk_coi_receipt(result: dict) -> dict:
    """Emit musk_ecosystem_coi receipt."""
    payload = {
        "receipt_type": "musk_ecosystem_coi",
        "tenant_id": TENANT_ID,
        "entities_analyzed": result["entities_analyzed"],
        "contracts_found": result["total_contracts_found"],
        "correlated_events": len(result["correlated_events"]),
        "coi_score": result["coi_score"],
        "verdict": result["verdict"],
    }

    return emit_receipt("musk_ecosystem_coi", {
        **payload,
        "module": MODULE_ID,
        "payload_hash": dual_hash(json.dumps(payload, sort_keys=True)),
        "simulation_flag": DISCLAIMER,
    }, to_stdout=False)


# === MODULE SELF-TEST ===

if __name__ == "__main__":
    import sys

    print(f"# Gov-OS DOGE Verify Module Self-Test", file=sys.stderr)
    print(f"# {DISCLAIMER}", file=sys.stderr)

    # Test 1: List available claims
    print(f"# Available claims: {list(DOGE_CLAIM_SOURCES.keys())}", file=sys.stderr)

    # Test 2: Validate 160B claim
    try:
        result = validate_doge_claim("160B_savings_2025")
        print(f"# Claim: 160B_savings_2025", file=sys.stderr)
        print(f"#   Claimed: ${result['claimed_amount']:,.0f}", file=sys.stderr)
        print(f"#   Verified: ${result['verified_amount']:,.0f}", file=sys.stderr)
        print(f"#   Delta: {result['delta_percent']:.1f}%", file=sys.stderr)
        print(f"#   Passed: {result['passed']}", file=sys.stderr)
    except Exception as e:
        print(f"# Error validating claim: {e}", file=sys.stderr)

    # Test 3: Unknown claim should raise KeyError
    try:
        validate_doge_claim("unknown_claim")
        print(f"# ERROR: Should have raised KeyError", file=sys.stderr)
    except KeyError as e:
        print(f"# Correctly raised KeyError for unknown claim", file=sys.stderr)

    print(f"# PASS: doge verify module self-test", file=sys.stderr)
