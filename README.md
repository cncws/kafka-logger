# kafka-logger

Python logging handler that sends JSON logs to Apache Kafka.

## Install

```bash
uv add kafka-logger
pip install kafka-logger
```

## Generate config

```bash
python -m kafka_logger generate_config
```

## Quick start

```python
from kafka_logger import setup_kafka_logger

logger = setup_kafka_logger("app")
logger.info("Hello Kafka")
```
