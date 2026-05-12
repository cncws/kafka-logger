"""Tests for CLI functionality."""

import tempfile
from pathlib import Path

import pytest
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

    def test_generate_with_existing_kafka_logger_config(self, tmp_path):
        """Test that existing kafka_logger config causes warning."""
        config_file = tmp_path / "config.yaml"

        # Create file with existing kafka_logger config
        with open(config_file, "w") as f:
            yaml.dump({"kafka_logger": {"topic": "existing"}}, f)

        # Should exit with error
        with pytest.raises(SystemExit) as exc_info:
            generate_config(str(config_file), force=False)

        assert exc_info.value.code == 1

    def test_generate_with_force_overwrite(self, tmp_path):
        """Test force overwrite of existing kafka_logger config."""
        config_file = tmp_path / "config.yaml"

        # Create file with existing kafka_logger config
        with open(config_file, "w") as f:
            yaml.dump({"kafka_logger": {"topic": "old"}}, f)

        # Should succeed with force=True
        generate_config(str(config_file), force=True)

        with open(config_file) as f:
            config = yaml.safe_load(f)

        assert config["kafka_logger"]["topic"] == "app-logs"

    def test_merge_into_existing_file(self, tmp_path):
        """Test merging kafka_logger config into existing file."""
        config_file = tmp_path / "config.yaml"

        # Create file with other config
        existing_config = {"other_service": {"key": "value"}}
        with open(config_file, "w") as f:
            yaml.dump(existing_config, f)

        # Should merge successfully
        generate_config(str(config_file))

        with open(config_file) as f:
            config = yaml.safe_load(f)

        assert "other_service" in config
        assert "kafka_logger" in config
        assert config["other_service"]["key"] == "value"
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
                    config = yaml.safe_load(f)
                assert "kafka_logger" in config
            finally:
                os.chdir(original_cwd)
