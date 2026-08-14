# 阶段 8：生产工程与毕业项目

课程编号：69–76  
前置阶段：阶段 0–7  
阶段目标：把前面的实验整合成可配置、可追踪、可评测、受权限和预算约束的 Agent 应用。

## 课程

| 课程 | 文件 | 唯一目标 |
|---|---|---|
| 69 | `lessons/69_config_management.py` | 分离配置、凭据和代码 |
| 70 | `lessons/70_logging.py` | 记录不泄密的结构化日志 |
| 71 | `lessons/71_state_persistence.py` | 持久化和恢复会话状态 |
| 72 | `lessons/72_concurrency_budget.py` | 限制并发、轮次和工具调用预算 |
| 73 | `lessons/73_permissions.py` | 为工具应用最小权限原则 |
| 74 | `lessons/74_cost_limit.py` | 记录并限制 token、工具和总成本 |
| 75 | `lessons/75_regression_eval.py` | 用回归评测防止行为退化 |
| 76 | `lessons/76_final_agent.py` | 整合并运行毕业项目入口 |

## 毕业项目能力

- 命令行或简单服务入口。
- OpenAI Responses API 与 Agents SDK。
- 本地 Function Tools 和 MCP Tools。
- 带引用的 RAG 知识库。
- 多 Agent Handoff，但仅在职责确实需要时使用。
- 人工审批、最小权限、停止条件和预算限制。
- 结构化日志、Tracing、单元测试和回归评测。

## 完成标准

- 新环境仅通过 `uv sync` 即可复现。
- 所有凭据都在代码之外，日志不泄露敏感数据。
- 成功、工具失败、模型错误、超预算和人工拒绝都有明确行为。
- 核心工具有单元测试，Agent 行为有固定评测集。
- 能逐层解释最终项目，而不是只会运行它。
- 可以从 Trace 和日志定位一次失败发生在哪一层。

## 最终交付结构

```text
simpleag/
├── lessons/              # 00–76 独立学习实验
├── src/                  # 毕业项目实现
├── tests/                # 工具和应用测试
├── evals/                # Agent 评测数据与评分
├── docs/learning/        # 课程规划与进度
├── pyproject.toml
└── uv.lock
```

