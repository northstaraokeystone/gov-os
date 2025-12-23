"""
SHIELDPROOF v2.1 Scenarios Module - Cross-Module Integration Tests

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

Provides:
- baseline: Standard flow test (register -> milestone -> verify -> pay -> reconcile -> dashboard)
- stress: High-volume stress test

"One receipt. One milestone. One truth."
"""

from .baseline import (
    run_baseline_scenario,
)

from .stress import (
    run_stress_scenario,
)

__all__ = [
    "run_baseline_scenario",
    "run_stress_scenario",
]
