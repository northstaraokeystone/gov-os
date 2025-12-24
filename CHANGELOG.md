# Changelog

All notable changes to Gov-OS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
