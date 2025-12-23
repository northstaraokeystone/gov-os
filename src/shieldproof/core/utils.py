"""
SHIELDPROOF v2.1 Core Utilities - Core Utility Functions

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

Provides:
- dual_hash: SHA256:BLAKE3 format per CLAUDEME §8
- merkle: Compute Merkle root using dual_hash
- StopRule: Exception raised when stoprule triggers
- validate_hash: Validate dual-hash format
- timestamp_iso: Return current UTC timestamp in ISO8601 format
"""

import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from typing import Union

try:
    import blake3
    HAS_BLAKE3 = True
except ImportError:
    HAS_BLAKE3 = False


class StopRuleException(Exception):
    """
    Raised when stoprule triggers. Never catch silently.

    Per CLAUDEME: stoprules halt execution on error paths.
    """
    pass


# Alias for compatibility with existing code
StopRule = StopRuleException


def dual_hash(data: Union[bytes, str]) -> str:
    """
    SHA256:BLAKE3 - ALWAYS use this, never single hash.
    Per CLAUDEME §8: HASH = "SHA256 + BLAKE3"

    If blake3 not installed, fallback to SHA256:SHA256.

    Args:
        data: Bytes or string to hash

    Returns:
        String in format "sha256hex:blake3hex"
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    sha = hashlib.sha256(data).hexdigest()
    b3 = blake3.blake3(data).hexdigest() if HAS_BLAKE3 else sha
    return f"{sha}:{b3}"


def merkle(items: list) -> str:
    """
    Compute Merkle root of items using dual_hash.

    Handles:
    - Empty list: hash of "empty"
    - Odd count: duplicate last item

    Args:
        items: List of items to compute root for

    Returns:
        Merkle root as dual-hash string
    """
    if not items:
        return dual_hash(b"empty")

    # Convert items to hashes
    hashes = []
    for item in items:
        if isinstance(item, dict):
            hashes.append(dual_hash(json.dumps(item, sort_keys=True)))
        else:
            hashes.append(dual_hash(str(item)))

    # Build Merkle tree
    while len(hashes) > 1:
        if len(hashes) % 2:
            hashes.append(hashes[-1])  # Duplicate last if odd
        hashes = [
            dual_hash(hashes[i] + hashes[i + 1])
            for i in range(0, len(hashes), 2)
        ]

    return hashes[0]


def validate_hash(hash_str: str) -> bool:
    """
    Validate dual-hash format.

    Args:
        hash_str: Hash string to validate

    Returns:
        True if valid dual-hash format, False otherwise
    """
    if not isinstance(hash_str, str):
        return False

    # Check format: 64 hex chars : 64 hex chars
    pattern = r'^[a-f0-9]{64}:[a-f0-9]{64}$'
    return bool(re.match(pattern, hash_str))


def timestamp_iso() -> str:
    """
    Return current UTC timestamp in ISO8601 format.

    Returns:
        ISO8601 timestamp string with Z suffix
    """
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


def generate_id(prefix: str = "id") -> str:
    """
    Generate a unique ID.

    Args:
        prefix: Prefix for the ID

    Returns:
        Unique ID string
    """
    return f"{prefix}_{uuid.uuid4().hex[:16]}"
