# 阶段 0：环境与安全

课程编号：00–02  
前置要求：能阅读基本 Python 语句  
阶段目标：使用 uv 建立可复现环境，并安全准备 API 凭据与 SDK。

## 课程

| 课程 | 文件 | 唯一目标 |
|---|---|---|
| 00 | `lessons/00_env_check.py` | 确认 uv 选择的 Python 解释器和 `.venv` |
| 01 | `lessons/01_read_env_key.py` | 从环境变量读取 API Key，但绝不输出真实值 |
| 02 | `lessons/02_sdk_version.py` | 使用 `uv add` 安装并检查 OpenAI SDK 版本 |

## 阶段作品

一个能够通过 `uv run` 执行、环境可复现、密钥不进入源码的最小 Python 项目。

## 完成标准

- 能解释 `.python-version`、`pyproject.toml`、`uv.lock` 和 `.venv` 的职责。
- 能解释 `sys.executable`、`sys.prefix` 与工作目录的区别。
- 能使用 `uv run --env-file .env` 安全加载环境变量。
- 能使用 `uv add` 添加依赖，并说明为什么不直接 `pip install`。
- 代码和输出中不存在真实 API Key。

## 本阶段不学习

不发送真实模型请求，不讨论 Prompt、Streaming 或 Tool Calling。

