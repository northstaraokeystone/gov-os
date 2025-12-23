"""
SHIELDPROOF v2.1 Core Ledger - Receipt Ledger Storage and Merkle Batching

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

Provides:
- load_ledger: Load all receipts from storage
- query_receipts: Query receipts with filters
- clear_ledger: Clear all receipts from storage
- get_ledger: Alias for load_ledger
- add_to_ledger: Add receipt to ledger
- anchor_batch: Compute Merkle root, emit anchor_receipt
- get_by_type: Filter receipts by type
- get_by_id: Get single receipt by ID
"""

import json
import os
from typing import Optional

from .constants import LEDGER_PATH, ANCHOR_BATCH_SIZE, TENANT_ID
from .receipt import emit_receipt, load_receipts, append_receipt
from .utils import merkle


def load_ledger() -> list:
    """
    Load all receipts from the ledger file.

    Returns:
        List of receipt dicts
    """
    return load_receipts(LEDGER_PATH)


def query_receipts(receipt_type: Optional[str] = None, **filters) -> list:
    """
    Query receipts from the ledger.

    Args:
        receipt_type: Filter by receipt type
        **filters: Additional field filters

    Returns:
        List of matching receipts
    """
    receipts = load_ledger()

    if receipt_type:
        receipts = [r for r in receipts if r.get("receipt_type") == receipt_type]

    for key, value in filters.items():
        receipts = [r for r in receipts if r.get(key) == value]

    return receipts


def clear_ledger(path: Optional[str] = None) -> None:
    """
    Clear the ledger file. Use only for testing.

    Args:
        path: Optional path to ledger file
    """
    storage_path = path or LEDGER_PATH
    if os.path.exists(storage_path):
        os.remove(storage_path)


# Aliases for v2.1 API
def get_ledger(path: Optional[str] = None) -> list:
    """
    Return all receipts from storage.
    Alias for load_ledger.

    Args:
        path: Optional path to receipt storage

    Returns:
        List of all receipts
    """
    return load_receipts(path or LEDGER_PATH)


def add_to_ledger(receipt: dict, path: Optional[str] = None) -> str:
    """
    Add receipt to ledger, return receipt_id.

    Args:
        receipt: Receipt dict to add
        path: Optional path to receipt storage

    Returns:
        receipt_id of added receipt
    """
    append_receipt(receipt, path or LEDGER_PATH)
    return receipt.get("receipt_id", receipt.get("payload_hash", ""))


def anchor_batch(receipts: list, path: Optional[str] = None) -> dict:
    """
    Compute Merkle root for batch, emit anchor_receipt.

    Args:
        receipts: List of receipts to anchor
        path: Optional path to receipt storage

    Returns:
        Anchor receipt
    """
    root = merkle(receipts)

    anchor = emit_receipt("anchor", {
        "tenant_id": TENANT_ID,
        "merkle_root": root,
        "batch_size": len(receipts),
        "hash_algos": ["SHA256", "BLAKE3"],
    }, to_ledger=bool(path))

    return anchor


def get_by_type(receipt_type: str, path: Optional[str] = None) -> list:
    """
    Filter receipts by type.

    Args:
        receipt_type: Type to filter by
        path: Optional path to receipt storage

    Returns:
        List of matching receipts
    """
    receipts = load_receipts(path or LEDGER_PATH)
    return [r for r in receipts if r.get("receipt_type") == receipt_type]


def get_by_id(receipt_id: str, path: Optional[str] = None) -> Optional[dict]:
    """
    Get single receipt by ID.

    Args:
        receipt_id: ID to search for
        path: Optional path to receipt storage

    Returns:
        Receipt dict or None if not found
    """
    receipts = load_receipts(path or LEDGER_PATH)
    for receipt in receipts:
        if receipt.get("receipt_id") == receipt_id:
            return receipt
        # Also check payload_hash for older receipts without receipt_id
        if receipt.get("payload_hash") == receipt_id:
            return receipt
    return None
