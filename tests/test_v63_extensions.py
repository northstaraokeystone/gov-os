"""
Gov-OS v6.3 Extension Tests

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

Tests for v6.3 extensions:
- Musk ecosystem COI detection (doge module)
- UN round-trip pathway (aid module)
- Temporal correlation analysis (graft module)
- Data layer additions (musk_ecosystem.json, UN cohorts)
- IL5 scope documentation
"""

import json
import os
import sys
from pathlib import Path

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# === GATE 1: MUSK ECOSYSTEM DATA LAYER ===


def test_musk_ecosystem_json_exists():
    """Verify data/musk_ecosystem.json exists."""
    path = PROJECT_ROOT / "data" / "musk_ecosystem.json"
    assert path.exists(), f"musk_ecosystem.json not found at {path}"


def test_musk_ecosystem_json_valid():
    """Verify musk_ecosystem.json has valid structure."""
    path = PROJECT_ROOT / "data" / "musk_ecosystem.json"
    with open(path) as f:
        data = json.load(f)

    # Check top-level structure
    assert "version" in data
    assert "entities" in data
    assert "doge_leadership" in data
    assert "coi_detection_config" in data

    # Check entities count
    entities = data["entities"]
    assert len(entities) == 6, f"Expected 6 entities, got {len(entities)}"

    # Check required entities exist
    required_entities = ["spacex", "starlink", "tesla", "boring_company", "neuralink", "xai"]
    for entity in required_entities:
        assert entity in entities, f"Missing entity: {entity}"

    # Check xAI has known_contracts
    assert "known_contracts" in entities["xai"], "xAI missing known_contracts"


def test_musk_ecosystem_entities_have_required_fields():
    """Verify each Musk entity has required fields."""
    path = PROJECT_ROOT / "data" / "musk_ecosystem.json"
    with open(path) as f:
        data = json.load(f)

    required_fields = ["legal_name", "agencies", "contract_types"]

    for entity_id, entity in data["entities"].items():
        for field in required_fields:
            assert field in entity, f"Entity {entity_id} missing field: {field}"


# === GATE 2: UN COHORTS DATA LAYER ===


def test_un_cohorts_added():
    """Verify foreignassistance_cohorts.json has UN cohorts."""
    path = PROJECT_ROOT / "data" / "foreignassistance_cohorts.json"
    with open(path) as f:
        data = json.load(f)

    cohorts = data["cohorts"]

    # Check UN cohorts exist
    un_cohorts = ["un_assessed_contributions", "un_voluntary_contributions", "un_implementing_partners"]
    for cohort in un_cohorts:
        assert cohort in cohorts, f"Missing UN cohort: {cohort}"


def test_un_cohorts_structure():
    """Verify UN cohorts have correct structure."""
    path = PROJECT_ROOT / "data" / "foreignassistance_cohorts.json"
    with open(path) as f:
        data = json.load(f)

    # Check un_voluntary_contributions has agencies
    un_vol = data["cohorts"]["un_voluntary_contributions"]
    assert "agencies" in un_vol
    assert "UNICEF" in un_vol["agencies"]
    assert "UNDP" in un_vol["agencies"]

    # Check un_implementing_partners has pathway
    un_impl = data["cohorts"]["un_implementing_partners"]
    assert "pathway" in un_impl


def test_foreignassistance_version_updated():
    """Verify foreignassistance_cohorts.json version is 6.3.0."""
    path = PROJECT_ROOT / "data" / "foreignassistance_cohorts.json"
    with open(path) as f:
        data = json.load(f)

    assert data["metadata"]["version"] == "6.3.0", "Version should be 6.3.0"


# === GATE 3: DOGE COI DETECTION ===


def test_doge_coi_detection_import():
    """Verify detect_musk_ecosystem_coi() exists and is importable."""
    from modules.doge.verify import detect_musk_ecosystem_coi

    assert callable(detect_musk_ecosystem_coi)


def test_doge_musk_entities_config():
    """Verify MUSK_ECOSYSTEM_ENTITIES is in config."""
    from modules.doge.config import MUSK_ECOSYSTEM_ENTITIES

    assert len(MUSK_ECOSYSTEM_ENTITIES) == 6
    assert "spacex" in MUSK_ECOSYSTEM_ENTITIES
    assert "xai" in MUSK_ECOSYSTEM_ENTITIES


def test_doge_coi_config_constants():
    """Verify COI config constants exist."""
    from modules.doge.config import (
        COI_DETECTION_ENABLED,
        COI_CORRELATION_WINDOW_DAYS,
        COI_MIN_CONTRACT_VALUE,
    )

    assert COI_DETECTION_ENABLED is True
    assert COI_CORRELATION_WINDOW_DAYS == 90
    assert COI_MIN_CONTRACT_VALUE == 100000


def test_doge_coi_detection_executes():
    """Verify detect_musk_ecosystem_coi() executes without error."""
    from modules.doge.verify import detect_musk_ecosystem_coi

    result = detect_musk_ecosystem_coi(lookback_days=365)

    assert "entities_analyzed" in result
    assert "total_contracts_found" in result
    assert "coi_score" in result
    assert "verdict" in result
    assert "receipt" in result


def test_doge_coi_receipt_structure():
    """Verify musk_ecosystem_coi_receipt has correct structure."""
    from modules.doge.verify import detect_musk_ecosystem_coi

    result = detect_musk_ecosystem_coi(lookback_days=365)
    receipt = result["receipt"]

    assert receipt["receipt_type"] == "musk_ecosystem_coi"
    assert "tenant_id" in receipt
    assert "entities_analyzed" in receipt
    assert "contracts_found" in receipt
    assert "coi_score" in receipt
    assert "verdict" in receipt
    assert "payload_hash" in receipt


def test_pentagon_xai_claim_exists():
    """Verify pentagon_xai claim is in DOGE_CLAIM_SOURCES."""
    from modules.doge.config import DOGE_CLAIM_SOURCES

    assert "pentagon_xai" in DOGE_CLAIM_SOURCES
    assert DOGE_CLAIM_SOURCES["pentagon_xai"]["coi_flag"] is True


# === GATE 4: AID UN PATHWAY ===


def test_aid_un_agencies_config():
    """Verify AGENCIES includes UN agencies."""
    from modules.aid.config import AGENCIES

    un_agencies = ["UN_REGULAR", "UN_PEACEKEEPING", "UNICEF", "UNDP", "WFP", "UNHCR", "WHO"]
    for agency in un_agencies:
        assert agency in AGENCIES, f"Missing agency: {agency}"


def test_aid_un_pathway_config():
    """Verify UN pathway config constants exist."""
    from modules.aid.config import (
        UN_PATHWAY_ENABLED,
        UN_VOLUNTARY_AGENCIES,
        UN_ROUND_TRIP_PATHWAY,
    )

    assert UN_PATHWAY_ENABLED is True
    assert len(UN_VOLUNTARY_AGENCIES) == 7
    assert "UNICEF" in UN_VOLUNTARY_AGENCIES
    assert "→" in UN_ROUND_TRIP_PATHWAY


def test_aid_un_round_trip_import():
    """Verify detect_round_trip() accepts pathway parameter."""
    from modules.aid.verify import detect_round_trip
    import inspect

    sig = inspect.signature(detect_round_trip)
    assert "pathway" in sig.parameters


def test_aid_un_round_trip_executes():
    """Verify detect_round_trip(pathway='un') executes."""
    from modules.aid.verify import detect_round_trip

    result = detect_round_trip("test-partner-001", pathway="un", _simulate=True)

    assert "pathway" in result
    assert result["pathway"] == "un"
    assert "un_agency" in result
    assert "un_grant_to_partner" in result


def test_aid_un_round_trip_receipt():
    """Verify UN pathway emits appropriate receipt."""
    from modules.aid.config import RECEIPT_TYPES

    assert "un_round_trip_receipt" in RECEIPT_TYPES


def test_aid_combined_pathway():
    """Verify detect_round_trip(pathway='both') works."""
    from modules.aid.verify import detect_round_trip

    result = detect_round_trip("test-partner-002", pathway="both", _simulate=True)

    assert result["pathway"] == "both"
    assert "USAID" in result["funding_source"] or "UN" in result["funding_source"]


# === GATE 5: GRAFT TEMPORAL CORRELATION ===


def test_graft_temporal_import():
    """Verify temporal_correlation_analysis() exists."""
    from modules.graft.verify import temporal_correlation_analysis

    assert callable(temporal_correlation_analysis)


def test_graft_temporal_config():
    """Verify temporal correlation config exists."""
    from modules.graft.config import (
        TEMPORAL_CORRELATION_ENABLED,
        EVENT_TYPE_WEIGHTS,
        DEFAULT_TEMPORAL_WINDOW_DAYS,
        MIN_SAMPLE_SIZE,
    )

    assert TEMPORAL_CORRELATION_ENABLED is True
    assert "DOGE_RECOMMENDATION" in EVENT_TYPE_WEIGHTS
    assert EVENT_TYPE_WEIGHTS["DOGE_RECOMMENDATION"] == 1.0
    assert DEFAULT_TEMPORAL_WINDOW_DAYS == 90
    assert MIN_SAMPLE_SIZE == 10


def test_graft_temporal_receipt_type():
    """Verify temporal_correlation_receipt in RECEIPT_TYPES."""
    from modules.graft.config import RECEIPT_TYPES

    assert "temporal_correlation_receipt" in RECEIPT_TYPES


def test_graft_temporal_insufficient_data():
    """Verify temporal analysis handles insufficient data."""
    from modules.graft.verify import temporal_correlation_analysis

    events = [{"event_type": "DOGE_RECOMMENDATION", "date": "2024-11-01"}]
    awards = [{"contract_id": "TEST-001", "award_date": "2024-11-15", "value": 1000000}]

    # Should return insufficient_data with < 10 awards
    result = temporal_correlation_analysis(events, awards)

    assert result["verdict"] == "insufficient_data"


def test_graft_temporal_with_sufficient_data():
    """Verify temporal analysis works with sufficient data."""
    from modules.graft.verify import temporal_correlation_analysis

    events = [
        {"event_type": "DOGE_RECOMMENDATION", "date": "2024-11-01", "description": "Test rec"},
    ]

    # Create 15 awards to meet minimum sample size
    awards = [
        {"contract_id": f"TEST-{i:03d}", "award_date": f"2024-11-{10 + i % 20:02d}", "value": 10_000_000, "awardee": "TestCorp"}
        for i in range(15)
    ]

    result = temporal_correlation_analysis(events, awards)

    assert "events_analyzed" in result
    assert "awards_analyzed" in result
    assert result["awards_analyzed"] == 15
    assert "correlations_found" in result
    assert "temporal_score" in result
    assert "verdict" in result
    assert result["verdict"] in ["pattern_detected", "weak_pattern", "no_pattern"]


def test_graft_temporal_receipt_structure():
    """Verify temporal_correlation_receipt structure."""
    from modules.graft.verify import temporal_correlation_analysis

    events = [{"event_type": "DOGE_RECOMMENDATION", "date": "2024-11-01"}]
    awards = [
        {"contract_id": f"TEST-{i}", "award_date": f"2024-11-{15 + i % 10:02d}", "value": 5_000_000}
        for i in range(12)
    ]

    result = temporal_correlation_analysis(events, awards)

    assert "receipt" in result
    receipt = result["receipt"]
    assert receipt["receipt_type"] == "temporal_correlation"
    assert "temporal_score" in receipt
    assert "p_value" in receipt
    assert "verdict" in receipt


# === GATE 6: DOCUMENTATION ===


def test_il5_scope_doc_exists():
    """Verify docs/il5_scope.md exists."""
    path = PROJECT_ROOT / "docs" / "il5_scope.md"
    assert path.exists(), f"il5_scope.md not found at {path}"


def test_il5_scope_doc_content():
    """Verify IL5 scope doc has key sections."""
    path = PROJECT_ROOT / "docs" / "il5_scope.md"
    content = path.read_text()

    required_sections = [
        "IL5",
        "CUI",
        "Pentagon-xAI",
        "Gov-OS",
        "Public",
        "Out of scope",
    ]

    for section in required_sections:
        assert section.lower() in content.lower(), f"Missing section: {section}"


# === CROSS-MODULE INTEGRATION ===


def test_doge_graft_integration():
    """Verify DOGE COI can use graft temporal analysis."""
    from modules.doge.verify import detect_musk_ecosystem_coi
    from modules.graft.verify import temporal_correlation_analysis

    # Get COI detection result
    coi_result = detect_musk_ecosystem_coi(lookback_days=365)

    # If we have correlated events, we can feed them to temporal analysis
    if coi_result.get("correlated_events"):
        events = [
            {
                "event_type": "DOGE_RECOMMENDATION",
                "date": e.get("recommendation_date", "2024-11-01"),
                "description": e.get("doge_recommendation", ""),
            }
            for e in coi_result["correlated_events"]
        ]
        awards = [
            {
                "contract_id": e.get("contract_id", ""),
                "award_date": e.get("award_date", ""),
                "value": e.get("contract_value", 0),
                "awardee": e.get("entity", ""),
            }
            for e in coi_result["correlated_events"]
        ]

        # Even if sample is small, function should handle gracefully
        result = temporal_correlation_analysis(events, awards)
        assert "verdict" in result


# === MOCK DATA FOR TESTING ===


MOCK_MUSK_CONTRACTS = [
    {
        "entity": "spacex",
        "contract_id": "TEST-001",
        "award_date": "2024-10-15",
        "value": 50_000_000,
        "agency": "DOD",
    }
]

MOCK_DOGE_EVENTS = [
    {
        "event_type": "DOGE_RECOMMENDATION",
        "date": "2024-10-01",
        "description": "Recommended cuts to legacy launch providers",
        "entity_affected": "ULA",
    }
]

MOCK_UN_PARTNER = {
    "partner_id": "NGO-UN-001",
    "un_agency": "UNDP",
    "grant_amount": 500_000,
    "fec_donations": 25_000,
    "donation_dates": ["2024-11-01", "2024-11-15"],
}


def test_mock_data_available():
    """Verify mock data is available for testing."""
    assert len(MOCK_MUSK_CONTRACTS) > 0
    assert len(MOCK_DOGE_EVENTS) > 0
    assert MOCK_UN_PARTNER["un_agency"] == "UNDP"


# === RUN SELF-TEST ===

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
