"""Command-line interface for kafka-logger."""

import argparse
import sys
from pathlib import Path

import yaml

from .config import get_default_config


def generate_config(output_file: str = "kafka_logger_config.yaml", force: bool = False):
    """
    Generate default configuration file.

    Args:
        output_file: Output file path.
        force: Force overwrite if kafka_logger config exists.
    """
    output_path = Path(output_file)

    # Get default configuration
    default_config = get_default_config()

    # Check if file exists
    if output_path.exists():
        # Load existing config
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                existing_config = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error: Failed to read existing config file: {e}")
            sys.exit(1)

        # Check if kafka_logger section exists
        if "kafka_logger" in existing_config:
            if not force:
                print(
                    f"Warning: '{output_file}' already contains 'kafka_logger' configuration."
                )
                print("Use '-f' or '--force' flag to overwrite existing configuration.")
                print(
                    f"\nExample: python -m kafka_logger generate_config {output_file} -f"
                )
                sys.exit(1)
            else:
                print(f"Overwriting 'kafka_logger' configuration in '{output_file}'...")
                existing_config["kafka_logger"] = default_config["kafka_logger"]
        else:
            print(f"Adding 'kafka_logger' configuration to '{output_file}'...")
            existing_config["kafka_logger"] = default_config["kafka_logger"]

        # Write merged config
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    existing_config,
                    f,
                    allow_unicode=True,
                    default_flow_style=False,
                    sort_keys=False,
                )
            print(f"✓ Configuration successfully written to '{output_file}'")
        except Exception as e:
            print(f"Error: Failed to write config file: {e}")
            sys.exit(1)
    else:
        # Create new file
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    default_config,
                    f,
                    allow_unicode=True,
                    default_flow_style=False,
                    sort_keys=False,
                )
            print(f"✓ Configuration file created: '{output_file}'")
        except Exception as e:
            print(f"Error: Failed to create config file: {e}")
            sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="kafka-logger",
        description="Kafka Logger - Python logging handler for Apache Kafka",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # generate_config command
    config_parser = subparsers.add_parser(
        "generate_config",
        help="Generate default configuration file",
    )
    config_parser.add_argument(
        "output",
        nargs="?",
        default="kafka_logger_config.yaml",
        help="Output file path (default: kafka_logger_config.yaml)",
    )
    config_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force overwrite if kafka_logger configuration exists",
    )

    # Parse arguments
    args = parser.parse_args()

    # Handle commands
    if args.command == "generate_config":
        generate_config(args.output, args.force)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
