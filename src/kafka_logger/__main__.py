"""Command-line interface for kafka-logger."""

import argparse
import sys
from pathlib import Path


def generate_config(output_file: str = "kafka_logger_config.yaml"):
    """Generate default configuration file.

    Args:
        output_file: Output file path.
    """
    template_path = Path(__file__).parent / "default_config.yaml"
    output_path = Path(output_file)

    try:
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✓ Configuration file created: '{output_file}'")
    except Exception as e:
        print(f"Error: {e}")
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

    # Parse arguments
    args = parser.parse_args()

    # Handle commands
    if args.command == "generate_config":
        generate_config(args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
