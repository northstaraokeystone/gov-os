"""
Gov-OS AidProof Module - Receipt Dataclasses

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

Receipt types for AidProof module:
1. aid_ingest_receipt - Data ingestion
2. partner_ingest_receipt - NGO partner data
3. aid_verification_receipt - Claim verification
4. round_trip_receipt - Round-trip detection
5. overhead_receipt - Admin cost analysis
6. country_allocation_receipt - Country breakdown
7. aid_anomaly_receipt - Anomaly detection
8. cross_reference_receipt - FEC/990 linkage
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from .config import DISCLAIMER


@dataclass
class AidIngestReceipt:
    """Receipt for foreign aid data ingestion."""
    receipt_type: str = "aid_ingest"
    agency: str = ""
    fiscal_year: int = 0
    record_count: int = 0
    total_amount: float = 0.0
    data_source: str = ""
    filters_applied: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    simulation_flag: str = DISCLAIMER

    def to_dict(self) -> dict:
        return {
            "receipt_type": self.receipt_type,
            "agency": self.agency,
            "fiscal_year": self.fiscal_year,
            "record_count": self.record_count,
            "total_amount": self.total_amount,
            "data_source": self.data_source,
            "filters_applied": self.filters_applied,
            "timestamp": self.timestamp,
            "simulation_flag": self.simulation_flag,
        }


@dataclass
class PartnerIngestReceipt:
    """Receipt for implementing partner data ingestion."""
    receipt_type: str = "partner_ingest"
    agency: str = ""
    partner_count: int = 0
    total_awards: float = 0.0
    cross_referenced: bool = False
    fec_linked: int = 0
    form_990_linked: int = 0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    simulation_flag: str = DISCLAIMER

    def to_dict(self) -> dict:
        return {
            "receipt_type": self.receipt_type,
            "agency": self.agency,
            "partner_count": self.partner_count,
            "total_awards": self.total_awards,
            "cross_referenced": self.cross_referenced,
            "fec_linked": self.fec_linked,
            "form_990_linked": self.form_990_linked,
            "timestamp": self.timestamp,
            "simulation_flag": self.simulation_flag,
        }


@dataclass
class AidVerificationReceipt:
    """Receipt for claim verification."""
    receipt_type: str = "aid_verification"
    claim_id: str = ""
    claim_type: str = ""
    data_sources_queried: List[str] = field(default_factory=list)
    records_analyzed: int = 0
    compression_ratio: float = 0.0
    anomaly_score: float = 0.0
    round_trip_score: float = 0.0
    verdict: str = ""  # supported, unsupported, insufficient_data
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    payload_hash: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    simulation_flag: str = DISCLAIMER

    def to_dict(self) -> dict:
        return {
            "receipt_type": self.receipt_type,
            "claim_id": self.claim_id,
            "claim_type": self.claim_type,
            "data_sources_queried": self.data_sources_queried,
            "records_analyzed": self.records_analyzed,
            "compression_ratio": self.compression_ratio,
            "anomaly_score": self.anomaly_score,
            "round_trip_score": self.round_trip_score,
            "verdict": self.verdict,
            "evidence": self.evidence,
            "payload_hash": self.payload_hash,
            "timestamp": self.timestamp,
            "simulation_flag": self.simulation_flag,
        }


@dataclass
class RoundTripReceipt:
    """Receipt for round-trip funding detection."""
    receipt_type: str = "round_trip"
    entity_id: str = ""
    entity_name: str = ""
    federal_awards_total: float = 0.0
    political_donations_total: float = 0.0
    temporal_correlation: float = 0.0
    round_trip_score: float = 0.0
    flagged: bool = False
    threshold_used: float = 0.10
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    simulation_flag: str = DISCLAIMER

    def to_dict(self) -> dict:
        return {
            "receipt_type": self.receipt_type,
            "entity_id": self.entity_id,
            "entity_name": self.entity_name,
            "federal_awards_total": self.federal_awards_total,
            "political_donations_total": self.political_donations_total,
            "temporal_correlation": self.temporal_correlation,
            "round_trip_score": self.round_trip_score,
            "flagged": self.flagged,
            "threshold_used": self.threshold_used,
            "timestamp": self.timestamp,
            "simulation_flag": self.simulation_flag,
        }


@dataclass
class OverheadReceipt:
    """Receipt for admin cost / overhead analysis."""
    receipt_type: str = "overhead"
    entity_id: str = ""
    entity_name: str = ""
    total_revenue: float = 0.0
    admin_expenses: float = 0.0
    program_expenses: float = 0.0
    overhead_ratio: float = 0.0
    flagged: bool = False
    threshold_used: float = 0.40
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    simulation_flag: str = DISCLAIMER

    def to_dict(self) -> dict:
        return {
            "receipt_type": self.receipt_type,
            "entity_id": self.entity_id,
            "entity_name": self.entity_name,
            "total_revenue": self.total_revenue,
            "admin_expenses": self.admin_expenses,
            "program_expenses": self.program_expenses,
            "overhead_ratio": self.overhead_ratio,
            "flagged": self.flagged,
            "threshold_used": self.threshold_used,
            "timestamp": self.timestamp,
            "simulation_flag": self.simulation_flag,
        }


@dataclass
class CountryAllocationReceipt:
    """Receipt for country-level allocation analysis."""
    receipt_type: str = "country_allocation"
    agency: str = ""
    fiscal_year: int = 0
    countries_analyzed: int = 0
    total_allocated: float = 0.0
    top_recipients: List[Dict[str, Any]] = field(default_factory=list)
    concentration_score: float = 0.0  # 0-1, higher = more concentrated
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    simulation_flag: str = DISCLAIMER

    def to_dict(self) -> dict:
        return {
            "receipt_type": self.receipt_type,
            "agency": self.agency,
            "fiscal_year": self.fiscal_year,
            "countries_analyzed": self.countries_analyzed,
            "total_allocated": self.total_allocated,
            "top_recipients": self.top_recipients,
            "concentration_score": self.concentration_score,
            "timestamp": self.timestamp,
            "simulation_flag": self.simulation_flag,
        }


@dataclass
class AidAnomalyReceipt:
    """Receipt for anomaly detection in aid data."""
    receipt_type: str = "aid_anomaly"
    anomaly_type: str = ""  # compression, overhead, round_trip, concentration
    entity_id: str = ""
    entity_name: str = ""
    anomaly_score: float = 0.0
    threshold_used: float = 0.0
    description: str = ""
    cross_domain_flag: bool = False  # Propagate to linked modules
    linked_modules: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    simulation_flag: str = DISCLAIMER

    def to_dict(self) -> dict:
        return {
            "receipt_type": self.receipt_type,
            "anomaly_type": self.anomaly_type,
            "entity_id": self.entity_id,
            "entity_name": self.entity_name,
            "anomaly_score": self.anomaly_score,
            "threshold_used": self.threshold_used,
            "description": self.description,
            "cross_domain_flag": self.cross_domain_flag,
            "linked_modules": self.linked_modules,
            "timestamp": self.timestamp,
            "simulation_flag": self.simulation_flag,
        }


@dataclass
class CrossReferenceReceipt:
    """Receipt for FEC/990 cross-reference linkage."""
    receipt_type: str = "cross_reference"
    source: str = ""  # fec, 990, usaspending
    query: str = ""
    entity_id: str = ""
    entity_name: str = ""
    match_found: bool = False
    match_details: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    simulation_flag: str = DISCLAIMER

    def to_dict(self) -> dict:
        return {
            "receipt_type": self.receipt_type,
            "source": self.source,
            "query": self.query,
            "entity_id": self.entity_id,
            "entity_name": self.entity_name,
            "match_found": self.match_found,
            "match_details": self.match_details,
            "timestamp": self.timestamp,
            "simulation_flag": self.simulation_flag,
        }
