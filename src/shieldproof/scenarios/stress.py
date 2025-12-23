"""
SHIELDPROOF v2.1 Stress Scenario - High-Volume Stress Test

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

High-volume test with many contracts to measure throughput.
"""

import time
from typing import Optional

from ..core import clear_ledger
from ..contract import register_contract
from ..milestone import submit_deliverable, verify_milestone
from ..payment import release_payment
from ..dashboard import generate_summary


def run_stress_scenario(n_contracts: int = 100) -> dict:
    """
    Run stress scenario.

    High-volume test with n contracts to measure throughput.

    Args:
        n_contracts: Number of contracts to register (default: 100)

    Returns:
        {"passed": bool, "receipts": list, "metrics": dict, "throughput_per_sec": float}
    """
    start_time = time.time()
    receipts = []
    errors = []

    try:
        # Clear ledger for clean test
        clear_ledger()

        # Register contracts
        contracts = []
        register_start = time.time()
        for i in range(n_contracts):
            contract = register_contract(
                contractor=f"StressContractor-{i+1:05d}",
                amount=100_000.0,  # $100K each
                milestones=[
                    {"id": f"S{i+1}-M1", "description": "Milestone 1", "amount": 100_000.0},
                ],
                terms={"scenario": "stress", "index": i},
            )
            contracts.append(contract)
            receipts.append(contract)
        register_time = time.time() - register_start

        # Submit and verify milestones
        verify_start = time.time()
        for contract in contracts:
            contract_id = contract["contract_id"]
            milestone_id = contract["milestones"][0]["id"]

            # Submit
            r = submit_deliverable(contract_id, milestone_id, b"Stress deliverable")
            receipts.append(r)

            # Verify
            r = verify_milestone(contract_id, milestone_id, "STRESS-VERIFIER", passed=True)
            receipts.append(r)
        verify_time = time.time() - verify_start

        # Release payments
        payment_start = time.time()
        for contract in contracts:
            contract_id = contract["contract_id"]
            milestone_id = contract["milestones"][0]["id"]
            r = release_payment(contract_id, milestone_id)
            receipts.append(r)
        payment_time = time.time() - payment_start

        # Generate summary
        summary_start = time.time()
        summary = generate_summary()
        summary_time = time.time() - summary_start

        elapsed_time = time.time() - start_time
        throughput = len(receipts) / elapsed_time if elapsed_time > 0 else 0

        # Validation
        if summary.get("total_contracts") != n_contracts:
            errors.append(f"Expected {n_contracts} contracts, got {summary.get('total_contracts')}")
        if summary.get("waste_identified", 0) > 0:
            errors.append(f"Unexpected waste: {summary.get('waste_identified')}")

        passed = len(errors) == 0

        return {
            "passed": passed,
            "receipts": receipts,
            "metrics": {
                "contracts_registered": n_contracts,
                "milestones_processed": n_contracts,
                "payments_released": n_contracts,
                "receipts_generated": len(receipts),
                "elapsed_seconds": round(elapsed_time, 3),
                "register_time_seconds": round(register_time, 3),
                "verify_time_seconds": round(verify_time, 3),
                "payment_time_seconds": round(payment_time, 3),
                "summary_time_seconds": round(summary_time, 3),
            },
            "throughput_per_sec": round(throughput, 2),
            "errors": errors,
        }

    except Exception as e:
        elapsed_time = time.time() - start_time
        return {
            "passed": False,
            "receipts": receipts,
            "metrics": {
                "elapsed_seconds": round(elapsed_time, 3),
                "receipts_generated": len(receipts),
            },
            "throughput_per_sec": 0,
            "errors": [str(e)] + errors,
        }
