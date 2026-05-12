"""Basic usage example for kafka-logger.

cd examples && uv run basic_usage.py
"""

import logging

from kafka_logger import setup_kafka_logger


def example_config_file():
    """Example using configuration file."""
    print("=== Example 1: Using Configuration File ===")

    # Create logger from config file
    # First, generate config: python -m kafka_logger generate_config
    try:
        setup_kafka_logger("myapp")
        # myapp 及 myapp 下的 logger 都会使用这个配置
        logger = logging.getLogger("myapp.biz")
        logger.info("Application started")
        logger.warning("This is a warning")
        logger.error("This is an error")
        print("Logs sent to Kafka using config file\n")
    except FileNotFoundError:
        print("Config file not found. Generate it first:")
        print("  python -m kafka_logger generate_config")
        print()


if __name__ == "__main__":
    # Run examples
    example_config_file()
