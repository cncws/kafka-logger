"""Tests for Kafka Logger Configuration."""

from kafka_logger import (
    FieldConfig,
    FormatterConfig,
    KafkaConfig,
    KafkaLoggerConfig,
    get_default_config,
)


class TestFieldConfig:
    """Tests for FieldConfig class."""

    def test_simple_field(self):
        """Test creating a simple field."""
        field = FieldConfig(name="message")
        assert field.name == "message"
        assert field.rename is None
        assert field.default is None
        assert field.static is None
        assert field.static_factory is None

    def test_field_with_rename(self):
        """Test field with rename."""
        field = FieldConfig(name="asctime", rename="timestamp")
        assert field.name == "asctime"
        assert field.rename == "timestamp"

    def test_field_with_default(self):
        """Test field with default value."""
        field = FieldConfig(name="traceid", default="")
        assert field.name == "traceid"
        assert field.default == ""

    def test_field_with_static(self):
        """Test field with static value."""
        field = FieldConfig(name="appname", static="test-app")
        assert field.name == "appname"
        assert field.static == "test-app"

    def test_field_with_static_factory(self):
        """Test field with static_factory."""
        field = FieldConfig(name="host", static_factory="builtin:get_host_ip")
        assert field.name == "host"
        assert field.static_factory == "builtin:get_host_ip"

    def test_field_with_dynamic_factory(self):
        """Test field with dynamic_factory."""
        field = FieldConfig(name="traceid", dynamic_factory="app.context:get_trace_id")
        assert field.name == "traceid"
        assert field.dynamic_factory == "app.context:get_trace_id"

    def test_to_dict(self):
        """Test converting field to dictionary."""
        field = FieldConfig(
            name="asctime",
            rename="timestamp",
            default="",
            static="test",
            static_factory="builtin:get_host_ip",
        )
        result = field.to_dict()
        assert result["name"] == "asctime"
        assert result["rename"] == "timestamp"
        assert result["default"] == ""
        assert result["static"] == "test"
        assert result["static_factory"] == "builtin:get_host_ip"


class TestFormatterConfig:
    """Tests for FormatterConfig class."""

    def test_default_formatter(self):
        """Test default formatter configuration."""
        formatter = FormatterConfig()
        assert formatter.default_time_format == "%Y-%m-%d %H:%M:%S"
        assert formatter.default_msec_format == "%s.%03d"
        assert formatter.fields == []

    def test_formatter_with_fields(self):
        """Test formatter with fields."""
        fields = [
            FieldConfig(name="message"),
            FieldConfig(name="asctime", rename="timestamp"),
        ]
        formatter = FormatterConfig(fields=fields)
        assert len(formatter.fields) == 2

    def test_get_fmt_fields(self):
        """Test getting field names."""
        fields = [
            FieldConfig(name="message"),
            FieldConfig(name="asctime", rename="timestamp"),
            FieldConfig(name="levelname"),
        ]
        formatter = FormatterConfig(fields=fields)
        field_names = formatter.get_fmt_fields()
        assert field_names == ["message", "asctime", "levelname"]

    def test_get_rename_fields(self):
        """Test getting renamed fields."""
        fields = [
            FieldConfig(name="message"),
            FieldConfig(name="asctime", rename="timestamp"),
            FieldConfig(name="name", rename="loggername"),
        ]
        formatter = FormatterConfig(fields=fields)
        renames = formatter.get_rename_fields()
        assert renames == {"asctime": "timestamp", "name": "loggername"}

    def test_get_defaults(self):
        """Test getting default values."""
        fields = [
            FieldConfig(name="message"),
            FieldConfig(name="traceid", default=""),
            FieldConfig(name="env", default="dev"),
        ]
        formatter = FormatterConfig(fields=fields)
        defaults = formatter.get_defaults()
        assert defaults == {"traceid": "", "env": "dev"}

    def test_get_static_fields(self):
        """Test getting static fields."""
        fields = [
            FieldConfig(name="message"),
            FieldConfig(name="appname", static="test-app"),
            FieldConfig(name="env", static="production"),
        ]
        formatter = FormatterConfig(fields=fields)
        statics = formatter.get_static_fields()
        assert statics == {"appname": "test-app", "env": "production"}


class TestKafkaConfig:
    """Tests for KafkaConfig class."""

    def test_basic_kafka_config(self):
        """Test basic Kafka configuration."""
        config = KafkaConfig(bootstrap_servers=["localhost:9092"], topic="test-topic")
        assert config.bootstrap_servers == ["localhost:9092"]
        assert config.topic == "test-topic"
        assert config.kafka_extra == {}

    def test_kafka_config_with_extras(self):
        """Test Kafka configuration with extra settings."""
        config = KafkaConfig(
            bootstrap_servers=["localhost:9092"],
            topic="test-topic",
            kafka_extra={"acks": 1, "retries": 5, "client_id": "test-client"},
        )
        assert config.kafka_extra["acks"] == 1
        assert config.kafka_extra["retries"] == 5
        assert config.kafka_extra["client_id"] == "test-client"

    def test_get_producer_config(self):
        """Test getting producer configuration."""
        config = KafkaConfig(
            bootstrap_servers=["localhost:9092"],
            topic="test-topic",
            kafka_extra={"acks": 1, "retries": 5},
        )
        producer_config = config.get_producer_config()
        assert producer_config["bootstrap_servers"] == ["localhost:9092"]
        assert producer_config["acks"] == 1
        assert producer_config["retries"] == 5


class TestKafkaLoggerConfig:
    """Tests for KafkaLoggerConfig class."""

    def test_from_dict_simple(self):
        """Test creating config from simple dictionary."""
        config_dict = {
            "kafka_logger": {
                "bootstrap_servers": ["localhost:9092"],
                "topic": "test-topic",
                "kafka_extra": {"acks": 0},
                "formatter": {
                    "default_time_format": "%Y-%m-%d %H:%M:%S",
                    "fields": [
                        {"name": "message"},
                        {"name": "asctime", "rename": "timestamp"},
                    ],
                },
            },
        }
        config = KafkaLoggerConfig.from_dict(config_dict)
        assert config.kafka.topic == "test-topic"
        assert len(config.formatter.fields) == 2

    def test_from_dict_with_string_fields(self):
        """Test creating config with string field names."""
        config_dict = {
            "kafka_logger": {
                "bootstrap_servers": ["localhost:9092"],
                "topic": "test-topic",
                "formatter": {"fields": ["message", "levelname", "asctime"]},
            },
        }
        config = KafkaLoggerConfig.from_dict(config_dict)
        field_names = config.formatter.get_fmt_fields()
        assert field_names == ["message", "levelname", "asctime"]

    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = KafkaLoggerConfig(
            kafka=KafkaConfig(
                bootstrap_servers=["localhost:9092"],
                topic="test-topic",
                kafka_extra={"acks": 1},
            ),
            formatter=FormatterConfig(
                fields=[
                    FieldConfig(name="message"),
                    FieldConfig(name="asctime", rename="timestamp"),
                ]
            ),
        )
        result = config.to_dict()
        assert result["kafka_logger"]["topic"] == "test-topic"
        assert len(result["kafka_logger"]["formatter"]["fields"]) == 2

    def test_default_config(self):
        """Test default configuration function."""
        default_dict = get_default_config()
        assert "kafka_logger" in default_dict
        assert default_dict["kafka_logger"]["topic"] == "app-logs"
        assert default_dict["kafka_logger"]["bootstrap_servers"] == ["localhost:9092"]
        assert len(default_dict["kafka_logger"]["formatter"]["fields"]) > 0

        # Test that it can be loaded as config
        config = KafkaLoggerConfig.from_dict(default_dict)
        assert config.kafka.topic == "app-logs"
        assert len(config.formatter.fields) > 0
