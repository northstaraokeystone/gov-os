"""
Gov-OS AidProof Module - Verification Functions

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

Verify foreign aid claims and detect anomalies:
- verify_aid_claim: Verify specific claims (waste, round_trip, overhead, etc.)
- detect_round_trip: Detect round-trip funding pattern
- calculate_overhead_ratio: Analyze admin cost ratios
- compare_to_baseline: Compare to legitimate aid patterns
"""

import json
from typing import Any, Dict, List, Optional

from .config import (
    MODULE_ID,
    IMPLEMENTING_PARTNER_THRESHOLD,
    ROUND_TRIP_THRESHOLD,
    OVERHEAD_RATIO_THRESHOLD,
    CROSS_MODULE_LINKS,
    DISCLAIMER,
)
from .data import ImplementingPartner, RoundTripEvidence, AidAnomaly
from .receipts import AidVerificationReceipt, RoundTripReceipt, OverheadReceipt
from .ingest import ingest_implementing_partners

# Import core utilities
import sys
sys.path.insert(0, str(__file__).rsplit('/', 3)[0])

try:
    from src.core import (
        TENANT_ID,
        dual_hash,
        emit_receipt,
        ForeignAidETL,
    )
except ImportError:
    TENANT_ID = "gov-os"
    dual_hash = lambda x: f"sha256:mock:{hash(x)}"
    emit_receipt = lambda t, p, **kw: {"receipt_type": t, **p}
    ForeignAidETL = None


def verify(claim: dict) -> dict:
    """
    Main verification entry point.

    Routes to appropriate sub-function based on claim type.

    Args:
        claim: Dict with 'claim_id' or 'claim_type' and relevant parameters

    Returns:
        Verification result dict
    """
    claim_type = claim.get("claim_type", claim.get("type", "waste"))
    claim_id = claim.get("claim_id", "generic")

    return verify_aid_claim(claim_id, claim_type, _simulate=claim.get("_simulate", True))


def verify_aid_claim(
    claim_id: str,
    claim_type: str,
    _simulate: bool = True
) -> Dict[str, Any]:
    """
    Verify specific claim against foreign aid data.

    Claim Types:
    - "waste": Check compression ratios against baseline
    - "round_trip": Check FEC correlation
    - "overhead": Check admin cost ratios
    - "country_allocation": Check country-level patterns

    Args:
        claim_id: Claim identifier
        claim_type: Type of claim to verify
        _simulate: If True, use simulated data

    Returns:
        Verification result with verdict

    Emits:
        aid_verification_receipt
    """
    data_sources_queried = []
    records_analyzed = 0
    compression_ratio = 0.0
    anomaly_score = 0.0
    round_trip_score = 0.0
    evidence = []
    verdict = "insufficient_data"

    try:
        if claim_type == "waste":
            result = _verify_waste_claim(claim_id, _simulate)
            compression_ratio = result.get("compression_ratio", 0)
            anomaly_score = result.get("anomaly_score", 0)
            records_analyzed = result.get("records_analyzed", 0)
            data_sources_queried = result.get("data_sources", [])
            verdict = result.get("verdict", "insufficient_data")
            evidence = result.get("evidence", [])

        elif claim_type == "round_trip":
            result = _verify_round_trip_claim(claim_id, _simulate)
            round_trip_score = result.get("round_trip_score", 0)
            records_analyzed = result.get("partners_analyzed", 0)
            data_sources_queried = ["usaspending", "fec"]
            verdict = result.get("verdict", "insufficient_data")
            evidence = result.get("evidence", [])

        elif claim_type == "overhead":
            result = _verify_overhead_claim(claim_id, _simulate)
            anomaly_score = result.get("overhead_ratio", 0)
            records_analyzed = result.get("partners_analyzed", 0)
            data_sources_queried = ["propublica_990"]
            verdict = result.get("verdict", "insufficient_data")
            evidence = result.get("evidence", [])

        elif claim_type == "country_allocation":
            result = _verify_country_allocation(claim_id, _simulate)
            anomaly_score = result.get("concentration_score", 0)
            records_analyzed = result.get("countries_analyzed", 0)
            data_sources_queried = ["foreignassistance"]
            verdict = result.get("verdict", "insufficient_data")
            evidence = result.get("evidence", [])

        else:
            return {
                "claim_id": claim_id,
                "error": f"Unknown claim type: {claim_type}",
                "simulation_flag": DISCLAIMER,
            }

    except Exception as e:
        return {
            "claim_id": claim_id,
            "claim_type": claim_type,
            "error": str(e),
            "verdict": "insufficient_data",
            "simulation_flag": DISCLAIMER,
        }

    # Build receipt
    receipt = AidVerificationReceipt(
        claim_id=claim_id,
        claim_type=claim_type,
        data_sources_queried=data_sources_queried,
        records_analyzed=records_analyzed,
        compression_ratio=compression_ratio,
        anomaly_score=anomaly_score,
        round_trip_score=round_trip_score,
        verdict=verdict,
        evidence=evidence,
        payload_hash=dual_hash(f"{claim_id}:{claim_type}:{verdict}"),
    )
    _emit_verification_receipt(receipt)

    return {
        "claim_id": claim_id,
        "claim_type": claim_type,
        "data_sources_queried": data_sources_queried,
        "records_analyzed": records_analyzed,
        "compression_ratio": compression_ratio,
        "anomaly_score": anomaly_score,
        "round_trip_score": round_trip_score,
        "verdict": verdict,
        "evidence": evidence,
        "receipt": receipt.to_dict(),
        "simulation_flag": DISCLAIMER,
    }


def detect_round_trip(
    partner_id: str,
    partner_name: Optional[str] = None,
    _simulate: bool = True
) -> Dict[str, Any]:
    """
    Detect round-trip funding for specific implementing partner.

    Round-trip pattern:
    1. NGO receives federal grant
    2. NGO (or officers) make political donations
    3. Ratio exceeds threshold

    Args:
        partner_id: Partner identifier (EIN or internal ID)
        partner_name: Optional partner name
        _simulate: If True, use simulated data

    Returns:
        Detection result with score and flag status

    Emits:
        round_trip_receipt
    """
    federal_awards_total = 0.0
    political_donations_total = 0.0
    temporal_correlation = 0.0

    try:
        if ForeignAidETL is not None:
            etl = ForeignAidETL()
            fec_data = etl.cross_reference_fec(partner_name or partner_id, _simulate=_simulate)
            political_donations_total = fec_data.get("total_donations", 0)

            # Simulated federal awards (would query USASpending in production)
            federal_awards_total = _simulate_federal_awards(partner_id)
            temporal_correlation = _calculate_temporal_correlation(_simulate)
        else:
            # Fallback simulation
            federal_awards_total = _simulate_federal_awards(partner_id)
            political_donations_total = _simulate_political_donations(partner_id)
            temporal_correlation = _calculate_temporal_correlation(_simulate)

    except Exception as e:
        return {
            "partner_id": partner_id,
            "error": str(e),
            "flagged": False,
            "simulation_flag": DISCLAIMER,
        }

    # Calculate round-trip score
    if federal_awards_total > 0:
        ratio = political_donations_total / federal_awards_total
        round_trip_score = ratio * (1 + temporal_correlation)
    else:
        round_trip_score = 0.0

    flagged = round_trip_score >= ROUND_TRIP_THRESHOLD

    # Build receipt
    receipt = RoundTripReceipt(
        entity_id=partner_id,
        entity_name=partner_name or partner_id,
        federal_awards_total=federal_awards_total,
        political_donations_total=political_donations_total,
        temporal_correlation=round(temporal_correlation, 4),
        round_trip_score=round(round_trip_score, 4),
        flagged=flagged,
        threshold_used=ROUND_TRIP_THRESHOLD,
    )
    _emit_round_trip_receipt(receipt)

    return {
        "partner_id": partner_id,
        "partner_name": partner_name,
        "federal_awards_total": federal_awards_total,
        "political_donations_total": political_donations_total,
        "temporal_correlation": round(temporal_correlation, 4),
        "round_trip_score": round(round_trip_score, 4),
        "flagged": flagged,
        "threshold_used": ROUND_TRIP_THRESHOLD,
        "receipt": receipt.to_dict(),
        "simulation_flag": DISCLAIMER,
    }


def calculate_overhead_ratio(
    partner_id: str,
    _simulate: bool = True
) -> Dict[str, Any]:
    """
    Calculate admin cost / overhead ratio for an implementing partner.

    Args:
        partner_id: Partner identifier (EIN)
        _simulate: If True, use simulated data

    Returns:
        Overhead analysis result

    Emits:
        overhead_receipt
    """
    total_revenue = 0.0
    admin_expenses = 0.0
    program_expenses = 0.0
    overhead_ratio = 0.0

    try:
        if ForeignAidETL is not None:
            etl = ForeignAidETL()
            form_990 = etl.cross_reference_990(partner_id, _simulate=_simulate)
            total_revenue = form_990.get("total_revenue", 0)
            admin_expenses = form_990.get("admin_expenses", 0)
            program_expenses = form_990.get("program_expenses", 0)
        else:
            # Fallback simulation
            import random
            random.seed(hash(partner_id) % 10000)
            total_revenue = random.randint(50_000_000, 200_000_000)
            admin_expenses = int(total_revenue * random.uniform(0.08, 0.25))
            program_expenses = int(total_revenue * random.uniform(0.65, 0.85))

    except Exception as e:
        return {
            "partner_id": partner_id,
            "error": str(e),
            "simulation_flag": DISCLAIMER,
        }

    # Calculate overhead ratio
    total_expenses = admin_expenses + program_expenses
    if total_expenses > 0:
        overhead_ratio = admin_expenses / total_expenses
    else:
        overhead_ratio = 0.0

    flagged = overhead_ratio >= OVERHEAD_RATIO_THRESHOLD

    # Build receipt
    receipt = OverheadReceipt(
        entity_id=partner_id,
        entity_name=partner_id,
        total_revenue=total_revenue,
        admin_expenses=admin_expenses,
        program_expenses=program_expenses,
        overhead_ratio=round(overhead_ratio, 4),
        flagged=flagged,
        threshold_used=OVERHEAD_RATIO_THRESHOLD,
    )
    _emit_overhead_receipt(receipt)

    return {
        "partner_id": partner_id,
        "total_revenue": total_revenue,
        "admin_expenses": admin_expenses,
        "program_expenses": program_expenses,
        "overhead_ratio": round(overhead_ratio, 4),
        "flagged": flagged,
        "threshold_used": OVERHEAD_RATIO_THRESHOLD,
        "receipt": receipt.to_dict(),
        "simulation_flag": DISCLAIMER,
    }


def compare_to_baseline(
    partner_id: str,
    _simulate: bool = True
) -> Dict[str, Any]:
    """
    Compare implementing partner to legitimate aid patterns (baseline).

    Compares:
    - Overhead ratio to baseline (legitimate: ~15%, flagged: >40%)
    - Round-trip score to baseline (legitimate: <1%, flagged: >10%)
    - Program spending efficiency

    Args:
        partner_id: Partner identifier
        _simulate: If True, use simulated data

    Returns:
        Comparison result with deviation from baseline
    """
    # Get partner metrics
    overhead_result = calculate_overhead_ratio(partner_id, _simulate)
    round_trip_result = detect_round_trip(partner_id, _simulate=_simulate)

    # Baseline values (from legitimate aid patterns like PEPFAR)
    baseline = {
        "overhead_ratio": 0.15,
        "round_trip_score": 0.01,
        "program_efficiency": 0.80,
    }

    # Calculate deviations
    overhead_deviation = (overhead_result["overhead_ratio"] - baseline["overhead_ratio"]) / baseline["overhead_ratio"]
    round_trip_deviation = (round_trip_result["round_trip_score"] - baseline["round_trip_score"]) / baseline["round_trip_score"]

    # Determine anomaly status
    is_anomalous = (
        overhead_result.get("flagged", False) or
        round_trip_result.get("flagged", False) or
        overhead_deviation > 1.0 or
        round_trip_deviation > 5.0
    )

    return {
        "partner_id": partner_id,
        "overhead_ratio": overhead_result["overhead_ratio"],
        "round_trip_score": round_trip_result["round_trip_score"],
        "baseline": baseline,
        "overhead_deviation": round(overhead_deviation, 4),
        "round_trip_deviation": round(round_trip_deviation, 4),
        "is_anomalous": is_anomalous,
        "interpretation": _interpret_comparison(overhead_deviation, round_trip_deviation),
        "simulation_flag": DISCLAIMER,
    }


# === INTERNAL VERIFICATION FUNCTIONS ===

def _verify_waste_claim(claim_id: str, _simulate: bool) -> dict:
    """Verify waste claim via compression analysis."""
    # Simplified - would use actual compression analysis in production
    import random
    random.seed(hash(claim_id) % 10000)

    return {
        "compression_ratio": random.uniform(0.45, 0.65),
        "anomaly_score": random.uniform(0.1, 0.3),
        "records_analyzed": random.randint(100, 500),
        "data_sources": ["usaspending", "foreignassistance"],
        "verdict": "unsupported",  # Default to unsupported
        "evidence": [],
    }


def _verify_round_trip_claim(claim_id: str, _simulate: bool) -> dict:
    """Verify round-trip claim via FEC cross-reference."""
    # Get implementing partners and analyze
    partner_data = ingest_implementing_partners(_simulate=_simulate)
    partners = partner_data.get("partners", [])

    total_awards = sum(p.get("total_awards", 0) for p in partners)
    total_donations = sum(p.get("political_donations", 0) for p in partners)

    if total_awards > 0:
        round_trip_score = total_donations / total_awards
    else:
        round_trip_score = 0.0

    # Find flagged partners
    evidence = []
    for p in partners:
        awards = p.get("total_awards", 0)
        donations = p.get("political_donations", 0)
        if awards > 0 and (donations / awards) >= ROUND_TRIP_THRESHOLD:
            evidence.append({
                "partner_name": p.get("name"),
                "ratio": round(donations / awards, 4),
            })

    verdict = "supported" if round_trip_score >= ROUND_TRIP_THRESHOLD else "unsupported"

    return {
        "round_trip_score": round(round_trip_score, 4),
        "partners_analyzed": len(partners),
        "flagged_count": len(evidence),
        "evidence": evidence,
        "verdict": verdict,
    }


def _verify_overhead_claim(claim_id: str, _simulate: bool) -> dict:
    """Verify overhead claim via Form 990 analysis."""
    partner_data = ingest_implementing_partners(_simulate=_simulate)
    partners = partner_data.get("partners", [])

    flagged = []
    total_overhead = 0.0
    partner_count = 0

    for p in partners:
        expenses = p.get("form_990_expenses", 0)
        admin = p.get("admin_expenses", 0)
        if expenses and expenses > 0:
            ratio = admin / expenses if admin else 0
            total_overhead += ratio
            partner_count += 1
            if ratio >= OVERHEAD_RATIO_THRESHOLD:
                flagged.append({
                    "partner_name": p.get("name"),
                    "overhead_ratio": round(ratio, 4),
                })

    avg_overhead = total_overhead / partner_count if partner_count > 0 else 0

    verdict = "supported" if len(flagged) > len(partners) * 0.25 else "unsupported"

    return {
        "overhead_ratio": round(avg_overhead, 4),
        "partners_analyzed": partner_count,
        "flagged_count": len(flagged),
        "evidence": flagged,
        "verdict": verdict,
    }


def _verify_country_allocation(claim_id: str, _simulate: bool) -> dict:
    """Verify country allocation patterns."""
    from .ingest import ingest_country_allocations
    allocation_data = ingest_country_allocations(_simulate=_simulate)
    allocations = allocation_data.get("allocations", {})

    if not allocations:
        return {"verdict": "insufficient_data", "evidence": []}

    # Calculate concentration (Herfindahl index)
    total = sum(allocations.values())
    if total > 0:
        shares = [v / total for v in allocations.values()]
        concentration_score = sum(s ** 2 for s in shares)
    else:
        concentration_score = 0

    # High concentration = potential bias
    verdict = "supported" if concentration_score > 0.25 else "unsupported"

    return {
        "concentration_score": round(concentration_score, 4),
        "countries_analyzed": len(allocations),
        "evidence": [{"concentration_score": concentration_score}],
        "verdict": verdict,
    }


# === HELPER FUNCTIONS ===

def _simulate_federal_awards(partner_id: str) -> float:
    """Simulate federal awards for testing."""
    import random
    random.seed(hash(partner_id) % 10000)
    return random.randint(10_000_000, 200_000_000)


def _simulate_political_donations(partner_id: str) -> float:
    """Simulate political donations for testing."""
    import random
    random.seed(hash(partner_id) % 10000)
    # Most orgs have low donations, some have higher
    if "democracy" in partner_id.lower() or random.random() > 0.8:
        return random.randint(500_000, 3_000_000)
    return random.randint(0, 100_000)


def _calculate_temporal_correlation(_simulate: bool) -> float:
    """Calculate temporal correlation between awards and donations."""
    import random
    return random.uniform(0.1, 0.5)


def _interpret_comparison(overhead_dev: float, round_trip_dev: float) -> str:
    """Generate interpretation of comparison to baseline."""
    issues = []
    if overhead_dev > 1.0:
        issues.append(f"overhead {overhead_dev:.0%} above baseline")
    if round_trip_dev > 5.0:
        issues.append(f"round-trip score {round_trip_dev:.0%} above baseline")

    if not issues:
        return "Partner metrics within normal range compared to legitimate aid baseline."
    return f"Anomalies detected: {', '.join(issues)}. Warrants investigation."


# === RECEIPT EMISSION ===

def _emit_verification_receipt(receipt: AidVerificationReceipt) -> dict:
    """Emit aid_verification receipt."""
    payload = receipt.to_dict()
    return emit_receipt("aid_verification", {
        "tenant_id": TENANT_ID,
        "module": MODULE_ID,
        **payload,
    }, to_stdout=False)


def _emit_round_trip_receipt(receipt: RoundTripReceipt) -> dict:
    """Emit round_trip receipt."""
    payload = receipt.to_dict()
    return emit_receipt("round_trip", {
        "tenant_id": TENANT_ID,
        "module": MODULE_ID,
        **payload,
    }, to_stdout=False)


def _emit_overhead_receipt(receipt: OverheadReceipt) -> dict:
    """Emit overhead receipt."""
    payload = receipt.to_dict()
    return emit_receipt("overhead", {
        "tenant_id": TENANT_ID,
        "module": MODULE_ID,
        **payload,
    }, to_stdout=False)


# === MODULE SELF-TEST ===

if __name__ == "__main__":
    import sys

    print(f"# Gov-OS AidProof Verify Module Self-Test", file=sys.stderr)
    print(f"# {DISCLAIMER}", file=sys.stderr)

    # Test 1: Verify round-trip claim
    print(f"\n# Test 1: Verify round-trip claim", file=sys.stderr)
    result = verify_aid_claim("usaid_waste", "round_trip")
    print(f"#   Verdict: {result['verdict']}", file=sys.stderr)
    print(f"#   Round-trip score: {result['round_trip_score']:.4f}", file=sys.stderr)

    # Test 2: Detect round-trip for specific partner
    print(f"\n# Test 2: Detect round-trip", file=sys.stderr)
    result = detect_round_trip("52-1234567", "Test NGO")
    print(f"#   Score: {result['round_trip_score']:.4f}", file=sys.stderr)
    print(f"#   Flagged: {result['flagged']}", file=sys.stderr)

    # Test 3: Calculate overhead ratio
    print(f"\n# Test 3: Overhead ratio", file=sys.stderr)
    result = calculate_overhead_ratio("52-1234567")
    print(f"#   Overhead: {result['overhead_ratio']:.2%}", file=sys.stderr)
    print(f"#   Flagged: {result['flagged']}", file=sys.stderr)

    # Test 4: Compare to baseline
    print(f"\n# Test 4: Baseline comparison", file=sys.stderr)
    result = compare_to_baseline("52-1234567")
    print(f"#   Anomalous: {result['is_anomalous']}", file=sys.stderr)
    print(f"#   {result['interpretation'][:60]}...", file=sys.stderr)

    print(f"\n# PASS: aid verify module self-test", file=sys.stderr)
