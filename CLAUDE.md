# Kafka Logger - AI Assistant Guide

本文件为 `kafka-logger` 项目的 AI 助手参考，提供关键架构、配置、工厂机制、处理器行为和常见开发流程。

使用 uv 管理项目，而不是 python/pip。

## 项目概述

`kafka-logger` 是一个 Python 日志处理器，使用标准的 `logging.dictConfig` 将结构化 JSON 日志发送到 Apache Kafka。它支持：
- 标准 Python logging.dictConfig 配置
- 自定义过滤器注入动态字段（如 host, trace_id）
- JSON 输出格式化
- 控制台彩色日志输出
- KafkaProducer 的全部配置透传

## 目录结构

```
src/kafka_logger/
  __init__.py
  __main__.py
  example_config.yaml
  filters.py
  handler.py
  py.typed
```

## 核心模块

### `src/kafka_logger/handler.py`

日志处理器：
- `KafkaLogHandler`: 继承自 `logging.Handler`，发送日志到 Kafka

### `src/kafka_logger/filters.py`

过滤器用于注入动态字段：
- `HostInjectFilter`: 注入主机 IP
- `TraceIdInjectFilter`: 注入 trace_id
- `get_trace_id()` / `set_trace_id()`: 上下文变量管理 trace_id

### `src/kafka_logger/__init__.py`

配置加载：
- `setup_logger()`: 加载 YAML 配置并应用 dictConfig

### `src/kafka_logger/__main__.py`

CLI 入口，用于生成默认 YAML 配置：
- `generate_config`: 生成示例配置文件

使用示例：

```bash
python -m kafka_logger generate_config
python -m kafka_logger generate_config my_config.yaml
uv run -m kafka_logger generate_config my_config.yaml
```

## 配置系统

日志配置基于标准的 `logging.dictConfig`，通过 YAML 文件配置。

典型 YAML 结构（见 `example_config.yaml`）：

```yaml
version: 1
filters:
  host_injector:
    (): kafka_logger.filters.HostInjectFilter
    bind_key: host
  traceid_injector:
    (): kafka_logger.filters.TraceIdInjectFilter
    bind_key: trace_id
formatters:
  json:
    (): pythonjsonlogger.json.JsonFormatter
    fmt: asctime,levelname,name,message,host,trace_id
  colorful:
    (): logzero.LogFormatter
    color: true
handlers:
  kafka:
    class: kafka_logger.handler.KafkaLogHandler
    formatter: json
    filters: [host_injector, traceid_injector]
    topic: log-topic
    producer_config:
      bootstrap_servers: localhost:9092
  console:
    class: logging.StreamHandler
    formatter: colorful
loggers:
  app:
    handlers: [kafka, console]
    level: INFO
```

## 过滤器机制

### 动态字段注入

使用过滤器在日志记录时注入动态值：

- `HostInjectFilter`: 在记录创建时添加主机 IP
- `TraceIdInjectFilter`: 添加当前上下文的 trace_id

### Trace ID 管理

```python
from kafka_logger import set_trace_id, get_trace_id

with set_trace_id("abc-123"):
    logger.info("This log will have trace_id: abc-123")
```

## 处理器实现

`KafkaLogHandler` 工作流程：
1. 初始化时创建 KafkaProducer
2. emit 时格式化日志记录为字符串
3. 发送到指定 Kafka topic

### 异常处理

- KafkaProducer 初始化失败时打印警告，producer 设为 None
- 发送失败时调用 handleError，不会阻塞应用

## 开发指南

### 代码风格

- 使用类型提示
- 遵循 PEP 8
- 为公共 API 编写 docstring

### 测试

- 使用 pytest
- 模拟 Kafka 依赖
- 测试配置加载、过滤器注入、日志发送

### 扩展说明

1. 新过滤器：继承 `logging.Filter`，在 `filters.py` 中实现
2. 新配置选项：更新 `example_config.yaml`
3. 新特性：扩展 handler 或添加新过滤器

## 常见任务

### 安装

```bash
uv sync
uv sync --dev
```

### 生成配置

```bash
python -m kafka_logger generate_config -o config.yaml
uv run -m kafka_logger generate_config -o config.yaml
```

### 代码检查

```bash
uv run ruff format .
uv run ruff check .
```

## 关键注意点

- 使用标准 `logging.dictConfig` 配置
- 过滤器用于注入动态字段
- KafkaProducer 配置通过 `producer_config` 传递
- 支持 JSON 和彩色控制台输出
