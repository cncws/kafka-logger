from pathlib import Path

from kafka_logger.__main__ import generate_config
from kafka_logger.filters import get_trace_id, set_trace_id


def test_trace_id_context_manager():
    assert get_trace_id() == ""

    with set_trace_id("abc-123"):
        assert get_trace_id() == "abc-123"

    assert get_trace_id() == ""


def test_generate_config_creates_file(tmp_path):
    output_file = tmp_path / "kafka_logger_config.yaml"
    generate_config(str(output_file))

    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "version: 1" in content
    assert "kafka_logger.handler.KafkaLogHandler" in content
