"""Tests for static_factory functionality."""

import sys
from types import ModuleType

import pytest

from kafka_logger.handler import resolve_static_factory


class TestResolveStaticFactory:
    """Tests for resolve_static_factory function."""

    def test_builtin_get_host_ip(self):
        """Test resolving builtin:get_host_ip."""
        func = resolve_static_factory("builtin:get_host_ip")
        assert callable(func)
        result = func()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_invalid_format_missing_colon(self):
        """Test invalid factory specification without colon."""
        with pytest.raises(ValueError, match="Invalid factory specification"):
            resolve_static_factory("invalid_format")

    def test_builtin_nonexistent_function(self):
        """Test builtin with non-existent function."""
        with pytest.raises(AttributeError, match="not found in kafka_logger module"):
            resolve_static_factory("builtin:nonexistent_function")

    def test_external_module_not_found(self):
        """Test external module that doesn't exist."""
        with pytest.raises(ImportError, match="Cannot import module"):
            resolve_static_factory("nonexistent.module:some_function")

    def test_external_function_not_found(self):
        """Test external module with non-existent function."""
        # Create a mock module
        test_module = ModuleType("test_module_for_static_factory")
        sys.modules["test_module_for_static_factory"] = test_module

        try:
            with pytest.raises(AttributeError, match="not found in module"):
                resolve_static_factory(
                    "test_module_for_static_factory:nonexistent_function"
                )
        finally:
            # Clean up
            del sys.modules["test_module_for_static_factory"]

    def test_external_module_valid_function(self):
        """Test external module with valid function."""
        # Create a mock module with a function
        test_module = ModuleType("test_module_valid")

        def test_function():
            return "test_value"

        setattr(test_module, "test_function", test_function)
        sys.modules["test_module_valid"] = test_module

        try:
            func = resolve_static_factory("test_module_valid:test_function")
            assert callable(func)
            assert func() == "test_value"
        finally:
            # Clean up
            del sys.modules["test_module_valid"]

    def test_not_callable(self):
        """Test that non-callable raises ValueError."""
        # Create a mock module with a non-callable attribute
        test_module = ModuleType("test_module_not_callable")
        setattr(test_module, "not_a_function", "just_a_string")
        sys.modules["test_module_not_callable"] = test_module

        try:
            with pytest.raises(ValueError, match="does not resolve to a callable"):
                resolve_static_factory("test_module_not_callable:not_a_function")
        finally:
            # Clean up
            del sys.modules["test_module_not_callable"]
