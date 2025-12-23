#!/bin/bash
# gate_t2h_shipyard.sh - T+2h Gate: SHIPYARD SKELETON
# Per CLAUDEME §3: RUN THIS OR KILL PROJECT
#
# ⚠️ SIMULATION ONLY - NOT REAL DoD DATA - FOR RESEARCH ONLY ⚠️

set -e

echo "=== WarrantProof SHIPYARD T+2h Gate ==="
echo "⚠️  THIS IS A SIMULATION. NOT REAL DoD DATA. FOR RESEARCH ONLY."
echo ""

# Check required files exist
echo "Checking required shipyard files..."

[ -d src/shipyard ] || { echo "FAIL: no src/shipyard/"; exit 1; }
echo "✓ src/shipyard/ exists"

[ -f src/shipyard/__init__.py ] || { echo "FAIL: no src/shipyard/__init__.py"; exit 1; }
echo "✓ src/shipyard/__init__.py exists"

[ -f src/shipyard/constants.py ] || { echo "FAIL: no src/shipyard/constants.py"; exit 1; }
echo "✓ src/shipyard/constants.py exists"

[ -f src/shipyard/receipts.py ] || { echo "FAIL: no src/shipyard/receipts.py"; exit 1; }
echo "✓ src/shipyard/receipts.py exists"

[ -f src/shipyard/lifecycle.py ] || { echo "FAIL: no src/shipyard/lifecycle.py"; exit 1; }
echo "✓ src/shipyard/lifecycle.py exists"

[ -f schemas/ledger_schema_shipyard.json ] || { echo "FAIL: no schemas/ledger_schema_shipyard.json"; exit 1; }
echo "✓ schemas/ledger_schema_shipyard.json exists"

[ -f data/citations/shipbuilding.json ] || { echo "FAIL: no data/citations/shipbuilding.json"; exit 1; }
echo "✓ data/citations/shipbuilding.json exists"

# Check constants are loadable
echo ""
echo "Testing constants..."
python -c "
from src.shipyard.constants import TRUMP_CLASS_PROGRAM_COST_B, ELON_SPHERE_COST_REDUCTION
assert TRUMP_CLASS_PROGRAM_COST_B == 200.0, 'Invalid program cost'
assert ELON_SPHERE_COST_REDUCTION == 0.50, 'Invalid cost reduction'
print(f'✓ Program: \${TRUMP_CLASS_PROGRAM_COST_B}B, Disruption: {ELON_SPHERE_COST_REDUCTION*100}%')
"

# Check receipts emit valid JSON
echo ""
echo "Testing receipt emission..."
python -c "
from src.shipyard.receipts import emit_keel_receipt
from datetime import datetime
receipt = emit_keel_receipt('TEST-001', 'YARD-001', datetime.utcnow().isoformat() + 'Z')
assert 'receipt_type' in receipt
assert receipt['receipt_type'] == 'keel'
assert ':' in receipt['payload_hash']  # dual-hash
print('✓ Keel receipt emits valid JSON with dual-hash')
"

# Check lifecycle phases
echo ""
echo "Testing lifecycle phases..."
python -c "
from src.shipyard.lifecycle import LIFECYCLE_PHASES
expected = ['DESIGN', 'KEEL_LAYING', 'BLOCK_ASSEMBLY', 'LAUNCH', 'FITTING_OUT', 'SEA_TRIALS', 'DELIVERY']
assert LIFECYCLE_PHASES == expected, f'Invalid phases: {LIFECYCLE_PHASES}'
print('✓ LIFECYCLE_PHASES defined correctly')
"

# Verify simulation disclaimers present
echo ""
echo "Checking simulation disclaimers..."
grep -rq "SIMULATION" src/shipyard/*.py || { echo "FAIL: Missing SIMULATION disclaimers in src/shipyard/"; exit 1; }
echo "✓ SIMULATION disclaimers present in src/shipyard/"

echo ""
echo "=== PASS: SHIPYARD T+2h Gate ==="
echo ""
echo "⚠️  THIS IS A SIMULATION. NOT REAL DoD DATA. FOR RESEARCH ONLY."
