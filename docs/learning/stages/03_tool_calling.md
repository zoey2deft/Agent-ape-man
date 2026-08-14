# 阶段 3：Tool Calling

课程编号：16–25  
前置阶段：阶段 2  
阶段目标：完整理解“模型请求工具—应用执行—结果返回模型”的闭环。

## 核心数据流

```text
用户问题 → 模型选择工具 → 返回工具名和参数
        → Python 校验并执行 → 返回工具结果 → 模型生成最终回答
```

## 课程

| 课程 | 文件 | 唯一目标 |
|---|---|---|
| 16 | `lessons/16_local_function.py` | 编写一个与模型无关的普通 Python 工具 |
| 17 | `lessons/17_tool_schema.py` | 使用 JSON Schema 描述工具能力和参数 |
| 18 | `lessons/18_receive_tool_call.py` | 从模型响应中识别工具调用项 |
| 19 | `lessons/19_parse_arguments.py` | 解析并校验模型提供的参数 |
| 20 | `lessons/20_execute_tool.py` | 根据工具名安全路由到本地函数 |
| 21 | `lessons/21_return_tool_output.py` | 将结果关联到对应 call ID 并返回模型 |
| 22 | `lessons/22_multiple_tool_calls.py` | 在一次响应中处理多个工具调用 |
| 23 | `lessons/23_parallel_tools.py` | 并行执行互不依赖的工具 |
| 24 | `lessons/24_tool_error.py` | 将参数错误和执行错误转为可处理结果 |
| 25 | `lessons/25_human_approval.py` | 在有副作用的工具执行前等待确认 |

## 阶段作品

重新实现天气工具调用程序，支持一次查询多个城市、错误处理和敏感操作审批。

## 完成标准

- 能明确说明模型没有直接执行 Python 函数。
- 能解释工具 Schema 为什么影响模型的选择和参数。
- 能完成至少一轮工具调用和结果回传。
- 多工具调用不会遗漏 call ID 或混淆结果。
- 有副作用的工具默认不自动执行。

## 本阶段不学习

只实现有限工具闭环，不实现开放式自主 Agent Loop，不接入 MCP。

