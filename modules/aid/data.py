"""
Gov-OS AidProof Module - Data Models

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

Data classes for AidProof module:
- AidAward: Single foreign aid award record
- ImplementingPartner: NGO implementing partner entity
- RoundTripEvidence: Detection result for round-trip funding
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class AidAward:
    """Single foreign aid award record."""
    id: str
    agency: str
    recipient: str
    amount: float
    country: str
    sector: str
    date: Optional[datetime] = None
    description: str = ""
    implementing_partner: bool = False
    recipient_ein: Optional[str] = None
    fiscal_year: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "agency": self.agency,
            "recipient": self.recipient,
            "amount": self.amount,
            "country": self.country,
            "sector": self.sector,
            "date": self.date.isoformat() if self.date else None,
            "description": self.description,
            "implementing_partner": self.implementing_partner,
            "recipient_ein": self.recipient_ein,
            "fiscal_year": self.fiscal_year,
        }


@dataclass
class ImplementingPartner:
    """NGO implementing partner entity."""
    id: str
    name: str
    ein: Optional[str] = None
    total_awards: float = 0.0
    political_donations: float = 0.0
    officers: List[Dict[str, str]] = field(default_factory=list)
    duns: Optional[str] = None
    award_count: int = 0
    agencies: List[str] = field(default_factory=list)
    countries_served: List[str] = field(default_factory=list)
    donation_recipients: List[Dict[str, Any]] = field(default_factory=list)
    form_990_revenue: Optional[float] = None
    form_990_expenses: Optional[float] = None
    admin_expenses: Optional[float] = None
    program_expenses: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "ein": self.ein,
            "total_awards": self.total_awards,
            "political_donations": self.political_donations,
            "officers": self.officers,
            "duns": self.duns,
            "award_count": self.award_count,
            "agencies": self.agencies,
            "countries_served": self.countries_served,
            "donation_recipients": self.donation_recipients,
            "form_990_revenue": self.form_990_revenue,
            "form_990_expenses": self.form_990_expenses,
            "admin_expenses": self.admin_expenses,
            "program_expenses": self.program_expenses,
        }

    @property
    def overhead_ratio(self) -> float:
        """Calculate overhead ratio (admin expenses / total expenses)."""
        if self.form_990_expenses and self.form_990_expenses > 0:
            admin = self.admin_expenses or 0
            return admin / self.form_990_expenses
        return 0.0

    @property
    def round_trip_score(self) -> float:
        """Calculate round-trip score (donations / awards)."""
        if self.total_awards > 0:
            return self.political_donations / self.total_awards
        return 0.0


@dataclass
class RoundTripEvidence:
    """Evidence of potential round-trip funding."""
    partner_id: str
    partner_name: str
    award_amount: float
    donation_amount: float
    temporal_gap_days: Optional[int] = None
    score: float = 0.0
    flagged: bool = False
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "partner_id": self.partner_id,
            "partner_name": self.partner_name,
            "award_amount": self.award_amount,
            "donation_amount": self.donation_amount,
            "temporal_gap_days": self.temporal_gap_days,
            "score": self.score,
            "flagged": self.flagged,
            "details": self.details,
        }


@dataclass
class CountryAllocation:
    """Country-level aid allocation."""
    country_code: str
    country_name: str
    total_amount: float
    agency: str
    fiscal_year: int
    sector_breakdown: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "country_code": self.country_code,
            "country_name": self.country_name,
            "total_amount": self.total_amount,
            "agency": self.agency,
            "fiscal_year": self.fiscal_year,
            "sector_breakdown": self.sector_breakdown,
        }


@dataclass
class AidAnomaly:
    """Detected anomaly in aid data."""
    anomaly_type: str  # compression, overhead, round_trip, concentration
    entity_id: str
    entity_name: str
    anomaly_score: float
    threshold_used: float
    description: str
    evidence: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "anomaly_type": self.anomaly_type,
            "entity_id": self.entity_id,
            "entity_name": self.entity_name,
            "anomaly_score": self.anomaly_score,
            "threshold_used": self.threshold_used,
            "description": self.description,
            "evidence": self.evidence,
        }
