"""
Tests for WarrantProof Shipyard Receipts Module

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY
"""

import pytest
import time
from datetime import datetime


class TestReceiptEmission:
    """Test all 8 receipt types emit valid JSON."""

    def test_keel_receipt_emission(self):
        """Test keel_receipt emits valid JSON with required fields."""
        from src.shipyard.receipts import emit_keel_receipt

        receipt = emit_keel_receipt(
            ship_id="TEST-001",
            yard_id="YARD-001",
            ts=datetime.utcnow().isoformat() + "Z",
        )

        assert "receipt_type" in receipt
        assert receipt["receipt_type"] == "keel"
        assert "ts" in receipt
        assert "tenant_id" in receipt
        assert "payload_hash" in receipt
        assert ":" in receipt["payload_hash"]  # dual-hash format

    def test_block_receipt_emission(self):
        """Test block_receipt emits valid JSON."""
        from src.shipyard.receipts import emit_block_receipt

        receipt = emit_block_receipt(
            block_id="BLOCK-001",
            ship_id="SHIP-001",
            weld_count=100,
            inspector_id="INSP-001",
            pass_rate=0.98,
        )

        assert receipt["receipt_type"] == "block"
        assert receipt["weld_count"] == 100
        assert receipt["pass_rate"] == 0.98

    def test_additive_receipt_emission(self):
        """Test additive_receipt emits valid JSON."""
        from src.shipyard.receipts import emit_additive_receipt

        receipt = emit_additive_receipt(
            part_id="PART-001",
            printer_id="PRINTER-001",
            material_kg=500.0,
            print_hours=24.0,
        )

        assert receipt["receipt_type"] == "additive"
        assert receipt["material_kg"] == 500.0

    def test_iteration_receipt_emission(self):
        """Test iteration_receipt emits valid JSON."""
        from src.shipyard.receipts import emit_iteration_receipt

        receipt = emit_iteration_receipt(
            cycle_id="ITER-001",
            ship_id="SHIP-001",
            changes_count=5,
            time_delta_days=7.0,
        )

        assert receipt["receipt_type"] == "iteration"
        assert receipt["changes_count"] == 5
        assert "cadence_per_month" in receipt

    def test_milestone_receipt_emission(self):
        """Test milestone_receipt emits valid JSON."""
        from src.shipyard.receipts import emit_milestone_receipt

        receipt = emit_milestone_receipt(
            milestone_id="MS-001",
            ship_id="SHIP-001",
            completion_pct=50.0,
            phase="BLOCK_ASSEMBLY",
        )

        assert receipt["receipt_type"] == "milestone"
        assert receipt["completion_pct"] == 50.0
        assert receipt["phase"] == "BLOCK_ASSEMBLY"

    def test_procurement_receipt_emission(self):
        """Test procurement_receipt emits valid JSON."""
        from src.shipyard.receipts import emit_procurement_receipt

        receipt = emit_procurement_receipt(
            contract_id="CONTRACT-001",
            vendor_id="VENDOR-001",
            amount_usd=10_000_000.0,
            contract_type="fixed_price",
        )

        assert receipt["receipt_type"] == "procurement"
        assert receipt["amount_usd"] == 10_000_000.0
        assert receipt["entropy_direction"] == "shedding"

    def test_propulsion_receipt_emission(self):
        """Test propulsion_receipt emits valid JSON."""
        from src.shipyard.receipts import emit_propulsion_receipt

        receipt = emit_propulsion_receipt(
            reactor_id="REACTOR-001",
            ship_id="SHIP-001",
            power_mwe=77.0,
        )

        assert receipt["receipt_type"] == "propulsion"
        assert receipt["power_mwe"] == 77.0

    def test_delivery_receipt_emission(self):
        """Test delivery_receipt emits valid JSON."""
        from src.shipyard.receipts import emit_delivery_receipt

        receipt = emit_delivery_receipt(
            ship_id="SHIP-001",
            yard_id="YARD-001",
            final_cost_usd=10_000_000_000.0,
            total_days=1095,
            baseline_cost_usd=9_000_000_000.0,
            baseline_days=1000,
        )

        assert receipt["receipt_type"] == "delivery"
        assert receipt["final_cost_usd"] == 10_000_000_000.0
        assert "cost_overrun_pct" in receipt


class TestReceiptSLO:
    """Test receipt emission latency SLOs."""

    def test_keel_receipt_latency(self):
        """Test keel_receipt <= 50ms latency."""
        from src.shipyard.receipts import emit_keel_receipt

        t0 = time.time()
        emit_keel_receipt("T", "Y", datetime.utcnow().isoformat() + "Z")
        latency_ms = (time.time() - t0) * 1000

        assert latency_ms <= 50, f"Latency {latency_ms}ms > 50ms SLO"

    def test_block_receipt_latency(self):
        """Test block_receipt <= 50ms latency."""
        from src.shipyard.receipts import emit_block_receipt

        t0 = time.time()
        emit_block_receipt("B", "S", 100, "I")
        latency_ms = (time.time() - t0) * 1000

        assert latency_ms <= 50, f"Latency {latency_ms}ms > 50ms SLO"


class TestDualHash:
    """Test dual-hash format on all receipts."""

    def test_all_receipts_have_dual_hash(self):
        """Test all receipt types have SHA256:BLAKE3 format."""
        from src.shipyard.receipts import (
            emit_keel_receipt,
            emit_block_receipt,
            emit_additive_receipt,
            emit_iteration_receipt,
            emit_milestone_receipt,
            emit_procurement_receipt,
            emit_propulsion_receipt,
            emit_delivery_receipt,
        )

        receipts = [
            emit_keel_receipt("T1", "Y1", "2025-01-01T00:00:00Z"),
            emit_block_receipt("B1", "S1", 50, "I1"),
            emit_additive_receipt("P1", "PR1", 100.0, 10.0),
            emit_iteration_receipt("IT1", "S1", 3, 7.0),
            emit_milestone_receipt("M1", "S1", 50.0, "BLOCK_ASSEMBLY"),
            emit_procurement_receipt("C1", "V1", 1000000.0, "fixed_price"),
            emit_propulsion_receipt("R1", "S1", 77.0),
            emit_delivery_receipt("S1", "Y1", 10e9, 1095, 9e9, 1000),
        ]

        for receipt in receipts:
            assert "payload_hash" in receipt
            assert ":" in receipt["payload_hash"], f"Missing dual-hash separator in {receipt['receipt_type']}"
            parts = receipt["payload_hash"].split(":")
            assert len(parts) == 2, f"Invalid dual-hash format in {receipt['receipt_type']}"
            assert len(parts[0]) == 64, f"Invalid SHA256 length in {receipt['receipt_type']}"
            assert len(parts[1]) == 64, f"Invalid BLAKE3 length in {receipt['receipt_type']}"
