import logging
from logging.config import dictConfig

import yaml

with open("examples/kafka_config.yaml") as f:
    config = yaml.safe_load(f)
    dictConfig(config)

logger = logging.getLogger("app")
logger.info("kafka usage example")
print()

logger.debug("debug 日志")
print()

try:
    _ = 1 / 0
except Exception:
    logger.exception("exception 日志")

print()
logger.warning("kafka usage example end")
