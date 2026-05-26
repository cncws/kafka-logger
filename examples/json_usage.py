import logging
from logging.config import dictConfig

import yaml

from kafka_logger import set_trace_id

with open("examples/json_config.yaml") as f:
    config = yaml.safe_load(f)
    dictConfig(config)

logger = logging.getLogger("app")
logger.info("json usage example")
print()

logger.debug("debug 日志")
print()

with set_trace_id("trace-id-123"):
    try:
        _ = 1 / 0
    except Exception:
        logger.exception("exception 日志")

print()
logger.warning("json usage example end")
