"""Integration tests."""

import pytest

def test_config_validation():
    """Test configuration validation."""
    try:
        import config
        # Test config loading
        summary = config.get_config_summary()
        assert isinstance(summary, dict)
    except Exception as e:
        pytest.fail(f"Config test failed: {e}")
