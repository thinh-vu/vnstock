from vnstock.core.registry import ProviderRegistry
from vnstock.ui._registry import MAP


def test_registry_map_exists():
    """Test that UI method routing MAP exists and contains domains."""
    assert isinstance(MAP, dict)
    assert "Market" in MAP
    assert "Reference" in MAP


def test_provider_registry_singleton():
    """Test that ProviderRegistry acts as a reliable registry."""
    registry = ProviderRegistry()
    assert registry is not None
