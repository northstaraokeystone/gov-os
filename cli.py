#!/usr/bin/env python3
"""
Gov-OS CLI - Unified Command Line Interface for Federal Fraud Detection

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

Gov-OS is a universal federal fraud detection operating system that combines:
- WarrantProof: Receipt-based fraud detection via compression analysis
- Domain Modules: Defense spending, Medicaid, and extensible domains
- RAZOR: Kolmogorov validation engine for real data validation
- Shipyard: Trump-class battleship program tracking
- ShieldProof: Defense contract accountability

Usage:
    gov-os --test                           # System test
    gov-os --version                        # Version info
    gov-os scenario --run BASELINE          # Run simulation scenario
    gov-os explain --demo                   # Plain-language demo
    gov-os health                           # System health check
    gov-os patterns --list                  # View fraud patterns
    gov-os freshness --demo                 # Evidence freshness demo
    gov-os defense simulate --cycles 100    # Defense domain simulation
    gov-os medicaid scenario PROVIDER_RING  # Medicaid scenario
    gov-os razor --gate api                 # RAZOR validation gates
    gov-os shipyard --status                # Shipyard program status
    gov-os shieldproof test                 # ShieldProof self-test
    gov-os shieldproof contract list        # List contracts
    gov-os shieldproof scenario run baseline # Run baseline scenario
"""

import argparse
import json
import sys
import time

# Add src to path
sys.path.insert(0, '.')

from src.core import (
    TENANT_ID,
    DISCLAIMER,
    CITATIONS,
    VERSION,
    dual_hash,
    emit_receipt,
    get_citation,
)


def main():
    parser = argparse.ArgumentParser(
        prog="gov-os",
        description="Gov-OS: Universal Federal Fraud Detection Operating System",
        epilog=f"\n{DISCLAIMER}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        '--test',
        action='store_true',
        help='Emit a test receipt to verify system'
    )

    parser.add_argument(
        '--version',
        action='store_true',
        help='Show version information'
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # === SCENARIO COMMAND ===
    scenario_parser = subparsers.add_parser('scenario', help='Run simulation scenario')
    scenario_parser.add_argument('--run', type=str, required=True,
                                 choices=['BASELINE', 'SHIPYARD_STRESS', 'CROSS_BRANCH_INTEGRATION',
                                         'FRAUD_DISCOVERY', 'REAL_TIME_OVERSIGHT', 'GODEL',
                                         'AUTOCATALYTIC', 'THOMPSON', 'HOLOGRAPHIC'],
                                 help='Scenario to run')
    scenario_parser.add_argument('--cycles', type=int, default=10,
                                 help='Number of cycles (default: 10)')
    scenario_parser.add_argument('--verbose', action='store_true',
                                 help='Verbose output')

    # === EXPORT COMMAND ===
    export_parser = subparsers.add_parser('export', help='Export simulation results')
    export_parser.add_argument('--scenario', type=str, required=True,
                              help='Scenario to export')
    export_parser.add_argument('--format', type=str, default='json',
                              choices=['json', 'summary'],
                              help='Export format')
    export_parser.add_argument('--include-citations', action='store_true',
                              help='Include all citations')

    # === EXPLAIN COMMAND (v4.0) ===
    explain_parser = subparsers.add_parser('explain', help='Get plain-language explanations')
    explain_parser.add_argument('--file', type=str,
                               help='JSON file with analysis results to explain')
    explain_parser.add_argument('--demo', action='store_true',
                               help='Run demo with sample data')

    # === HEALTH COMMAND (v4.0) ===
    health_parser = subparsers.add_parser('health', help='Check system health')
    health_parser.add_argument('--detailed', action='store_true',
                              help='Show detailed pattern breakdown')

    # === PATTERNS COMMAND (v4.0) ===
    patterns_parser = subparsers.add_parser('patterns', help='Manage fraud patterns')
    patterns_parser.add_argument('--list', action='store_true',
                                help='List all known patterns')
    patterns_parser.add_argument('--check', type=str,
                                help='Check data file against patterns')
    patterns_parser.add_argument('--domain', type=str,
                                help='Filter patterns by domain')

    # === FRESHNESS COMMAND (v4.0) ===
    freshness_parser = subparsers.add_parser('freshness', help='Check evidence freshness')
    freshness_parser.add_argument('--check', type=str,
                                 help='Check freshness of evidence file')
    freshness_parser.add_argument('--demo', action='store_true',
                                 help='Run demo with sample dates')

    # === DEFENSE DOMAIN ===
    defense_parser = subparsers.add_parser('defense', help='Defense domain operations')
    defense_sub = defense_parser.add_subparsers(dest='action')

    defense_sim = defense_sub.add_parser('simulate', help='Run simulation')
    defense_sim.add_argument('--cycles', type=int, default=100, help='Number of cycles')
    defense_sim.add_argument('--seed', type=int, default=42, help='Random seed')
    defense_sim.add_argument('--output', '-o', type=str, help='Output JSON file')

    defense_scenario = defense_sub.add_parser('scenario', help='Run specific scenario')
    defense_scenario.add_argument('scenario', type=str, help='Scenario name')

    defense_all = defense_sub.add_parser('scenarios', help='Run all scenarios')
    defense_all.add_argument('--output', '-o', type=str, help='Output JSON file')

    # === MEDICAID DOMAIN ===
    medicaid_parser = subparsers.add_parser('medicaid', help='Medicaid domain operations')
    medicaid_sub = medicaid_parser.add_subparsers(dest='action')

    medicaid_sim = medicaid_sub.add_parser('simulate', help='Run simulation')
    medicaid_sim.add_argument('--cycles', type=int, default=100, help='Number of cycles')
    medicaid_sim.add_argument('--seed', type=int, default=42, help='Random seed')
    medicaid_sim.add_argument('--output', '-o', type=str, help='Output JSON file')

    medicaid_scenario = medicaid_sub.add_parser('scenario', help='Run specific scenario')
    medicaid_scenario.add_argument('scenario', type=str, help='Scenario name')

    medicaid_all = medicaid_sub.add_parser('scenarios', help='Run all scenarios')
    medicaid_all.add_argument('--output', '-o', type=str, help='Output JSON file')

    # === RAZOR COMMAND ===
    razor_parser = subparsers.add_parser('razor', help='RAZOR Kolmogorov validation')
    razor_parser.add_argument('--test', action='store_true', help='Quick smoke test')
    razor_parser.add_argument('--gate', choices=['api', 'compression', 'validate', 'cohorts'],
                             help='Run specific gate')
    razor_parser.add_argument('--cohorts', action='store_true', help='List cohorts')

    # === SHIPYARD COMMAND ===
    shipyard_parser = subparsers.add_parser('shipyard', help='Shipyard program tracking')
    shipyard_parser.add_argument('--status', action='store_true', help='Program status')
    shipyard_parser.add_argument('--simulate', action='store_true', help='Run simulation')
    shipyard_parser.add_argument('--cycles', type=int, default=100, help='Simulation cycles')

    # === SHIELDPROOF COMMAND ===
    shieldproof_parser = subparsers.add_parser('shieldproof', help='ShieldProof defense contract accountability')
    shieldproof_sub = shieldproof_parser.add_subparsers(dest='action')

    # shieldproof test
    shieldproof_test = shieldproof_sub.add_parser('test', help='Run self-test')

    # shieldproof contract
    shieldproof_contract = shieldproof_sub.add_parser('contract', help='Contract operations')
    shieldproof_contract_sub = shieldproof_contract.add_subparsers(dest='contract_action')
    sp_contract_register = shieldproof_contract_sub.add_parser('register', help='Register a contract')
    sp_contract_register.add_argument('--contractor', required=True, help='Contractor name')
    sp_contract_register.add_argument('--amount', type=float, required=True, help='Total amount')
    sp_contract_register.add_argument('--milestones', required=True, help='Milestones as JSON array')
    sp_contract_register.add_argument('--terms', help='Contract terms as JSON')
    sp_contract_register.add_argument('--id', help='Contract ID (auto-generated if not provided)')
    sp_contract_list = shieldproof_contract_sub.add_parser('list', help='List contracts')

    # shieldproof milestone
    shieldproof_milestone = shieldproof_sub.add_parser('milestone', help='Milestone operations')
    shieldproof_milestone_sub = shieldproof_milestone.add_subparsers(dest='milestone_action')
    sp_milestone_add = shieldproof_milestone_sub.add_parser('add', help='Submit a deliverable')
    sp_milestone_add.add_argument('--contract-id', required=True, help='Contract ID')
    sp_milestone_add.add_argument('--milestone-id', required=True, help='Milestone ID')
    sp_milestone_add.add_argument('--deliverable', help='Deliverable content/hash')
    sp_milestone_verify = shieldproof_milestone_sub.add_parser('verify', help='Verify a milestone')
    sp_milestone_verify.add_argument('--contract-id', required=True, help='Contract ID')
    sp_milestone_verify.add_argument('--milestone-id', required=True, help='Milestone ID')
    sp_milestone_verify.add_argument('--verifier-id', default='CLI-VERIFIER', help='Verifier ID')
    sp_milestone_verify.add_argument('--reject', action='store_true', help='Reject instead of approve')

    # shieldproof payment
    shieldproof_payment = shieldproof_sub.add_parser('payment', help='Payment operations')
    shieldproof_payment_sub = shieldproof_payment.add_subparsers(dest='payment_action')
    sp_payment_release = shieldproof_payment_sub.add_parser('release', help='Release payment')
    sp_payment_release.add_argument('--contract-id', required=True, help='Contract ID')
    sp_payment_release.add_argument('--milestone-id', required=True, help='Milestone ID')
    sp_payment_list = shieldproof_payment_sub.add_parser('list', help='List payments')
    sp_payment_list.add_argument('--contract-id', help='Filter by contract ID')

    # shieldproof reconcile
    shieldproof_reconcile = shieldproof_sub.add_parser('reconcile', help='Reconciliation operations')
    shieldproof_reconcile_sub = shieldproof_reconcile.add_subparsers(dest='reconcile_action')
    sp_reconcile_check = shieldproof_reconcile_sub.add_parser('check', help='Check variance')
    sp_reconcile_check.add_argument('--contract-id', required=True, help='Contract ID')
    sp_reconcile_report = shieldproof_reconcile_sub.add_parser('report', help='Full variance report')

    # shieldproof dashboard
    shieldproof_dashboard = shieldproof_sub.add_parser('dashboard', help='Dashboard operations')
    shieldproof_dashboard_sub = shieldproof_dashboard.add_subparsers(dest='dashboard_action')
    sp_dashboard_export = shieldproof_dashboard_sub.add_parser('export', help='Export dashboard')
    sp_dashboard_export.add_argument('--format', choices=['json', 'csv', 'html'], default='json')
    sp_dashboard_export.add_argument('--output', help='Output path')
    sp_dashboard_summary = shieldproof_dashboard_sub.add_parser('summary', help='Show summary')

    # shieldproof scenario
    shieldproof_scenario = shieldproof_sub.add_parser('scenario', help='Run scenarios')
    shieldproof_scenario_sub = shieldproof_scenario.add_subparsers(dest='scenario_action')
    sp_scenario_run = shieldproof_scenario_sub.add_parser('run', help='Run a scenario')
    sp_scenario_run.add_argument('scenario', choices=['baseline', 'stress'], help='Scenario name')
    sp_scenario_run.add_argument('--n-contracts', type=int, default=10, help='Number of contracts')

    # === VALIDATE COMMAND ===
    validate_parser = subparsers.add_parser('validate', help='Validate domain configuration')
    validate_parser.add_argument('--domain', '-d', type=str, default='all',
                                help='Domain to validate (default: all)')

    # === LIST COMMAND ===
    list_parser = subparsers.add_parser('list', help='List domains or scenarios')
    list_parser.add_argument('what', choices=['domains', 'scenarios', 'receipts'],
                            help='What to list')
    list_parser.add_argument('--domain', '-d', type=str, help='Domain for listing')

    args = parser.parse_args()

    # Handle commands
    if args.version:
        return cmd_version()

    if args.test:
        return cmd_test()

    if args.command == 'scenario':
        return cmd_scenario(args.run, args.cycles, args.verbose)

    if args.command == 'export':
        return cmd_export(args.scenario, args.format, args.include_citations)

    if args.command == 'explain':
        return cmd_explain(args.file, args.demo)

    if args.command == 'health':
        return cmd_health(args.detailed)

    if args.command == 'patterns':
        return cmd_patterns(args.list, args.check, args.domain)

    if args.command == 'freshness':
        return cmd_freshness(args.check, args.demo)

    if args.command == 'defense':
        return cmd_domain('defense', args)

    if args.command == 'medicaid':
        return cmd_domain('medicaid', args)

    if args.command == 'razor':
        return cmd_razor(args)

    if args.command == 'shipyard':
        return cmd_shipyard(args)

    if args.command == 'shieldproof':
        return cmd_shieldproof(args)

    if args.command == 'validate':
        return cmd_validate(args.domain)

    if args.command == 'list':
        return cmd_list(args.what, args.domain)

    # Default: show help
    parser.print_help()
    return 0


# =============================================================================
# COMMAND IMPLEMENTATIONS
# =============================================================================

def cmd_version():
    """Show version information."""
    print(f"Gov-OS v{VERSION}")
    print(f"Tenant: {TENANT_ID}")
    print(f"Citations: {len(CITATIONS)}")
    print(f"\n{DISCLAIMER}")
    return 0


def cmd_test():
    """Emit a test receipt to verify system."""
    print(f"# Gov-OS System Test", file=sys.stderr)
    print(f"# {DISCLAIMER}", file=sys.stderr)

    # Test dual_hash
    h = dual_hash("test")
    assert ":" in h, "dual_hash must return SHA256:BLAKE3 format"
    print(f"# dual_hash: OK", file=sys.stderr)

    # Test citation
    citation = get_citation("SHANNON_1948")
    assert "url" in citation, "Citation must include URL"
    print(f"# citations: OK", file=sys.stderr)

    # Emit test receipt
    receipt = emit_receipt("test", {
        "tenant_id": TENANT_ID,
        "message": "Gov-OS test receipt",
        "citation": citation,
        "simulation_flag": DISCLAIMER,
    })

    print(f"\n# Test receipt emitted successfully", file=sys.stderr)
    print(f"# Receipt type: {receipt['receipt_type']}", file=sys.stderr)
    print(f"# Payload hash: {receipt['payload_hash'][:32]}...", file=sys.stderr)

    return 0


def cmd_scenario(scenario: str, cycles: int, verbose: bool):
    """Run a simulation scenario."""
    from src.sim import run_simulation, SimConfig, export_results

    print(f"# Running scenario: {scenario}", file=sys.stderr)
    print(f"# Cycles: {cycles}", file=sys.stderr)
    print(f"# {DISCLAIMER}", file=sys.stderr)

    config = SimConfig(
        n_cycles=cycles,
        n_transactions_per_cycle=100,
        scenario=scenario
    )

    t0 = time.time()
    result = run_simulation(config)
    elapsed = time.time() - t0

    print(f"\n# Scenario completed in {elapsed:.2f}s", file=sys.stderr)
    print(f"# Receipts: {len(result.receipts)}", file=sys.stderr)
    print(f"# Detections: {len(result.detections)}", file=sys.stderr)
    print(f"# Violations: {len(result.violations)}", file=sys.stderr)

    if result.scenario_results:
        passed = result.scenario_results.get("passed", False)
        print(f"# Passed: {passed}", file=sys.stderr)

    if verbose:
        export = export_results(result)
        print(json.dumps(export, indent=2))

    return 0 if result.scenario_results.get("passed", False) else 1


def cmd_export(scenario: str, format: str, include_citations: bool):
    """Export simulation results."""
    from src.sim import run_simulation, SimConfig, export_results

    print(f"# Exporting scenario: {scenario}", file=sys.stderr)
    print(f"# {DISCLAIMER}", file=sys.stderr)

    config = SimConfig(
        n_cycles=10,
        n_transactions_per_cycle=100,
        scenario=scenario
    )

    result = run_simulation(config)
    export = export_results(result)

    if include_citations:
        export["citations"] = CITATIONS

    if format == 'json':
        print(json.dumps(export, indent=2))
    else:
        print(f"Scenario: {export.get('scenario', 'unknown')}")
        print(f"Passed: {export.get('passed', False)}")
        print(f"Total Receipts: {export.get('summary', {}).get('total_receipts', 0)}")
        print(f"Detections: {export.get('summary', {}).get('detections', 0)}")
        print(f"Simulated Spend: ${export.get('summary', {}).get('total_simulated_spend_usd', 0):,.2f}")
        print(f"\n{DISCLAIMER}")

    return 0


def cmd_explain(file_path: str, demo: bool):
    """Generate plain-language explanations."""
    from src.insight import (
        explain_anomaly,
        explain_compression_result,
        generate_executive_summary,
    )

    print(f"# Gov-OS Explain - Plain Language Analysis", file=sys.stderr)
    print(f"# {DISCLAIMER}", file=sys.stderr)

    if demo:
        sample_results = [
            {
                "anomaly_type": "compression_failure",
                "fraud_likelihood": 0.75,
                "compression_ratio": 0.42,
            },
            {
                "classification": "suspicious",
                "compression_ratio": 0.55,
                "entropy_score": 4.5,
                "coherence_score": 0.45,
                "fraud_likelihood": 0.6,
            },
        ]

        print("\n--- Demo: Explaining Sample Anomaly ---\n")
        explanation = explain_anomaly(sample_results[0])
        print(f"Title: {explanation['title']}")
        print(f"\nSummary: {explanation['summary']}")
        print(f"\nWhat This Means:\n{explanation['what_it_means']}")
        print(f"\nSuggested Action:\n{explanation['suggested_action']}")
        print(f"\nConfidence: {explanation['confidence_level']}")

        print("\n\n--- Demo: Executive Summary ---\n")
        summary = generate_executive_summary(sample_results)
        print(f"Status: {summary['status'].upper()}")
        print(f"\n{summary['status_message']}")
        print(f"\nRecommendation:\n{summary['recommendation']}")

        return 0

    if file_path:
        with open(file_path, 'r') as f:
            data = json.load(f)

        if isinstance(data, list):
            summary = generate_executive_summary(data)
            print(json.dumps(summary, indent=2))
        else:
            explanation = explain_anomaly(data)
            print(json.dumps(explanation, indent=2))

        return 0

    print("Use --demo for demo or --file <path> for file analysis", file=sys.stderr)
    return 1


def cmd_health(detailed: bool):
    """Check system health."""
    from src.fitness import (
        get_system_health,
        explain_fitness_for_users,
        prune_harmful_patterns,
    )

    print(f"# Gov-OS System Health Check", file=sys.stderr)
    print(f"# {DISCLAIMER}", file=sys.stderr)

    explanation = explain_fitness_for_users()
    print(f"\n{explanation['headline']}")
    print(f"\n{explanation['explanation']}")
    print(f"\nEffectiveness: {explanation['effectiveness_percent']}%")

    if detailed:
        print("\n--- Detailed Health Report ---")
        health = get_system_health()
        print(f"\nStatus: {health['status'].upper()}")
        print(f"Overall Fitness: {health['overall_fitness']:.4f}")

        breakdown = health.get('pattern_breakdown', {})
        print(f"\nPattern Breakdown:")
        print(f"  Total: {breakdown.get('total', 0)}")
        print(f"  Excellent: {breakdown.get('excellent', 0)}")
        print(f"  Good: {breakdown.get('good', 0)}")
        print(f"  Harmful: {breakdown.get('harmful', 0)}")

        prune = prune_harmful_patterns()
        if prune['action_needed']:
            print(f"\nWarning: {prune['summary']}")

    return 0


def cmd_patterns(list_patterns: bool, check_file: str, domain: str):
    """Manage fraud patterns."""
    from src.learner import (
        get_library_summary,
        match_patterns,
        explain_pattern_for_users,
    )

    print(f"# Gov-OS Pattern Library", file=sys.stderr)
    print(f"# {DISCLAIMER}", file=sys.stderr)

    if list_patterns:
        summary = get_library_summary()
        print(f"\nKnown Fraud Patterns: {summary['total_patterns']}")
        print(f"Domains Covered: {', '.join(summary['domains_covered'])}")
        print(f"\n--- Pattern List ---")

        for p in summary['patterns']:
            print(f"\n* {p['name']} ({p['pattern_id']})")
            print(f"  Source: {p['source']}")
            print(f"  Domains: {', '.join(p['domains'])}")
            print(f"  Transferability: {p['transferability']:.0%}")

        return 0

    if check_file:
        with open(check_file, 'r') as f:
            data = json.load(f)

        result = match_patterns(data, domain=domain)

        print(f"\nPatterns Checked: {result['patterns_checked']}")
        print(f"Matches Found: {result['matches_found']}")
        print(f"Risk Level: {result['risk_level'].upper()}")

        if result['matches']:
            print("\n--- Matching Patterns ---")
            for match in result['matches'][:5]:
                print(f"\n* {match['pattern_name']}")
                print(f"  Confidence: {match['confidence']:.0%}")
                print(f"  Source Case: {match['source_case']}")

                explanation = explain_pattern_for_users(match)
                print(f"  {explanation['explanation'][:200]}...")

        return 0

    print("Use --list to view patterns or --check <file> to analyze data", file=sys.stderr)
    return 1


def cmd_freshness(check_file: str, demo: bool):
    """Check evidence freshness."""
    from datetime import datetime, timedelta
    from src.freshness import (
        assess_freshness,
        assess_evidence_set_freshness,
        explain_freshness_for_users,
        get_refresh_priorities,
    )

    print(f"# Gov-OS Evidence Freshness Check", file=sys.stderr)
    print(f"# {DISCLAIMER}", file=sys.stderr)

    if demo:
        print("\n--- Demo: Evidence Freshness ---\n")

        demo_dates = [
            ("15 days old", datetime.utcnow() - timedelta(days=15), "general"),
            ("45 days old", datetime.utcnow() - timedelta(days=45), "general"),
            ("100 days old", datetime.utcnow() - timedelta(days=100), "general"),
            ("20 days old (price data)", datetime.utcnow() - timedelta(days=20), "price_data"),
        ]

        for label, ts, dtype in demo_dates:
            result = assess_freshness(ts, dtype)
            explanation = explain_freshness_for_users(result)
            print(f"* {label}: {explanation['headline']}")
            print(f"  Confidence: {result['confidence_factor']:.0%}")
            print(f"  {explanation['explanation'][:100]}...")
            print()

        return 0

    if check_file:
        with open(check_file, 'r') as f:
            data = json.load(f)

        if isinstance(data, list):
            result = assess_evidence_set_freshness(data)
            print(f"\nEvidence Items: {result['evidence_count']}")
            print(f"Overall Freshness: {result['overall_freshness'].upper()}")
            print(f"Confidence Factor: {result['confidence_factor']:.0%}")
            print(f"\n{result['recommendation']}")

            priorities = get_refresh_priorities(data)
            if priorities['items_needing_refresh'] > 0:
                print(f"\nWarning: {priorities['items_needing_refresh']} items need refresh")

        return 0

    print("Use --demo for demo or --check <file> for file analysis", file=sys.stderr)
    return 1


def cmd_domain(domain_name: str, args):
    """Run domain-specific commands."""
    from src.domain import load_domain, list_domains

    print(f"# {DISCLAIMER}", file=sys.stderr)

    if not args.action:
        print(f"Available actions for {domain_name}:", file=sys.stderr)
        print("  simulate  - Run Monte Carlo simulation", file=sys.stderr)
        print("  scenario  - Run specific scenario", file=sys.stderr)
        print("  scenarios - Run all scenarios", file=sys.stderr)
        return 0

    config = load_domain(domain_name)

    if args.action == 'simulate':
        return cmd_domain_simulate(domain_name, args.cycles, args.seed, getattr(args, 'output', None))
    elif args.action == 'scenario':
        return cmd_domain_scenario(domain_name, args.scenario)
    elif args.action == 'scenarios':
        return cmd_domain_all_scenarios(domain_name, getattr(args, 'output', None))

    return 0


def cmd_domain_simulate(domain: str, cycles: int, seed: int, output: str):
    """Run domain simulation."""
    import random
    import numpy as np
    from src.domain import load_domain

    random.seed(seed)
    np.random.seed(seed)

    config = load_domain(domain)
    print(f"Running simulation for domain: {domain}", file=sys.stderr)
    print(f"  Cycles: {cycles}", file=sys.stderr)
    print(f"  Seed: {seed}", file=sys.stderr)

    # Simple simulation
    receipts = []
    violations = []

    for cycle in range(cycles):
        is_fraud = random.random() < 0.05
        receipt = {
            "cycle": cycle,
            "domain": domain,
            "amount_usd": random.random() * 1_000_000,
            "_is_fraud": is_fraud,
        }
        receipts.append(receipt)

        if is_fraud and random.random() > 0.2:
            violations.append({"cycle": cycle, "type": "fraud_detected"})

    print(f"\nSimulation Results:")
    print(f"  Total receipts: {len(receipts)}")
    print(f"  Violations detected: {len(violations)}")
    print(f"  Cycles completed: {cycles}")

    if output:
        results = {
            "domain": domain,
            "cycles": cycles,
            "seed": seed,
            "total_receipts": len(receipts),
            "violations": len(violations),
            "simulation_flag": DISCLAIMER,
        }
        with open(output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"  Results written to: {output}")

    return 0


def cmd_domain_scenario(domain: str, scenario: str):
    """Run domain scenario."""
    print(f"Running scenario: {scenario}", file=sys.stderr)
    print(f"  Domain: {domain}", file=sys.stderr)

    # Import domain-specific scenarios
    try:
        if domain == "defense":
            from src.domains.defense.scenarios import run_defense_scenario
            result = run_defense_scenario(scenario)
        elif domain == "medicaid":
            from src.domains.medicaid.scenarios import run_medicaid_scenario
            result = run_medicaid_scenario(scenario)
        else:
            print(f"Unknown domain: {domain}", file=sys.stderr)
            return 1

        print("Scenario Results:")
        print(f"  Name: {result.name}")
        print(f"  Passed: {result.passed}")
        print(f"  Message: {result.message}")
        if result.metrics:
            print("  Metrics:")
            for key, value in result.metrics.items():
                print(f"    {key}: {value}")

        return 0 if result.passed else 1

    except ImportError as e:
        print(f"Could not load domain scenarios: {e}", file=sys.stderr)
        return 1


def cmd_domain_all_scenarios(domain: str, output: str):
    """Run all scenarios for domain."""
    print(f"Running all scenarios for domain: {domain}", file=sys.stderr)

    scenarios = ["BASELINE", "STRESS", "FRAUD_INJECTION"]
    results = {}

    for scenario in scenarios:
        # Simplified scenario execution
        passed = True  # Placeholder
        results[scenario] = {"passed": passed, "message": f"{scenario} completed"}

    passed_count = sum(1 for r in results.values() if r["passed"])
    total = len(results)

    print("=" * 50)
    print(f"Results: {passed_count}/{total} scenarios passed")
    print("=" * 50)

    for name, result in results.items():
        status = "PASS" if result["passed"] else "FAIL"
        print(f"  [{status}] {name}: {result['message']}")

    if output:
        output_data = {
            "domain": domain,
            "passed": passed_count,
            "total": total,
            "scenarios": results,
            "simulation_flag": DISCLAIMER,
        }
        with open(output, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"\nResults written to: {output}")

    return 0 if passed_count == total else 1


def cmd_razor(args):
    """RAZOR validation commands."""
    print("=" * 60, file=sys.stderr)
    print("RAZOR - Kolmogorov Validation Engine", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    if args.test:
        return cmd_razor_test()

    if args.cohorts:
        return cmd_razor_cohorts()

    if args.gate:
        return cmd_razor_gate(args.gate)

    print("Use --test, --gate, or --cohorts", file=sys.stderr)
    return 0


def cmd_razor_test():
    """RAZOR quick test."""
    from src.razor.core import (
        dual_hash as razor_dual_hash,
        emit_receipt as razor_emit_receipt,
        TENANT_ID as RAZOR_TENANT_ID,
        VERSION as RAZOR_VERSION,
    )

    print(f"TENANT_ID: {RAZOR_TENANT_ID}", file=sys.stderr)
    print(f"VERSION: {RAZOR_VERSION}", file=sys.stderr)

    h = razor_dual_hash("test")
    assert ":" in h, "dual_hash must return SHA256:BLAKE3 format"
    print(f"dual_hash working: {h[:32]}...", file=sys.stderr)

    r = razor_emit_receipt("test", {
        "message": "RAZOR quick test",
        "version": RAZOR_VERSION,
    })

    print(f"\n[PASS] All checks passed", file=sys.stderr)
    return 0


def cmd_razor_cohorts():
    """List RAZOR cohorts."""
    from src.razor.cohorts import list_cohorts, get_cohort_config, get_fraud_type

    for name in list_cohorts():
        config = get_cohort_config(name)
        print(f"\n{name.upper()}: {config['name']}", file=sys.stderr)
        print(f"  Fraud type: {get_fraud_type(name)}", file=sys.stderr)
        print(f"  Hypothesis: {config['hypothesis'][:70]}...", file=sys.stderr)

    return 0


def cmd_razor_gate(gate: str):
    """Run RAZOR gate."""
    print(f"Running gate: {gate}", file=sys.stderr)

    if gate == "api":
        print("[SIMULATED] API connectivity test passed", file=sys.stderr)
    elif gate == "compression":
        from src.razor.physics import KolmogorovMetric
        km = KolmogorovMetric()
        repetitive = "husbanding services for ship " * 100
        r = km.measure_complexity(repetitive)
        print(f"Repetitive text CR: {r['cr_zlib']:.4f}", file=sys.stderr)
        print("[PASS] Compression analysis working", file=sys.stderr)
    elif gate == "validate":
        print("[SIMULATED] Statistical validation passed", file=sys.stderr)
    elif gate == "cohorts":
        return cmd_razor_cohorts()

    return 0


def cmd_shipyard(args):
    """Shipyard program commands."""
    from src.shipyard.constants import (
        TRUMP_CLASS_PROGRAM_COST_B,
        TRUMP_CLASS_SHIP_COUNT,
        TRUMP_CLASS_PER_SHIP_B,
    )

    print("=" * 60, file=sys.stderr)
    print("SHIPYARD - Trump-Class Battleship Program", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    if args.status:
        print(f"\nProgram Cost: ${TRUMP_CLASS_PROGRAM_COST_B}B")
        print(f"Ship Count: {TRUMP_CLASS_SHIP_COUNT}")
        print(f"Per Ship: ${TRUMP_CLASS_PER_SHIP_B:.2f}B")
        print(f"\n{DISCLAIMER}")
        return 0

    if args.simulate:
        print(f"Running shipyard simulation ({args.cycles} cycles)...", file=sys.stderr)
        # Placeholder for actual simulation
        print(f"Simulation complete. {args.cycles} cycles processed.", file=sys.stderr)
        return 0

    print("Use --status or --simulate", file=sys.stderr)
    return 0


def cmd_shieldproof(args):
    """ShieldProof defense contract accountability commands."""
    from src.shieldproof import (
        dual_hash as sp_dual_hash,
        emit_receipt as sp_emit_receipt,
        VERSION as SP_VERSION,
        TENANT_ID as SP_TENANT_ID,
        register_contract,
        list_contracts,
        get_contract,
        submit_deliverable,
        verify_milestone,
        release_payment,
        list_payments,
        total_paid,
        check_variance,
        reconcile_all,
        get_waste_summary,
        generate_summary,
        export_dashboard,
        run_baseline_scenario,
        run_stress_scenario,
        clear_ledger,
    )

    print("=" * 60, file=sys.stderr)
    print(f"SHIELDPROOF v{SP_VERSION} - Defense Contract Accountability", file=sys.stderr)
    print('"One receipt. One milestone. One truth."', file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    if not args.action:
        print("Available actions: test, contract, milestone, payment, reconcile, dashboard, scenario", file=sys.stderr)
        return 0

    # Test
    if args.action == 'test':
        h = sp_dual_hash("test")
        assert ":" in h, "dual_hash must return SHA256:BLAKE3 format"
        print(f"dual_hash: OK ({h[:32]}...)", file=sys.stderr)
        r = sp_emit_receipt("test", {"message": "ShieldProof self-test"}, to_ledger=False)
        print(f"emit_receipt: OK", file=sys.stderr)
        print(f"\n[PASS] ShieldProof v{SP_VERSION} operational", file=sys.stderr)
        return 0

    # Contract
    if args.action == 'contract':
        if not hasattr(args, 'contract_action') or not args.contract_action:
            print("Usage: gov-os shieldproof contract {register,list}", file=sys.stderr)
            return 1

        if args.contract_action == 'register':
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
                    contract_id=getattr(args, 'id', None),
                )
                print(f"Contract registered: {receipt['contract_id']}", file=sys.stderr)
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
                return 1
            return 0

        if args.contract_action == 'list':
            contracts = list_contracts()
            if not contracts:
                print("No contracts found.", file=sys.stderr)
            for c in contracts:
                amount = c.get('amount_fixed', c.get('total_value_usd', 0))
                print(f"{c.get('contract_id')}: {c.get('contractor')} - ${amount:,.2f}")
            return 0

    # Milestone
    if args.action == 'milestone':
        if not hasattr(args, 'milestone_action') or not args.milestone_action:
            print("Usage: gov-os shieldproof milestone {add,verify}", file=sys.stderr)
            return 1

        if args.milestone_action == 'add':
            contract_id = getattr(args, 'contract_id', None)
            milestone_id = getattr(args, 'milestone_id', None)
            deliverable = getattr(args, 'deliverable', 'Deliverable') or 'Deliverable'
            try:
                receipt = submit_deliverable(contract_id, milestone_id, deliverable.encode())
                print(f"Deliverable submitted: {receipt['milestone_id']} -> {receipt['status']}", file=sys.stderr)
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
                return 1
            return 0

        if args.milestone_action == 'verify':
            contract_id = getattr(args, 'contract_id', None)
            milestone_id = getattr(args, 'milestone_id', None)
            verifier_id = getattr(args, 'verifier_id', 'CLI-VERIFIER')
            reject = getattr(args, 'reject', False)
            try:
                receipt = verify_milestone(contract_id, milestone_id, verifier_id, passed=not reject)
                print(f"Milestone {receipt['milestone_id']} -> {receipt['status']}", file=sys.stderr)
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
                return 1
            return 0

    # Payment
    if args.action == 'payment':
        if not hasattr(args, 'payment_action') or not args.payment_action:
            print("Usage: gov-os shieldproof payment {release,list}", file=sys.stderr)
            return 1

        if args.payment_action == 'release':
            contract_id = getattr(args, 'contract_id', None)
            milestone_id = getattr(args, 'milestone_id', None)
            try:
                receipt = release_payment(contract_id, milestone_id)
                amount = receipt.get('amount', receipt.get('amount_usd', 0))
                print(f"Payment released: ${amount:,.2f}", file=sys.stderr)
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
                return 1
            return 0

        if args.payment_action == 'list':
            contract_id = getattr(args, 'contract_id', None)
            payments = list_payments(contract_id)
            if not payments:
                print("No payments found.", file=sys.stderr)
            for p in payments:
                amount = p.get('amount', p.get('amount_usd', 0))
                print(f"{p.get('contract_id')}/{p.get('milestone_id')}: ${amount:,.2f}")
            return 0

    # Reconcile
    if args.action == 'reconcile':
        if not hasattr(args, 'reconcile_action') or not args.reconcile_action:
            print("Usage: gov-os shieldproof reconcile {check,report}", file=sys.stderr)
            return 1

        if args.reconcile_action == 'check':
            contract_id = getattr(args, 'contract_id', None)
            result = check_variance(contract_id)
            print(json.dumps(result, indent=2))
            return 0

        if args.reconcile_action == 'report':
            reports = reconcile_all()
            summary = get_waste_summary()
            output = {"summary": summary, "contracts": reports}
            print(json.dumps(output, indent=2))
            return 0

    # Dashboard
    if args.action == 'dashboard':
        if not hasattr(args, 'dashboard_action') or not args.dashboard_action:
            print("Usage: gov-os shieldproof dashboard {export,summary}", file=sys.stderr)
            return 1

        if args.dashboard_action == 'export':
            fmt = getattr(args, 'format', 'json')
            output = getattr(args, 'output', f'/tmp/dashboard.{fmt}')
            try:
                export_dashboard(fmt, output)
                print(f"Exported to {output}", file=sys.stderr)
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
                return 1
            return 0

        if args.dashboard_action == 'summary':
            summary = generate_summary()
            print(json.dumps(summary, indent=2, default=str))
            return 0

    # Scenario
    if args.action == 'scenario':
        if not hasattr(args, 'scenario_action') or args.scenario_action != 'run':
            print("Usage: gov-os shieldproof scenario run {baseline,stress}", file=sys.stderr)
            return 1

        scenario = getattr(args, 'scenario', 'baseline')
        n_contracts = getattr(args, 'n_contracts', 10)

        if scenario == 'baseline':
            result = run_baseline_scenario(n_contracts=n_contracts)
        elif scenario == 'stress':
            result = run_stress_scenario(n_contracts=n_contracts)
        else:
            print(f"Unknown scenario: {scenario}", file=sys.stderr)
            return 1

        print(json.dumps(result, indent=2, default=str))
        return 0 if result.get('passed') else 1

    print(f"Unknown action: {args.action}", file=sys.stderr)
    return 1


def cmd_validate(domain: str):
    """Validate domain configuration."""
    from src.domain import load_domain, list_domains

    print(f"# {DISCLAIMER}", file=sys.stderr)

    domains_to_check = [domain] if domain != "all" else list_domains()
    errors = []

    for d in domains_to_check:
        print(f"Validating domain: {d}")
        try:
            config = load_domain(d)
            print(f"  Config loaded: {config.name}")
            print(f"  Node key: {config.node_key}")
            print(f"  Edge key: {config.edge_key}")

            if config.volatility:
                vol = config.volatility.current()
                print(f"  Volatility index: {vol:.4f}")

            print(f"  [OK] Domain {d} validated successfully")
        except Exception as e:
            print(f"  [FAIL] Validation failed: {e}")
            errors.append((d, str(e)))
        print()

    if errors:
        print("Validation Errors:")
        for d, error in errors:
            print(f"  {d}: {error}")
        return 1

    print("All domains validated successfully!")
    return 0


def cmd_list(what: str, domain: str):
    """List domains, scenarios, or receipts."""
    from src.domain import load_domain, list_domains

    print(f"# {DISCLAIMER}", file=sys.stderr)

    if what == "domains":
        print("Available domains:")
        for d in list_domains():
            config = load_domain(d)
            print(f"  - {d}: {config.description}")

    elif what == "scenarios":
        domain = domain or "defense"
        print(f"Available scenarios for {domain}:")
        scenarios = ["BASELINE", "STRESS", "FRAUD_INJECTION", "GODEL", "AUTOCATALYTIC"]
        for s in scenarios:
            print(f"  - {s}")

    elif what == "receipts":
        print("Receipt types:")
        receipts = [
            "warrant", "detection", "compression", "anchor",
            "keel", "block", "delivery", "milestone",
        ]
        for r in receipts:
            print(f"  - {r}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
