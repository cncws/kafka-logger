"""Kafka Logger - Python logging handler for Apache Kafka."""

from .handler import get_trace_id, set_trace_id, setup_kafka_logger

__all__ = [
    "get_trace_id",
    "set_trace_id",
    "setup_kafka_logger",
]
