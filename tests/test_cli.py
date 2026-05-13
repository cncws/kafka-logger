"""Tests for CLI functionality."""

import tempfile
from pathlib import Path

import yaml

from kafka_logger.__main__ import generate_config


class TestGenerateConfig:
    """Tests for generate_config CLI command."""

    def test_generate_new_file(self, tmp_path):
        """Test generating config to a new file."""
        config_file = tmp_path / "config.yaml"
        generate_config(str(config_file))

        assert config_file.exists()

        with open(config_file) as f:
            config = yaml.safe_load(f)

        assert "kafka_logger" in config
        assert config["kafka_logger"]["topic"] == "app-logs"
        assert len(config["kafka_logger"]["formatter"]["fields"]) > 0

    def test_overwrite_existing_file(self, tmp_path):
        """Test overwriting existing file."""
        config_file = tmp_path / "config.yaml"

        # Create file with existing content
        with open(config_file, "w") as f:
            yaml.dump({"old_config": {"key": "value"}}, f)

        # Should overwrite directly
        generate_config(str(config_file))

        with open(config_file) as f:
            config = yaml.safe_load(f)

        assert "old_config" not in config
        assert "kafka_logger" in config
        assert config["kafka_logger"]["topic"] == "app-logs"

    def test_default_filename(self):
        """Test default filename is used when no argument provided."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import os

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                generate_config()

                default_file = Path("kafka_logger_config.yaml")
                assert default_file.exists()

                with open(default_file) as f:
                    content = f.read()
                    config = yaml.safe_load(content)

                assert "kafka_logger" in config
                # Verify comments are preserved
                assert "# Kafka Logger" in content
            finally:
                os.chdir(original_cwd)
