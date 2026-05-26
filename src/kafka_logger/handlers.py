"""Kafka logging handler."""

import atexit
import logging

from confluent_kafka import Producer


def delivery_callback(err, msg):
    """Callback for delivery reports."""
    if err:
        print("ERROR: Message failed delivery: {}".format(err))


class KafkaHandler(logging.Handler):
    """Kafka logging handler using confluent_kafka."""

    def __init__(
        self,
        topic: str,
        producer_config: dict,
        close_timeout: float = 5,
        callback=delivery_callback,
        level: int = logging.NOTSET,
    ):
        super().__init__(level)
        self._topic = topic
        self._producer_config = producer_config
        self._close_timeout = close_timeout
        self._callback = callback

        self._producer = Producer(self._producer_config)
        # Ensure all messages are delivered on exit
        atexit.register(self._producer.flush, self._close_timeout)

    def emit(self, record: logging.LogRecord) -> None:
        try:
            value = self.format(record).encode("utf-8")
            self._producer.produce(self._topic, value, callback=self._callback)
            # Poll to trigger callbacks
            self._producer.poll(0)
        except Exception:
            self.handleError(record)
