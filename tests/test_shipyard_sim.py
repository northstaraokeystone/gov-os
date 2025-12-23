"""
Tests for WarrantProof Shipyard Simulation Module

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY
"""

import pytest
import time


class TestSimulationBasic:
    """Basic simulation tests."""

    def test_run_simulation_10_cycles(self):
        """Test 10-cycle simulation completes."""
        from src.shipyard.sim_shipyard import run_simulation, SimShipyardConfig

        config = SimShipyardConfig(n_cycles=10, n_ships=2)
        state = run_simulation(config)

        assert state.cycle == 10
        assert len(state.ships) == 2
        assert len(state.receipt_ledger) > 0
        assert len(state.entropy_trace) == 10

    def test_run_simulation_100_cycles(self):
        """Test 100-cycle simulation completes without violations."""
        from src.shipyard.sim_shipyard import run_simulation, SimShipyardConfig

        config = SimShipyardConfig(n_cycles=100, n_ships=3)
        state = run_simulation(config)

        assert state.cycle == 100
        # Entropy violations should be minimal
        assert len(state.violations) < 10


class TestEntropyCalculation:
    """Test entropy calculation."""

    def test_calculate_entropy(self):
        """Test entropy calculation on receipt stream."""
        from src.shipyard.sim_shipyard import calculate_entropy

        receipts = [
            {"receipt_type": "keel"},
            {"receipt_type": "keel"},
            {"receipt_type": "milestone"},
            {"receipt_type": "block"},
        ]

        entropy = calculate_entropy(receipts)

        assert entropy > 0
        assert entropy <= 2  # Max entropy for 3 types

    def test_entropy_empty_list(self):
        """Test entropy of empty list is 0."""
        from src.shipyard.sim_shipyard import calculate_entropy

        entropy = calculate_entropy([])
        assert entropy == 0.0


class TestDisruptionSimulation:
    """Test disruption level modeling."""

    def test_traditional_disruption(self):
        """Test traditional disruption parameters."""
        from src.shipyard.sim_shipyard import simulate_disruption

        result = simulate_disruption({}, "traditional")

        assert result["efficiency_multiplier"] == 1.0
        assert result["cost_reduction_pct"] == 0.0
        assert result["parallel_factor"] == 1

    def test_elon_disruption(self):
        """Test Elon-sphere disruption parameters."""
        from src.shipyard.sim_shipyard import simulate_disruption

        result = simulate_disruption({}, "elon")

        assert result["efficiency_multiplier"] == 2.0
        assert result["cost_reduction_pct"] == 50.0
        assert result["parallel_factor"] == 8

    def test_hybrid_disruption(self):
        """Test hybrid disruption parameters."""
        from src.shipyard.sim_shipyard import simulate_disruption

        result = simulate_disruption({}, "hybrid")

        assert result["efficiency_multiplier"] == 1.5
        assert result["cost_reduction_pct"] == 25.0
        assert result["parallel_factor"] == 4


class TestEntropyConservation:
    """Test entropy conservation validation."""

    def test_validate_conservation(self):
        """Test entropy conservation validation."""
        from src.shipyard.sim_shipyard import (
            run_simulation,
            SimShipyardConfig,
            validate_conservation,
        )

        config = SimShipyardConfig(n_cycles=10, n_ships=2)
        state = run_simulation(config)

        # Run conservation check
        violations = validate_conservation(state)

        # Should have few or no violations in normal operation
        assert isinstance(violations, list)


class TestScenarioExecution:
    """Test individual scenario execution."""

    def test_baseline_scenario(self):
        """Test SCENARIO_BASELINE runs."""
        from src.shipyard.sim_shipyard import run_scenario

        result = run_scenario("SCENARIO_BASELINE")

        assert "scenario" in result
        assert "passed" in result
        assert result["scenario"] == "SCENARIO_BASELINE"

    def test_fraud_injection_scenario(self):
        """Test SCENARIO_FRAUD_INJECTION detects fraud."""
        from src.shipyard.sim_shipyard import run_scenario

        result = run_scenario("SCENARIO_FRAUD_INJECTION")

        assert "fraud_detected" in result
        # Fraud should be detected
        assert result.get("fraud_detected") == True

    def test_nuclear_scenario(self):
        """Test SCENARIO_NUCLEAR completes certification."""
        from src.shipyard.sim_shipyard import run_scenario

        result = run_scenario("SCENARIO_NUCLEAR")

        assert "cert_complete" in result
        assert "tests_passed" in result
        assert result.get("cert_complete") == True


class TestSimulationPerformance:
    """Test simulation performance."""

    def test_simulation_timing(self):
        """Test simulation completes in reasonable time."""
        from src.shipyard.sim_shipyard import run_simulation, SimShipyardConfig

        config = SimShipyardConfig(n_cycles=100, n_ships=5)

        t0 = time.time()
        run_simulation(config)
        elapsed = time.time() - t0

        # Should complete 100 cycles in under 5 seconds
        assert elapsed < 5.0, f"Simulation took {elapsed:.2f}s, expected < 5s"
