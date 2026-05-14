"""Basic usage example for kafka-logger.

cd examples && uv run basic_usage.py
"""

import logging
from logging.config import dictConfig

import yaml

from kafka_logger import set_trace_id

with open("config.yaml") as f:
    config = yaml.safe_load(f)
    dictConfig(config)

# 示例文件配置的 app logger
logger = logging.getLogger("app")

logger.info("Application started")
print()

with set_trace_id("trace-123"):
    logger.warning("logging with trace_id")
print()

try:
    _ = 1 / 0
except Exception:
    logger.exception("something error")
