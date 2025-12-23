"""
WarrantProof Shipyard Module v1.0 - Elon-Sphere Disruption Infrastructure

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

This module models SpaceX-style rapid iteration, 3D-printed hull validation,
robotic assembly tracking, and real-time procurement accountability for
shipbuilding programs.

The paradigm shift: Shipbuilding is information compression, not block construction.
Elon-sphere iteration + receipts-native procurement = 40-60% disruption potential.

Modules:
- constants: Verified constants with citations
- receipts: 8 shipbuilding-specific receipt types
- lifecycle: Keel-to-delivery state machine
- iterate: SpaceX-style rapid iteration modeling
- additive: 3D printing hull validation
- assembly: Robotic welding receipt tracking
- procurement: Fixed-price vs cost-plus entropy modeling
- nuclear: SMR propulsion integration
- sim_shipyard: Monte Carlo simulation harness

LAW_1 = "No receipt -> not real"
LAW_2 = "No test -> not shipped"
LAW_3 = "No gate -> not alive"
"""

from .constants import (
    TRUMP_CLASS_PROGRAM_COST_B,
    TRUMP_CLASS_SHIP_COUNT,
    TRUMP_CLASS_PER_SHIP_B,
    STARFACTORY_CADENCE_WEEKS,
    LFAM_TIME_SAVINGS_PCT,
    LFAM_WEIGHT_SAVINGS_PCT,
    NAVY_ADDITIVE_SPARES_SAVINGS,
    COMAU_WELD_EFFICIENCY_GAIN,
    ELON_SPHERE_COST_REDUCTION,
    FORD_CVN78_OVERRUN_PCT,
    ZUMWALT_COST_INCREASE_PCT,
    DOD_FRAUD_CONFIRMED_B,
    EARLY_DETECTION_PCT,
    NUSCALE_POWER_MWE,
    SHIPYARD_TENANT_ID,
    SHIPYARD_DISCLAIMER,
)

from .receipts import (
    RECEIPT_SCHEMA,
    emit_keel_receipt,
    emit_block_receipt,
    emit_additive_receipt,
    emit_iteration_receipt,
    emit_milestone_receipt,
    emit_procurement_receipt,
    emit_propulsion_receipt,
    emit_delivery_receipt,
)

from .lifecycle import (
    LIFECYCLE_PHASES,
    create_ship,
    advance_phase,
    calculate_variance,
    complete_ship,
)

from .iterate import (
    calculate_iteration_cadence,
    model_parallel_assembly,
    compression_from_iteration,
    detect_waterfall_pattern,
)

from .additive import (
    print_section,
    validate_layer,
    calculate_material_savings,
    detect_print_anomaly,
)

from .assembly import (
    weld_joint,
    inspect_weld,
    batch_block_assembly,
    detect_weld_fraud,
)

from .procurement import (
    create_contract,
    process_change_order,
    calculate_overrun_rate,
    compare_contract_types,
)

from .nuclear import (
    install_reactor,
    conduct_power_test,
    calculate_lifetime_savings,
    certification_chain,
)

from .sim_shipyard import (
    SimShipyardConfig,
    SimShipyardState,
    run_simulation,
    simulate_cycle,
    simulate_disruption,
    calculate_entropy,
    validate_conservation,
    SCENARIOS,
)

__version__ = "1.0.0"
__all__ = [
    # Constants
    "TRUMP_CLASS_PROGRAM_COST_B",
    "TRUMP_CLASS_SHIP_COUNT",
    "STARFACTORY_CADENCE_WEEKS",
    "LFAM_TIME_SAVINGS_PCT",
    "ELON_SPHERE_COST_REDUCTION",
    "NUSCALE_POWER_MWE",
    # Receipts
    "RECEIPT_SCHEMA",
    "emit_keel_receipt",
    "emit_block_receipt",
    "emit_additive_receipt",
    "emit_iteration_receipt",
    "emit_milestone_receipt",
    "emit_procurement_receipt",
    "emit_propulsion_receipt",
    "emit_delivery_receipt",
    # Lifecycle
    "create_ship",
    "advance_phase",
    "complete_ship",
    # Iterate
    "calculate_iteration_cadence",
    "model_parallel_assembly",
    # Additive
    "print_section",
    "calculate_material_savings",
    # Assembly
    "weld_joint",
    "batch_block_assembly",
    # Procurement
    "create_contract",
    "compare_contract_types",
    # Nuclear
    "install_reactor",
    "certification_chain",
    # Simulation
    "SimShipyardConfig",
    "SimShipyardState",
    "run_simulation",
    "SCENARIOS",
]
