# ShieldProof v2.1 Specification

**"One receipt. One milestone. One truth."**

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

## Overview

ShieldProof v2.1 is the minimal viable truth for defense accountability. It strips away physics theater and focuses on what matters: receipts that prove payment follows verification.

## Directory Structure (v2.1 Modular)

```
src/shieldproof/
├── __init__.py          # Main exports (backward compatible with v2.0)
├── spec.md              # This document
├── core/                # Shared infrastructure
│   ├── __init__.py
│   ├── constants.py     # VERSION, TENANT_ID, RECEIPT_TYPES, etc.
│   ├── utils.py         # dual_hash, merkle, StopRule
│   ├── receipt.py       # emit_receipt, validate_receipt
│   ├── ledger.py        # load_ledger, query_receipts, clear_ledger
│   ├── anchor.py        # anchor_receipt, anchor_chain
│   └── gate.py          # check_t2h, check_t24h, check_t48h
├── contract/            # Contract registration
│   ├── __init__.py
│   ├── config.py        # MODULE_ID, CONTRACT_TYPES
│   ├── register.py      # register_contract, get_contract, list_contracts
│   └── receipts.py      # emit_contract_receipt
├── milestone/           # Deliverable tracking
│   ├── __init__.py
│   ├── config.py        # MODULE_ID, MILESTONE_STATES
│   ├── verify.py        # submit_deliverable, verify_milestone
│   └── receipts.py      # emit_milestone_receipt
├── payment/             # Payment release
│   ├── __init__.py
│   ├── config.py        # MODULE_ID, REQUIRE_VERIFIED_MILESTONE
│   ├── release.py       # release_payment (STOPRULE enforced)
│   └── receipts.py      # emit_payment_receipt
├── reconcile/           # Variance tracking
│   ├── __init__.py
│   ├── config.py        # VARIANCE_THRESHOLD, VARIANCE_CRITICAL
│   ├── variance.py      # check_variance, reconcile_all
│   └── receipts.py      # emit_variance_receipt
├── dashboard/           # Public audit trail
│   ├── __init__.py
│   ├── config.py        # Dashboard configuration
│   ├── export.py        # export_dashboard, generate_summary
│   └── receipts.py      # emit_dashboard_receipt
└── scenarios/           # Integration tests
    ├── __init__.py
    ├── baseline.py      # run_baseline_scenario (standard flow)
    └── stress.py        # run_stress_scenario (throughput test)
```

## Components

1. **Immutable Receipts** - contract, milestone, payment, variance, dashboard, anchor, anomaly
2. **Automated Reconciliation** - spend vs deliverable matching with variance tracking
3. **Public Audit Trail** - aggregate dashboard with health scoring
4. **Scenarios** - baseline and stress tests for validation

## Receipt Types (v2.1)

| Type | Purpose | Key Fields |
|------|---------|------------|
| `contract` | Register fixed-price contract | contract_id, contractor, amount_fixed, milestones[], terms_hash |
| `milestone` | Track deliverable verification | contract_id, milestone_id, deliverable_hash, status, verifier_id |
| `payment` | Release payment on verification | contract_id, milestone_id, amount, payment_hash, released_at |
| `variance` | Contract budget tracking | contract_id, expected_usd, actual_usd, variance_pct, status |
| `dashboard` | Dashboard export | export_format, output_path, contract_count, total_value_usd |
| `anchor` | Merkle tree anchor | merkle_root, receipt_count, receipts_hash |
| `anomaly` | Stoprule violation | metric, delta, action |

## Milestone States

```
PENDING → DELIVERED → VERIFIED → PAID
                  ↘ DISPUTED
```

## Variance Thresholds

| Level | Threshold | Action |
|-------|-----------|--------|
| Warning | > 5% | Flag for review |
| Critical | > 15% | Immediate escalation |

## SLOs (v2.1)

| Operation | Target |
|-----------|--------|
| Contract registration | ≤ 100ms |
| Milestone verification | ≤ 150ms |
| Payment release | ≤ 200ms |
| Dashboard generation | ≤ 2s |
| Receipt emission | ≤ 10ms |

## Stoprules

| Rule | Trigger | Action |
|------|---------|--------|
| stoprule_duplicate_contract | contract_id exists | Raise StopRule |
| stoprule_invalid_amount | amount ≤ 0 or milestones don't sum | Raise StopRule |
| stoprule_unknown_contract | contract_id not found | Raise StopRule |
| stoprule_unknown_milestone | milestone_id not in contract | Raise StopRule |
| stoprule_already_verified | milestone already VERIFIED/PAID | Raise StopRule |
| stoprule_unverified_milestone | payment on non-VERIFIED | **HALT** |
| stoprule_already_paid | milestone already PAID | Raise StopRule |
| stoprule_amount_mismatch | payment ≠ milestone amount | Raise StopRule |

## Critical STOPRULE

**PAYMENT BLOCKED IF MILESTONE NOT VERIFIED**

This is the core enforcement mechanism. The `release_payment` function will raise `StopRuleException` if the milestone is not in VERIFIED state.

## Hash Strategy

```
SHA256:BLAKE3 (dual-hash per CLAUDEME §8)
```

## Gate Timelines

| Gate | Deadline | Requirements |
|------|----------|--------------|
| T+2h | Skeleton | Files exist, imports work, dual_hash format |
| T+24h | MVP | Baseline scenario passes, tests pass |
| T+48h | Hardened | Stress scenario passes, STOPRULE enforced |

## The SpaceX Model

Fixed-price contracts where payment follows verification. A public dashboard showing taxpayers exactly where their money went.

*No receipt → not real. Ship at T+24h or kill.*
