# 阶段 6：MCP

课程编号：47–60  
前置阶段：阶段 4；建议完成阶段 5  
阶段目标：理解并实现 MCP Server、Client、Tools、Resources、Prompts、审批和远程连接。

## 概念边界

- Tool Calling 是模型请求工具的交互模式。
- MCP 是客户端发现并调用工具、资源和提示模板的标准协议。
- RAG 是检索知识的技术，可以被包装为 MCP Tool 或 Resource，但不等于 MCP。

## 课程

| 课程 | 文件 | 唯一目标 |
|---|---|---|
| 47 | `lessons/47_first_mcp_server.py` | 启动最小本地 MCP Server |
| 48 | `lessons/48_mcp_function_tool.py` | 暴露第一个 MCP Tool |
| 49 | `lessons/49_mcp_tool_parameters.py` | 定义并校验 MCP Tool 参数 |
| 50 | `lessons/50_mcp_resource.py` | 暴露只读 MCP Resource |
| 51 | `lessons/51_mcp_prompt.py` | 暴露可复用 MCP Prompt |
| 52 | `lessons/52_first_mcp_client.py` | 建立 MCP Client 与 Server 的连接 |
| 53 | `lessons/53_mcp_list_tools.py` | 发现服务器提供的工具 |
| 54 | `lessons/54_mcp_call_tool.py` | 通过客户端调用一个 MCP Tool |
| 55 | `lessons/55_mcp_with_agent.py` | 让 Agent 使用 MCP 工具列表和结果 |
| 56 | `lessons/56_mcp_approval.py` | 在 MCP 工具执行前加入审批 |
| 57 | `lessons/57_mcp_security.py` | 防御提示注入、越权和数据泄露 |
| 58 | `lessons/58_remote_mcp.py` | 连接远程 MCP Server |
| 59 | `lessons/59_mcp_auth.py` | 理解 Token/OAuth 与凭据边界 |
| 60 | `lessons/60_mcp_error_handling.py` | 处理协议、网络和远程执行错误 |

## 阶段作品

将天气能力和一个只读知识资源做成 MCP Server，编写独立 Client，并让 Agent 在审批规则下调用它。

## 完成标准

- 能画出 Host、MCP Client、MCP Server 和外部服务的关系。
- 能解释 Tool、Resource 和 Prompt 的不同职责。
- Client 可以列出并调用 Server 工具。
- 敏感参数和返回数据不会被默认发送到不可信服务器。
- 远程连接有身份验证、超时和错误处理。

## 本阶段不学习

不把第三方 MCP Server 默认视为可信，不在没有审批的情况下执行有副作用操作。

