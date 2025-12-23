"""
SHIELDPROOF v2.1 Contract Module - Fixed-Price Contract Registration

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

Register contracts with fixed-price terms and milestone definitions.
Per Grok: "Fixed-price everything" - the SpaceX model.

"One receipt. One milestone. One truth."
"""

from .config import (
    MODULE_ID,
    CONTRACT_TYPES,
    DEFAULT_TYPE,
)

from .register import (
    register_contract,
    get_contract,
    list_contracts,
    get_contract_milestones,
    update_contract,
)

from .receipts import (
    emit_contract_receipt,
)

__all__ = [
    # Config
    "MODULE_ID",
    "CONTRACT_TYPES",
    "DEFAULT_TYPE",
    # Register
    "register_contract",
    "get_contract",
    "list_contracts",
    "get_contract_milestones",
    "update_contract",
    # Receipts
    "emit_contract_receipt",
]
