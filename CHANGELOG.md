# Changelog

All notable changes to Gov-OS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [6.2.0] - 2024-12-24

### Added
- **AidProof module** (P1): Foreign aid accountability for USAID, State, MCC
  - `modules/aid/` with config, ingest, verify, receipts, data, scenario
  - Implementing partner analysis with Form 990 cross-reference
  - Country allocation pattern detection
- **Round-trip funding detection**: FEC + Form 990 cross-reference
  - `detect_round_trip()` in `modules/graft/verify.py`
  - `ROUND_TRIP_THRESHOLD = 0.10` for flagging
- **ForeignAssistance.gov API integration**: `src/core/foreignaid_etl.py`
  - `ForeignAidETL` class with implementing partner, FEC, 990 cross-reference
- **USAID cohorts** in `data/usaspending_cohorts.json`:
  - `usaid_implementing_partners`: NGO grants
  - `usaid_direct_country`: Direct foreign grants
  - `state_dept_foreign_assistance`: State Dept comparison
- **Foreign aid cohorts**: `data/foreignassistance_cohorts.json`
  - `democracy_programs`: Political activity correlation
  - `pepfar_health`: Baseline legitimate aid
  - `mcc_compacts`: Structured aid baseline
- **Cross-domain links**: aid↔spend, aid↔graft, aid↔origin
- **ZK_ENABLED flag** per module (updated)
- **New thresholds** in `config/compression_params.yaml`:
  - `foreign_aid_grants`: 0.50
  - `ngo_overhead`: 0.40

### Changed
- **Contagion module** now includes 'aid' in cross-domain super-graph
- **spec.md** updated with AidProof documentation
- **Module count**: 12 → 13 (added aid)

### Political Context
- Tests Musk's USAID claim: "most funding went to far left political causes"
- Provides neutral, receipts-based verification
- Neither supports nor refutes without evidence
- `MUSK_CLAIM` scenario in `modules/aid/scenario.py`

---

## [6.1.0] - 2024-12-24

### Added
- **Real Data Gate**: USASpending API integration with 5 cohorts:
  - `doge_medicaid`: HHS Medicaid grants
  - `dod_transdigm`: DoD sole-source contracts
  - `fat_leonard`: Navy husbanding contracts
  - `federal_real_estate`: GSA property leases
  - `dod_shipbuilding`: Navy shipbuilding contracts
- **Domain-specific compression thresholds** via `config/compression_params.yaml`:
  - `medicaid_claims`: 0.45 (tight distribution)
  - `dod_logistics`: 0.55 (high variance)
  - `federal_real_estate`: 0.60 (moderate variance)
  - `r_and_d_contracts`: 0.75 (standard baseline)
  - `default`: 0.75 (fallback)
- **DOGE claim validation**: `validate_doge_claim()` function in `modules/doge/verify.py`
- **ZK_ENABLED flag** per module (opt-in for PII modules only):
  - `claim`: ZK_ENABLED = True (claimant PII)
  - `benefit`: ZK_ENABLED = True (beneficiary PII)
  - All other modules: ZK_ENABLED = False
- **Module directory structure** at `modules/` with 12 domain modules

### Changed
- **Constants now loaded dynamically** via `load_threshold(domain)` instead of hardcoded values
- **ZK proving now optional** (default OFF, opt-in for PII modules)
- **Module defaults** configurable via `config/module_defaults.yaml`

### Removed
- Hardcoded `COMPRESSION_THRESHOLD = 0.75` (now dynamic)
- Hardcoded `KOLMOGOROV_THRESHOLD = 0.65` (now dynamic)
- Bekenstein metaphor from main documentation (archived to `docs/archive/`)

### Fixed
- Threshold calibration now based on real data distributions instead of arbitrary constants

### Security
- PII-containing modules (claim, benefit) now require ZK proofs by default
- Non-PII modules skip expensive ZK computation

---

## [6.0.0] - 2024-12-23

### Added
- ShieldProof v2.1 CLI commands for defense contract accountability
- Simplified spec.md for executive readability
- Priority module table in spec.md §1

---

## [5.1.0] - 2024-12-22

### Added
- Temporal decay physics (exponential decay model)
- Cross-domain contagion detection
- Zombie entity detection
- Shell company pattern matching

---

**SIMULATION FOR RESEARCH PURPOSES ONLY**
