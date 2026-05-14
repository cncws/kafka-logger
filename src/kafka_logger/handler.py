"""Kafka logging handler."""

import atexit
import logging

from kafka import KafkaProducer


class KafkaLogHandler(logging.Handler):
    def __init__(
        self,
        topic: str,
        producer_config: dict,
        close_timeout=5,
        level=logging.NOTSET,
    ):
        super().__init__(level)
        self._topic = topic
        self._producer_config = producer_config
        self._close_timeout = close_timeout
        self._producer = KafkaProducer(**self._producer_config)
        atexit.register(self._producer.close, timeout=self._close_timeout)

    def emit(self, record: logging.LogRecord) -> None:
        if not self._producer or self._producer._closed:
            return
        try:
            value = self.format(record)
            self._producer.send(self._topic, value.encode("utf-8"))
        except Exception:
            self.handleError(record)
