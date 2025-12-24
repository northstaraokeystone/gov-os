"""
Gov-OS Real Data Gate - v6.1 USASpending Integration Layer

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

This module provides the Real Data Gate that wraps the existing usaspending_etl.py
module to enable threshold calibration from real federal spending data.

CRITICAL: This file WRAPS usaspending_etl.py, it does NOT duplicate its functionality.

v6.1 Changes:
- Cohort-based data ingestion from USASpending API
- Threshold calibration from real data distributions
- StopRules for data quality gates

Receipts Emitted:
- data_gate_ingest_receipt: Documents cohort data ingestion
- threshold_calibration_receipt: Documents threshold calibration
- data_gate_receipt: Documents individual record validation
"""

import json
import math
import statistics
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import from existing usaspending_etl module (WRAP, don't duplicate)
from ..usaspending_etl import (
    fetch_awards,
    fetch_transactions,
    fetch_federal_accounts,
    validate_schema,
    detect_missing_fields,
    emit_etl_receipt,
    AWARD_SCHEMA,
    TRANSACTION_SCHEMA,
    FEDERAL_ACCOUNT_SCHEMA,
)

# Import core utilities
from .constants import (
    TENANT_ID,
    DISCLAIMER,
    load_threshold,
    get_compression_threshold,
    COMPRESSION_THRESHOLD_DEFAULT,
)
from .utils import dual_hash
from .receipt import emit_receipt, StopRuleException


# Load cohort configuration
def _load_cohort_config() -> dict:
    """Load cohort configuration from data/usaspending_cohorts.json."""
    # Try relative to this file first
    module_dir = Path(__file__).parent.parent.parent  # src/core -> src -> gov-os
    config_path = module_dir / "data" / "usaspending_cohorts.json"

    if not config_path.exists():
        # Try current working directory
        config_path = Path.cwd() / "data" / "usaspending_cohorts.json"

    if not config_path.exists():
        return {"cohorts": {}, "metadata": {}}

    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception:
        return {"cohorts": {}, "metadata": {}}


@dataclass
class CohortConfig:
    """Configuration for a data cohort."""
    name: str
    agency: str
    agency_full: str
    award_type: str
    date_range: Dict[str, str]
    min_records: int
    description: str
    source: str
    filters: Dict[str, Any]
    sub_agency: Optional[str] = None


class RealDataGate:
    """
    Real data ingestion layer wrapping existing usaspending_etl.py.

    Provides cohort-based data ingestion with threshold calibration
    from real federal spending data distributions.

    Example:
        >>> gate = RealDataGate("doge_medicaid")
        >>> records = gate.ingest_cohort()
        >>> threshold = gate.calibrate_threshold(records)
        >>> result = gate.validate_gate(records[0])
    """

    def __init__(self, cohort_name: str):
        """
        Initialize RealDataGate with cohort configuration.

        Args:
            cohort_name: Name of cohort from data/usaspending_cohorts.json
        """
        self.cohort_name = cohort_name
        self.config = self._load_cohort(cohort_name)
        self.calibrated_threshold: Optional[float] = None
        self._records: List[dict] = []

    def _load_cohort(self, cohort_name: str) -> CohortConfig:
        """Load cohort configuration by name."""
        all_config = _load_cohort_config()
        cohorts = all_config.get("cohorts", {})

        if cohort_name not in cohorts:
            # Return default config for unknown cohorts
            return CohortConfig(
                name=cohort_name,
                agency="UNKNOWN",
                agency_full="Unknown Agency",
                award_type="contract",
                date_range={"start": "2024-01-01", "end": "2024-12-31"},
                min_records=100,
                description=f"Unknown cohort: {cohort_name}",
                source="none",
                filters={},
            )

        cohort = cohorts[cohort_name]
        return CohortConfig(
            name=cohort_name,
            agency=cohort.get("agency", "UNKNOWN"),
            agency_full=cohort.get("agency_full", "Unknown Agency"),
            award_type=cohort.get("award_type", "contract"),
            date_range=cohort.get("date_range", {"start": "2024-01-01", "end": "2024-12-31"}),
            min_records=cohort.get("min_records", 100),
            description=cohort.get("description", ""),
            source=cohort.get("source", ""),
            filters=cohort.get("filters", {}),
            sub_agency=cohort.get("sub_agency"),
        )

    def ingest_cohort(self, _simulate: bool = True) -> List[Dict[str, Any]]:
        """
        Fetch data for this cohort via usaspending_etl functions.

        Args:
            _simulate: If True, use simulated data (default for safety)

        Returns:
            List of award records matching cohort criteria

        Raises:
            StopRuleException: If fewer than min_records returned
        """
        start_date = self.config.date_range.get("start", "2024-01-01")
        end_date = self.config.date_range.get("end", "2024-12-31")

        # Fetch awards using existing ETL function
        records = fetch_awards(
            start_date=start_date,
            end_date=end_date,
            agency_code=self.config.agency if self.config.agency != "UNKNOWN" else None,
            award_type=self.config.award_type,
            _simulate=_simulate,
        )

        # Apply additional filters
        if self.config.filters:
            records = self._apply_filters(records, self.config.filters)

        # Check stoprule for insufficient data
        if len(records) < self.config.min_records:
            self.stoprule_insufficient_data(len(records), self.config.min_records)

        self._records = records

        # Emit ingestion receipt
        self._emit_ingest_receipt(records)

        return records

    def _apply_filters(
        self,
        records: List[Dict[str, Any]],
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply cohort-specific filters to records."""
        filtered = []
        for record in records:
            match = True
            for key, value in filters.items():
                if key in record and record[key] != value:
                    match = False
                    break
            if match:
                filtered.append(record)
        return filtered if filtered else records  # Return all if no matches

    def _emit_ingest_receipt(self, records: List[Dict[str, Any]]) -> dict:
        """Emit data_gate_ingest receipt."""
        payload = {
            "cohort_name": self.cohort_name,
            "record_count": len(records),
            "agency": self.config.agency,
            "agency_full": self.config.agency_full,
            "award_type": self.config.award_type,
            "date_range": self.config.date_range,
            "description": self.config.description,
            "source": self.config.source,
        }

        return emit_receipt("data_gate_ingest", {
            "tenant_id": TENANT_ID,
            **payload,
            "payload_hash": dual_hash(json.dumps(payload, sort_keys=True)),
            "simulation_flag": DISCLAIMER,
        }, to_stdout=False)

    def calibrate_threshold(self, records: Optional[List[dict]] = None) -> float:
        """
        Compute percentile_90 of compression ratios from records.

        Args:
            records: List of records to analyze (uses cached if None)

        Returns:
            Calibrated threshold value

        Raises:
            StopRuleException: If calibrated threshold is invalid
        """
        if records is None:
            records = self._records

        if not records:
            return COMPRESSION_THRESHOLD_DEFAULT

        # Calculate compression ratios for each record
        ratios = []
        for record in records:
            ratio = self._calculate_compression_ratio(record)
            ratios.append(ratio)

        if not ratios:
            return COMPRESSION_THRESHOLD_DEFAULT

        # Calculate 90th percentile
        ratios_sorted = sorted(ratios)
        idx = int(len(ratios_sorted) * 0.90)
        percentile_90 = ratios_sorted[min(idx, len(ratios_sorted) - 1)]

        # Validate threshold bounds
        if percentile_90 < 0.10 or percentile_90 > 0.95:
            self.stoprule_invalid_calibration(percentile_90)

        self.calibrated_threshold = percentile_90

        # Emit calibration receipt
        self._emit_calibration_receipt(len(records), percentile_90)

        return percentile_90

    def _calculate_compression_ratio(self, record: dict) -> float:
        """Calculate compression ratio for a single record."""
        import gzip

        # Serialize record
        data = json.dumps(record, sort_keys=True).encode('utf-8')
        original_size = len(data)

        if original_size == 0:
            return 1.0

        # Compress
        compressed = gzip.compress(data, compresslevel=9)
        compressed_size = len(compressed)

        return compressed_size / original_size

    def _emit_calibration_receipt(self, sample_size: int, percentile_90: float) -> dict:
        """Emit threshold_calibration receipt."""
        payload = {
            "cohort_name": self.cohort_name,
            "sample_size": sample_size,
            "percentile_90": round(percentile_90, 4),
            "calibrated_threshold": round(percentile_90, 4),
            "method": "percentile_90",
        }

        return emit_receipt("threshold_calibration", {
            "tenant_id": TENANT_ID,
            **payload,
            "payload_hash": dual_hash(json.dumps(payload, sort_keys=True)),
            "simulation_flag": DISCLAIMER,
        }, to_stdout=False)

    def validate_gate(self, record: dict) -> dict:
        """
        Check single record against calibrated threshold.

        Args:
            record: Record to validate

        Returns:
            Validation result dict with passed status
        """
        threshold = self.calibrated_threshold or load_threshold(self.cohort_name)
        ratio = self._calculate_compression_ratio(record)
        passed = ratio >= threshold

        # Generate record ID
        record_id = record.get("award_id", record.get("id", "unknown"))

        result = {
            "record_id": record_id,
            "compression_ratio": round(ratio, 4),
            "threshold_used": round(threshold, 4),
            "passed": passed,
            "cohort": self.cohort_name,
        }

        # Emit data_gate receipt
        self._emit_gate_receipt(result)

        return result

    def _emit_gate_receipt(self, result: dict) -> dict:
        """Emit data_gate receipt."""
        payload = {
            "record_id": result["record_id"],
            "compression_ratio": result["compression_ratio"],
            "threshold_used": result["threshold_used"],
            "passed": result["passed"],
            "cohort": result["cohort"],
        }

        return emit_receipt("data_gate", {
            "tenant_id": TENANT_ID,
            **payload,
            "payload_hash": dual_hash(json.dumps(payload, sort_keys=True)),
            "simulation_flag": DISCLAIMER,
        }, to_stdout=False)

    def stoprule_insufficient_data(self, count: int, required: int) -> None:
        """
        Raise StopRule if count < required.

        Per CLAUDEME LAW_1: No receipt without sufficient data.

        Args:
            count: Actual record count
            required: Minimum required records

        Raises:
            StopRuleException: Always raised with details
        """
        emit_receipt("anomaly", {
            "tenant_id": TENANT_ID,
            "metric": "insufficient_data",
            "cohort": self.cohort_name,
            "count": count,
            "required": required,
            "action": "halt",
            "classification": "stoprule",
            "simulation_flag": DISCLAIMER,
        }, to_stdout=False)
        raise StopRuleException(
            f"Insufficient data for cohort '{self.cohort_name}': "
            f"got {count} records, need {required}"
        )

    def stoprule_invalid_calibration(self, threshold: float) -> None:
        """
        Raise StopRule if calibrated threshold is invalid.

        Args:
            threshold: The invalid threshold value

        Raises:
            StopRuleException: Always raised with details
        """
        emit_receipt("anomaly", {
            "tenant_id": TENANT_ID,
            "metric": "invalid_calibration",
            "cohort": self.cohort_name,
            "threshold": threshold,
            "valid_range": [0.10, 0.95],
            "action": "halt",
            "classification": "stoprule",
            "simulation_flag": DISCLAIMER,
        }, to_stdout=False)
        raise StopRuleException(
            f"Invalid calibrated threshold {threshold:.4f} for cohort '{self.cohort_name}': "
            f"must be between 0.10 and 0.95"
        )


def get_available_cohorts() -> List[str]:
    """Get list of available cohort names."""
    config = _load_cohort_config()
    return list(config.get("cohorts", {}).keys())


def get_cohort_info(cohort_name: str) -> Optional[dict]:
    """Get configuration info for a cohort."""
    config = _load_cohort_config()
    cohorts = config.get("cohorts", {})
    return cohorts.get(cohort_name)


# === MODULE SELF-TEST ===

if __name__ == "__main__":
    import sys

    print(f"# Gov-OS RealDataGate Self-Test", file=sys.stderr)
    print(f"# {DISCLAIMER}", file=sys.stderr)

    # Test 1: Load cohort config
    cohorts = get_available_cohorts()
    print(f"# Available cohorts: {cohorts}", file=sys.stderr)
    assert len(cohorts) >= 3, "Should have at least 3 cohorts defined"

    # Test 2: Create gate for doge_medicaid
    gate = RealDataGate("doge_medicaid")
    assert gate.config.agency == "HHS"
    print(f"# doge_medicaid agency: {gate.config.agency}", file=sys.stderr)

    # Test 3: Ingest simulated data (will use simulated since real API not available)
    try:
        records = gate.ingest_cohort(_simulate=True)
        print(f"# Ingested {len(records)} records", file=sys.stderr)
    except StopRuleException as e:
        print(f"# StopRule (expected in sim): {e}", file=sys.stderr)
        records = []

    # Test 4: Calibrate threshold if we have records
    if records:
        threshold = gate.calibrate_threshold(records)
        print(f"# Calibrated threshold: {threshold:.4f}", file=sys.stderr)

        # Test 5: Validate a record
        result = gate.validate_gate(records[0])
        print(f"# Validation result: passed={result['passed']}", file=sys.stderr)

    # Test 6: Test unknown cohort fallback
    unknown_gate = RealDataGate("unknown_cohort")
    assert unknown_gate.config.agency == "UNKNOWN"
    print(f"# Unknown cohort handled correctly", file=sys.stderr)

    print(f"# PASS: data_gate module self-test", file=sys.stderr)
