"""Kafka Logger - Python logging handler for Apache Kafka."""

from .handler import set_trace_id, setup_kafka_logger

__all__ = [
    "set_trace_id",
    "setup_kafka_logger",
]
