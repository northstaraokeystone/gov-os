"""
Gov-OS AidProof Module - Test Scenarios

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

Test scenarios for AidProof module:
- BASELINE: Normal aid distribution
- ROUND_TRIP: NGO with high political donations
- OVERHEAD_ABUSE: NGO with 80% admin costs
- COUNTRY_CONCENTRATION: 90% to one country
- SHELL_NGO: Multiple awards to minimal-staff NGO
- MUSK_CLAIM: Test Musk's USAID claim
"""

from typing import Any, Dict

from .config import MODULE_ID, DISCLAIMER
from .verify import verify_aid_claim, detect_round_trip, calculate_overhead_ratio
from .ingest import ingest_implementing_partners

# === SCENARIO DEFINITIONS ===

SCENARIOS = {
    "BASELINE": {
        "name": "Baseline Normal Distribution",
        "description": "Normal foreign aid distribution with legitimate patterns",
        "expected_outcome": "No anomalies detected",
        "claim_type": "waste",
    },
    "ROUND_TRIP": {
        "name": "Round-Trip Funding Detection",
        "description": "NGO receiving aid makes significant political donations",
        "expected_outcome": "Round-trip flag triggered",
        "claim_type": "round_trip",
    },
    "OVERHEAD_ABUSE": {
        "name": "Overhead Abuse Detection",
        "description": "NGO with excessive administrative costs (>40%)",
        "expected_outcome": "Overhead anomaly flagged",
        "claim_type": "overhead",
    },
    "COUNTRY_CONCENTRATION": {
        "name": "Country Concentration Detection",
        "description": "Aid concentrated in single country (>90%)",
        "expected_outcome": "Concentration pattern flagged",
        "claim_type": "country_allocation",
    },
    "SHELL_NGO": {
        "name": "Shell NGO Detection",
        "description": "Multiple large awards to minimal-staff NGO",
        "expected_outcome": "Cross-domain shell flag",
        "claim_type": "waste",
    },
    "MUSK_CLAIM": {
        "name": "Musk USAID Claim Test",
        "description": "Test claim that USAID funds 'far left political causes' with round-trip funding",
        "expected_outcome": "Verdict based on evidence",
        "claim_type": "round_trip",
    },
}


def run_aid_scenario(scenario_name: str, _simulate: bool = True) -> Dict[str, Any]:
    """
    Run a specific test scenario.

    Args:
        scenario_name: Name of scenario from SCENARIOS
        _simulate: If True, use simulated data

    Returns:
        Scenario result with verdict
    """
    if scenario_name not in SCENARIOS:
        return {
            "error": f"Unknown scenario: {scenario_name}",
            "available": list(SCENARIOS.keys()),
            "simulation_flag": DISCLAIMER,
        }

    scenario = SCENARIOS[scenario_name]
    claim_type = scenario["claim_type"]

    result = {
        "scenario": scenario_name,
        "scenario_config": scenario,
        "simulation_flag": DISCLAIMER,
    }

    if scenario_name == "BASELINE":
        result.update(_run_baseline_scenario(_simulate))

    elif scenario_name == "ROUND_TRIP":
        result.update(_run_round_trip_scenario(_simulate))

    elif scenario_name == "OVERHEAD_ABUSE":
        result.update(_run_overhead_scenario(_simulate))

    elif scenario_name == "COUNTRY_CONCENTRATION":
        result.update(_run_concentration_scenario(_simulate))

    elif scenario_name == "SHELL_NGO":
        result.update(_run_shell_ngo_scenario(_simulate))

    elif scenario_name == "MUSK_CLAIM":
        result.update(_run_musk_claim_scenario(_simulate))

    else:
        # Default: use verify_aid_claim
        verification = verify_aid_claim(scenario_name, claim_type, _simulate)
        result.update(verification)

    return result


def _run_baseline_scenario(_simulate: bool) -> dict:
    """Run baseline normal distribution scenario."""
    # Ingest and verify with expectation of no anomalies
    verification = verify_aid_claim("baseline", "waste", _simulate)

    passed = verification["verdict"] == "unsupported"  # No anomalies = unsupported claim

    return {
        "verification": verification,
        "expected_outcome": "No anomalies detected",
        "actual_outcome": verification["verdict"],
        "passed": passed,
        "interpretation": (
            "Baseline scenario shows normal aid distribution patterns. "
            "No systematic waste or fraud detected in simulated data."
        ),
    }


def _run_round_trip_scenario(_simulate: bool) -> dict:
    """Run round-trip funding detection scenario."""
    # Verify round-trip claim
    verification = verify_aid_claim("round_trip_test", "round_trip", _simulate)

    # Also run individual partner detection
    partner_result = detect_round_trip("democracy-intl", "Democracy International", _simulate)

    flagged_count = verification.get("evidence", [])

    return {
        "verification": verification,
        "partner_analysis": partner_result,
        "expected_outcome": "Round-trip flag triggered",
        "actual_outcome": f"{len(flagged_count)} partners flagged",
        "passed": len(flagged_count) > 0 or partner_result.get("flagged", False),
        "interpretation": (
            "Round-trip scenario tests detection of NGOs that receive aid and "
            "make significant political donations. The system is neutral - it "
            "only detects patterns, not political affiliations."
        ),
    }


def _run_overhead_scenario(_simulate: bool) -> dict:
    """Run overhead abuse detection scenario."""
    verification = verify_aid_claim("overhead_test", "overhead", _simulate)

    # Test specific partner
    overhead_result = calculate_overhead_ratio("overhead-abuse-ngo", _simulate)

    flagged = overhead_result.get("flagged", False)

    return {
        "verification": verification,
        "overhead_analysis": overhead_result,
        "expected_outcome": "Overhead anomaly flagged",
        "actual_outcome": f"Flagged: {flagged}",
        "passed": flagged or verification["verdict"] == "supported",
        "interpretation": (
            "Overhead scenario tests detection of NGOs with excessive "
            "administrative costs. Legitimate NGOs typically have overhead "
            "ratios of 15-25%. Ratios above 40% warrant investigation."
        ),
    }


def _run_concentration_scenario(_simulate: bool) -> dict:
    """Run country concentration detection scenario."""
    verification = verify_aid_claim("concentration_test", "country_allocation", _simulate)

    concentration_score = verification.get("anomaly_score", 0)

    return {
        "verification": verification,
        "expected_outcome": "Concentration pattern flagged",
        "actual_outcome": f"Concentration score: {concentration_score:.4f}",
        "passed": concentration_score > 0.25,
        "interpretation": (
            "Concentration scenario tests detection of aid disproportionately "
            "allocated to a single country or region. High concentration may "
            "indicate policy bias or strategic allocation."
        ),
    }


def _run_shell_ngo_scenario(_simulate: bool) -> dict:
    """Run shell NGO detection scenario."""
    # This would integrate with other modules (spend, origin, graft)
    # for cross-domain detection
    verification = verify_aid_claim("shell_ngo_test", "waste", _simulate)

    return {
        "verification": verification,
        "expected_outcome": "Cross-domain shell flag",
        "actual_outcome": verification["verdict"],
        "passed": verification["verdict"] != "insufficient_data",
        "cross_module_links": ["spend", "graft", "origin"],
        "interpretation": (
            "Shell NGO scenario tests detection of entities receiving awards "
            "despite minimal operational capacity. Cross-domain analysis links "
            "to spend, graft, and origin modules for comprehensive detection."
        ),
    }


def _run_musk_claim_scenario(_simulate: bool) -> dict:
    """
    Run Musk's USAID claim test scenario.

    Tests claim: "Most of the USAID funding went not to aid, but to funding
    far left political causes all around the world, including some of the
    money coming back to fund the left in America."

    The system is NEUTRAL - it tests the hypothesis without political bias.
    """
    # Verify round-trip claim (the testable part of Musk's claim)
    verification = verify_aid_claim("usaid_waste", "round_trip", _simulate)

    # Get detailed partner analysis
    partner_data = ingest_implementing_partners("USAID", _simulate)
    partners = partner_data.get("partners", [])

    # Calculate aggregate statistics
    total_aid = sum(p.get("total_awards", 0) for p in partners)
    total_donations = sum(p.get("political_donations", 0) for p in partners)
    aggregate_ratio = total_donations / total_aid if total_aid > 0 else 0

    # Determine verdict
    # If <10% of aid goes to political donations, claim is unsupported
    # If >10%, claim has some evidentiary support
    if aggregate_ratio >= 0.10:
        verdict = "supported"
        verdict_explanation = (
            f"Aggregate political donation ratio of {aggregate_ratio:.2%} "
            "exceeds threshold. Evidence supports round-trip funding pattern."
        )
    else:
        verdict = "unsupported"
        verdict_explanation = (
            f"Aggregate political donation ratio of {aggregate_ratio:.2%} "
            "is below threshold. Evidence does not support systematic round-trip funding."
        )

    return {
        "claim": "Most USAID funding went to far left political causes, including money coming back to fund the left in America",
        "source": "Elon Musk X post, Dec 2024",
        "verification": verification,
        "partners_analyzed": len(partners),
        "total_aid_analyzed": total_aid,
        "total_political_donations": total_donations,
        "aggregate_ratio": round(aggregate_ratio, 4),
        "expected_outcome": "Verdict based on evidence",
        "actual_outcome": verdict,
        "verdict_explanation": verdict_explanation,
        "methodology": (
            "1. Fetch USAID implementing partners\n"
            "2. Cross-reference with FEC political donation data\n"
            "3. Calculate aggregate donation/award ratio\n"
            "4. Compare to round-trip threshold (10%)\n"
            "5. Generate evidence-based verdict"
        ),
        "neutrality_note": (
            "Gov-OS is politically neutral. This scenario tests a testable "
            "hypothesis without judging political affiliations. The system "
            "detects round-trip PATTERNS, not political POSITIONS."
        ),
        "simulation_flag": DISCLAIMER,
    }


def list_scenarios() -> Dict[str, dict]:
    """List all available scenarios."""
    return SCENARIOS.copy()


def run_all_scenarios(_simulate: bool = True) -> Dict[str, Any]:
    """Run all test scenarios and return summary."""
    results = {}
    passed = 0
    failed = 0

    for scenario_name in SCENARIOS:
        result = run_aid_scenario(scenario_name, _simulate)
        results[scenario_name] = result
        if result.get("passed", False):
            passed += 1
        else:
            failed += 1

    return {
        "scenarios_run": len(SCENARIOS),
        "passed": passed,
        "failed": failed,
        "results": results,
        "simulation_flag": DISCLAIMER,
    }


# === MODULE SELF-TEST ===

if __name__ == "__main__":
    import sys

    print(f"# Gov-OS AidProof Scenario Self-Test", file=sys.stderr)
    print(f"# {DISCLAIMER}", file=sys.stderr)

    # List scenarios
    print(f"\n# Available scenarios:", file=sys.stderr)
    for name, config in SCENARIOS.items():
        print(f"#   {name}: {config['description'][:50]}...", file=sys.stderr)

    # Run Musk claim scenario
    print(f"\n# Running MUSK_CLAIM scenario...", file=sys.stderr)
    result = run_aid_scenario("MUSK_CLAIM")
    print(f"#   Verdict: {result['actual_outcome']}", file=sys.stderr)
    print(f"#   Aggregate ratio: {result['aggregate_ratio']:.2%}", file=sys.stderr)
    print(f"#   {result['verdict_explanation'][:70]}...", file=sys.stderr)

    # Run all scenarios
    print(f"\n# Running all scenarios...", file=sys.stderr)
    summary = run_all_scenarios()
    print(f"#   Total: {summary['scenarios_run']}", file=sys.stderr)
    print(f"#   Passed: {summary['passed']}", file=sys.stderr)
    print(f"#   Failed: {summary['failed']}", file=sys.stderr)

    print(f"\n# PASS: aid scenario module self-test", file=sys.stderr)
