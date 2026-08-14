# 阶段 7：Agents SDK 与 Multi-Agent

课程编号：61–68  
前置阶段：阶段 4，建议完成阶段 5 和阶段 6  
阶段目标：在理解底层循环后，使用 Agents SDK 构建可观测、可交接的多 Agent 系统。

## 课程

| 课程 | 文件 | 唯一目标 |
|---|---|---|
| 61 | `lessons/61_first_sdk_agent.py` | 使用 Agents SDK 运行第一个 Agent |
| 62 | `lessons/62_sdk_function_tool.py` | 给 SDK Agent 添加本地 Function Tool |
| 63 | `lessons/63_sdk_mcp_tool.py` | 让 SDK Agent 使用 MCP Server |
| 64 | `lessons/64_agent_handoff.py` | 将任务和回复所有权交给专业 Agent |
| 65 | `lessons/65_guardrail.py` | 对输入、输出或工具动作设置 Guardrail |
| 66 | `lessons/66_tracing.py` | 查看模型、工具、Handoff 的运行轨迹 |
| 67 | `lessons/67_multi_agent.py` | 编排多个职责明确的 Agent |
| 68 | `lessons/68_agent_eval.py` | 使用数据集和评分器评测 Agent 工作流 |

## 阶段作品

一个由总控 Agent、天气 Agent 和知识库 Agent 组成的系统，支持 Tool、MCP、Handoff、Guardrail 和 Trace。

## 完成标准

- 能指出 SDK 替手写 Agent Loop 完成了哪些工作。
- 每个 Agent 的职责、工具和交接条件清晰且不重叠。
- Handoff 后回复所有权明确。
- 关键失败可以从 Trace 中定位。
- 有固定数据集评测路由、工具调用和最终答案。

## 本阶段不学习

不以增加 Agent 数量代替合理设计；能由一个 Agent 完成的任务不拆成多个。

