"""Configuration classes for Kafka Logger."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class FieldConfig:
    """Configuration for a single log field."""

    name: str
    rename: Optional[str] = None
    default: Any = None
    static: Any = None
    static_factory: Optional[str] = None
    dynamic_factory: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format used by JsonFormatter."""
        result = {"name": self.name}
        if self.rename is not None:
            result["rename"] = self.rename
        if self.default is not None:
            result["default"] = self.default
        if self.static is not None:
            result["static"] = self.static
        if self.static_factory is not None:
            result["static_factory"] = self.static_factory
        if self.dynamic_factory is not None:
            result["dynamic_factory"] = self.dynamic_factory
        return result


@dataclass
class FormatterConfig:
    """Configuration for JSON formatter."""

    default_time_format: str = "%Y-%m-%d %H:%M:%S"
    default_msec_format: str = "%s.%03d"
    fields: List[FieldConfig] = field(default_factory=list)

    def get_fmt_fields(self) -> List[str]:
        """Get list of field names for JsonFormatter fmt parameter."""
        return [f.name for f in self.fields]

    def get_rename_fields(self) -> Dict[str, str]:
        """Get dictionary of field renames."""
        return {f.name: f.rename for f in self.fields if f.rename is not None}

    def get_defaults(self) -> Dict[str, Any]:
        """Get dictionary of default values."""
        return {f.name: f.default for f in self.fields if f.default is not None}

    def get_static_fields(self) -> Dict[str, Any]:
        """Get dictionary of static values."""
        return {f.name: f.static for f in self.fields if f.static is not None}


@dataclass
class KafkaConfig:
    """Configuration for Kafka producer."""

    bootstrap_servers: List[str]
    topic: str
    kafka_extra: Dict[str, Any] = field(default_factory=dict)

    def get_producer_config(self) -> Dict[str, Any]:
        """Get configuration dictionary for KafkaProducer."""
        return {"bootstrap_servers": self.bootstrap_servers, **self.kafka_extra}


@dataclass
class KafkaLoggerConfig:
    """Complete configuration for Kafka logger."""

    kafka: KafkaConfig
    formatter: FormatterConfig

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "KafkaLoggerConfig":
        """Create configuration from dictionary."""
        # Parse Kafka config
        kafka_dict = config_dict.get("kafka_logger", {})
        kafka_config = KafkaConfig(
            bootstrap_servers=kafka_dict.get("bootstrap_servers", []),
            topic=kafka_dict.get("topic", "default-topic"),
            kafka_extra=kafka_dict.get("kafka_extra", {}),
        )

        # Parse Formatter config
        formatter_dict = kafka_dict.get("formatter", {})
        fields = []
        for field_dict in formatter_dict.get("fields", []):
            if isinstance(field_dict, str):
                fields.append(FieldConfig(name=field_dict))
            elif isinstance(field_dict, dict):
                field_name = field_dict.get("name")
                if field_name:
                    fields.append(
                        FieldConfig(
                            name=field_name,
                            rename=field_dict.get("rename"),
                            default=field_dict.get("default"),
                            static=field_dict.get("static"),
                            static_factory=field_dict.get("static_factory"),
                            dynamic_factory=field_dict.get("dynamic_factory"),
                        )
                    )

        formatter_config = FormatterConfig(
            default_time_format=formatter_dict.get(
                "default_time_format", "%Y-%m-%d %H:%M:%S"
            ),
            default_msec_format=formatter_dict.get("default_msec_format", "%s.%03d"),
            fields=fields,
        )

        return cls(kafka=kafka_config, formatter=formatter_config)

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "KafkaLoggerConfig":
        """Create configuration from YAML file."""
        with open(yaml_path, "r", encoding="utf-8") as f:
            config_dict = yaml.safe_load(f)
        return cls.from_dict(config_dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "kafka_logger": {
                "bootstrap_servers": self.kafka.bootstrap_servers,
                "topic": self.kafka.topic,
                "kafka_extra": self.kafka.kafka_extra,
                "formatter": {
                    "default_time_format": self.formatter.default_time_format,
                    "default_msec_format": self.formatter.default_msec_format,
                    "fields": [f.to_dict() for f in self.formatter.fields],
                },
            }
        }

    def to_yaml(self, yaml_path: str) -> None:
        """Save configuration to YAML file."""
        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(self.to_dict(), f, allow_unicode=True, default_flow_style=False)


def get_default_config() -> dict:
    """Get default configuration as a dictionary.

    Returns:
        Dictionary containing default kafka_logger configuration.
    """
    return {
        "kafka_logger": {
            "bootstrap_servers": ["localhost:9092"],
            "topic": "app-logs",
            "kafka_extra": {
                "client_id": "kafka-logger",
                "acks": 1,
                "retries": 3,
            },
            "formatter": {
                "default_time_format": "%Y-%m-%d %H:%M:%S",
                "default_msec_format": "%s.%03d",
                "fields": [
                    {"name": "asctime", "rename": "timestamp"},
                    {"name": "levelname"},
                    {"name": "name", "rename": "loggername"},
                    {"name": "threadName", "rename": "threadname"},
                    {"name": "module", "rename": "modulename"},
                    {"name": "lineno"},
                    {"name": "message"},
                    {"name": "exc_info", "rename": "stacktrace"},
                    {"name": "host", "static_factory": "builtin:get_host_ip"},
                    {"name": "appname", "static": "my-app"},
                    {"name": "env", "static": "dev"},
                ],
            },
        }
    }
