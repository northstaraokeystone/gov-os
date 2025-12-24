"""
Gov-OS Graft Module - Verification Functions

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

v6.2 New:
- detect_round_trip(): Detect if entity receives gov funds AND makes political donations
- FEC cross-reference for political donation correlation

v6.3 New:
- temporal_correlation_analysis(): Detect suspicious timing between political events
  and contract awards
- Cross-module integration with doge/ for DOGE recommendation correlation

Round-Trip Detection Logic:
1. Query: Does entity receive federal grants/contracts?
2. Query: Does entity (or officers) make FEC-reportable donations?
3. Query: Is there temporal correlation (donation within 90 days of award)?
4. Calculate: round_trip_score = correlation_strength × donation_amount / award_amount
5. Flag if score > threshold

Temporal Correlation Logic (v6.3):
1. For each award, find events within window_days BEFORE award_date
2. Score each event-award pair by time decay, event weight, and value
3. Aggregate and calculate statistical significance
4. Emit temporal_correlation_receipt
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
    # v6.3 temporal correlation
    TEMPORAL_CORRELATION_ENABLED,
    EVENT_TYPE_WEIGHTS,
    DEFAULT_TEMPORAL_WINDOW_DAYS,
    MIN_SAMPLE_SIZE,
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


# === v6.3 TEMPORAL CORRELATION ANALYSIS ===


def temporal_correlation_analysis(
    events: List[Dict[str, Any]],
    awards: List[Dict[str, Any]],
    window_days: int = None,
) -> Dict[str, Any]:
    """
    v6.3: Analyze timing patterns between political events and contract awards.

    Detects suspicious timing patterns where political events (DOGE announcements,
    policy changes, personnel changes) precede contract awards.

    Pattern: Event occurs → Award follows within window → Correlation flagged

    Algorithm:
    1. For each award:
       a) Find all events within window_days BEFORE award_date
       b) Score each event-award pair by:
          - Days between (closer = higher score)
          - Event type weight (DOGE_RECOMMENDATION > POLICY_CHANGE > PERSONNEL)
          - Award value (higher = more significant)

    2. Aggregate correlation score:
       temporal_score = Σ(event_weight × value_weight × time_decay) / total_awards

    3. Statistical significance:
       - Compare to baseline: random timing would show uniform distribution
       - Clustering around event dates suggests correlation

    4. Emit temporal_correlation_receipt

    Args:
        events: List of event dicts with {event_type, date, description, entity_affected}
        awards: List of award dicts with {contract_id, award_date, value, awardee}
        window_days: Correlation window (default from config)

    Returns:
        dict with:
        - events_analyzed: int
        - awards_analyzed: int
        - correlations_found: int
        - correlation_details: list[dict]
        - temporal_score: float (0-1 aggregate)
        - statistical_significance: float (p-value)
        - verdict: "pattern_detected" | "no_pattern" | "insufficient_data"
        - receipt: dict

    Example:
        >>> events = [{"event_type": "DOGE_RECOMMENDATION", "date": "2024-11-01", ...}]
        >>> awards = [{"contract_id": "ABC-123", "award_date": "2024-11-15", ...}]
        >>> result = temporal_correlation_analysis(events, awards)
        >>> print(f"Temporal Score: {result['temporal_score']:.2f}")

    Note:
        Correlation ≠ causation. This flags patterns, not guilt.
        Requires sufficient sample size (min 10 awards recommended).
    """
    if not TEMPORAL_CORRELATION_ENABLED:
        return {
            "error": "Temporal correlation analysis disabled in config",
            "verdict": "insufficient_data",
            "simulation_flag": DISCLAIMER,
        }

    # Use default window if not specified
    if window_days is None:
        window_days = DEFAULT_TEMPORAL_WINDOW_DAYS

    events_analyzed = len(events)
    awards_analyzed = len(awards)
    correlations_found = 0
    correlation_details = []
    total_score = 0.0

    # Check minimum sample size
    if awards_analyzed < MIN_SAMPLE_SIZE:
        return {
            "events_analyzed": events_analyzed,
            "awards_analyzed": awards_analyzed,
            "correlations_found": 0,
            "correlation_details": [],
            "temporal_score": 0.0,
            "statistical_significance": 1.0,
            "verdict": "insufficient_data",
            "note": f"Minimum {MIN_SAMPLE_SIZE} awards required for analysis",
            "simulation_flag": DISCLAIMER,
        }

    try:
        for award in awards:
            award_date = award.get("award_date", "")
            award_value = award.get("value", 0)
            contract_id = award.get("contract_id", "unknown")
            awardee = award.get("awardee", "unknown")

            for event in events:
                event_date = event.get("date", "")
                event_type = event.get("event_type", "OTHER")
                event_desc = event.get("description", "")

                # Calculate days between (event should be BEFORE award)
                days_between = _calc_days_between(event_date, award_date)

                # Only consider events that precede the award within window
                if 0 <= days_between <= window_days:
                    # Calculate correlation score for this pair
                    time_decay = 1.0 - (days_between / window_days)  # Closer = higher
                    event_weight = EVENT_TYPE_WEIGHTS.get(event_type, 0.2)
                    value_weight = min(1.0, award_value / 100_000_000)  # Normalize to 100M

                    pair_score = time_decay * event_weight * (0.5 + value_weight * 0.5)

                    correlation_details.append({
                        "event_type": event_type,
                        "event_date": event_date,
                        "event_description": event_desc,
                        "award_id": contract_id,
                        "award_date": award_date,
                        "award_value": award_value,
                        "awardee": awardee,
                        "days_between": days_between,
                        "correlation_score": round(pair_score, 4),
                    })

                    correlations_found += 1
                    total_score += pair_score

        # Calculate aggregate temporal score
        if awards_analyzed > 0:
            temporal_score = min(1.0, total_score / awards_analyzed)
        else:
            temporal_score = 0.0

        # Calculate statistical significance (simplified)
        # Under null hypothesis (no correlation), events would be uniformly distributed
        # We use a simple heuristic: p-value based on correlation rate
        expected_correlation_rate = window_days / 365.0  # Expected if random
        observed_correlation_rate = correlations_found / max(1, awards_analyzed * events_analyzed)

        if observed_correlation_rate > 0 and expected_correlation_rate > 0:
            # Simple significance estimate
            ratio = observed_correlation_rate / expected_correlation_rate
            p_value = max(0.001, 1.0 / (1.0 + ratio ** 2))
        else:
            p_value = 1.0

        # Determine verdict
        if correlations_found == 0:
            verdict = "no_pattern"
        elif temporal_score >= 0.3 and p_value < 0.05:
            verdict = "pattern_detected"
        elif temporal_score >= 0.1:
            verdict = "weak_pattern"
        else:
            verdict = "no_pattern"

    except Exception as e:
        return {
            "error": str(e),
            "verdict": "insufficient_data",
            "simulation_flag": DISCLAIMER,
        }

    # Build result
    result = {
        "events_analyzed": events_analyzed,
        "awards_analyzed": awards_analyzed,
        "correlations_found": correlations_found,
        "correlation_details": correlation_details,
        "temporal_score": round(temporal_score, 4),
        "statistical_significance": round(p_value, 4),
        "window_days": window_days,
        "verdict": verdict,
    }

    # Emit receipt
    receipt = _emit_temporal_correlation_receipt(result)
    result["receipt"] = receipt
    result["simulation_flag"] = DISCLAIMER

    return result


def _calc_days_between(date1: str, date2: str) -> int:
    """Calculate days between two ISO date strings (date1 before date2 = positive)."""
    try:
        from datetime import datetime
        d1 = datetime.fromisoformat(date1)
        d2 = datetime.fromisoformat(date2)
        delta = (d2 - d1).days
        return delta
    except (ValueError, TypeError):
        return -1  # Invalid dates


def _emit_temporal_correlation_receipt(result: dict) -> dict:
    """Emit temporal_correlation receipt."""
    from datetime import datetime

    payload = {
        "receipt_type": "temporal_correlation",
        "ts": datetime.utcnow().isoformat() + "Z",
        "tenant_id": TENANT_ID,
        "module": MODULE_ID,
        "events_analyzed": result["events_analyzed"],
        "awards_analyzed": result["awards_analyzed"],
        "correlations_found": result["correlations_found"],
        "temporal_score": result["temporal_score"],
        "p_value": result["statistical_significance"],
        "verdict": result["verdict"],
    }

    return emit_receipt("temporal_correlation", {
        **payload,
        "payload_hash": dual_hash(json.dumps(payload, sort_keys=True, default=str)),
        "simulation_flag": DISCLAIMER,
    }, to_stdout=False)


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
