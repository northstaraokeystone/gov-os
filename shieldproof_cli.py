#!/usr/bin/env python3
"""
ShieldProof v2.1 CLI

Minimal command-line interface for ShieldProof operations.
Per CLAUDEME: cli.py must emit valid receipt JSON to stdout.

v2.1 Commands (per spec):
  shield --version                        # Version info
  shield --test                           # System self-test
  shield contract register --file <path>  # Register contract
  shield contract list                    # List contracts
  shield milestone add --contract-id <id> --deliverable <hash>
  shield milestone verify --id <id>       # Verify milestone
  shield payment release --contract-id <id> --milestone-id <id> --amount <usd>
  shield payment list --contract-id <id>  # List payments
  shield reconcile check --contract-id <id>  # Check variance
  shield reconcile report                 # Full variance report
  shield dashboard export --format json|html --output <path>
  shield scenario run baseline            # Run baseline scenario
  shield scenario run stress              # Run stress scenario

"One receipt. One milestone. One truth."
"""

import argparse
import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.shieldproof import (
    # Core
    dual_hash,
    emit_receipt,
    merkle,
    TENANT_ID,
    RECEIPT_TYPES,
    VERSION,
    clear_ledger,
    # Contract
    register_contract,
    get_contract,
    list_contracts,
    # Milestone
    submit_deliverable,
    verify_milestone,
    list_pending,
    list_verified,
    # Payment
    release_payment,
    list_payments,
    total_paid,
    # Reconcile
    reconcile_contract,
    reconcile_all,
    get_waste_summary,
    check_variance,
    # Dashboard
    generate_summary,
    print_dashboard,
    serve,
    check,
    export_csv,
    export_json,
    export_dashboard,
    # Scenarios
    run_baseline_scenario,
    run_stress_scenario,
)


def cmd_test(args):
    """Run self-test and emit test receipt."""
    # Test dual_hash
    h = dual_hash("test")
    assert ":" in h, "dual_hash must return SHA256:BLAKE3 format"

    # Emit test receipt
    receipt = emit_receipt("test", {
        "message": "ShieldProof v2.1 self-test",
        "test_hash": h,
    }, to_ledger=False)

    return 0


def cmd_hash(args):
    """Compute dual-hash of input."""
    if args.input == "-":
        data = sys.stdin.read()
    else:
        data = args.input
    print(dual_hash(data))
    return 0


def cmd_receipt(args):
    """Emit a custom receipt."""
    try:
        data = json.loads(args.data)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        return 1

    emit_receipt(args.type, data, to_ledger=not args.no_ledger)
    return 0


def cmd_contract(args):
    """Register a new contract (legacy v2.0 API)."""
    try:
        milestones = json.loads(args.milestones)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid milestones JSON: {e}", file=sys.stderr)
        return 1

    terms = {}
    if args.terms:
        try:
            terms = json.loads(args.terms)
        except json.JSONDecodeError:
            terms = {"raw": args.terms}

    try:
        receipt = register_contract(
            contractor=args.contractor,
            amount=args.amount,
            milestones=milestones,
            terms=terms,
            contract_id=args.id,
        )
        print(f"Contract registered: {receipt['contract_id']}", file=sys.stderr)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


def cmd_contract_register(args):
    """Register a new contract (v2.1 API)."""
    # Load from file if specified
    if hasattr(args, 'file') and args.file:
        with open(args.file, 'r') as f:
            data = json.load(f)
            contractor = data.get('contractor', data.get('contractor_name'))
            amount = data.get('amount', data.get('total_value_usd'))
            milestones = data.get('milestones', [])
            terms = data.get('terms', {})
            contract_id = data.get('contract_id', data.get('id'))
    else:
        try:
            milestones = json.loads(args.milestones)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid milestones JSON: {e}", file=sys.stderr)
            return 1
        contractor = args.contractor
        amount = args.amount
        terms = {}
        if args.terms:
            try:
                terms = json.loads(args.terms)
            except json.JSONDecodeError:
                terms = {"raw": args.terms}
        contract_id = args.id if hasattr(args, 'id') else None

    try:
        receipt = register_contract(
            contractor=contractor,
            amount=amount,
            milestones=milestones,
            terms=terms,
            contract_id=contract_id,
        )
        print(f"Contract registered: {receipt['contract_id']}", file=sys.stderr)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


def cmd_contract_list(args):
    """List contracts."""
    contracts = list_contracts()
    for c in contracts:
        amount = c.get('amount_fixed', c.get('total_value_usd', 0))
        print(f"{c.get('contract_id')}: {c.get('contractor')} - ${amount:,.2f}")
    return 0


def cmd_submit(args):
    """Submit a milestone deliverable (legacy v2.0 API)."""
    if args.file:
        with open(args.file, "rb") as f:
            deliverable = f.read()
    else:
        deliverable = args.content or ""

    try:
        receipt = submit_deliverable(args.contract_id, args.milestone_id, deliverable)
        print(f"Deliverable submitted: {receipt['milestone_id']} -> {receipt['status']}", file=sys.stderr)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


def cmd_milestone_add(args):
    """Add/submit a milestone deliverable (v2.1 API)."""
    deliverable = args.deliverable if hasattr(args, 'deliverable') and args.deliverable else "Deliverable"
    try:
        receipt = submit_deliverable(args.contract_id, args.milestone_id, deliverable.encode() if isinstance(deliverable, str) else deliverable)
        print(f"Deliverable submitted: {receipt['milestone_id']} -> {receipt['status']}", file=sys.stderr)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


def cmd_verify(args):
    """Verify a milestone (legacy v2.0 API)."""
    try:
        receipt = verify_milestone(
            args.contract_id,
            args.milestone_id,
            args.verifier_id,
            passed=not args.reject,
        )
        print(f"Milestone {receipt['milestone_id']} -> {receipt['status']}", file=sys.stderr)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


def cmd_milestone_verify(args):
    """Verify a milestone (v2.1 API)."""
    contract_id = args.contract_id if hasattr(args, 'contract_id') else None
    milestone_id = args.id if hasattr(args, 'id') else args.milestone_id
    verifier_id = args.verifier_id if hasattr(args, 'verifier_id') and args.verifier_id else "CLI-VERIFIER"
    reject = args.reject if hasattr(args, 'reject') else False

    try:
        receipt = verify_milestone(
            contract_id,
            milestone_id,
            verifier_id,
            passed=not reject,
        )
        print(f"Milestone {receipt['milestone_id']} -> {receipt['status']}", file=sys.stderr)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


def cmd_pay(args):
    """Release payment for a verified milestone (legacy v2.0 API)."""
    try:
        receipt = release_payment(args.contract_id, args.milestone_id)
        amount = receipt.get('amount', receipt.get('amount_usd', 0))
        print(f"Payment released: ${amount:,.2f}", file=sys.stderr)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


def cmd_payment_release(args):
    """Release payment (v2.1 API)."""
    try:
        receipt = release_payment(args.contract_id, args.milestone_id)
        amount = receipt.get('amount', receipt.get('amount_usd', 0))
        print(f"Payment released: ${amount:,.2f}", file=sys.stderr)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


def cmd_payment_list(args):
    """List payments (v2.1 API)."""
    contract_id = args.contract_id if hasattr(args, 'contract_id') and args.contract_id else None
    payments = list_payments(contract_id)
    for p in payments:
        amount = p.get('amount', p.get('amount_usd', 0))
        print(f"{p.get('contract_id')}/{p.get('milestone_id')}: ${amount:,.2f}")
    return 0


def cmd_reconcile(args):
    """Reconcile contracts (legacy v2.0 API)."""
    if args.contract_id:
        report = reconcile_contract(args.contract_id)
        print(json.dumps(report, indent=2))
    else:
        reports = reconcile_all()
        summary = get_waste_summary()
        output = {"summary": summary, "contracts": reports}
        print(json.dumps(output, indent=2))

    return 0


def cmd_reconcile_check(args):
    """Check variance for a contract (v2.1 API)."""
    result = check_variance(args.contract_id)
    print(json.dumps(result, indent=2))
    return 0


def cmd_reconcile_report(args):
    """Full variance report (v2.1 API)."""
    contract_id = args.contract_id if hasattr(args, 'contract_id') and args.contract_id else None
    if contract_id:
        report = reconcile_contract(contract_id)
        print(json.dumps(report, indent=2))
    else:
        reports = reconcile_all()
        summary = get_waste_summary()
        output = {"summary": summary, "contracts": reports}
        print(json.dumps(output, indent=2))
    return 0


def cmd_dashboard(args):
    """Show or serve dashboard (legacy v2.0 API)."""
    if args.check:
        if check():
            print("Dashboard: OK")
            return 0
        else:
            print("Dashboard: FAIL")
            return 1

    if args.serve:
        serve(args.port)
        return 0

    if args.export_csv:
        export_csv(args.export_csv)
        print(f"Exported to {args.export_csv}", file=sys.stderr)
        return 0

    if args.export_json:
        export_json(args.export_json)
        print(f"Exported to {args.export_json}", file=sys.stderr)
        return 0

    if args.json:
        summary = generate_summary()
        print(json.dumps(summary, indent=2))
    else:
        print_dashboard()

    return 0


def cmd_dashboard_export(args):
    """Export dashboard (v2.1 API)."""
    fmt = args.format if hasattr(args, 'format') and args.format else "json"
    output = args.output if hasattr(args, 'output') and args.output else f"/tmp/dashboard.{fmt}"

    try:
        receipt = export_dashboard(fmt, output)
        print(f"Exported to {output}", file=sys.stderr)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


def cmd_scenario_run(args):
    """Run a scenario (v2.1 API)."""
    scenario = args.scenario

    if scenario == "baseline":
        result = run_baseline_scenario()
    elif scenario == "stress":
        n = args.n_contracts if hasattr(args, 'n_contracts') and args.n_contracts else 100
        result = run_stress_scenario(n_contracts=n)
    else:
        print(f"Unknown scenario: {scenario}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, default=str))
    return 0 if result.get("passed") else 1


def main():
    parser = argparse.ArgumentParser(
        description="ShieldProof v2.1 CLI - Defense Contract Accountability",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='"One receipt. One milestone. One truth."',
    )
    parser.add_argument("--version", action="version", version=f"ShieldProof {VERSION}")
    parser.add_argument("--test", action="store_true", help="Run self-test")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Test command
    test_parser = subparsers.add_parser("test", help="Run self-test")

    # Hash command
    hash_parser = subparsers.add_parser("hash", help="Compute dual-hash")
    hash_parser.add_argument("input", nargs="?", default="-", help="Input to hash (- for stdin)")

    # Receipt command
    receipt_parser = subparsers.add_parser("receipt", help="Emit a receipt")
    receipt_parser.add_argument("type", help="Receipt type")
    receipt_parser.add_argument("data", help="Receipt data as JSON")
    receipt_parser.add_argument("--no-ledger", action="store_true", help="Don't write to ledger")

    # Contract subcommand (v2.1)
    contract_parser = subparsers.add_parser("contract", help="Contract operations")
    contract_sub = contract_parser.add_subparsers(dest="contract_cmd")

    contract_register = contract_sub.add_parser("register", help="Register a contract")
    contract_register.add_argument("--contractor", help="Contractor name")
    contract_register.add_argument("--amount", type=float, help="Total amount")
    contract_register.add_argument("--milestones", help="Milestones as JSON array")
    contract_register.add_argument("--terms", help="Contract terms")
    contract_register.add_argument("--id", help="Contract ID (generated if not provided)")
    contract_register.add_argument("--file", help="Load contract from JSON file")

    contract_list = contract_sub.add_parser("list", help="List contracts")

    # Milestone subcommand (v2.1)
    milestone_parser = subparsers.add_parser("milestone", help="Milestone operations")
    milestone_sub = milestone_parser.add_subparsers(dest="milestone_cmd")

    milestone_add = milestone_sub.add_parser("add", help="Add/submit a milestone")
    milestone_add.add_argument("--contract-id", required=True, help="Contract ID")
    milestone_add.add_argument("--milestone-id", required=True, help="Milestone ID")
    milestone_add.add_argument("--deliverable", help="Deliverable content/hash")

    milestone_verify = milestone_sub.add_parser("verify", help="Verify a milestone")
    milestone_verify.add_argument("--id", required=True, help="Milestone ID")
    milestone_verify.add_argument("--contract-id", required=True, help="Contract ID")
    milestone_verify.add_argument("--verifier-id", help="Verifier ID")
    milestone_verify.add_argument("--reject", action="store_true", help="Reject instead of approve")

    # Payment subcommand (v2.1)
    payment_parser = subparsers.add_parser("payment", help="Payment operations")
    payment_sub = payment_parser.add_subparsers(dest="payment_cmd")

    payment_release = payment_sub.add_parser("release", help="Release payment")
    payment_release.add_argument("--contract-id", required=True, help="Contract ID")
    payment_release.add_argument("--milestone-id", required=True, help="Milestone ID")
    payment_release.add_argument("--amount", type=float, help="Amount (uses milestone amount if not specified)")

    payment_list = payment_sub.add_parser("list", help="List payments")
    payment_list.add_argument("--contract-id", help="Filter by contract")

    # Reconcile subcommand (v2.1)
    reconcile_parser = subparsers.add_parser("reconcile", help="Reconciliation operations")
    reconcile_sub = reconcile_parser.add_subparsers(dest="reconcile_cmd")

    reconcile_check = reconcile_sub.add_parser("check", help="Check variance")
    reconcile_check.add_argument("--contract-id", required=True, help="Contract ID")

    reconcile_report = reconcile_sub.add_parser("report", help="Full variance report")
    reconcile_report.add_argument("--contract-id", help="Single contract to reconcile")

    # Legacy reconcile args
    reconcile_parser.add_argument("--contract-id", help="Single contract to reconcile", dest="legacy_contract_id")

    # Dashboard subcommand (v2.1)
    dashboard_parser = subparsers.add_parser("dashboard", help="Dashboard operations")
    dashboard_sub = dashboard_parser.add_subparsers(dest="dashboard_cmd")

    dashboard_export = dashboard_sub.add_parser("export", help="Export dashboard")
    dashboard_export.add_argument("--format", choices=["json", "html", "csv"], default="json", help="Export format")
    dashboard_export.add_argument("--output", help="Output path")

    # Legacy dashboard args
    dashboard_parser.add_argument("--check", action="store_true", help="Health check only")
    dashboard_parser.add_argument("--serve", action="store_true", help="Serve as HTTP")
    dashboard_parser.add_argument("--port", type=int, default=8080, help="HTTP port")
    dashboard_parser.add_argument("--json", action="store_true", help="Output as JSON")
    dashboard_parser.add_argument("--export-csv", help="Export to CSV file")
    dashboard_parser.add_argument("--export-json", help="Export to JSON file")

    # Scenario subcommand (v2.1)
    scenario_parser = subparsers.add_parser("scenario", help="Run scenarios")
    scenario_sub = scenario_parser.add_subparsers(dest="scenario_cmd")

    scenario_run = scenario_sub.add_parser("run", help="Run a scenario")
    scenario_run.add_argument("scenario", choices=["baseline", "stress"], help="Scenario to run")
    scenario_run.add_argument("--n-contracts", type=int, help="Number of contracts (for stress)")

    # Legacy commands (v2.0 backward compat)
    submit_parser = subparsers.add_parser("submit", help="Submit a deliverable (legacy)")
    submit_parser.add_argument("contract_id", help="Contract ID")
    submit_parser.add_argument("milestone_id", help="Milestone ID")
    submit_parser.add_argument("--file", help="Deliverable file")
    submit_parser.add_argument("--content", help="Deliverable content")

    verify_parser = subparsers.add_parser("verify", help="Verify a milestone (legacy)")
    verify_parser.add_argument("contract_id", help="Contract ID")
    verify_parser.add_argument("milestone_id", help="Milestone ID")
    verify_parser.add_argument("--verifier-id", required=True, help="Verifier ID")
    verify_parser.add_argument("--reject", action="store_true", help="Reject instead of approve")

    pay_parser = subparsers.add_parser("pay", help="Release payment (legacy)")
    pay_parser.add_argument("contract_id", help="Contract ID")
    pay_parser.add_argument("milestone_id", help="Milestone ID")

    args = parser.parse_args()

    # Handle --test flag on root
    if args.test or args.command == "test":
        return cmd_test(args)

    if args.command == "hash":
        return cmd_hash(args)
    elif args.command == "receipt":
        return cmd_receipt(args)
    elif args.command == "contract":
        if hasattr(args, 'contract_cmd'):
            if args.contract_cmd == "register":
                return cmd_contract_register(args)
            elif args.contract_cmd == "list":
                return cmd_contract_list(args)
        # Legacy: direct contract command with args
        if hasattr(args, 'contractor') and args.contractor:
            return cmd_contract(args)
        print("Usage: shieldproof_cli.py contract {register,list}", file=sys.stderr)
        return 1
    elif args.command == "milestone":
        if hasattr(args, 'milestone_cmd'):
            if args.milestone_cmd == "add":
                return cmd_milestone_add(args)
            elif args.milestone_cmd == "verify":
                return cmd_milestone_verify(args)
        print("Usage: shieldproof_cli.py milestone {add,verify}", file=sys.stderr)
        return 1
    elif args.command == "payment":
        if hasattr(args, 'payment_cmd'):
            if args.payment_cmd == "release":
                return cmd_payment_release(args)
            elif args.payment_cmd == "list":
                return cmd_payment_list(args)
        print("Usage: shieldproof_cli.py payment {release,list}", file=sys.stderr)
        return 1
    elif args.command == "reconcile":
        if hasattr(args, 'reconcile_cmd') and args.reconcile_cmd:
            if args.reconcile_cmd == "check":
                return cmd_reconcile_check(args)
            elif args.reconcile_cmd == "report":
                return cmd_reconcile_report(args)
        # Legacy reconcile
        if hasattr(args, 'legacy_contract_id'):
            args.contract_id = args.legacy_contract_id
        return cmd_reconcile(args)
    elif args.command == "dashboard":
        if hasattr(args, 'dashboard_cmd') and args.dashboard_cmd:
            if args.dashboard_cmd == "export":
                return cmd_dashboard_export(args)
        return cmd_dashboard(args)
    elif args.command == "scenario":
        if hasattr(args, 'scenario_cmd') and args.scenario_cmd == "run":
            return cmd_scenario_run(args)
        print("Usage: shieldproof_cli.py scenario run {baseline,stress}", file=sys.stderr)
        return 1
    # Legacy commands
    elif args.command == "submit":
        return cmd_submit(args)
    elif args.command == "verify":
        return cmd_verify(args)
    elif args.command == "pay":
        return cmd_pay(args)
    else:
        # Default: run test
        return cmd_test(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
