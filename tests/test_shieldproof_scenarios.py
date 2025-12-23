"""
ShieldProof v2.1 Scenarios Module Tests

Tests for baseline and stress scenarios.
"""

import pytest

from src.shieldproof.core import clear_ledger
from src.shieldproof.scenarios import (
    run_baseline_scenario,
    run_stress_scenario,
)


@pytest.fixture(autouse=True)
def clean_ledger():
    """Clear ledger before and after each test."""
    clear_ledger()
    yield
    clear_ledger()


class TestBaselineScenario:
    """Tests for run_baseline_scenario function."""

    def test_baseline_scenario_passes(self):
        """baseline scenario should pass with default settings."""
        result = run_baseline_scenario(n_contracts=3)
        assert result["passed"] is True
        assert result["errors"] == []

    def test_baseline_scenario_metrics(self):
        """baseline scenario should include all required metrics."""
        result = run_baseline_scenario(n_contracts=3)
        metrics = result["metrics"]
        assert "contracts_registered" in metrics
        assert "milestones_verified" in metrics
        assert "payments_released" in metrics
        assert "elapsed_seconds" in metrics
        assert "receipts_generated" in metrics

    def test_baseline_scenario_counts(self):
        """baseline scenario should have correct counts."""
        n = 5
        result = run_baseline_scenario(n_contracts=n)
        metrics = result["metrics"]
        assert metrics["contracts_registered"] == n
        assert metrics["milestones_verified"] == n * 2  # 2 milestones per contract
        assert metrics["payments_released"] == n * 2

    def test_baseline_scenario_receipts(self):
        """baseline scenario should generate receipts."""
        result = run_baseline_scenario(n_contracts=3)
        assert len(result["receipts"]) > 0


class TestStressScenario:
    """Tests for run_stress_scenario function."""

    def test_stress_scenario_passes(self):
        """stress scenario should pass with small count."""
        result = run_stress_scenario(n_contracts=10)
        assert result["passed"] is True
        assert result["errors"] == []

    def test_stress_scenario_metrics(self):
        """stress scenario should include all required metrics."""
        result = run_stress_scenario(n_contracts=10)
        metrics = result["metrics"]
        assert "contracts_registered" in metrics
        assert "milestones_processed" in metrics
        assert "payments_released" in metrics
        assert "elapsed_seconds" in metrics
        assert "receipts_generated" in metrics

    def test_stress_scenario_throughput(self):
        """stress scenario should calculate throughput."""
        result = run_stress_scenario(n_contracts=10)
        assert "throughput_per_sec" in result
        assert result["throughput_per_sec"] > 0

    def test_stress_scenario_timing(self):
        """stress scenario should track timing breakdown."""
        result = run_stress_scenario(n_contracts=10)
        metrics = result["metrics"]
        assert "register_time_seconds" in metrics
        assert "verify_time_seconds" in metrics
        assert "payment_time_seconds" in metrics
        assert "summary_time_seconds" in metrics

    def test_stress_scenario_counts(self):
        """stress scenario should have correct counts."""
        n = 20
        result = run_stress_scenario(n_contracts=n)
        metrics = result["metrics"]
        assert metrics["contracts_registered"] == n
        assert metrics["milestones_processed"] == n
        assert metrics["payments_released"] == n
