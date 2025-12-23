"""
SHIELDPROOF v2.1 Core Receipt - Receipt Emission and Validation

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

Provides:
- emit_receipt: Create receipt with ts, tenant_id, payload_hash
- validate_receipt: Validate receipt has required fields
- load_receipts: Load receipts from JSONL file
- append_receipt: Append receipt to JSONL file
"""

import json
import os
from datetime import datetime
from typing import Optional

from .constants import TENANT_ID, LEDGER_PATH
from .utils import dual_hash


def emit_receipt(
    receipt_type: str,
    data: dict,
    to_stdout: bool = True,
    to_ledger: bool = True,
    storage_path: Optional[str] = None
) -> dict:
    """
    Create receipt with ts, tenant_id, payload_hash.
    Print JSON to stdout. Return receipt dict.

    Args:
        receipt_type: Type of receipt (e.g., "contract", "milestone", "payment")
        data: Receipt-specific fields
        to_stdout: Whether to print to stdout (default True)
        to_ledger: Whether to append to ledger file (default True)
        storage_path: Optional custom path to store receipt

    Returns:
        Receipt dict with all fields
    """
    # Create receipt
    receipt = {
        "receipt_type": receipt_type,
        "ts": datetime.utcnow().isoformat() + "Z",
        "tenant_id": data.get("tenant_id", TENANT_ID),
        "payload_hash": dual_hash(json.dumps(data, sort_keys=True)),
        **data
    }

    receipt_json = json.dumps(receipt, sort_keys=True)

    if to_stdout:
        print(receipt_json, flush=True)

    if to_ledger:
        path = storage_path or LEDGER_PATH
        with open(path, "a") as f:
            f.write(receipt_json + "\n")

    return receipt


def validate_receipt(receipt: dict) -> bool:
    """
    Validate receipt has required fields and valid hash.

    Args:
        receipt: Receipt dict to validate

    Returns:
        True if valid, False otherwise
    """
    required_fields = ["receipt_type", "ts", "tenant_id", "payload_hash"]

    # Check required fields
    for field in required_fields:
        if field not in receipt:
            return False

    # Validate hash format (64 hex : 64 hex)
    payload_hash = receipt.get("payload_hash", "")
    if not isinstance(payload_hash, str) or ":" not in payload_hash:
        return False

    parts = payload_hash.split(":")
    if len(parts) != 2:
        return False

    # Each part should be 64 hex characters
    for part in parts:
        if len(part) != 64 or not all(c in '0123456789abcdef' for c in part):
            return False

    return True


def load_receipts(path: Optional[str] = None) -> list:
    """
    Load receipts from JSONL file.

    Args:
        path: Path to JSONL file (default: LEDGER_PATH)

    Returns:
        List of receipt dicts
    """
    path = path or LEDGER_PATH

    if not os.path.exists(path):
        return []

    receipts = []
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    receipts.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    return receipts


def append_receipt(receipt: dict, path: Optional[str] = None) -> None:
    """
    Append receipt to JSONL file.

    Args:
        receipt: Receipt dict to append
        path: Path to JSONL file (default: LEDGER_PATH)
    """
    path = path or LEDGER_PATH

    with open(path, 'a') as f:
        f.write(json.dumps(receipt, sort_keys=True) + '\n')
