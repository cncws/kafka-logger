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
# Creates kafka_logger_config.yaml with comments

# Custom filename
python -m kafka_logger generate_config my_config.yaml
```

## Quick start

```python
from kafka_logger import setup_kafka_logger

logger = setup_kafka_logger("app")
logger.info("Hello Kafka")
```

## Features

- JSON formatted logs to Kafka
- Field mapping & renaming
- Static/dynamic field values
- Static/dynamic factory functions
- Full KafkaProducer config support
- Type hints & dataclass design
