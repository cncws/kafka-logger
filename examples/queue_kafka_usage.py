import atexit
import logging
from logging.handlers import QueueHandler, QueueListener
from queue import Queue

from kafka_logger.handler import KafkaLogHandler

# 配置 listener
q = Queue(maxsize=500)
kafka_handler = KafkaLogHandler(
    topic="orgweb",
    producer_config={
        "bootstrap.servers": "10.228.129.157:19092,10.228.129.158:19092,10.228.130.198:19092"
    },
)
listener = QueueListener(q, kafka_handler, respect_handler_level=True)
listener.start()
atexit.register(listener.stop)

# 配置 logger
logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)
logger.addHandler(QueueHandler(q))

logger.info("This is an info message.")
logger.error("This is an error message.")
