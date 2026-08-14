# 阶段 1：API 调用基础

课程编号：03–09  
前置阶段：阶段 0  
阶段目标：理解一次 LLM 请求从本地程序到服务端再返回的完整过程。

## 课程

| 课程 | 文件 | 唯一目标 |
|---|---|---|
| 03 | `lessons/03_first_http_request.py` | 观察 HTTP 请求的 URL、Header、Body 和响应 |
| 04 | `lessons/04_first_response.py` | 使用 OpenAI SDK 发出第一次 Responses API 请求 |
| 05 | `lessons/05_inspect_response.py` | 查看响应对象和 `output_text` 的来源 |
| 06 | `lessons/06_instructions.py` | 区分开发者指令与用户输入 |
| 07 | `lessons/07_streaming.py` | 逐事件接收流式输出 |
| 08 | `lessons/08_api_errors.py` | 识别认证、限流、超时和服务端错误 |
| 09 | `lessons/09_async_request.py` | 使用异步客户端执行一个请求 |

## 阶段作品

一个支持普通输出或流式输出，并能友好报告常见错误的单轮命令行模型客户端。

## 完成标准

- 能画出客户端、网络、API 和模型之间的数据流。
- 能区分 SDK 对象与实际 HTTP 请求。
- 能读取最终文本，而不是依赖不稳定的对象打印结果。
- 能说明同步与异步调用的区别。
- 阶段作品可通过 `uv run` 执行。

## 本阶段不学习

不实现多轮记忆、工具调用或 Agent Loop。

