# Changelog

## [0.1.3]

### Changed

- **Breaking**: 删除 `get_default_config()` 函数
- **Breaking**: `generate_config` 删除 `-f` 参数，直接覆盖无校验
- 改用 `default_config.yaml` 配置模板文件（带完整注释）
- CLI 命令 `generate_config` 简化为直接复制模板

### Added

- `src/kafka_logger/default_config.yaml` - 带注释的配置模板

### Updated

- 文档更新：`CLAUDE.md`, `README.md`
- 测试更新：适配新的配置生成行为
- `pyproject.toml`: 添加 YAML 文件打包配置

## [0.1.2]

### Added

- Dynamic factory support
- Static factory support
- Enhanced configuration system
