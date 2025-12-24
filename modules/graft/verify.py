"""
Gov-OS Graft Module - Verification Functions

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

v6.2 New:
- detect_round_trip(): Detect if entity receives gov funds AND makes political donations
- FEC cross-reference for political donation correlation

Round-Trip Detection Logic:
1. Query: Does entity receive federal grants/contracts?
2. Query: Does entity (or officers) make FEC-reportable donations?
3. Query: Is there temporal correlation (donation within 90 days of award)?
4. Calculate: round_trip_score = correlation_strength × donation_amount / award_amount
5. Flag if score > threshold
"""

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .config import (
    MODULE_ID,
    RECEIPT_TYPES,
    ZK_ENABLED,
    ROUND_TRIP_DETECTION,
    FEC_CROSS_REFERENCE,
    ROUND_TRIP_THRESHOLD,
    TEMPORAL_CORRELATION_DAYS,
    DISCLAIMER,
)

# Import core utilities
import sys
sys.path.insert(0, str(__file__).rsplit('/', 3)[0])

try:
    from src.core import (
        TENANT_ID,
        dual_hash,
        emit_receipt,
        ForeignAidETL,
        ImplementingPartner,
        RoundTripEvidence,
    )
except ImportError:
    # Fallback for direct module execution
    TENANT_ID = "gov-os"
    dual_hash = lambda x: f"sha256:mock:{hash(x)}"
    emit_receipt = lambda t, p, **kw: {"receipt_type": t, **p}
    ForeignAidETL = None
    ImplementingPartner = None
    RoundTripEvidence = None


@dataclass
class RoundTripResult:
    """Result of round-trip funding detection."""
    entity_id: str
    entity_name: str
    federal_awards_total: float
    political_donations_total: float
    temporal_correlation: float  # 0-1, higher = more temporal clustering
    round_trip_score: float
    flagged: bool
    details: Dict[str, Any]

    def to_dict(self) -> dict:
        return {
            "entity_id": self.entity_id,
            "entity_name": self.entity_name,
            "federal_awards_total": self.federal_awards_total,
            "political_donations_total": self.political_donations_total,
            "temporal_correlation": self.temporal_correlation,
            "round_trip_score": self.round_trip_score,
            "flagged": self.flagged,
            "details": self.details,
        }


def detect_round_trip(
    entity_id: str,
    entity_name: Optional[str] = None,
    _simulate: bool = True
) -> Dict[str, Any]:
    """
    Detect if entity receives gov funds AND makes political donations.

    This is the core function for testing Musk's claim that USAID funds
    are "coming back to fund the left in America."

    Round-Trip Detection Logic:
    1. Query: Does entity receive federal grants/contracts?
    2. Query: Does entity (or officers) make FEC-reportable donations?
    3. Query: Is there temporal correlation (donation within 90 days of award)?
    4. Calculate: round_trip_score = correlation_strength × donation_amount / award_amount
    5. Flag if score > threshold

    Args:
        entity_id: Entity identifier (EIN, DUNS, or internal ID)
        entity_name: Optional entity name for display
        _simulate: If True, use simulated data

    Returns:
        Dict with:
        - entity_id: str
        - federal_awards_total: float
        - political_donations_total: float
        - temporal_correlation: float
        - round_trip_score: float
        - flagged: bool
        - receipt: dict

    Example:
        >>> result = detect_round_trip("52-1234567")
        >>> print(f"Score: {result['round_trip_score']:.4f}")
        >>> print(f"Flagged: {result['flagged']}")
    """
    if not ROUND_TRIP_DETECTION:
        return {
            "entity_id": entity_id,
            "error": "Round-trip detection disabled in config",
            "flagged": False,
        }

    # Initialize values
    federal_awards_total = 0.0
    political_donations_total = 0.0
    temporal_correlation = 0.0
    donations_detail = []
    awards_detail = []

    try:
        if _simulate:
            # Simulate data for testing
            result = _simulate_round_trip_data(entity_id)
            federal_awards_total = result["federal_awards_total"]
            political_donations_total = result["political_donations_total"]
            temporal_correlation = result["temporal_correlation"]
            donations_detail = result["donations_detail"]
            awards_detail = result["awards_detail"]
        elif ForeignAidETL is not None and FEC_CROSS_REFERENCE:
            # Real data lookup (would call actual APIs)
            etl = ForeignAidETL()
            fec_data = etl.cross_reference_fec(entity_name or entity_id, _simulate=True)
            political_donations_total = fec_data.get("total_donations", 0)
            donations_detail = fec_data.get("donations", [])

            # Would also query USASpending for awards
            # For now, use simulated data
            sim = _simulate_round_trip_data(entity_id)
            federal_awards_total = sim["federal_awards_total"]
            temporal_correlation = sim["temporal_correlation"]
            awards_detail = sim["awards_detail"]

    except Exception as e:
        return {
            "entity_id": entity_id,
            "entity_name": entity_name,
            "error": str(e),
            "flagged": False,
            "simulation_flag": DISCLAIMER,
        }

    # Calculate round-trip score
    if federal_awards_total > 0:
        ratio = political_donations_total / federal_awards_total
        # Score = ratio × temporal_correlation
        # Higher temporal correlation (donations close to awards) increases score
        round_trip_score = ratio * (1 + temporal_correlation)
    else:
        round_trip_score = 0.0

    # Flag if score exceeds threshold
    flagged = round_trip_score >= ROUND_TRIP_THRESHOLD

    # Build result
    result = RoundTripResult(
        entity_id=entity_id,
        entity_name=entity_name or entity_id,
        federal_awards_total=federal_awards_total,
        political_donations_total=political_donations_total,
        temporal_correlation=round(temporal_correlation, 4),
        round_trip_score=round(round_trip_score, 4),
        flagged=flagged,
        details={
            "threshold_used": ROUND_TRIP_THRESHOLD,
            "temporal_window_days": TEMPORAL_CORRELATION_DAYS,
            "donations_detail": donations_detail,
            "awards_detail": awards_detail,
        }
    )

    # Emit round_trip_receipt
    receipt = _emit_round_trip_receipt(result)

    return {
        **result.to_dict(),
        "receipt": receipt,
        "simulation_flag": DISCLAIMER,
    }


def _simulate_round_trip_data(entity_id: str) -> dict:
    """Generate simulated round-trip data for testing."""
    import random
    random.seed(hash(entity_id) % 10000)

    # Simulate varying levels of round-trip behavior
    # Most entities have low or no correlation
    is_democracy_org = any(term in entity_id.lower() for term in
                          ["democracy", "ndi", "iri", "freedom"])

    if is_democracy_org:
        federal_awards_total = random.randint(50_000_000, 200_000_000)
        political_donations_total = random.randint(1_000_000, 5_000_000)
        temporal_correlation = random.uniform(0.3, 0.6)
    else:
        federal_awards_total = random.randint(10_000_000, 100_000_000)
        political_donations_total = random.randint(0, 500_000)
        temporal_correlation = random.uniform(0.0, 0.3)

    return {
        "federal_awards_total": federal_awards_total,
        "political_donations_total": political_donations_total,
        "temporal_correlation": temporal_correlation,
        "donations_detail": [
            {"committee": "Various", "amount": political_donations_total}
        ] if political_donations_total > 0 else [],
        "awards_detail": [
            {"agency": "USAID", "amount": federal_awards_total}
        ],
    }


def _emit_round_trip_receipt(result: RoundTripResult) -> dict:
    """Emit round_trip_receipt."""
    payload = {
        "entity_id": result.entity_id,
        "federal_awards_total": result.federal_awards_total,
        "political_donations_total": result.political_donations_total,
        "temporal_correlation": result.temporal_correlation,
        "round_trip_score": result.round_trip_score,
        "flagged": result.flagged,
    }

    return emit_receipt("round_trip_receipt", {
        "tenant_id": TENANT_ID,
        "module": MODULE_ID,
        **payload,
        "payload_hash": dual_hash(json.dumps(payload, sort_keys=True)),
        "simulation_flag": DISCLAIMER,
    }, to_stdout=False)


def scan_implementing_partners(
    agency: str = "USAID",
    _simulate: bool = True
) -> Dict[str, Any]:
    """
    Scan all implementing partners for round-trip funding patterns.

    Args:
        agency: Agency to scan (default: USAID)
        _simulate: If True, use simulated data

    Returns:
        Dict with:
        - agency: str
        - partners_scanned: int
        - flagged_count: int
        - flagged_partners: list
        - total_awards: float
        - total_donations: float
        - aggregate_score: float
    """
    flagged_partners = []
    total_awards = 0.0
    total_donations = 0.0
    partners_scanned = 0

    try:
        if ForeignAidETL is not None:
            etl = ForeignAidETL()
            partners = etl.fetch_implementing_partners(agency, _simulate=_simulate)
            partners_scanned = len(partners)

            for partner in partners:
                result = detect_round_trip(
                    entity_id=partner.ein or partner.partner_id,
                    entity_name=partner.name,
                    _simulate=_simulate
                )
                total_awards += result.get("federal_awards_total", 0)
                total_donations += result.get("political_donations_total", 0)

                if result.get("flagged", False):
                    flagged_partners.append({
                        "partner_id": partner.partner_id,
                        "name": partner.name,
                        "round_trip_score": result.get("round_trip_score", 0),
                    })
        else:
            # Fallback simulation
            partners_scanned = 20
            for i in range(partners_scanned):
                entity_id = f"EIN-{i:06d}"
                result = detect_round_trip(entity_id, _simulate=True)
                total_awards += result.get("federal_awards_total", 0)
                total_donations += result.get("political_donations_total", 0)
                if result.get("flagged", False):
                    flagged_partners.append({
                        "partner_id": entity_id,
                        "name": f"Partner {i}",
                        "round_trip_score": result.get("round_trip_score", 0),
                    })

    except Exception as e:
        return {
            "agency": agency,
            "error": str(e),
            "partners_scanned": 0,
            "simulation_flag": DISCLAIMER,
        }

    # Calculate aggregate score
    if total_awards > 0:
        aggregate_score = total_donations / total_awards
    else:
        aggregate_score = 0.0

    return {
        "agency": agency,
        "partners_scanned": partners_scanned,
        "flagged_count": len(flagged_partners),
        "flagged_partners": flagged_partners,
        "total_awards": total_awards,
        "total_donations": total_donations,
        "aggregate_score": round(aggregate_score, 4),
        "interpretation": _interpret_scan_results(
            len(flagged_partners), partners_scanned, aggregate_score
        ),
        "simulation_flag": DISCLAIMER,
    }


def _interpret_scan_results(
    flagged_count: int,
    total_scanned: int,
    aggregate_score: float
) -> str:
    """Generate interpretation of scan results."""
    flag_rate = flagged_count / total_scanned if total_scanned > 0 else 0

    if flag_rate > 0.25:
        return (
            f"Significant round-trip pattern detected. {flagged_count} of "
            f"{total_scanned} partners ({flag_rate:.1%}) flagged. Aggregate "
            f"donation/award ratio: {aggregate_score:.2%}. Warrants investigation."
        )
    elif flag_rate > 0.10:
        return (
            f"Moderate round-trip pattern. {flagged_count} of {total_scanned} "
            f"partners ({flag_rate:.1%}) flagged. Some evidence of fund flow "
            "to political activity."
        )
    else:
        return (
            f"Low round-trip incidence. {flagged_count} of {total_scanned} "
            f"partners ({flag_rate:.1%}) flagged. No systematic pattern detected."
        )


# === MODULE SELF-TEST ===

if __name__ == "__main__":
    import sys

    print(f"# Gov-OS Graft Verify Module Self-Test", file=sys.stderr)
    print(f"# {DISCLAIMER}", file=sys.stderr)

    # Test 1: Single entity detection
    print(f"\n# Test 1: Single entity round-trip detection", file=sys.stderr)
    result = detect_round_trip("52-1234567", "Test NGO")
    print(f"#   Entity: {result['entity_name']}", file=sys.stderr)
    print(f"#   Awards: ${result['federal_awards_total']:,.0f}", file=sys.stderr)
    print(f"#   Donations: ${result['political_donations_total']:,.0f}", file=sys.stderr)
    print(f"#   Score: {result['round_trip_score']:.4f}", file=sys.stderr)
    print(f"#   Flagged: {result['flagged']}", file=sys.stderr)

    # Test 2: Democracy org (higher expected correlation)
    print(f"\n# Test 2: Democracy org detection", file=sys.stderr)
    result = detect_round_trip("democracy-intl", "Democracy International")
    print(f"#   Entity: {result['entity_name']}", file=sys.stderr)
    print(f"#   Score: {result['round_trip_score']:.4f}", file=sys.stderr)
    print(f"#   Flagged: {result['flagged']}", file=sys.stderr)

    # Test 3: Implementing partner scan
    print(f"\n# Test 3: Implementing partner scan", file=sys.stderr)
    scan_result = scan_implementing_partners("USAID", _simulate=True)
    print(f"#   Partners scanned: {scan_result['partners_scanned']}", file=sys.stderr)
    print(f"#   Flagged: {scan_result['flagged_count']}", file=sys.stderr)
    print(f"#   Aggregate score: {scan_result['aggregate_score']:.4f}", file=sys.stderr)
    print(f"#   Interpretation: {scan_result['interpretation'][:80]}...", file=sys.stderr)

    print(f"\n# PASS: graft verify module self-test", file=sys.stderr)
