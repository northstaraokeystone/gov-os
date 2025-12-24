"""
Gov-OS AidProof Module - Data Ingestion

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

Ingest foreign aid data from multiple sources:
- USASpending.gov (USAID, State, MCC entries)
- ForeignAssistance.gov
- FEC (for cross-reference)
- ProPublica Nonprofit Explorer (Form 990)
"""

import json
from typing import Any, Dict, List, Optional

from .config import (
    MODULE_ID,
    DATA_SOURCES,
    AGENCIES,
    DISCLAIMER,
)
from .data import AidAward, ImplementingPartner
from .receipts import AidIngestReceipt, PartnerIngestReceipt

# Import core utilities
import sys
sys.path.insert(0, str(__file__).rsplit('/', 3)[0])

try:
    from src.core import (
        TENANT_ID,
        dual_hash,
        emit_receipt,
        ForeignAidETL,
    )
except ImportError:
    TENANT_ID = "gov-os"
    dual_hash = lambda x: f"sha256:mock:{hash(x)}"
    emit_receipt = lambda t, p, **kw: {"receipt_type": t, **p}
    ForeignAidETL = None


def ingest(data: dict) -> dict:
    """
    Main ingestion entry point.

    Routes to appropriate sub-function based on data type.

    Args:
        data: Dict with 'type' and relevant parameters

    Returns:
        Ingestion result dict
    """
    data_type = data.get("type", "awards")

    if data_type == "awards":
        return ingest_usaid_awards(
            fiscal_year=data.get("fiscal_year", 2024),
            agency=data.get("agency", "USAID"),
            _simulate=data.get("_simulate", True),
        )
    elif data_type == "partners":
        return ingest_implementing_partners(
            agency=data.get("agency", "USAID"),
            _simulate=data.get("_simulate", True),
        )
    elif data_type == "countries":
        return ingest_country_allocations(
            fiscal_year=data.get("fiscal_year", 2024),
            _simulate=data.get("_simulate", True),
        )
    else:
        return {"error": f"Unknown data type: {data_type}"}


def ingest_usaid_awards(
    fiscal_year: int = 2024,
    agency: str = "USAID",
    _simulate: bool = True
) -> Dict[str, Any]:
    """
    Fetch USAID awards from USASpending.

    Args:
        fiscal_year: Fiscal year to query
        agency: Agency to query (USAID, STATE, MCC)
        _simulate: If True, use simulated data

    Returns:
        Dict with awards list and metadata

    Emits:
        aid_ingest_receipt
    """
    awards = []
    total_amount = 0.0

    try:
        if ForeignAidETL is not None:
            etl = ForeignAidETL()
            raw_awards = etl.fetch_awards(
                filters={"agency": agency, "fiscal_year": fiscal_year},
                _simulate=_simulate
            )
            for raw in raw_awards:
                award = AidAward(
                    id=raw.get("award_id", ""),
                    agency=raw.get("agency", agency),
                    recipient=raw.get("recipient_name", ""),
                    amount=raw.get("amount", 0),
                    country=raw.get("target_country", "USA"),
                    sector=raw.get("sector", ""),
                    description=raw.get("description", ""),
                    implementing_partner=raw.get("implementing_partner", False),
                    recipient_ein=raw.get("recipient_ein"),
                    fiscal_year=raw.get("fiscal_year", fiscal_year),
                )
                awards.append(award)
                total_amount += award.amount
        else:
            # Fallback simulation
            awards = _generate_simulated_awards(agency, fiscal_year, 50)
            total_amount = sum(a.amount for a in awards)

    except Exception as e:
        return {
            "error": str(e),
            "agency": agency,
            "fiscal_year": fiscal_year,
            "simulation_flag": DISCLAIMER,
        }

    # Emit receipt
    receipt = AidIngestReceipt(
        agency=agency,
        fiscal_year=fiscal_year,
        record_count=len(awards),
        total_amount=total_amount,
        data_source="usaspending",
    )
    _emit_aid_ingest_receipt(receipt)

    return {
        "agency": agency,
        "fiscal_year": fiscal_year,
        "awards": [a.to_dict() for a in awards],
        "record_count": len(awards),
        "total_amount": total_amount,
        "receipt": receipt.to_dict(),
        "simulation_flag": DISCLAIMER,
    }


def ingest_implementing_partners(
    agency: str = "USAID",
    _simulate: bool = True
) -> Dict[str, Any]:
    """
    Fetch NGO implementing partners for an agency.

    Args:
        agency: Foreign aid agency
        _simulate: If True, use simulated data

    Returns:
        Dict with partners list and metadata

    Emits:
        partner_ingest_receipt
    """
    partners = []
    total_awards = 0.0

    try:
        if ForeignAidETL is not None:
            etl = ForeignAidETL()
            raw_partners = etl.fetch_implementing_partners(agency, _simulate=_simulate)
            for raw in raw_partners:
                partner = ImplementingPartner(
                    id=raw.partner_id,
                    name=raw.name,
                    ein=raw.ein,
                    total_awards=raw.total_awards,
                    political_donations=raw.political_donations,
                    officers=raw.officers,
                    duns=raw.duns,
                    award_count=raw.award_count,
                    agencies=raw.agencies,
                    countries_served=raw.countries_served,
                    donation_recipients=raw.donation_recipients,
                    form_990_revenue=raw.form_990_revenue,
                    form_990_expenses=raw.form_990_expenses,
                )
                partners.append(partner)
                total_awards += partner.total_awards
        else:
            # Fallback simulation
            partners = _generate_simulated_partners(agency, 20)
            total_awards = sum(p.total_awards for p in partners)

    except Exception as e:
        return {
            "error": str(e),
            "agency": agency,
            "simulation_flag": DISCLAIMER,
        }

    # Count cross-references
    fec_linked = sum(1 for p in partners if p.political_donations > 0)
    form_990_linked = sum(1 for p in partners if p.form_990_revenue is not None)

    # Emit receipt
    receipt = PartnerIngestReceipt(
        agency=agency,
        partner_count=len(partners),
        total_awards=total_awards,
        cross_referenced=True,
        fec_linked=fec_linked,
        form_990_linked=form_990_linked,
    )
    _emit_partner_ingest_receipt(receipt)

    return {
        "agency": agency,
        "partners": [p.to_dict() for p in partners],
        "partner_count": len(partners),
        "total_awards": total_awards,
        "fec_linked": fec_linked,
        "form_990_linked": form_990_linked,
        "receipt": receipt.to_dict(),
        "simulation_flag": DISCLAIMER,
    }


def ingest_country_allocations(
    fiscal_year: int = 2024,
    _simulate: bool = True
) -> Dict[str, Any]:
    """
    Fetch country-level aid allocation breakdown.

    Args:
        fiscal_year: Fiscal year to query
        _simulate: If True, use simulated data

    Returns:
        Dict mapping country codes to allocations
    """
    allocations = {}

    try:
        if ForeignAidETL is not None:
            etl = ForeignAidETL()
            allocations = etl.fetch_country_allocations(fiscal_year, _simulate=_simulate)
        else:
            # Fallback simulation
            allocations = {
                "UKR": 15_000_000_000,
                "ISR": 3_800_000_000,
                "EGY": 1_500_000_000,
                "JOR": 1_200_000_000,
                "AFG": 800_000_000,
                "ETH": 700_000_000,
                "KEN": 600_000_000,
                "NGA": 550_000_000,
                "IND": 500_000_000,
                "PHL": 400_000_000,
            }

    except Exception as e:
        return {
            "error": str(e),
            "fiscal_year": fiscal_year,
            "simulation_flag": DISCLAIMER,
        }

    total_allocated = sum(allocations.values())
    sorted_countries = sorted(allocations.items(), key=lambda x: x[1], reverse=True)

    return {
        "fiscal_year": fiscal_year,
        "allocations": allocations,
        "country_count": len(allocations),
        "total_allocated": total_allocated,
        "top_5": sorted_countries[:5],
        "simulation_flag": DISCLAIMER,
    }


def cross_reference_political(partner_list: List[ImplementingPartner]) -> List[ImplementingPartner]:
    """
    Add FEC/990 data to implementing partners.

    Args:
        partner_list: List of ImplementingPartner objects

    Returns:
        Updated list with cross-reference data
    """
    if ForeignAidETL is None:
        return partner_list

    try:
        etl = ForeignAidETL()
        for partner in partner_list:
            # FEC cross-reference
            fec_data = etl.cross_reference_fec(partner.name, _simulate=True)
            partner.political_donations = fec_data.get("total_donations", 0)
            partner.donation_recipients = fec_data.get("donations", [])

            # Form 990 cross-reference
            if partner.ein:
                form_990 = etl.cross_reference_990(partner.ein, _simulate=True)
                partner.form_990_revenue = form_990.get("total_revenue")
                partner.form_990_expenses = form_990.get("total_expenses")
                partner.admin_expenses = form_990.get("admin_expenses")
                partner.program_expenses = form_990.get("program_expenses")

    except Exception:
        pass  # Graceful degradation

    return partner_list


# === SIMULATED DATA GENERATORS ===

def _generate_simulated_awards(agency: str, fiscal_year: int, n: int) -> List[AidAward]:
    """Generate simulated awards for testing."""
    import random
    random.seed(42)

    ngos = [
        "Democracy International", "Freedom House", "CARE International",
        "Save the Children", "World Vision", "Mercy Corps",
        "International Rescue Committee", "Catholic Relief Services",
    ]
    countries = ["UKR", "AFG", "ETH", "KEN", "NGA", "IND", "PHL"]
    sectors = ["democracy_governance", "health", "education", "economic_growth"]

    awards = []
    for i in range(n):
        awards.append(AidAward(
            id=f"AID-{agency}-{fiscal_year}-{i:04d}",
            agency=agency,
            recipient=random.choice(ngos),
            amount=random.randint(100_000, 50_000_000),
            country=random.choice(countries),
            sector=random.choice(sectors),
            implementing_partner=True,
            fiscal_year=fiscal_year,
        ))
    return awards


def _generate_simulated_partners(agency: str, n: int) -> List[ImplementingPartner]:
    """Generate simulated partners for testing."""
    import random
    random.seed(43)

    ngos = [
        ("Democracy International", "52-1234567"),
        ("Freedom House", "13-4567890"),
        ("CARE International", "13-5678901"),
        ("Save the Children", "06-6789012"),
        ("World Vision", "95-7890123"),
        ("Mercy Corps", "91-8901234"),
        ("International Rescue Committee", "13-9012345"),
        ("Catholic Relief Services", "52-0123456"),
    ]

    partners = []
    for i, (name, ein) in enumerate(ngos[:n]):
        total_awards = random.randint(10_000_000, 200_000_000)
        partners.append(ImplementingPartner(
            id=f"IP-{i:04d}",
            name=name,
            ein=ein,
            total_awards=total_awards,
            political_donations=random.randint(0, 2_000_000),
            award_count=random.randint(10, 100),
            agencies=[agency],
            form_990_revenue=total_awards * 1.5,
            form_990_expenses=total_awards * 1.4,
            admin_expenses=total_awards * 0.15,
            program_expenses=total_awards * 1.2,
        ))
    return partners


# === RECEIPT EMISSION ===

def _emit_aid_ingest_receipt(receipt: AidIngestReceipt) -> dict:
    """Emit aid_ingest receipt."""
    payload = receipt.to_dict()
    return emit_receipt("aid_ingest", {
        "tenant_id": TENANT_ID,
        "module": MODULE_ID,
        **payload,
        "payload_hash": dual_hash(json.dumps(payload, sort_keys=True, default=str)),
    }, to_stdout=False)


def _emit_partner_ingest_receipt(receipt: PartnerIngestReceipt) -> dict:
    """Emit partner_ingest receipt."""
    payload = receipt.to_dict()
    return emit_receipt("partner_ingest", {
        "tenant_id": TENANT_ID,
        "module": MODULE_ID,
        **payload,
        "payload_hash": dual_hash(json.dumps(payload, sort_keys=True, default=str)),
    }, to_stdout=False)
