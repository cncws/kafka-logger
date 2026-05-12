"""Tests for dynamic_factory functionality."""

import logging
import sys
from types import ModuleType
from unittest.mock import MagicMock, patch

from kafka_logger import FieldConfig, FormatterConfig, KafkaConfig, KafkaLoggerConfig
from kafka_logger.handler import KafkaLogHandler


class TestDynamicFactory:
    """Tests for dynamic_factory feature."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create a mock context module
        self.context_module = ModuleType("test_context")

        # Counter to track calls
        self.call_count = 0

        def get_dynamic_value():
            """Function that returns different values each call."""
            self.call_count += 1
            return f"value-{self.call_count}"

        setattr(self.context_module, "get_dynamic_value", get_dynamic_value)
        sys.modules["test_context"] = self.context_module

    def teardown_method(self):
        """Clean up test fixtures."""
        if "test_context" in sys.modules:
            del sys.modules["test_context"]

    def test_dynamic_factory_called_on_each_emit(self):
        """Test that dynamic_factory is called on each log emit."""
        config = KafkaLoggerConfig(
            kafka=KafkaConfig(
                bootstrap_servers=["localhost:9092"],
                topic="test-topic",
            ),
            formatter=FormatterConfig(
                fields=[
                    FieldConfig(name="message"),
                    FieldConfig(
                        name="dynamic_field",
                        dynamic_factory="test_context:get_dynamic_value",
                    ),
                ]
            ),
        )

        # Mock the Kafka producer
        with patch("kafka_logger.handler.KafkaProducer") as mock_producer_class:
            mock_producer = MagicMock()
            mock_producer._closed = False
            mock_producer_class.return_value = mock_producer

            handler = KafkaLogHandler(config)

            # Create test logger
            logger = logging.getLogger("test_dynamic")
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

            # Emit multiple logs
            logger.info("First log")
            logger.info("Second log")
            logger.info("Third log")

            # Check that producer.send was called 3 times
            assert mock_producer.send.call_count == 3

            # Verify that dynamic_factory was called and values changed
            assert self.call_count == 3

    def test_dynamic_factory_failure_handling(self):
        """Test that dynamic_factory failures are handled gracefully."""
        # Create a module with a failing function
        failing_module = ModuleType("test_failing")

        def failing_function():
            raise ValueError("Dynamic factory failed")

        setattr(failing_module, "failing_function", failing_function)
        sys.modules["test_failing"] = failing_module

        try:
            config = KafkaLoggerConfig(
                kafka=KafkaConfig(
                    bootstrap_servers=["localhost:9092"],
                    topic="test-topic",
                ),
                formatter=FormatterConfig(
                    fields=[
                        FieldConfig(name="message"),
                        FieldConfig(
                            name="fail_field",
                            dynamic_factory="test_failing:failing_function",
                        ),
                    ]
                ),
            )

            with patch("kafka_logger.handler.KafkaProducer") as mock_producer_class:
                mock_producer = MagicMock()
                mock_producer._closed = False
                mock_producer_class.return_value = mock_producer

                # Should not raise exception
                handler = KafkaLogHandler(config)

                logger = logging.getLogger("test_failing_dynamic")
                logger.addHandler(handler)
                logger.setLevel(logging.INFO)

                # Should not raise exception, field should be set to None
                logger.info("Test log")

                assert mock_producer.send.call_count == 1
        finally:
            del sys.modules["test_failing"]

    def test_multiple_dynamic_factories(self):
        """Test multiple dynamic_factory fields."""
        # Create module with multiple functions
        multi_module = ModuleType("test_multi")

        self.counter_a = 0
        self.counter_b = 0

        def get_value_a():
            self.counter_a += 1
            return f"a-{self.counter_a}"

        def get_value_b():
            self.counter_b += 1
            return f"b-{self.counter_b}"

        setattr(multi_module, "get_value_a", get_value_a)
        setattr(multi_module, "get_value_b", get_value_b)
        sys.modules["test_multi"] = multi_module

        try:
            config = KafkaLoggerConfig(
                kafka=KafkaConfig(
                    bootstrap_servers=["localhost:9092"],
                    topic="test-topic",
                ),
                formatter=FormatterConfig(
                    fields=[
                        FieldConfig(name="message"),
                        FieldConfig(
                            name="field_a", dynamic_factory="test_multi:get_value_a"
                        ),
                        FieldConfig(
                            name="field_b", dynamic_factory="test_multi:get_value_b"
                        ),
                    ]
                ),
            )

            with patch("kafka_logger.handler.KafkaProducer") as mock_producer_class:
                mock_producer = MagicMock()
                mock_producer._closed = False
                mock_producer_class.return_value = mock_producer

                handler = KafkaLogHandler(config)

                logger = logging.getLogger("test_multi_dynamic")
                logger.addHandler(handler)
                logger.setLevel(logging.INFO)

                # Emit two logs
                logger.info("First")
                logger.info("Second")

                # Both counters should be incremented twice
                assert self.counter_a == 2
                assert self.counter_b == 2
        finally:
            del sys.modules["test_multi"]

    def test_dynamic_factory_with_static_factory(self):
        """Test that dynamic_factory and static_factory can coexist."""
        config = KafkaLoggerConfig(
            kafka=KafkaConfig(
                bootstrap_servers=["localhost:9092"],
                topic="test-topic",
            ),
            formatter=FormatterConfig(
                fields=[
                    FieldConfig(name="message"),
                    FieldConfig(
                        name="static_field", static_factory="builtin:get_host_ip"
                    ),
                    FieldConfig(
                        name="dynamic_field",
                        dynamic_factory="test_context:get_dynamic_value",
                    ),
                ]
            ),
        )

        with patch("kafka_logger.handler.KafkaProducer") as mock_producer_class:
            mock_producer = MagicMock()
            mock_producer._closed = False
            mock_producer_class.return_value = mock_producer

            handler = KafkaLogHandler(config)

            logger = logging.getLogger("test_mixed")
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

            logger.info("Test log")

            assert mock_producer.send.call_count == 1
            # dynamic_factory should have been called once
            assert self.call_count == 1
