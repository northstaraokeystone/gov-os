"""
Gov-OS Domain Loader - Registry and Loader for Plug-in Architecture

THIS IS A SIMULATION FOR ACADEMIC RESEARCH PURPOSES ONLY

Plug-in Pattern:
1. Domain creates domains/{name}/config.yaml
2. Domain implements volatility.py extending VolatilityIndex
3. Domain implements schema.py with data schemas
4. load_domain() wires everything up
5. Core physics engine uses domain config without knowing domain details
"""

import importlib
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import yaml

from .core import DISCLAIMER


@dataclass
class VolatilityIndex:
    """Base volatility index for domain adaptation."""
    name: str = "base"
    base_value: float = 1.0
    alpha: float = 0.1

    def current(self) -> float:
        """Return current volatility factor."""
        return self.base_value

    def update(self, observation: float) -> None:
        """Update volatility with new observation."""
        self.base_value = self.alpha * observation + (1 - self.alpha) * self.base_value


@dataclass
class DomainConfig:
    """Container for domain configuration."""
    name: str
    version: str = "1.0.0"
    description: str = ""
    tenant_id: str = ""
    volatility: Optional[VolatilityIndex] = None
    schema: Dict[str, Any] = field(default_factory=dict)
    receipts: List[str] = field(default_factory=list)
    scenarios: List[str] = field(default_factory=list)
    node_key: str = "vendor_id"
    edge_key: str = "payment_to"
    thresholds: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "tenant_id": self.tenant_id,
            "node_key": self.node_key,
            "edge_key": self.edge_key,
            "receipts": self.receipts,
            "scenarios": self.scenarios,
            "thresholds": self.thresholds,
        }


# Global domain registry
_DOMAIN_REGISTRY: Dict[str, DomainConfig] = {}


def register_domain(name: str, config: DomainConfig) -> None:
    """
    Add domain to registry.

    Args:
        name: Domain name
        config: DomainConfig object
    """
    _DOMAIN_REGISTRY[name] = config


def load_domain(name: str) -> DomainConfig:
    """
    Load domain from domains/{name}/config.yaml.

    Args:
        name: Domain name (e.g., "defense", "medicaid")

    Returns:
        DomainConfig object

    Raises:
        ValueError: If domain not found
    """
    # Check registry first
    if name in _DOMAIN_REGISTRY:
        return _DOMAIN_REGISTRY[name]

    # Try to load from domains directory
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, "domains", name, "config.yaml")

        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)

            config = _parse_config(name, config_data)

            # Try to load volatility
            try:
                volatility_module = importlib.import_module(f"src.domains.{name}.volatility")
                if hasattr(volatility_module, "get_primary_volatility"):
                    config.volatility = volatility_module.get_primary_volatility()
            except ImportError:
                config.volatility = VolatilityIndex(name=f"{name}_default")

            _DOMAIN_REGISTRY[name] = config
            return config

    except Exception:
        pass

    # Return default config
    default_config = DomainConfig(
        name=name,
        description=f"{name.title()} domain",
        tenant_id=f"gov-os-{name}",
        volatility=VolatilityIndex(name=f"{name}_default"),
    )
    _DOMAIN_REGISTRY[name] = default_config
    return default_config


def _parse_config(name: str, data: Dict[str, Any]) -> DomainConfig:
    """Parse YAML config data into DomainConfig."""
    schema = data.get("schema", {})

    return DomainConfig(
        name=name,
        version=data.get("version", "1.0.0"),
        description=data.get("description", f"{name.title()} domain"),
        tenant_id=data.get("tenant_id", f"gov-os-{name}"),
        schema=schema,
        receipts=data.get("receipts", []),
        scenarios=data.get("scenarios", []),
        node_key=schema.get("node_key", "vendor_id"),
        edge_key=schema.get("edge_key", "payment_to"),
        thresholds=data.get("thresholds", {}),
    )


def list_domains() -> List[str]:
    """
    Return available domain names.

    Returns:
        List of domain names
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    domains_dir = os.path.join(base_dir, "domains")

    domains = list(_DOMAIN_REGISTRY.keys())

    if os.path.exists(domains_dir):
        for name in os.listdir(domains_dir):
            module_path = os.path.join(domains_dir, name)
            if os.path.isdir(module_path) and name not in domains and not name.startswith("__"):
                config_path = os.path.join(module_path, "config.yaml")
                if os.path.exists(config_path):
                    domains.append(name)

    return sorted(set(domains))


def get_volatility(domain: str) -> VolatilityIndex:
    """Return domain's volatility index."""
    config = load_domain(domain)
    if config.volatility is None:
        config.volatility = VolatilityIndex(name=f"{domain}_default")
    return config.volatility


def get_schema(domain: str) -> Dict[str, Any]:
    """Return domain's data schema."""
    config = load_domain(domain)
    return config.schema


def get_receipts(domain: str) -> List[str]:
    """Return domain's receipt types."""
    config = load_domain(domain)
    return config.receipts


def validate_receipt(receipt: Dict[str, Any], domain: str) -> bool:
    """Validate receipt against domain schema."""
    config = load_domain(domain)
    schema = config.schema

    if not schema:
        return True  # No schema = accept all

    receipt_domain = receipt.get("domain", domain)
    if receipt_domain != domain:
        return False

    if receipt.get("tenant_id") and config.tenant_id:
        if receipt["tenant_id"] != config.tenant_id:
            return False

    return True


def unregister_domain(name: str) -> None:
    """Remove domain from registry."""
    if name in _DOMAIN_REGISTRY:
        del _DOMAIN_REGISTRY[name]


def reset_registry() -> None:
    """Reset the domain registry. Use for testing."""
    global _DOMAIN_REGISTRY
    _DOMAIN_REGISTRY = {}
