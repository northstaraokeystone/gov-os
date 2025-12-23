# WarrantProof Specification v4.0

**⚠️ SIMULATION ONLY - NOT REAL DoD DATA - FOR RESEARCH ONLY ⚠️**

---

## System Purpose

WarrantProof detects federal procurement fraud by measuring data complexity. Legitimate markets are chaotic (high entropy). Fraud requires coordination, which creates patterns (low entropy). Low entropy data compresses better than legitimate data.

**Core Principle:** Compression ratio reveals fraud.

---

## Architecture Summary

| Version | Focus | Key Innovation |
|---------|-------|----------------|
| v1.0 | Detection | Receipt chains + Merkle anchors |
| v2.0 | Physics | Entropy-based pattern emergence |
| v3.0 OMEGA | Certainty | Kolmogorov complexity + ZK proofs |
| v4.0 | Usability | Plain-language explanations + self-improvement |
| Shipyard | Application | Trump-class battleship program tracking |

---

## Detection Thresholds

| Metric | Fraud Threshold | Legitimate Threshold | Source |
|--------|-----------------|---------------------|--------|
| Kolmogorov Complexity | K(x) < 0.65 | K(x) ≥ 0.75 | Compression physics |
| Compression Ratio | < 0.50 | ≥ 0.80 | Shannon 1948 |
| RAF Cycle Length | 3-5 entities | N/A | Network topology |
| ZKP Proof Size | 22 KB constant | N/A | Mina IVC |
| Evidence Freshness | > 90 days = stale | < 30 days = fresh | v4.0 |
| Pattern Confidence | > 0.50 match | N/A | v4.0 learner |

---

## Module Inventory

### Core Detection (src/)

| Module | Lines | Purpose |
|--------|-------|---------|
| core.py | 602 | Hash, receipts, citations, constants |
| compress.py | 642 | Entropy compression analysis |
| detect.py | 680 | Multi-stage anomaly detection |
| kolmogorov.py | 339 | Algorithmic complexity |
| zkp.py | 438 | Zero-knowledge proofs |
| raf.py | 510 | Network cycle detection |
| holographic.py | 810 | Boundary-only detection |
| thompson.py | 474 | Bayesian audit sampling |

### v4.0 User-Friendly (src/)

| Module | Lines | Purpose |
|--------|-------|---------|
| insight.py | 380 | Plain-language explanations |
| fitness.py | 340 | Self-improving pattern tracking |
| guardian.py | 420 | Evidence quality gates |
| freshness.py | 310 | Evidence staleness detection |
| learner.py | 390 | Cross-domain pattern transfer |

### Shipyard (src/shipyard/)

| Module | Lines | Purpose |
|--------|-------|---------|
| constants.py | 196 | Verified values with citations |
| receipts.py | 591 | 8 shipbuilding receipt types |
| lifecycle.py | 431 | Keel-to-delivery state machine |
| assembly.py | 444 | Block welding + robotics |
| additive.py | 381 | 3D printing validation |
| iterate.py | 446 | SpaceX-style rapid iteration |
| nuclear.py | 467 | SMR reactor installation |
| procurement.py | 440 | Contract management |
| sim_shipyard.py | 671 | Monte Carlo simulation |

### Integration (src/)

| Module | Lines | Purpose |
|--------|-------|---------|
| ledger.py | 400 | Merkle ledger + Bekenstein bounds |
| bridge.py | 1,374 | Cross-branch translation |
| sim.py | 1,356 | Scenario simulation engine |
| usaspending_etl.py | 426 | Real data integration |
| sam_validator.py | 447 | Vendor validation |

**Total:** 29 modules, 20,000+ lines

---

## Shipyard Module: Trump-Class Program

The Shipyard module tracks the announced $200B, 22-ship battleship program using receipts-native accountability.

### Program Constants (Cited)

| Constant | Value | Citation |
|----------|-------|----------|
| TRUMP_CLASS_PROGRAM_COST_B | $200B | TRUMP_2025 |
| TRUMP_CLASS_SHIP_COUNT | 22 ships | TRUMP_2025 |
| TRUMP_CLASS_PER_SHIP_B | $9.09B/ship | Derived |
| ELON_SPHERE_COST_REDUCTION | 50% | Combined analysis |
| FORD_CVN78_OVERRUN_PCT | 23% | GAO_2022 |
| ZUMWALT_COST_INCREASE_PCT | 81% | GAO_2018 |
| DOD_FRAUD_CONFIRMED_B | $11B | GAO_2025 |
| SHIPBUILDING_OVERRUN_2025_B | $10.4B | GAO_2025 |

### Disruption Technologies

| Technology | Savings | Citation |
|------------|---------|----------|
| Large Format Additive (LFAM) | 45% time, 40% weight | UMAINE_2025 |
| Navy Additive Spares | 35% cost | NAVY_2025 |
| Robotic Welding (COMAU) | 30% efficiency | COMAU_2024 |
| SpaceX Starfactory Cadence | 1 week/unit | SPACEX_2025 |
| NuScale SMR Propulsion | 77 MWe | NRC_2025 |

### Shipyard Receipt Types (8)

| Receipt | Trigger | Key Fields |
|---------|---------|------------|
| keel | Ship construction start | ship_id, hull_number |
| block | Hull section assembly | block_id, welds, inspection |
| additive | 3D printed section | material, layer_hash |
| iteration | Design cycle complete | iteration_count, delta |
| milestone | Phase complete | phase, cost_to_date |
| procurement | Contract action | contract_type, amount |
| propulsion | Reactor installation | reactor_type, power_mwe |
| delivery | Ship handoff | final_cost, variance_pct |

### Detection Goals

| Metric | Historical | Target | Method |
|--------|------------|--------|--------|
| Overrun Detection | 23% variance | 12% variance | Compression tracking |
| Weld Fraud | Ship 26 (too late) | Ship 10 | Block-level receipts |
| Cost Prediction | ±40% | ±15% | Entropy modeling |

---

## v4.0 User-Friendly Features

### Plain-Language Explanations (insight.py)

Converts technical metrics to understandable summaries:

```
Technical: compression_ratio=0.42, kolmogorov=0.38, entropy=5.2
Plain: "This contract appears to involve copied or templated billing.
       The billing records show unusually repetitive patterns."
```

### Self-Improving Detection (fitness.py)

Patterns that reduce uncertainty survive. Patterns that add noise fade.

| Fitness Score | Meaning | Action |
|---------------|---------|--------|
| > 0.5 | Excellent | Study for expansion |
| > 0.3 | Good | Keep active |
| > 0.1 | Acceptable | Monitor |
| < 0 | Harmful | Prune |

**Formula:** Fitness = (entropy_before - entropy_after) / receipts_processed

### Evidence Quality Gates (guardian.py)

| Gate | Threshold | Abstention Trigger |
|------|-----------|-------------------|
| Evidence Quality | < 0.30 confidence | insufficient_data |
| Counter-Evidence | > 15% of total | conflicting_signals |
| Evidence Freshness | > 90 days | stale_evidence |
| Chain Integrity | < 90% valid | leak |

**Abstention is valid.** The system says "I don't know" when evidence is weak.

### Evidence Freshness (freshness.py)

| Level | Age | Confidence | Action |
|-------|-----|------------|--------|
| Fresh | < 30 days | 100% | Use freely |
| Recent | 30-60 days | 90% | Use with note |
| Aging | 60-90 days | 70% | Refresh for decisions |
| Stale | 90-180 days | 40% | Refresh required |
| Expired | > 180 days | 10% | Do not use |

**Data type multipliers:** Price data expires 2x faster. Contract awards persist 2x longer.

### Cross-Domain Pattern Transfer (learner.py)

Known fraud patterns transferable across domains:

| Pattern | Source Case | Domains | Transferability |
|---------|-------------|---------|-----------------|
| Repetitive Billing | Fat Leonard | logistics, maintenance, services | 85% |
| Price Gouging | TransDigm | spare_parts, consumables | 90% |
| Shell Company | General | all | 95% |
| Conflict of Interest | Boeing/Druyun | major_contracts, sole_source | 75% |
| Cost Escalation | General | construction, shipbuilding | 80% |

---

## Receipt Types (62 Total)

### Core (12)
warrant, quality_attestation, milestone, cost_variance, anchor, detection, compression, lineage, bridge, simulation, anomaly, violation

### v2 Physics (8)
threshold, pattern_emergence, entropy_tree, cascade_alert, epidemic_warning, holographic, meta_receipt, mutual_info

### v3 OMEGA (12)
kolmogorov, zkp, raf, das, adversarial, usaspending, layout_entropy, sam_validation, catalytic, holographic_da, thompson_audit, bekenstein

### v4 User-Friendly (17)
insight, fitness, health, quality, abstain, counter_evidence, integrity, gate, freshness, refresh_priority, monitoring, pattern_match, transfer, learn, library_summary, prune

### Shipyard (8)
keel, block, additive, iteration, milestone, procurement, propulsion, delivery

### RAZOR (5)
ingest, cohort, compression, validation, signal

---

## SLO Thresholds

### Performance

| Operation | Threshold | Test |
|-----------|-----------|------|
| Warrant generation | ≤ 50ms | `assert time <= 50` |
| Scan latency | ≤ 100ms/1000 receipts | `assert time <= 100` |
| ZKP verification | ≤ 100ms | `assert time <= 100` |

### Detection

| Metric | Threshold | Test |
|--------|-----------|------|
| Detection recall | ≥ 90% | `assert recall >= 0.90` |
| False positive rate | ≤ 5% | `assert fp_rate <= 0.05` |
| Thompson FP rate | ≤ 2% | `assert fp_rate <= 0.02` |

### Quality

| Metric | Threshold | Test |
|--------|-----------|------|
| Merkle verification | 100% | `assert all_verify` |
| Citation coverage | 100% | `assert all_cited` |
| Lineage completeness | ≥ 95% | `assert completeness >= 0.95` |

---

## Scenarios (12)

### Core Scenarios

| Scenario | Purpose | Pass Criteria |
|----------|---------|---------------|
| BASELINE | Standard procurement | compression ≥ 0.85, recall ≥ 0.90 |
| SHIPYARD_STRESS | Trump-class simulation | detect fraud by ship 10, predict ±15% |
| CROSS_BRANCH_INTEGRATION | Multi-system | zero proof failures |
| FRAUD_DISCOVERY | Novel patterns | legitimate ≥ 0.80, fraud ≤ 0.40 |
| REAL_TIME_OVERSIGHT | Streaming | latency ≤ 100ms, alert ≤ 5s |
| GODEL | Edge cases | no crashes, stoprules trigger |

### Physics Scenarios

| Scenario | Purpose | Pass Criteria |
|----------|---------|---------------|
| AUTOCATALYTIC | Pattern emergence | N_critical < 10,000, coherence ≥ 0.80 |
| THOMPSON | Bayesian calibration | FP ≤ 2%, variance converged |
| HOLOGRAPHIC | Boundary detection | p > 0.9999, bits ≤ 2N |

### Shipyard Scenarios

| Scenario | Purpose | Pass Criteria |
|----------|---------|---------------|
| TRUMP_CLASS_BASELINE | Normal operation | variance ≤ 15%, receipts valid |
| TRUMP_CLASS_DISRUPTION | Elon-sphere | 40-60% cost reduction |
| WELD_FRAUD_INJECTION | Fraud detection | detect by ship 10 |

---

## Stoprules

### Critical (HALT)

| Stoprule | Trigger | Action |
|----------|---------|--------|
| hash_mismatch | Merkle verification fails | HALT |
| uncited_data | Missing citation | HALT |
| zkp_verification_failed | ZKP proof invalid | HALT + reject |
| data_unavailable | DA confidence < 99% | HALT + investigate |

### Alert

| Stoprule | Trigger | Action |
|----------|---------|--------|
| kolmogorov_anomaly | K(x) < 0.65 | Flag for review |
| raf_cycle_detected | 3-5 entity cycle | Escalate |
| cascade_imminent | dC/dt > threshold | Early warning |
| stale_evidence | Age > 90 days | Require refresh |

### Deviation

| Stoprule | Trigger | Action |
|----------|---------|--------|
| entropy_gap_insufficient | ΔH < 0.15 | Fall back to v1 |
| pattern_incoherent | Coherence < 0.80 | Wait for receipts |
| abstention_triggered | Evidence weak | Return "unknown" |

---

## Data Sources

### Real Data Integration

| Source | Module | Data Type |
|--------|--------|-----------|
| USASpending.gov | usaspending_etl.py | Awards, transactions |
| SAM.gov | sam_validator.py | Vendor registration |

### Validation Targets

| Case | Years | Pattern | Expected Signal |
|------|-------|---------|-----------------|
| Fat Leonard (GDMA) | 2006-2013 | Repetitive billing | Z < -2.0 |
| TransDigm | 2015-2019 | Price gouging | Price/estimate > 2x |
| Boeing/Druyun | 2000-2003 | Conflict of interest | Approval anomaly |

---

## CLI Commands

```bash
# Core
python cli.py --test                    # Emit test receipt
python cli.py scenario --run BASELINE   # Run scenario

# v4.0 User-Friendly
python cli.py explain --demo            # Plain-language demo
python cli.py health                    # System health check
python cli.py patterns --list           # View fraud patterns
python cli.py freshness --demo          # Freshness demo
```

---

## File Structure

```
warrentproof/
├── cli.py                  # Command-line interface
├── spec.md                 # This specification
├── ledger_schema.json      # 62 receipt type definitions
├── CLAUDEME.md             # Execution standard
├── CITATIONS.md            # Source references
├── src/
│   ├── core.py             # Foundation
│   ├── insight.py          # v4.0 explanations
│   ├── fitness.py          # v4.0 self-improvement
│   ├── guardian.py         # v4.0 quality gates
│   ├── freshness.py        # v4.0 staleness
│   ├── learner.py          # v4.0 pattern transfer
│   ├── kolmogorov.py       # Algorithmic complexity
│   ├── compress.py         # Entropy analysis
│   ├── detect.py           # Anomaly detection
│   └── shipyard/           # Trump-class module
│       ├── constants.py
│       ├── receipts.py
│       ├── lifecycle.py
│       └── ...
├── razor/                  # Kolmogorov validation engine
└── tests/
    ├── test_v4_modules.py
    ├── test_shipyard_*.py
    └── ...
```

---

## Key Formulas

### Kolmogorov Complexity
```
K(x) = compressed_size / original_size
K(x) < 0.65 → likely generated/templated
K(x) ≥ 0.75 → likely legitimate
```

### Entropy Fitness
```
fitness = (H_before - H_after) / receipts_processed
fitness > 0 → pattern reduces uncertainty
fitness < 0 → pattern adds noise
```

### N_critical (Phase Transition)
```
N_critical = log₂(1/ΔH) × (H_legit / ΔH)
When N > N_critical, patterns become distinguishable
```

### Bekenstein Bound
```
S ≤ BEKENSTEIN_BITS_PER_DOLLAR × amount_usd
$1M transaction requires ≥ 1 bit of digital trail
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-01-01 | Initial: receipts, compression, detection |
| 2.0.0 | 2024-12-23 | Physics: entropy, autocatalytic, Thompson |
| 3.0.0 | 2024-12-23 | OMEGA: Kolmogorov, ZKP, RAF, DA sampling |
| 3.1.0 | 2024-12-23 | Shipyard: Trump-class, 8 receipt types |
| 4.0.0 | 2024-12-23 | User-friendly: insight, fitness, guardian, freshness, learner |

---

**⚠️ THIS IS A SIMULATION. NOT REAL DoD DATA. FOR RESEARCH ONLY. ⚠️**
