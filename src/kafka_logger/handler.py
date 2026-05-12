"""Kafka logging handler."""

import atexit
import importlib
import logging
import socket
from typing import Callable

from kafka import KafkaProducer
from pythonjsonlogger.json import JsonFormatter

from .config import KafkaLoggerConfig


def get_host_ip() -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        ip, _ = s.getsockname()
        return ip


def resolve_static_factory(factory_spec: str) -> Callable:
    if ":" not in factory_spec:
        raise ValueError(
            f"Invalid factory specification: {factory_spec}. "
            'Expected format: "builtin:func_name" or "module.path:func_name"'
        )

    module_path, func_name = factory_spec.split(":", 1)

    if module_path == "builtin":
        func = globals().get(func_name)
        if func is None:
            raise AttributeError(
                f"Built-in function '{func_name}' not found in kafka_logger module"
            )
    else:
        try:
            module = importlib.import_module(module_path)
        except ImportError as e:
            raise ImportError(f"Cannot import module '{module_path}': {e}") from e

        if not hasattr(module, func_name):
            raise AttributeError(
                f"Function '{func_name}' not found in module '{module_path}'"
            )
        func = getattr(module, func_name)

    if not callable(func):
        raise ValueError(f"'{factory_spec}' does not resolve to a callable function")

    return func


class KafkaLogHandler(logging.Handler):
    def __init__(self, config: KafkaLoggerConfig):
        super().__init__()
        self.config = config
        producer_config = self.config.kafka.get_producer_config()
        self.producer = KafkaProducer(**producer_config)
        atexit.register(self.producer.close, timeout=5)
        self.topic = self.config.kafka.topic
        self._setup_formatter()
        self._setup_dynamic_factories()

    def _setup_formatter(self) -> None:
        fmt_config = self.config.formatter
        static_fields = fmt_config.get_static_fields()

        if "host" in static_fields and static_fields["host"] is None:
            static_fields["host"] = get_host_ip()

        for field_config in fmt_config.fields:
            if field_config.static_factory:
                try:
                    factory_func = resolve_static_factory(field_config.static_factory)
                    static_fields[field_config.name] = factory_func()
                except Exception as e:
                    print(
                        f"Warning: Failed to resolve static_factory '{field_config.static_factory}' "
                        f"for field '{field_config.name}': {e}"
                    )
                    static_fields[field_config.name] = None

        self.fmt = JsonFormatter(
            fmt=fmt_config.get_fmt_fields(),
            rename_fields=fmt_config.get_rename_fields(),
            defaults=fmt_config.get_defaults(),
            static_fields=static_fields,
        )
        self.fmt.default_time_format = fmt_config.default_time_format
        self.fmt.default_msec_format = fmt_config.default_msec_format

    def _setup_dynamic_factories(self) -> None:
        self.dynamic_factories = {}
        for field_config in self.config.formatter.fields:
            if field_config.dynamic_factory:
                try:
                    factory_func = resolve_static_factory(field_config.dynamic_factory)
                    self.dynamic_factories[field_config.name] = factory_func
                except Exception as e:
                    print(
                        f"Warning: Failed to resolve dynamic_factory '{field_config.dynamic_factory}' "
                        f"for field '{field_config.name}': {e}"
                    )

    def emit(self, record: logging.LogRecord) -> None:
        if self.producer._closed:
            return
        try:
            for field_name, factory_func in self.dynamic_factories.items():
                try:
                    value = factory_func()
                    setattr(record, field_name, value)
                except Exception as e:
                    print(f"Warning: Dynamic factory for '{field_name}' failed: {e}")
                    setattr(record, field_name, None)

            value = self.fmt.format(record)
            self.producer.send(self.topic, value.encode("utf-8"))
        except Exception:
            self.handleError(record)


def setup_kafka_logger(
    name: str = "app",
    level: int = logging.DEBUG,
    config_dict_loader: str = "config_loader:load_yaml",
) -> logging.Logger:
    loader_func = resolve_static_factory(config_dict_loader)
    config_dict = loader_func()
    config = KafkaLoggerConfig.from_dict(config_dict)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(KafkaLogHandler(config))
    return logger
