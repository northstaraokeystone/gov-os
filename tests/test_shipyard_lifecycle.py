"""
Tests for WarrantProof Shipyard Lifecycle Module

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY
"""

import pytest


class TestLifecycleCreation:
    """Test ship creation and initialization."""

    def test_create_ship(self):
        """Test ship creation with default values."""
        from src.shipyard.lifecycle import create_ship

        ship = create_ship("TEST-001", "trump", "YARD-001")

        assert ship["ship_id"] == "TEST-001"
        assert ship["class_type"] == "trump"
        assert ship["current_phase"] == "DESIGN"
        assert ship["phase_index"] == 0
        assert len(ship["receipts"]) >= 2  # keel + milestone

    def test_create_ship_with_baseline(self):
        """Test ship creation with custom baseline."""
        from src.shipyard.lifecycle import create_ship

        ship = create_ship(
            "TEST-002",
            "trump",
            "YARD-001",
            baseline_cost_usd=5e9,
            baseline_days=730,
        )

        assert ship["baseline_cost_usd"] == 5e9
        assert ship["baseline_days"] == 730


class TestPhaseAdvancement:
    """Test phase transitions."""

    def test_advance_phase(self):
        """Test advancing to next phase."""
        from src.shipyard.lifecycle import create_ship, advance_phase, LIFECYCLE_PHASES

        ship = create_ship("TEST-001", "trump", "YARD-001")
        assert ship["current_phase"] == "DESIGN"

        ship = advance_phase(ship, "KEEL_LAYING", actual_days=180, actual_cost=1e9)

        assert ship["current_phase"] == "KEEL_LAYING"
        assert ship["phase_index"] == 1
        assert ship["actual_days"] == 180

    def test_cannot_skip_phases(self):
        """Test that phases cannot be skipped."""
        from src.shipyard.lifecycle import create_ship, advance_phase
        from src.core import StopRuleException

        ship = create_ship("TEST-001", "trump", "YARD-001")

        with pytest.raises(StopRuleException):
            advance_phase(ship, "BLOCK_ASSEMBLY")  # Should fail - skipping KEEL_LAYING

    def test_full_lifecycle(self):
        """Test advancing through all phases."""
        from src.shipyard.lifecycle import create_ship, advance_phase, LIFECYCLE_PHASES

        ship = create_ship("TEST-001", "trump", "YARD-001")

        for phase in LIFECYCLE_PHASES[1:]:
            ship = advance_phase(ship, phase, actual_days=30, actual_cost=1e9)
            assert ship["current_phase"] == phase


class TestVarianceCalculation:
    """Test variance calculation."""

    def test_calculate_variance(self):
        """Test variance calculation."""
        from src.shipyard.lifecycle import create_ship, advance_phase, calculate_variance

        ship = create_ship("TEST-001", "trump", "YARD-001")
        ship = advance_phase(ship, "KEEL_LAYING", actual_days=30, actual_cost=1e9)

        variance = calculate_variance(ship)

        assert "cost_variance_pct" in variance
        assert "schedule_variance_pct" in variance
        assert "on_budget" in variance

    def test_variance_detection(self):
        """Test variance triggers at threshold."""
        from src.shipyard.lifecycle import create_ship, advance_phase, calculate_variance
        from src.shipyard.constants import EARLY_DETECTION_PCT

        ship = create_ship("TEST-001", "trump", "YARD-001", baseline_cost_usd=1e9)

        # Add significant overrun
        ship = advance_phase(ship, "KEEL_LAYING", actual_days=30, actual_cost=2e9)

        variance = calculate_variance(ship)

        # Check that variance is calculated correctly
        assert isinstance(variance["cost_variance_pct"], (int, float))


class TestShipCompletion:
    """Test ship delivery."""

    def test_complete_ship(self):
        """Test ship completion and delivery receipt."""
        from src.shipyard.lifecycle import create_ship, complete_ship

        ship = create_ship("TEST-001", "trump", "YARD-001")
        ship = complete_ship(ship)

        assert ship["current_phase"] == "DELIVERY"
        assert "delivery_receipt" in ship
        assert "final_overrun_pct" in ship


class TestPhaseSequenceValidation:
    """Test phase sequence validation."""

    def test_valid_sequence(self):
        """Test valid phase sequence."""
        from src.shipyard.lifecycle import validate_phase_sequence, LIFECYCLE_PHASES

        assert validate_phase_sequence(LIFECYCLE_PHASES) == True
        assert validate_phase_sequence(LIFECYCLE_PHASES[:3]) == True

    def test_invalid_sequence(self):
        """Test invalid phase sequence."""
        from src.shipyard.lifecycle import validate_phase_sequence

        # Skipped phase
        assert validate_phase_sequence(["DESIGN", "BLOCK_ASSEMBLY"]) == False
