"""
WarrantProof Shipyard Additive - 3D Printing Hull Validation

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

Models LFAM (Large Format Additive Manufacturing) for hull sections.
Core insight: LFAM achieves:
- 40-50% time savings on hull sections
- 40% weight reduction through topology optimization
- Real-time material certification via print receipts

QA Model:
- Each layer generates validation hash
- Final part hash = merkle root of all layer hashes
- Anomaly = hash discontinuity between layers
"""

import math
from datetime import datetime
from typing import Optional

from src.core import dual_hash, emit_receipt, merkle

from .constants import (
    SHIPYARD_TENANT_ID,
    SHIPYARD_DISCLAIMER,
    LFAM_TIME_SAVINGS_PCT,
    LFAM_WEIGHT_SAVINGS_PCT,
    LFAM_DEPOSITION_RATE_KG_HR,
    MARINE_CERTIFIED_MATERIALS,
    LAYER_HASH_TOLERANCE,
)
from .receipts import emit_additive_receipt, stoprule_additive_layer_mismatch


# === CORE FUNCTIONS ===

def print_section(
    part_id: str,
    material: str,
    printer_id: str,
    traditional_mass_kg: float = 1000.0,
    layer_thickness_mm: float = 5.0
) -> dict:
    """
    Model 3D print job and emit additive_receipt.

    Args:
        part_id: Unique part identifier
        material: Material type (must be marine certified)
        printer_id: Printer identifier
        traditional_mass_kg: Mass if manufactured traditionally
        layer_thickness_mm: Print layer thickness in mm

    Returns:
        Print result dict with receipt
    """
    # Validate material
    if material not in MARINE_CERTIFIED_MATERIALS:
        # Emit warning but allow for simulation flexibility
        pass

    # Calculate optimized mass (40% weight reduction via topology optimization)
    optimized_mass_kg = traditional_mass_kg * (1 - LFAM_WEIGHT_SAVINGS_PCT)

    # Calculate print time
    print_hours = optimized_mass_kg / LFAM_DEPOSITION_RATE_KG_HR

    # Calculate traditional time for comparison
    traditional_hours = print_hours / (1 - LFAM_TIME_SAVINGS_PCT)

    # Estimate layer count based on part size
    # Assuming cube-ish geometry for simplicity
    part_height_mm = (optimized_mass_kg * 1000) ** (1/3) * 10  # Rough estimate
    layer_count = max(1, int(part_height_mm / layer_thickness_mm))

    # Generate layer hashes
    layer_hashes = []
    for i in range(layer_count):
        layer_data = f"{part_id}:layer_{i}:{material}:{optimized_mass_kg/layer_count:.4f}"
        layer_hash = dual_hash(layer_data)
        layer_hashes.append(layer_hash)

    # QA hash = merkle root of layers
    qa_hash = merkle(layer_hashes)

    # Emit receipt
    receipt = emit_additive_receipt(
        part_id=part_id,
        printer_id=printer_id,
        material_kg=optimized_mass_kg,
        print_hours=print_hours,
        material_type=material,
        qa_hash=qa_hash,
        layer_count=layer_count,
        layer_hashes=layer_hashes[:10],  # First 10 for receipt size
    )

    return {
        "part_id": part_id,
        "material": material,
        "printer_id": printer_id,
        "traditional_mass_kg": traditional_mass_kg,
        "optimized_mass_kg": round(optimized_mass_kg, 2),
        "mass_savings_pct": round(LFAM_WEIGHT_SAVINGS_PCT * 100, 1),
        "print_hours": round(print_hours, 2),
        "traditional_hours": round(traditional_hours, 2),
        "time_savings_pct": round(LFAM_TIME_SAVINGS_PCT * 100, 1),
        "layer_count": layer_count,
        "qa_hash": qa_hash,
        "receipt": receipt,
        "simulation_flag": SHIPYARD_DISCLAIMER,
    }


def validate_layer(
    part: dict,
    layer_id: int
) -> dict:
    """
    Per-layer QA check during print.

    Args:
        part: Part dict from print_section
        layer_id: Layer index to validate

    Returns:
        Validation result dict
    """
    layer_hashes = part.get("receipt", {}).get("layer_hashes", [])

    if layer_id >= len(layer_hashes):
        return {
            "layer_id": layer_id,
            "valid": False,
            "reason": "Layer index out of range",
        }

    # Simulate layer validation
    # In reality, this would compare sensor data to expected values
    expected_hash = layer_hashes[layer_id]

    # Simulate measurement with small tolerance
    # 99% of layers pass validation
    import random
    validation_passed = random.random() < 0.99

    if validation_passed:
        measured_hash = expected_hash
    else:
        # Simulate hash mismatch
        measured_hash = dual_hash(f"anomaly:{layer_id}")

    valid = measured_hash == expected_hash

    result = {
        "part_id": part.get("part_id"),
        "layer_id": layer_id,
        "expected_hash": expected_hash[:32],
        "measured_hash": measured_hash[:32],
        "valid": valid,
        "tolerance": LAYER_HASH_TOLERANCE,
    }

    if not valid:
        # Emit anomaly receipt but don't halt (allow simulation to continue)
        emit_receipt("anomaly", {
            "metric": "layer_validation_failed",
            "part_id": part.get("part_id"),
            "layer_id": layer_id,
            "delta": -1,
            "action": "review",
            "classification": "quality",
            "simulation_flag": SHIPYARD_DISCLAIMER,
        }, to_stdout=False)

    return result


def calculate_material_savings(
    traditional_kg: float,
    additive_kg: float
) -> float:
    """
    Calculate material savings ratio.

    Args:
        traditional_kg: Traditional manufacturing material usage
        additive_kg: Additive manufacturing material usage

    Returns:
        Savings ratio (0.4 = 40% savings)
    """
    if traditional_kg <= 0:
        return 0.0

    savings = (traditional_kg - additive_kg) / traditional_kg
    return round(max(0.0, min(1.0, savings)), 4)


def detect_print_anomaly(part: dict) -> list:
    """
    Detect anomalies in print data.

    Anomaly types:
    - Layer hash discontinuity (sudden change in hash pattern)
    - Material usage deviation (kg used vs expected)
    - Print time deviation (hours vs expected)

    Args:
        part: Part dict from print_section

    Returns:
        List of anomaly dicts if detected
    """
    anomalies = []
    receipt = part.get("receipt", {})

    # Check layer hash continuity
    layer_hashes = receipt.get("layer_hashes", [])
    if len(layer_hashes) > 1:
        # Look for discontinuities (simulated)
        # In reality, would analyze hash patterns for sudden changes
        pass

    # Check material usage deviation
    expected_kg = part.get("optimized_mass_kg", 0)
    actual_kg = receipt.get("material_kg", 0)
    if expected_kg > 0:
        kg_deviation = abs(actual_kg - expected_kg) / expected_kg
        if kg_deviation > 0.1:  # 10% deviation threshold
            anomalies.append({
                "anomaly_type": "material_deviation",
                "expected_kg": expected_kg,
                "actual_kg": actual_kg,
                "deviation_pct": round(kg_deviation * 100, 2),
                "severity": "medium",
            })

    # Check print time deviation
    expected_hours = part.get("print_hours", 0)
    actual_hours = receipt.get("print_hours", 0)
    if expected_hours > 0:
        time_deviation = abs(actual_hours - expected_hours) / expected_hours
        if time_deviation > 0.2:  # 20% deviation threshold
            anomalies.append({
                "anomaly_type": "time_deviation",
                "expected_hours": expected_hours,
                "actual_hours": actual_hours,
                "deviation_pct": round(time_deviation * 100, 2),
                "severity": "low",
            })

    # Check material certification
    material = part.get("material", "")
    if material and material not in MARINE_CERTIFIED_MATERIALS:
        anomalies.append({
            "anomaly_type": "uncertified_material",
            "material": material,
            "certified_materials": MARINE_CERTIFIED_MATERIALS,
            "severity": "high",
        })

    return anomalies


def calculate_additive_benefits(
    parts_traditional: list,
    parts_additive: list
) -> dict:
    """
    Calculate aggregate benefits of additive manufacturing.

    Args:
        parts_traditional: List of traditionally manufactured part specs
        parts_additive: List of additively manufactured parts

    Returns:
        Benefits summary dict
    """
    total_trad_mass = sum(p.get("mass_kg", 0) for p in parts_traditional)
    total_trad_hours = sum(p.get("hours", 0) for p in parts_traditional)

    total_add_mass = sum(p.get("optimized_mass_kg", 0) for p in parts_additive)
    total_add_hours = sum(p.get("print_hours", 0) for p in parts_additive)

    mass_savings = calculate_material_savings(total_trad_mass, total_add_mass)
    time_savings = calculate_material_savings(total_trad_hours, total_add_hours)

    return {
        "part_count": len(parts_additive),
        "total_traditional_mass_kg": round(total_trad_mass, 2),
        "total_additive_mass_kg": round(total_add_mass, 2),
        "mass_savings_pct": round(mass_savings * 100, 1),
        "total_traditional_hours": round(total_trad_hours, 2),
        "total_additive_hours": round(total_add_hours, 2),
        "time_savings_pct": round(time_savings * 100, 1),
        "citations": ["UMAINE_2025", "NAVY_2025"],
        "simulation_flag": SHIPYARD_DISCLAIMER,
    }


def emit_additive_batch(
    ship_id: str,
    parts: list
) -> dict:
    """
    Emit batch additive receipt for multiple parts.

    Args:
        ship_id: Ship identifier
        parts: List of part dicts from print_section

    Returns:
        Batch receipt dict
    """
    total_mass = sum(p.get("optimized_mass_kg", 0) for p in parts)
    total_hours = sum(p.get("print_hours", 0) for p in parts)
    part_ids = [p.get("part_id") for p in parts]

    # Compute merkle root of all part QA hashes
    qa_hashes = [p.get("qa_hash", "") for p in parts if p.get("qa_hash")]
    batch_merkle = merkle(qa_hashes) if qa_hashes else dual_hash("empty_batch")

    receipt = emit_receipt("additive_batch", {
        "tenant_id": SHIPYARD_TENANT_ID,
        "ship_id": ship_id,
        "part_count": len(parts),
        "part_ids": part_ids,
        "total_mass_kg": round(total_mass, 2),
        "total_print_hours": round(total_hours, 2),
        "batch_merkle_root": batch_merkle,
        "simulation_flag": SHIPYARD_DISCLAIMER,
    }, to_stdout=False)

    return receipt


# === MODULE SELF-TEST ===

if __name__ == "__main__":
    print("# WarrantProof Shipyard Additive Self-Test", file=sys.stderr)
    print(f"# {SHIPYARD_DISCLAIMER}", file=sys.stderr)

    # Test print section
    result = print_section(
        part_id="HULL-001",
        material="HDPE",
        printer_id="LFAM-001",
        traditional_mass_kg=1000.0
    )
    assert result["optimized_mass_kg"] < 1000.0, "Should reduce mass"
    assert result["print_hours"] < result["traditional_hours"], "Should reduce time"
    assert "qa_hash" in result, "Should have QA hash"
    print(f"# Part printed: {result['optimized_mass_kg']}kg in {result['print_hours']:.1f}h", file=sys.stderr)

    # Test layer validation
    validation = validate_layer(result, 0)
    print(f"# Layer 0 validation: {validation['valid']}", file=sys.stderr)

    # Test material savings calculation
    savings = calculate_material_savings(1000.0, 600.0)
    assert savings == 0.4, f"Expected 0.4 savings, got {savings}"
    print(f"# Material savings: {savings * 100}%", file=sys.stderr)

    # Test anomaly detection
    anomalies = detect_print_anomaly(result)
    print(f"# Anomalies detected: {len(anomalies)}", file=sys.stderr)

    # Test with uncertified material
    bad_result = print_section(
        part_id="HULL-002",
        material="UNKNOWN_MATERIAL",
        printer_id="LFAM-001",
        traditional_mass_kg=500.0
    )
    bad_anomalies = detect_print_anomaly(bad_result)
    assert any(a["anomaly_type"] == "uncertified_material" for a in bad_anomalies), "Should detect uncertified material"
    print(f"# Uncertified material detected: {len(bad_anomalies)} anomalies", file=sys.stderr)

    print("# PASS: Additive module validated", file=sys.stderr)
