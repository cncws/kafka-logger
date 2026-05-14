# kafka-logger

Python logging handler that sends structured JSON logs to Apache Kafka using standard `logging.dictConfig`.

## Install

```bash
uv add kafka-logger
pip install kafka-logger
```

## Generate config

```bash
python -m kafka_logger generate_config
# Creates kafka_logger_config.yaml with example configuration

# Custom filename
python -m kafka_logger generate_config my_config.yaml
```

or

```bash
uv run -m kafka_logger generate_config my_config.yaml
```

## Quick start

```python
import logging.config
import yaml

with open("kafka_logger_config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

logging.config.dictConfig(config)
logger = logging.getLogger("app")
logger.info("Hello Kafka")
```

Use the generated YAML file from `python -m kafka_logger generate_config` or `uv run -m kafka_logger generate_config my_config.yaml`.

## Features

- Standard `logging.dictConfig` configuration
- JSON formatted logs to Kafka
- Custom filters for dynamic field injection (host, trace_id)
- Full KafkaProducer configuration support
- Colored console logging support
- Type hints and clean design
- Simple CLI for generating a default YAML config
