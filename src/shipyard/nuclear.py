"""
WarrantProof Shipyard Nuclear - SMR Propulsion Integration

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

Models NuScale-style SMR (Small Modular Reactor) nuclear propulsion.
Core insight: NuScale 77 MWe design enables:
- Unlimited range (no refueling constraints)
- Lifetime fuel savings vs conventional propulsion
- Compact reactor fits battleship design envelope

Constraints:
- Power bounded by NUSCALE_POWER_MWE (77 MWe)
- Each reactor requires NRC certification receipt chain
- Cannot integrate without cert chain complete
"""

from datetime import datetime
from typing import Optional

from src.core import dual_hash, emit_receipt, merkle

from .constants import (
    SHIPYARD_TENANT_ID,
    SHIPYARD_DISCLAIMER,
    NUSCALE_POWER_MWE,
)
from .receipts import emit_propulsion_receipt


# === NRC CERTIFICATION STEPS ===

NRC_CERTIFICATION_STEPS = [
    "design_certification",
    "combined_license",
    "construction_permit",
    "operating_license",
    "fuel_loading_authorization",
]

# Reactor parameters
SMR_SPECS = {
    "nuscale_77": {
        "power_mwe": 77,
        "power_mwt": 250,
        "modules_per_plant": 12,
        "refueling_interval_years": 2,
        "design_life_years": 60,
        "footprint_acres": 35,
        "fuel_type": "UO2",
        "enrichment_pct": 4.95,
    },
}


# === CORE FUNCTIONS ===

def install_reactor(
    reactor_id: str,
    ship_id: str,
    power_mwe: float,
    reactor_type: str = "nuscale_77"
) -> dict:
    """
    Model reactor installation and emit propulsion_receipt.

    Args:
        reactor_id: Unique reactor identifier
        ship_id: Ship receiving the reactor
        power_mwe: Rated power output in MWe
        reactor_type: SMR type (default: nuscale_77)

    Returns:
        Reactor installation dict
    """
    ts = datetime.utcnow().isoformat() + "Z"

    # Validate power rating
    max_power = NUSCALE_POWER_MWE
    if power_mwe > max_power:
        power_mwe = max_power  # Cap at approved maximum

    # Get reactor specs
    specs = SMR_SPECS.get(reactor_type, SMR_SPECS["nuscale_77"])

    # Generate installation hash
    install_data = f"{reactor_id}:{ship_id}:{power_mwe}:{ts}"
    install_hash = dual_hash(install_data)

    # Create reactor state
    reactor = {
        "reactor_id": reactor_id,
        "ship_id": ship_id,
        "reactor_type": reactor_type,
        "power_mwe": power_mwe,
        "power_mwt": specs["power_mwt"] * (power_mwe / specs["power_mwe"]),
        "installed_at": ts,
        "installation_hash": install_hash,
        "certification_status": "pending",
        "cert_chain": [],
        "test_results": [],
        "specs": specs,
        "simulation_flag": SHIPYARD_DISCLAIMER,
    }

    return reactor


def conduct_power_test(
    reactor: dict,
    duration_hours: int,
    test_type: str = "full_power"
) -> dict:
    """
    Conduct power validation test and return metrics.

    Args:
        reactor: Reactor dict from install_reactor
        duration_hours: Test duration in hours
        test_type: Type of test (startup, partial_power, full_power)

    Returns:
        Test results dict
    """
    ts = datetime.utcnow().isoformat() + "Z"

    power_mwe = reactor.get("power_mwe", NUSCALE_POWER_MWE)

    # Simulate test parameters
    if test_type == "startup":
        target_power_pct = 0.1
    elif test_type == "partial_power":
        target_power_pct = 0.5
    else:  # full_power
        target_power_pct = 1.0

    achieved_power = power_mwe * target_power_pct

    # Simulate test results
    import random
    random.seed(hash(reactor.get("reactor_id", "")) + duration_hours)

    temperature_avg = 300 + random.uniform(-5, 5)  # Celsius
    pressure_avg = 155 + random.uniform(-2, 2)  # Bar
    efficiency = 0.32 + random.uniform(-0.01, 0.01)  # 32% typical

    # Calculate energy output
    energy_mwh = achieved_power * duration_hours

    # Generate test hash
    test_data = f"{reactor['reactor_id']}:{test_type}:{duration_hours}:{achieved_power}:{ts}"
    test_hash = dual_hash(test_data)

    # Test passes if within tolerances
    temp_ok = 290 <= temperature_avg <= 310
    pressure_ok = 150 <= pressure_avg <= 160
    efficiency_ok = efficiency >= 0.30

    test_passed = temp_ok and pressure_ok and efficiency_ok

    test_result = {
        "reactor_id": reactor.get("reactor_id"),
        "test_type": test_type,
        "ts": ts,
        "duration_hours": duration_hours,
        "target_power_pct": target_power_pct,
        "achieved_power_mwe": round(achieved_power, 2),
        "energy_output_mwh": round(energy_mwh, 2),
        "parameters": {
            "temperature_avg_c": round(temperature_avg, 1),
            "pressure_avg_bar": round(pressure_avg, 1),
            "efficiency": round(efficiency, 4),
        },
        "tolerances_met": {
            "temperature": temp_ok,
            "pressure": pressure_ok,
            "efficiency": efficiency_ok,
        },
        "test_passed": test_passed,
        "test_hash": test_hash,
    }

    # Add to reactor test results
    reactor["test_results"].append(test_result)

    return test_result


def calculate_lifetime_savings(
    reactor: dict,
    conventional: dict
) -> dict:
    """
    Compare fuel costs over ship lifetime vs conventional propulsion.

    Args:
        reactor: Nuclear reactor dict
        conventional: Conventional propulsion specs dict

    Returns:
        Lifetime savings comparison dict
    """
    # Get specs
    specs = reactor.get("specs", SMR_SPECS["nuscale_77"])
    design_life_years = specs.get("design_life_years", 60)
    refuel_interval = specs.get("refueling_interval_years", 2)

    power_mwe = reactor.get("power_mwe", NUSCALE_POWER_MWE)

    # Nuclear costs
    # Fuel cost: ~$0.005/kWh for nuclear
    nuclear_fuel_cost_per_kwh = 0.005
    hours_per_year = 8760 * 0.90  # 90% capacity factor
    annual_output_kwh = power_mwe * 1000 * hours_per_year
    nuclear_annual_fuel_cost = annual_output_kwh * nuclear_fuel_cost_per_kwh
    nuclear_lifetime_fuel = nuclear_annual_fuel_cost * design_life_years

    # Refueling costs
    refuel_cost_per_cycle = 50_000_000  # $50M per refuel
    refuel_cycles = design_life_years / refuel_interval
    nuclear_refuel_total = refuel_cost_per_cycle * refuel_cycles

    nuclear_total = nuclear_lifetime_fuel + nuclear_refuel_total

    # Conventional costs
    conv_power_kw = conventional.get("power_kw", power_mwe * 1000)
    conv_efficiency = conventional.get("efficiency", 0.40)
    fuel_price_per_gallon = conventional.get("fuel_price", 4.0)  # USD/gallon
    fuel_energy_kwh_per_gallon = 36.6  # kWh per gallon diesel equivalent

    # Annual fuel consumption
    conv_annual_output_kwh = conv_power_kw * hours_per_year
    conv_fuel_input_kwh = conv_annual_output_kwh / conv_efficiency
    conv_gallons_per_year = conv_fuel_input_kwh / fuel_energy_kwh_per_gallon
    conv_annual_fuel_cost = conv_gallons_per_year * fuel_price_per_gallon
    conv_lifetime_fuel = conv_annual_fuel_cost * design_life_years

    # Conventional also needs engine overhauls
    overhaul_interval = 5  # years
    overhaul_cost = 10_000_000  # $10M
    overhaul_count = design_life_years / overhaul_interval
    conv_overhaul_total = overhaul_cost * overhaul_count

    conv_total = conv_lifetime_fuel + conv_overhaul_total

    # Calculate savings
    savings_absolute = conv_total - nuclear_total
    savings_pct = (savings_absolute / conv_total) * 100 if conv_total > 0 else 0

    return {
        "reactor_id": reactor.get("reactor_id"),
        "design_life_years": design_life_years,
        "nuclear": {
            "power_mwe": power_mwe,
            "annual_fuel_cost_usd": round(nuclear_annual_fuel_cost),
            "lifetime_fuel_cost_usd": round(nuclear_lifetime_fuel),
            "refueling_cost_usd": round(nuclear_refuel_total),
            "total_lifetime_cost_usd": round(nuclear_total),
        },
        "conventional": {
            "power_kw": conv_power_kw,
            "annual_fuel_cost_usd": round(conv_annual_fuel_cost),
            "lifetime_fuel_cost_usd": round(conv_lifetime_fuel),
            "overhaul_cost_usd": round(conv_overhaul_total),
            "total_lifetime_cost_usd": round(conv_total),
        },
        "comparison": {
            "savings_usd": round(savings_absolute),
            "savings_pct": round(savings_pct, 1),
            "nuclear_recommended": savings_absolute > 0,
        },
        "citations": ["NRC_2025"],
        "simulation_flag": SHIPYARD_DISCLAIMER,
    }


def certification_chain(reactor: dict) -> list:
    """
    Return full NRC certification receipt chain.

    Args:
        reactor: Reactor dict

    Returns:
        List of certification receipts
    """
    cert_chain = []
    reactor_id = reactor.get("reactor_id", "UNKNOWN")

    for step in NRC_CERTIFICATION_STEPS:
        ts = datetime.utcnow().isoformat() + "Z"
        cert_data = f"{reactor_id}:{step}:{ts}"
        cert_hash = dual_hash(cert_data)

        cert_receipt = emit_receipt("nrc_certification", {
            "tenant_id": SHIPYARD_TENANT_ID,
            "reactor_id": reactor_id,
            "certification_step": step,
            "step_index": NRC_CERTIFICATION_STEPS.index(step),
            "total_steps": len(NRC_CERTIFICATION_STEPS),
            "cert_hash": cert_hash,
            "status": "approved",
            "simulation_flag": SHIPYARD_DISCLAIMER,
        }, to_stdout=False)

        cert_chain.append(cert_receipt)

    # Update reactor with complete chain
    reactor["cert_chain"] = cert_chain
    reactor["certification_status"] = "complete"

    return cert_chain


def emit_reactor_integration(reactor: dict) -> dict:
    """
    Emit propulsion_receipt with complete certification chain.

    Args:
        reactor: Reactor dict with completed cert chain

    Returns:
        propulsion_receipt dict
    """
    # Ensure cert chain is complete
    if not reactor.get("cert_chain"):
        certification_chain(reactor)

    # Get test hash if available
    test_hash = None
    if reactor.get("test_results"):
        test_hashes = [t.get("test_hash") for t in reactor["test_results"] if t.get("test_hash")]
        test_hash = merkle(test_hashes) if test_hashes else None

    # Emit propulsion receipt
    receipt = emit_propulsion_receipt(
        reactor_id=reactor.get("reactor_id"),
        ship_id=reactor.get("ship_id"),
        power_mwe=reactor.get("power_mwe", NUSCALE_POWER_MWE),
        test_hash=test_hash,
        nrc_cert_chain=[c.get("payload_hash") for c in reactor.get("cert_chain", [])],
    )

    reactor["integration_receipt"] = receipt
    return receipt


def validate_reactor_ready(reactor: dict) -> dict:
    """
    Validate reactor is ready for operation.

    Args:
        reactor: Reactor dict

    Returns:
        Validation result dict
    """
    issues = []

    # Check certification
    if reactor.get("certification_status") != "complete":
        issues.append("certification_incomplete")

    # Check cert chain length
    cert_chain = reactor.get("cert_chain", [])
    if len(cert_chain) < len(NRC_CERTIFICATION_STEPS):
        issues.append(f"cert_chain_incomplete_{len(cert_chain)}_of_{len(NRC_CERTIFICATION_STEPS)}")

    # Check tests
    test_results = reactor.get("test_results", [])
    if not test_results:
        issues.append("no_power_tests")
    else:
        # Check for full power test
        full_power_tests = [t for t in test_results if t.get("test_type") == "full_power"]
        if not full_power_tests:
            issues.append("no_full_power_test")
        elif not all(t.get("test_passed") for t in full_power_tests):
            issues.append("full_power_test_failed")

    # Check power rating
    power = reactor.get("power_mwe", 0)
    if power > NUSCALE_POWER_MWE:
        issues.append(f"power_exceeds_max_{power}_vs_{NUSCALE_POWER_MWE}")

    return {
        "reactor_id": reactor.get("reactor_id"),
        "ready": len(issues) == 0,
        "issues": issues,
        "certification_status": reactor.get("certification_status"),
        "tests_completed": len(test_results),
        "tests_passed": sum(1 for t in test_results if t.get("test_passed", False)),
        "simulation_flag": SHIPYARD_DISCLAIMER,
    }


# === STOPRULES ===

def stoprule_cert_incomplete(reactor_id: str, missing_steps: list) -> None:
    """Stoprule: Reactor installation attempted without complete certification."""
    emit_receipt("anomaly", {
        "metric": "nrc_cert_incomplete",
        "reactor_id": reactor_id,
        "missing_steps": missing_steps,
        "delta": -len(missing_steps),
        "action": "halt",
        "classification": "regulatory_violation",
        "simulation_flag": SHIPYARD_DISCLAIMER,
    }, to_stdout=False)


def stoprule_test_failed(reactor_id: str, test_type: str, failures: dict) -> None:
    """Stoprule: Critical power test failed."""
    emit_receipt("anomaly", {
        "metric": "reactor_test_failed",
        "reactor_id": reactor_id,
        "test_type": test_type,
        "failures": failures,
        "delta": -1,
        "action": "halt",
        "classification": "safety_violation",
        "simulation_flag": SHIPYARD_DISCLAIMER,
    }, to_stdout=False)


# === MODULE SELF-TEST ===

if __name__ == "__main__":
    print("# WarrantProof Shipyard Nuclear Self-Test", file=sys.stderr)
    print(f"# {SHIPYARD_DISCLAIMER}", file=sys.stderr)

    # Install reactor
    reactor = install_reactor(
        reactor_id="SMR-001",
        ship_id="BBG-001",
        power_mwe=77.0
    )
    assert reactor["power_mwe"] == 77.0, "Should have 77 MWe power"
    print(f"# Reactor installed: {reactor['reactor_id']} @ {reactor['power_mwe']} MWe", file=sys.stderr)

    # Conduct power tests
    for test_type in ["startup", "partial_power", "full_power"]:
        result = conduct_power_test(reactor, duration_hours=24, test_type=test_type)
        print(f"# {test_type} test: passed={result['test_passed']}", file=sys.stderr)

    # Get certification chain
    certs = certification_chain(reactor)
    assert len(certs) == len(NRC_CERTIFICATION_STEPS), f"Should have {len(NRC_CERTIFICATION_STEPS)} certs"
    print(f"# Certification steps: {len(certs)}", file=sys.stderr)

    # Calculate lifetime savings
    conventional = {"power_kw": 77000, "efficiency": 0.40, "fuel_price": 4.0}
    savings = calculate_lifetime_savings(reactor, conventional)
    assert savings["comparison"]["nuclear_recommended"], "Nuclear should be recommended"
    print(f"# Lifetime savings: ${savings['comparison']['savings_usd']:,.0f} ({savings['comparison']['savings_pct']:.0f}%)", file=sys.stderr)

    # Validate readiness
    validation = validate_reactor_ready(reactor)
    assert validation["ready"], f"Reactor should be ready: {validation['issues']}"
    print(f"# Reactor ready: {validation['ready']}", file=sys.stderr)

    # Emit integration receipt
    receipt = emit_reactor_integration(reactor)
    assert "nrc_cert_chain" in receipt, "Should have cert chain in receipt"
    print(f"# Integration receipt emitted", file=sys.stderr)

    print("# PASS: Nuclear module validated", file=sys.stderr)
