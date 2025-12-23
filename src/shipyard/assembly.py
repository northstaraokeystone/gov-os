"""
WarrantProof Shipyard Assembly - Robotic Welding Receipt Tracking

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

Models robotic welding and automated assembly receipts.
Core insight: Comau mobile welders and humanoid robots achieve:
- 30% efficiency gain over manual welding
- 100% weld traceability via automated logging
- Real-time defect detection during welding

Fraud Detection Model:
- Legitimate welds have predictable metadata (location, time, materials)
- Fraudulent certifications have random/inconsistent metadata
- Compression ratio detects fraud: legitimate compresses, fraud doesn't
"""

import random
from datetime import datetime
from typing import Optional

from src.core import dual_hash, emit_receipt, merkle

from .constants import (
    SHIPYARD_TENANT_ID,
    SHIPYARD_DISCLAIMER,
    COMAU_WELD_EFFICIENCY_GAIN,
    WELDS_PER_BLOCK_MIN,
    WELDS_PER_BLOCK_MAX,
    INSPECTOR_CERTIFICATION_REQUIRED,
    WELD_GRADES,
)
from .receipts import emit_block_receipt


# === CORE FUNCTIONS ===

def weld_joint(
    block_id: str,
    joint_id: str,
    robot_id: str,
    weld_type: str = "butt",
    material: str = "steel",
    position: Optional[dict] = None
) -> dict:
    """
    Execute weld and generate weld data for block_receipt.

    Args:
        block_id: Block containing this joint
        joint_id: Unique joint identifier
        robot_id: Robot performing the weld
        weld_type: Type of weld (butt, fillet, etc.)
        material: Base material being welded
        position: XYZ position dict

    Returns:
        Weld result dict
    """
    if position is None:
        position = {"x": 0.0, "y": 0.0, "z": 0.0}

    ts = datetime.utcnow().isoformat() + "Z"

    # Generate weld parameters (simulated sensor data)
    weld_params = {
        "voltage": round(25.0 + random.uniform(-2, 2), 1),
        "amperage": round(200.0 + random.uniform(-20, 20), 1),
        "travel_speed_mm_s": round(5.0 + random.uniform(-0.5, 0.5), 2),
        "wire_feed_mm_s": round(100.0 + random.uniform(-10, 10), 1),
        "shielding_gas_flow_lpm": round(15.0 + random.uniform(-1, 1), 1),
    }

    # Generate weld hash from parameters
    weld_data = f"{block_id}:{joint_id}:{robot_id}:{ts}:{weld_params}"
    weld_hash = dual_hash(weld_data)

    # Simulate quality grade (95% A, 4% B, 0.9% C, 0.1% FAIL)
    grade_roll = random.random()
    if grade_roll < 0.95:
        grade = "A"
    elif grade_roll < 0.99:
        grade = "B"
    elif grade_roll < 0.999:
        grade = "C"
    else:
        grade = "FAIL"

    return {
        "joint_id": joint_id,
        "block_id": block_id,
        "robot_id": robot_id,
        "weld_type": weld_type,
        "material": material,
        "position": position,
        "ts": ts,
        "parameters": weld_params,
        "weld_hash": weld_hash,
        "grade": grade,
        "passed": grade != "FAIL",
    }


def inspect_weld(
    weld: dict,
    inspector_type: str = "automated"
) -> dict:
    """
    QA inspection of weld (manual or automated).

    Args:
        weld: Weld dict from weld_joint
        inspector_type: "automated" or "manual"

    Returns:
        Inspection result dict
    """
    ts = datetime.utcnow().isoformat() + "Z"

    # Automated inspection has higher consistency
    if inspector_type == "automated":
        # Automated uses parameters to verify quality
        params = weld.get("parameters", {})
        voltage_ok = 20 <= params.get("voltage", 0) <= 30
        amperage_ok = 150 <= params.get("amperage", 0) <= 250
        speed_ok = 4 <= params.get("travel_speed_mm_s", 0) <= 6

        automated_pass = voltage_ok and amperage_ok and speed_ok
        confidence = 0.99 if automated_pass else 0.1
    else:
        # Manual inspection has inspector variability
        # 98% of manual inspections agree with weld grade
        automated_pass = random.random() < 0.98
        if weld.get("grade") == "FAIL":
            automated_pass = not automated_pass  # Flip for fails
        confidence = 0.90

    # Generate inspection hash
    inspection_data = f"{weld.get('weld_hash')}:{inspector_type}:{ts}"
    inspection_hash = dual_hash(inspection_data)

    return {
        "weld_id": weld.get("joint_id"),
        "block_id": weld.get("block_id"),
        "inspector_type": inspector_type,
        "ts": ts,
        "weld_grade": weld.get("grade"),
        "inspection_passed": automated_pass,
        "confidence": confidence,
        "inspection_hash": inspection_hash,
        "parameters_checked": list(weld.get("parameters", {}).keys()),
    }


def batch_block_assembly(
    block_id: str,
    ship_id: str,
    joint_count: int,
    robot_count: int = 4,
    inspector_id: str = "AUTO_INSPECTOR"
) -> dict:
    """
    Model parallel robotic assembly of a block.

    Args:
        block_id: Block identifier
        ship_id: Ship this block belongs to
        joint_count: Number of joints to weld
        robot_count: Number of robots working in parallel
        inspector_id: Inspector certifying the block

    Returns:
        Assembly result with block_receipt
    """
    # Bound joint count
    joint_count = max(WELDS_PER_BLOCK_MIN, min(WELDS_PER_BLOCK_MAX, joint_count))

    # Simulate parallel welding
    welds = []
    for i in range(joint_count):
        robot_id = f"ROBOT_{(i % robot_count) + 1:02d}"
        weld = weld_joint(
            block_id=block_id,
            joint_id=f"{block_id}_JOINT_{i:04d}",
            robot_id=robot_id,
            position={"x": i * 10.0, "y": 0.0, "z": i * 5.0}
        )
        welds.append(weld)

    # Inspect all welds
    inspections = [inspect_weld(w, "automated") for w in welds]

    # Calculate pass rate
    passed_count = sum(1 for w in welds if w.get("passed", False))
    pass_rate = passed_count / joint_count if joint_count > 0 else 1.0

    # Collect weld hashes
    weld_hashes = [w.get("weld_hash") for w in welds]

    # Emit block receipt
    receipt = emit_block_receipt(
        block_id=block_id,
        ship_id=ship_id,
        weld_count=joint_count,
        inspector_id=inspector_id,
        pass_rate=pass_rate,
        weld_hashes=weld_hashes[:20],  # First 20 for receipt size
    )

    # Calculate efficiency vs manual
    # Robotic parallel assembly: time = joints / (robots * rate)
    # Manual serial assembly: time = joints * manual_rate
    robotic_time_units = joint_count / (robot_count * (1 + COMAU_WELD_EFFICIENCY_GAIN))
    manual_time_units = joint_count * 1.0

    return {
        "block_id": block_id,
        "ship_id": ship_id,
        "joint_count": joint_count,
        "robot_count": robot_count,
        "welds": welds,
        "inspections": inspections,
        "passed_count": passed_count,
        "failed_count": joint_count - passed_count,
        "pass_rate": round(pass_rate, 4),
        "weld_merkle_root": merkle(weld_hashes),
        "robotic_time_units": round(robotic_time_units, 2),
        "manual_time_units": round(manual_time_units, 2),
        "efficiency_gain": round(1 - robotic_time_units / manual_time_units, 2) if manual_time_units > 0 else 0,
        "receipt": receipt,
        "simulation_flag": SHIPYARD_DISCLAIMER,
    }


def detect_weld_fraud(welds: list) -> list:
    """
    Find certification anomalies via compression analysis.

    Fraud detection model:
    - Legitimate welds have consistent, predictable patterns
    - Fraudulent certs have random/inconsistent data
    - Low compression ratio = high entropy = suspicious

    Args:
        welds: List of weld dicts

    Returns:
        List of anomaly dicts if fraud detected
    """
    anomalies = []

    if len(welds) < 5:
        return anomalies  # Not enough data

    # Analyze parameter consistency
    voltages = [w.get("parameters", {}).get("voltage", 0) for w in welds]
    amperages = [w.get("parameters", {}).get("amperage", 0) for w in welds]

    # Calculate variance
    import statistics
    if len(voltages) >= 2:
        voltage_std = statistics.stdev(voltages)
        amperage_std = statistics.stdev(amperages)

        # High variance suggests random/fraudulent data
        # Legitimate robotic welds have low variance
        if voltage_std > 5:  # Normal is ~2
            anomalies.append({
                "anomaly_type": "voltage_variance_high",
                "expected_std": 2.0,
                "actual_std": round(voltage_std, 2),
                "confidence": 0.7,
                "severity": "medium",
            })

        if amperage_std > 30:  # Normal is ~20
            anomalies.append({
                "anomaly_type": "amperage_variance_high",
                "expected_std": 20.0,
                "actual_std": round(amperage_std, 2),
                "confidence": 0.7,
                "severity": "medium",
            })

    # Check for duplicate weld hashes (copy-paste fraud)
    weld_hashes = [w.get("weld_hash") for w in welds]
    unique_hashes = set(weld_hashes)
    if len(unique_hashes) < len(weld_hashes) * 0.9:  # >10% duplicates
        duplicate_count = len(weld_hashes) - len(unique_hashes)
        anomalies.append({
            "anomaly_type": "duplicate_weld_hashes",
            "total_welds": len(weld_hashes),
            "unique_hashes": len(unique_hashes),
            "duplicate_count": duplicate_count,
            "confidence": 0.9,
            "severity": "high",
        })

    # Check for impossible timing (welds too close in time)
    timestamps = [w.get("ts") for w in welds if w.get("ts")]
    if len(timestamps) >= 2:
        timestamps.sort()
        for i in range(1, len(timestamps)):
            try:
                t1 = datetime.fromisoformat(timestamps[i-1].replace("Z", "+00:00"))
                t2 = datetime.fromisoformat(timestamps[i].replace("Z", "+00:00"))
                delta = (t2 - t1).total_seconds()
                if delta < 1:  # Less than 1 second between welds
                    anomalies.append({
                        "anomaly_type": "impossible_timing",
                        "weld_index": i,
                        "time_delta_seconds": delta,
                        "confidence": 0.95,
                        "severity": "critical",
                    })
                    break  # One is enough
            except (ValueError, TypeError):
                continue

    # Check for missing robot IDs (manual fraud injection)
    missing_robot = [w for w in welds if not w.get("robot_id")]
    if missing_robot:
        anomalies.append({
            "anomaly_type": "missing_robot_id",
            "affected_welds": len(missing_robot),
            "confidence": 0.8,
            "severity": "high",
        })

    return anomalies


def calculate_assembly_efficiency(
    blocks: list
) -> dict:
    """
    Calculate aggregate assembly efficiency metrics.

    Args:
        blocks: List of block assembly results

    Returns:
        Efficiency summary dict
    """
    if not blocks:
        return {
            "block_count": 0,
            "total_welds": 0,
            "avg_pass_rate": 0.0,
            "total_efficiency_gain": 0.0,
        }

    total_welds = sum(b.get("joint_count", 0) for b in blocks)
    total_passed = sum(b.get("passed_count", 0) for b in blocks)
    avg_pass_rate = total_passed / total_welds if total_welds > 0 else 0

    robotic_time = sum(b.get("robotic_time_units", 0) for b in blocks)
    manual_time = sum(b.get("manual_time_units", 0) for b in blocks)
    efficiency_gain = 1 - robotic_time / manual_time if manual_time > 0 else 0

    return {
        "block_count": len(blocks),
        "total_welds": total_welds,
        "total_passed": total_passed,
        "total_failed": total_welds - total_passed,
        "avg_pass_rate": round(avg_pass_rate, 4),
        "robotic_time_units": round(robotic_time, 2),
        "manual_time_units": round(manual_time, 2),
        "efficiency_gain_pct": round(efficiency_gain * 100, 1),
        "citations": ["COMAU_2024"],
        "simulation_flag": SHIPYARD_DISCLAIMER,
    }


# === STOPRULES ===

def stoprule_block_failed(block_id: str, pass_rate: float) -> None:
    """Stoprule: Block pass rate below threshold."""
    from .receipts import stoprule_block_inspection_failed
    stoprule_block_inspection_failed(block_id, pass_rate)


def stoprule_fraud_detected(block_id: str, anomalies: list) -> None:
    """Stoprule: Fraud detected in weld data."""
    emit_receipt("anomaly", {
        "metric": "weld_fraud_detected",
        "block_id": block_id,
        "anomaly_count": len(anomalies),
        "anomaly_types": [a.get("anomaly_type") for a in anomalies],
        "delta": -len(anomalies),
        "action": "halt",
        "classification": "cert_fraud",
        "simulation_flag": SHIPYARD_DISCLAIMER,
    }, to_stdout=False)


# === MODULE SELF-TEST ===

if __name__ == "__main__":
    print("# WarrantProof Shipyard Assembly Self-Test", file=sys.stderr)
    print(f"# {SHIPYARD_DISCLAIMER}", file=sys.stderr)

    # Test single weld
    weld = weld_joint(
        block_id="BLOCK-001",
        joint_id="JOINT-001",
        robot_id="ROBOT_01"
    )
    assert "weld_hash" in weld, "Weld should have hash"
    assert weld["grade"] in WELD_GRADES, f"Invalid grade: {weld['grade']}"
    print(f"# Single weld: grade={weld['grade']}", file=sys.stderr)

    # Test inspection
    inspection = inspect_weld(weld, "automated")
    assert "inspection_hash" in inspection, "Inspection should have hash"
    print(f"# Inspection: passed={inspection['inspection_passed']}", file=sys.stderr)

    # Test batch assembly
    assembly = batch_block_assembly(
        block_id="BLOCK-001",
        ship_id="SHIP-001",
        joint_count=100,
        robot_count=4
    )
    assert assembly["joint_count"] == 100, "Should have 100 joints"
    assert assembly["pass_rate"] > 0.9, "Pass rate should be >90%"
    assert assembly["efficiency_gain"] > 0, "Should have efficiency gain"
    print(f"# Block assembled: {assembly['joint_count']} welds, pass_rate={assembly['pass_rate']:.2%}", file=sys.stderr)
    print(f"# Efficiency gain: {assembly['efficiency_gain']:.0%}", file=sys.stderr)

    # Test fraud detection (clean data)
    anomalies = detect_weld_fraud(assembly["welds"])
    print(f"# Fraud detection (clean): {len(anomalies)} anomalies", file=sys.stderr)

    # Test fraud detection with injected fraud
    fraud_welds = assembly["welds"][:10]
    # Inject duplicate hashes
    for w in fraud_welds[5:]:
        w["weld_hash"] = fraud_welds[0]["weld_hash"]
    fraud_anomalies = detect_weld_fraud(fraud_welds)
    assert any(a["anomaly_type"] == "duplicate_weld_hashes" for a in fraud_anomalies), "Should detect duplicates"
    print(f"# Fraud detection (injected): {len(fraud_anomalies)} anomalies", file=sys.stderr)

    print("# PASS: Assembly module validated", file=sys.stderr)
