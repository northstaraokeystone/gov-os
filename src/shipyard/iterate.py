"""
WarrantProof Shipyard Iterate - SpaceX-Style Rapid Iteration Modeling

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

Models Starfactory-style rapid iteration for shipbuilding.
Core insight: Starfactory achieves 10x cadence through:
- Parallel mega-bay assembly (not serial)
- On-site vertical integration (no transport delays)
- Rapid prototype-test-iterate cycles (not waterfall)

Entropy Model:
- Higher iteration cadence -> lower entropy (more information per unit time)
- Parallel assembly -> multiplicative entropy reduction
- Waterfall pattern -> entropy accumulation (fraud-like signal)
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from src.core import dual_hash, emit_receipt

from .constants import (
    SHIPYARD_TENANT_ID,
    SHIPYARD_DISCLAIMER,
    STARFACTORY_CADENCE_WEEKS,
    MIN_ITERATION_DAYS,
    MAX_ITERATIONS_PER_MONTH,
    STARFACTORY_MEGA_BAYS,
    TRADITIONAL_SERIAL_BAYS,
)
from .receipts import emit_iteration_receipt


# === ITERATION METRICS ===

@dataclass
class IterationMetrics:
    """Metrics for iteration cadence analysis."""
    cadence_per_month: float
    parallel_factor: float
    entropy_reduction: float
    is_waterfall: bool
    efficiency_score: float


# === CORE FUNCTIONS ===

def calculate_iteration_cadence(
    changes: list,
    duration_days: int
) -> float:
    """
    Calculate iterations per month from change history.

    Args:
        changes: List of changes (each representing an iteration cycle)
        duration_days: Total duration in days

    Returns:
        Iterations per month rate
    """
    if duration_days <= 0:
        return 0.0

    iterations = len(changes)
    days_per_month = 30.0
    cadence = (iterations / duration_days) * days_per_month

    return round(cadence, 2)


def model_parallel_assembly(
    blocks: list,
    bays: int
) -> dict:
    """
    Model parallelization efficiency across mega-bays.

    Args:
        blocks: List of blocks to assemble
        bays: Number of parallel assembly bays

    Returns:
        Parallelization metrics dict
    """
    if not blocks:
        return {
            "blocks": 0,
            "bays": bays,
            "parallel_efficiency": 1.0,
            "theoretical_speedup": 1.0,
            "actual_speedup": 1.0,
        }

    n_blocks = len(blocks)

    # Theoretical speedup = min(bays, blocks)
    theoretical_speedup = min(bays, n_blocks)

    # Actual speedup accounts for coordination overhead
    # Amdahl's law: speedup = 1 / (s + (1-s)/p)
    # where s = serial fraction, p = parallel processors
    serial_fraction = 0.1  # 10% serial overhead
    actual_speedup = 1.0 / (serial_fraction + (1 - serial_fraction) / min(bays, n_blocks))

    # Parallel efficiency = actual / theoretical
    parallel_efficiency = actual_speedup / theoretical_speedup if theoretical_speedup > 0 else 1.0

    return {
        "blocks": n_blocks,
        "bays": bays,
        "parallel_efficiency": round(parallel_efficiency, 3),
        "theoretical_speedup": round(theoretical_speedup, 2),
        "actual_speedup": round(actual_speedup, 2),
        "serial_fraction": serial_fraction,
    }


def compression_from_iteration(
    cadence: float,
    baseline: float
) -> float:
    """
    Calculate entropy reduction from faster iteration cycles.

    Physics: More iterations = more learning = lower entropy.
    The compression ratio increases with iteration cadence.

    Args:
        cadence: Current iteration cadence (per month)
        baseline: Baseline cadence for comparison

    Returns:
        Entropy reduction factor (1.0 = no change, <1.0 = reduction)
    """
    if baseline <= 0:
        return 1.0

    if cadence <= baseline:
        return 1.0  # No improvement over baseline

    # Logarithmic compression: doubling cadence reduces entropy by ~30%
    import math
    ratio = cadence / baseline
    entropy_reduction = 1.0 / (1.0 + 0.3 * math.log2(ratio))

    return round(entropy_reduction, 3)


def detect_waterfall_pattern(iterations: list) -> bool:
    """
    Detect if iterations follow waterfall pattern (bad) vs parallel (good).

    Waterfall indicators:
    - Long gaps between iterations
    - Sequential dependencies
    - No overlapping work

    Args:
        iterations: List of iteration dicts with timestamps

    Returns:
        True if serial/waterfall pattern detected (bad)
    """
    if len(iterations) < 3:
        return False  # Not enough data

    # Extract timestamps
    timestamps = []
    for it in iterations:
        ts = it.get("ts") or it.get("timestamp")
        if ts:
            try:
                if isinstance(ts, str):
                    ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                timestamps.append(ts)
            except (ValueError, TypeError):
                continue

    if len(timestamps) < 3:
        return False

    # Sort timestamps
    timestamps.sort()

    # Calculate gaps between iterations
    gaps = []
    for i in range(1, len(timestamps)):
        gap = (timestamps[i] - timestamps[i - 1]).days
        gaps.append(gap)

    # Waterfall pattern: consistently long gaps (>2 weeks between iterations)
    avg_gap = sum(gaps) / len(gaps) if gaps else 0

    # If average gap > 14 days, likely waterfall
    if avg_gap > 14:
        return True

    # Also check for irregular spacing (high variance = waterfall)
    if len(gaps) >= 3:
        import statistics
        gap_std = statistics.stdev(gaps)
        gap_cv = gap_std / avg_gap if avg_gap > 0 else 0

        # High coefficient of variation suggests irregular (waterfall) pattern
        if gap_cv > 1.0:
            return True

    return False


def calculate_iteration_efficiency(
    iterations: list,
    baseline_cadence: float = 1.0
) -> IterationMetrics:
    """
    Calculate comprehensive iteration efficiency metrics.

    Args:
        iterations: List of iteration records
        baseline_cadence: Baseline iterations per month

    Returns:
        IterationMetrics dataclass
    """
    if not iterations:
        return IterationMetrics(
            cadence_per_month=0.0,
            parallel_factor=1.0,
            entropy_reduction=1.0,
            is_waterfall=False,
            efficiency_score=0.0,
        )

    # Calculate time span
    first_ts = None
    last_ts = None
    for it in iterations:
        ts = it.get("ts") or it.get("timestamp")
        if ts:
            try:
                if isinstance(ts, str):
                    ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                if first_ts is None or ts < first_ts:
                    first_ts = ts
                if last_ts is None or ts > last_ts:
                    last_ts = ts
            except (ValueError, TypeError):
                continue

    # Calculate duration
    if first_ts and last_ts:
        duration_days = max(1, (last_ts - first_ts).days)
    else:
        duration_days = 30  # Default to 1 month

    # Calculate cadence
    cadence = calculate_iteration_cadence(iterations, duration_days)

    # Detect waterfall
    is_waterfall = detect_waterfall_pattern(iterations)

    # Calculate parallel factor from iteration data
    parallel_factors = [it.get("parallel_factor", 1.0) for it in iterations]
    avg_parallel = sum(parallel_factors) / len(parallel_factors) if parallel_factors else 1.0

    # Calculate entropy reduction
    entropy_reduction = compression_from_iteration(cadence, baseline_cadence)

    # Calculate efficiency score (0-100)
    # Based on cadence, parallelization, and pattern
    cadence_score = min(100, (cadence / 4.0) * 100)  # 4 iterations/month = 100
    parallel_score = min(100, avg_parallel * 20)  # 5x parallel = 100
    pattern_penalty = 30 if is_waterfall else 0

    efficiency_score = max(0, (cadence_score + parallel_score) / 2 - pattern_penalty)

    return IterationMetrics(
        cadence_per_month=cadence,
        parallel_factor=round(avg_parallel, 2),
        entropy_reduction=entropy_reduction,
        is_waterfall=is_waterfall,
        efficiency_score=round(efficiency_score, 1),
    )


def emit_iteration_cycle(
    ship_id: str,
    cycle_number: int,
    changes: list,
    duration_days: float,
    parallel_bays: int = 1
) -> dict:
    """
    Emit a complete iteration cycle with metrics.

    Args:
        ship_id: Ship identifier
        cycle_number: Iteration cycle number
        changes: List of changes in this cycle
        duration_days: Days spent in this cycle
        parallel_bays: Number of parallel bays used

    Returns:
        iteration_receipt dict
    """
    cycle_id = f"{ship_id}_ITER_{cycle_number:04d}"

    # Calculate parallel factor
    parallel = model_parallel_assembly(
        blocks=[f"block_{i}" for i in range(len(changes))],
        bays=parallel_bays
    )

    receipt = emit_iteration_receipt(
        cycle_id=cycle_id,
        ship_id=ship_id,
        changes_count=len(changes),
        time_delta_days=duration_days,
        change_descriptions=[str(c) for c in changes[:5]],  # First 5 descriptions
        parallel_factor=parallel["actual_speedup"],
    )

    return receipt


def compare_iteration_modes(
    traditional_iterations: list,
    disruption_iterations: list
) -> dict:
    """
    Compare traditional vs Elon-sphere iteration approaches.

    Args:
        traditional_iterations: Iterations from traditional approach
        disruption_iterations: Iterations from disruption approach

    Returns:
        Comparison metrics dict
    """
    trad_metrics = calculate_iteration_efficiency(traditional_iterations)
    disr_metrics = calculate_iteration_efficiency(disruption_iterations)

    # Calculate improvement ratios
    cadence_improvement = (
        disr_metrics.cadence_per_month / trad_metrics.cadence_per_month
        if trad_metrics.cadence_per_month > 0 else 0
    )
    entropy_improvement = (
        trad_metrics.entropy_reduction / disr_metrics.entropy_reduction
        if disr_metrics.entropy_reduction > 0 else 0
    )

    return {
        "traditional": {
            "cadence": trad_metrics.cadence_per_month,
            "parallel_factor": trad_metrics.parallel_factor,
            "entropy_reduction": trad_metrics.entropy_reduction,
            "is_waterfall": trad_metrics.is_waterfall,
            "efficiency_score": trad_metrics.efficiency_score,
        },
        "disruption": {
            "cadence": disr_metrics.cadence_per_month,
            "parallel_factor": disr_metrics.parallel_factor,
            "entropy_reduction": disr_metrics.entropy_reduction,
            "is_waterfall": disr_metrics.is_waterfall,
            "efficiency_score": disr_metrics.efficiency_score,
        },
        "improvements": {
            "cadence_multiplier": round(cadence_improvement, 2),
            "entropy_improvement": round(entropy_improvement, 2),
            "efficiency_delta": round(
                disr_metrics.efficiency_score - trad_metrics.efficiency_score, 1
            ),
        },
        "simulation_flag": SHIPYARD_DISCLAIMER,
    }


# === STOPRULES ===

def stoprule_cadence_collapse(ship_id: str, cadence: float, min_cadence: float = 0.5) -> None:
    """Stoprule: Iteration cadence dropped below minimum."""
    emit_receipt("anomaly", {
        "metric": "cadence_collapse",
        "ship_id": ship_id,
        "cadence": cadence,
        "min_cadence": min_cadence,
        "delta": cadence - min_cadence,
        "action": "review",
        "classification": "efficiency_degradation",
        "simulation_flag": SHIPYARD_DISCLAIMER,
    }, to_stdout=False)


# === MODULE SELF-TEST ===

if __name__ == "__main__":
    print("# WarrantProof Shipyard Iterate Self-Test", file=sys.stderr)
    print(f"# {SHIPYARD_DISCLAIMER}", file=sys.stderr)

    # Test cadence calculation
    changes = list(range(10))  # 10 iterations
    cadence = calculate_iteration_cadence(changes, 30)
    assert cadence == 10.0, f"Expected 10.0 iterations/month, got {cadence}"
    print(f"# Cadence test: {cadence} iterations/month", file=sys.stderr)

    # Test parallel assembly model
    blocks = [f"block_{i}" for i in range(20)]
    parallel = model_parallel_assembly(blocks, bays=8)
    assert parallel["theoretical_speedup"] == 8, "8 bays should give 8x theoretical speedup"
    print(f"# Parallel speedup: {parallel['actual_speedup']:.2f}x", file=sys.stderr)

    # Test entropy compression
    entropy = compression_from_iteration(cadence=4.0, baseline=1.0)
    assert entropy < 1.0, "Higher cadence should reduce entropy"
    print(f"# Entropy reduction: {entropy:.3f}", file=sys.stderr)

    # Test waterfall detection
    waterfall_iters = [
        {"ts": "2025-01-01T00:00:00Z"},
        {"ts": "2025-02-01T00:00:00Z"},
        {"ts": "2025-03-01T00:00:00Z"},
    ]
    is_waterfall = detect_waterfall_pattern(waterfall_iters)
    assert is_waterfall == True, "Monthly iterations should be detected as waterfall"
    print(f"# Waterfall detection (monthly): {is_waterfall}", file=sys.stderr)

    rapid_iters = [
        {"ts": "2025-01-01T00:00:00Z"},
        {"ts": "2025-01-08T00:00:00Z"},
        {"ts": "2025-01-15T00:00:00Z"},
        {"ts": "2025-01-22T00:00:00Z"},
    ]
    is_waterfall = detect_waterfall_pattern(rapid_iters)
    assert is_waterfall == False, "Weekly iterations should not be waterfall"
    print(f"# Waterfall detection (weekly): {is_waterfall}", file=sys.stderr)

    # Test comparison
    comparison = compare_iteration_modes(waterfall_iters, rapid_iters)
    assert comparison["disruption"]["cadence"] > comparison["traditional"]["cadence"]
    print(f"# Cadence improvement: {comparison['improvements']['cadence_multiplier']:.1f}x", file=sys.stderr)

    print("# PASS: Iteration module validated", file=sys.stderr)
