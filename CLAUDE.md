# Kafka Logger - AI Assistant Guide

本文件为 `kafka-logger` 项目的 AI 助手参考，提供关键架构、配置、工厂机制、处理器行为和常见开发流程。

## 项目概述

`kafka-logger` 是一个 Python 日志处理器，将结构化 JSON 日志发送到 Apache Kafka。它支持：
- YAML / dict / dataclass 配置
- JSON 输出字段映射
- 静态工厂与动态工厂函数
- KafkaProducer 的全部配置透传
- 类型提示与 dataclass 设计

## 目录结构

```
src/kafka_logger/
  __init__.py
  __main__.py
  config.py
  handler.py
  py.typed

tests/
  test_cli.py
  test_config.py
  test_dynamic_factory.py
  test_static_factory.py

examples/
  basic_usage.py
  config.yaml
```

## 核心模块

### `src/kafka_logger/config.py`

配置类：
- `FieldConfig`
- `FormatterConfig`
- `KafkaConfig`
- `KafkaLoggerConfig`
- `default_config.yaml` 默认配置模板

### `src/kafka_logger/handler.py`

日志处理器与工厂支持：
- `KafkaLogHandler`
- `get_host_ip()`
- `resolve_static_factory()`
- `create_kafka_logger()`

### `src/kafka_logger/__main__.py`

CLI 入口，用于生成默认 YAML 配置：
- `generate_config`
- `python -m kafka_logger generate_config`

## 配置系统

日志配置基于 dataclass，要求显式提供配置，可通过 `default_config.yaml` 模板生成。

典型 YAML 结构：

```yaml
kafka_logger:
  bootstrap_servers:
    - localhost:9092
  topic: my-topic
  kafka_extra:
    acks: 0
  formatter:
    default_time_format: "%Y-%m-%d %H:%M:%S"
    fields:
      - name: message
      - name: levelname
```

### `FieldConfig` 关键字段

- `name`: 必填，LogRecord 属性名
- `rename`: 可选，输出字段重命名
- `default`: 可选，缺失时使用默认值
- `static`: 可选，静态常量值
- `static_factory`: 可选，一次性计算值
- `dynamic_factory`: 可选，每次 emit 时计算值

## 工厂机制

### 静态工厂 `static_factory`

用于生成在处理器初始化时计算一次的字段值。

配置格式：
- `builtin:func_name`（本地内置函数）
- `module.path:function_name`（外部模块）

要求：
- 无参数函数
- 可调用
- 返回 JSON 可序列化值

示例：

```yaml
kafka_logger:
  formatter:
    fields:
      - name: host
        static_factory: builtin:get_host_ip
```

### 动态工厂 `dynamic_factory`

用于每次日志发出时重新计算字段值，适合请求上下文、trace id、user id 等动态数据。

要求同静态工厂，且函数应当线程安全。

示例：

```yaml
kafka_logger:
  formatter:
    fields:
      - name: trace_id
        dynamic_factory: app.context:get_trace_id
      - name: user_id
        dynamic_factory: app.auth:get_current_user_id
        default: anonymous
```

### 静态与动态工厂对比

- `static_factory`: 初始化时计算一次
- `dynamic_factory`: 每次 emit 计算
- `static_factory` 更高性能
- `dynamic_factory` 适合 request-scoped 或线程上下文数据

## 处理器实现

`KafkaLogHandler` 工作流程：
1. 初始化 KafkaProducer
2. 解析配置并建立 JSON formatter
3. 解析 `static_factory` 和 `dynamic_factory`
4. emit 时：
   - 调用动态工厂获取最新值
   - 注入 LogRecord
   - 格式化为 JSON
   - 发送到 Kafka

### 异常与容错

- 静态/动态工厂解析失败时打印警告，字段设置为 `None`
- KafkaProducer 使用自己的重试与错误处理策略

## 开发指南

### 代码风格

- 使用类型提示
- 使用 dataclass
- 遵循 PEP 8
- 为公共 API 编写 docstring

### 测试

- 测试结构应与源文件对应
- 使用 pytest fixture
- 模拟 Kafka 及网络依赖
- 优先测试配置、工厂解析和 JSON 输出

### 扩展说明

1. 新配置选项：更新 dataclass、解析函数、测试、文档、示例
2. 新静态工厂函数：添加 handler.py，写测试，文档说明
3. 新 formatter 特性：扩展 `FormatterConfig`，更新 handler，增加测试

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

### 运行测试

```bash
uv run pytest
uv run pytest tests/test_config.py
uv run pytest --cov=kafka_logger --cov-report=term-missing
```

### 代码检查

```bash
uv run ruff format .
uv run ruff check .
uv run mypy src/kafka_logger
```

### 构建

```bash
rm -rf dist/ build/ *.egg-info
uv build
uv run twine check dist/*
```

## 关键注意点

- YAML 配置必须显式提供
- 选择 `static_factory` 或 `dynamic_factory` 时，根据值是否会变化
- 动态工厂在高吞吐场景下可能带来性能开销
- 外部模块路径必须可导入

