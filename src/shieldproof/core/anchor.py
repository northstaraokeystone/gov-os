"""
SHIELDPROOF v2.1 Core Anchor - Dual-Hash Anchoring Operations

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

Provides:
- anchor_receipt: Create anchor for single receipt
- anchor_chain: Create Merkle chain anchor for batch
- verify_anchor: Verify receipt against anchor
"""

import json
from typing import Optional

from .constants import TENANT_ID
from .receipt import emit_receipt
from .utils import dual_hash, merkle


def anchor_receipt(receipt: dict, storage_path: Optional[str] = None) -> dict:
    """
    Create anchor for single receipt.

    Args:
        receipt: Receipt to anchor
        storage_path: Optional path to store anchor

    Returns:
        Anchor receipt
    """
    # Compute hash of the receipt
    receipt_hash = dual_hash(json.dumps(receipt, sort_keys=True))

    anchor = emit_receipt("anchor", {
        "tenant_id": receipt.get("tenant_id", TENANT_ID),
        "anchor_type": "single",
        "receipt_id": receipt.get("receipt_id", receipt.get("payload_hash")),
        "receipt_hash": receipt_hash,
        "hash_algos": ["SHA256", "BLAKE3"],
    }, to_ledger=bool(storage_path))

    return anchor


def anchor_chain(receipts: list, storage_path: Optional[str] = None) -> dict:
    """
    Create Merkle chain anchor for batch.

    Args:
        receipts: List of receipts to anchor
        storage_path: Optional path to store anchor

    Returns:
        Chain anchor receipt
    """
    # Compute Merkle root
    root = merkle(receipts)

    # Get receipt IDs
    receipt_ids = []
    for r in receipts:
        rid = r.get("receipt_id") or r.get("payload_hash")
        if rid:
            receipt_ids.append(rid)

    anchor = emit_receipt("anchor", {
        "tenant_id": TENANT_ID,
        "anchor_type": "chain",
        "merkle_root": root,
        "batch_size": len(receipts),
        "receipt_ids": receipt_ids,
        "hash_algos": ["SHA256", "BLAKE3"],
    }, to_ledger=bool(storage_path))

    return anchor


def verify_anchor(receipt: dict, anchor: dict) -> bool:
    """
    Verify receipt against anchor.

    Args:
        receipt: Receipt to verify
        anchor: Anchor to verify against

    Returns:
        True if verification passes, False otherwise
    """
    anchor_type = anchor.get("anchor_type", "single")

    if anchor_type == "single":
        # Verify single receipt hash
        expected_hash = anchor.get("receipt_hash")
        actual_hash = dual_hash(json.dumps(receipt, sort_keys=True))
        return expected_hash == actual_hash

    elif anchor_type == "chain":
        # Verify receipt is in the chain
        receipt_id = receipt.get("receipt_id") or receipt.get("payload_hash")
        receipt_ids = anchor.get("receipt_ids", [])
        return receipt_id in receipt_ids

    return False
