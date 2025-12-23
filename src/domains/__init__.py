"""
Gov-OS Domain Modules - Plug-in Architecture for Federal Spending Domains

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

Available domains:
- defense: Defense spending, shipbuilding, military contracts
- medicaid: Healthcare spending, provider payments
"""

from typing import List

__version__ = "1.0.0"

AVAILABLE_DOMAINS = ["defense", "medicaid"]


def list_domains() -> List[str]:
    """Return available domain names."""
    return AVAILABLE_DOMAINS.copy()


__all__ = [
    "AVAILABLE_DOMAINS",
    "list_domains",
]
