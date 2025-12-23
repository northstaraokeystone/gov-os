#!/bin/bash
# gate_t24h_shipyard.sh - T+24h Gate: SHIPYARD MVP
# Per CLAUDEME §3: RUN THIS OR KILL PROJECT
#
# ⚠️ SIMULATION ONLY - NOT REAL DoD DATA - FOR RESEARCH ONLY ⚠️

set -e

echo "=== WarrantProof SHIPYARD T+24h Gate ==="
echo "⚠️  THIS IS A SIMULATION. NOT REAL DoD DATA. FOR RESEARCH ONLY."
echo ""

# First, verify T+2h gate passes
echo "Running SHIPYARD T+2h gate first..."
./gate_t2h_shipyard.sh || { echo "FAIL: T+2h shipyard gate failed"; exit 1; }

echo ""
echo "=== SHIPYARD T+24h Specific Checks ==="
echo ""

# Run shipyard tests
echo "Running shipyard tests..."
python -m pytest tests/test_shipyard_*.py -q || { echo "FAIL: shipyard tests failed"; exit 1; }
echo "✓ All shipyard tests pass"

# Check all 8 receipt types exist
echo ""
echo "Checking all 8 receipt types..."
python -c "
from src.shipyard.receipts import (
    emit_keel_receipt,
    emit_block_receipt,
    emit_additive_receipt,
    emit_iteration_receipt,
    emit_milestone_receipt,
    emit_procurement_receipt,
    emit_propulsion_receipt,
    emit_delivery_receipt,
)
print('✓ All 8 receipt types importable')
"

# Check all modules have emit_receipt or emit_* functions
echo ""
echo "Checking receipt emission in shipyard modules..."
for f in src/shipyard/*.py; do
    if [[ "$f" != "src/shipyard/__init__.py" && "$f" != "src/shipyard/constants.py" ]]; then
        grep -q "emit_" "$f" || { echo "FAIL: $f missing emit_ function"; exit 1; }
        echo "✓ $f has emit function"
    fi
done

# Run 10-cycle shipyard simulation
echo ""
echo "Running 10-cycle shipyard simulation..."
python -c "
from src.shipyard.sim_shipyard import run_simulation, SimShipyardConfig

config = SimShipyardConfig(n_cycles=10, n_ships=2)
state = run_simulation(config)

print(f'✓ 10 cycles completed')
print(f'  Ships: {len(state.ships)}')
print(f'  Receipts: {len(state.receipt_ledger)}')
print(f'  Entropy trace: {len(state.entropy_trace)}')
print(f'  Violations: {len(state.violations)}')

assert len(state.receipt_ledger) > 0, 'No receipts generated'
"

# Check lifecycle state machine
echo ""
echo "Testing lifecycle state machine..."
python -c "
from src.shipyard.lifecycle import create_ship, advance_phase, LIFECYCLE_PHASES

ship = create_ship('TEST-001', 'trump', 'YARD-001')
assert ship['current_phase'] == 'DESIGN'

ship = advance_phase(ship, 'KEEL_LAYING', actual_days=30, actual_cost=1e9)
assert ship['current_phase'] == 'KEEL_LAYING'

print('✓ Lifecycle state machine working')
"

# Check disruption levels
echo ""
echo "Testing disruption levels..."
python -c "
from src.shipyard.sim_shipyard import simulate_disruption

trad = simulate_disruption({}, 'traditional')
assert trad['efficiency_multiplier'] == 1.0

elon = simulate_disruption({}, 'elon')
assert elon['efficiency_multiplier'] == 2.0
assert elon['cost_reduction_pct'] == 50.0

print('✓ Disruption levels configured correctly')
"

# Verify citations loaded
echo ""
echo "Checking shipbuilding citations..."
python -c "
import json
with open('data/citations/shipbuilding.json') as f:
    data = json.load(f)
    citations = data.get('citations', {})
    assert len(citations) >= 10, f'Insufficient citations: {len(citations)}'
    print(f'✓ Shipbuilding citations loaded: {len(citations)}')
"

echo ""
echo "=== PASS: SHIPYARD T+24h Gate ==="
echo ""
echo "⚠️  THIS IS A SIMULATION. NOT REAL DoD DATA. FOR RESEARCH ONLY."
