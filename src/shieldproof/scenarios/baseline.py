"""
SHIELDPROOF v2.1 Baseline Scenario - Standard Flow Test

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

Register 10 contracts -> Add milestones -> Verify -> Pay -> Check variance -> Export dashboard.
"""

import time
from typing import Optional

from ..core import clear_ledger
from ..contract import register_contract
from ..milestone import submit_deliverable, verify_milestone
from ..payment import release_payment
from ..reconcile import check_variance, reconcile_all
from ..dashboard import export_dashboard


def run_baseline_scenario(n_contracts: int = 10, output_path: Optional[str] = None) -> dict:
    """
    Run baseline scenario.

    Register n contracts -> Add milestones -> Verify -> Pay -> Check variance -> Export dashboard.

    Args:
        n_contracts: Number of contracts to register (default: 10)
        output_path: Optional path for dashboard export

    Returns:
        {"passed": bool, "receipts": list, "metrics": dict}
    """
    start_time = time.time()
    receipts = []
    errors = []

    try:
        # Clear ledger for clean test
        clear_ledger()

        # Step 1: Register contracts
        contracts = []
        for i in range(n_contracts):
            contract = register_contract(
                contractor=f"Contractor-{i+1:03d}",
                amount=1_000_000.0 * (i + 1),  # $1M to $10M
                milestones=[
                    {"id": f"M{i+1}-1", "description": "Phase 1", "amount": 500_000.0 * (i + 1)},
                    {"id": f"M{i+1}-2", "description": "Phase 2", "amount": 500_000.0 * (i + 1)},
                ],
                terms={"scenario": "baseline", "index": i},
            )
            contracts.append(contract)
            receipts.append(contract)

        # Step 2: Submit deliverables
        for contract in contracts:
            contract_id = contract["contract_id"]
            for milestone in contract.get("milestones", []):
                milestone_id = milestone["id"]
                r = submit_deliverable(
                    contract_id,
                    milestone_id,
                    f"Deliverable for {milestone_id}".encode(),
                )
                receipts.append(r)

        # Step 3: Verify milestones
        for contract in contracts:
            contract_id = contract["contract_id"]
            for milestone in contract.get("milestones", []):
                milestone_id = milestone["id"]
                r = verify_milestone(
                    contract_id,
                    milestone_id,
                    "BASELINE-VERIFIER-001",
                    passed=True,
                )
                receipts.append(r)

        # Step 4: Release payments
        for contract in contracts:
            contract_id = contract["contract_id"]
            for milestone in contract.get("milestones", []):
                milestone_id = milestone["id"]
                r = release_payment(contract_id, milestone_id)
                receipts.append(r)

        # Step 5: Check variance
        for contract in contracts:
            contract_id = contract["contract_id"]
            variance = check_variance(contract_id)
            # Variance should be 0 since all milestones are paid
            if abs(variance.get("variance", 0)) > 0.01:
                errors.append(f"Unexpected variance for {contract_id}: {variance}")

        # Step 6: Reconcile all
        reports = reconcile_all()
        for report in reports:
            if report.get("status") != "ON_TRACK":
                errors.append(f"Contract not on track: {report.get('contract_id')} - {report.get('status')}")

        # Step 7: Export dashboard
        if output_path:
            dashboard_receipt = export_dashboard("json", output_path)
            receipts.append(dashboard_receipt)

        elapsed_time = time.time() - start_time
        passed = len(errors) == 0

        return {
            "passed": passed,
            "receipts": receipts,
            "metrics": {
                "contracts_registered": len(contracts),
                "milestones_verified": n_contracts * 2,
                "payments_released": n_contracts * 2,
                "elapsed_seconds": round(elapsed_time, 3),
                "receipts_generated": len(receipts),
            },
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
            "errors": [str(e)] + errors,
        }
