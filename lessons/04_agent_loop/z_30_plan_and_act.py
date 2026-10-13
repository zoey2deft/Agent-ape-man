"""第 30 课：区分不可执行的计划信息与受控的实际动作。"""

from __future__ import annotations

import json
import os
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Literal

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from pydantic import BaseModel, ConfigDict, Field, ValidationError


MODEL = "deepseek-flash"
MAX_ROUNDS = 5

WEATHER_DATA = {
    "北京": {"condition": "晴", "temperature_c": 26},
    "上海": {"condition": "多云", "temperature_c": 28},
}

LOCAL_NOTES = {
    "出门清单": "晴天带水并注意防晒；多云天气可以随身带一把折叠伞。",
    "计算说明": "涉及数字计算时必须使用计算器工具，不要心算后冒充工具结果。",
}

TOOLS = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "查询本地示例天气数据。",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "enum": ["北京", "上海"]}
            },
            "required": ["city"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "calculate",
        "description": "执行两个数字之间的基础算术。",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                },
                "left": {"type": "number"},
                "right": {"type": "number"},
            },
            "required": ["operation", "left", "right"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "local_search",
        "description": "按关键词搜索本地笔记。",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "minLength": 1},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
]

PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "steps": {
            "type": "array",
            "minItems": 1,
            "maxItems": 6,
            "items": {
                "type": "object",
                "properties": {
                    "goal": {"type": "string"},
                    "suggested_tool": {
                        "type": "string",
                        "enum": [
                            "get_weather",
                            "calculate",
                            "local_search",
                            "none",
                        ],
                    },
                },
                "required": ["goal", "suggested_tool"],
                "additionalProperties": False,
            },
        },
        "done_when": {"type": "string"},
    },
    "required": ["steps", "done_when"],
    "additionalProperties": False,
}


class WeatherArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    city: Literal["北京", "上海"]


class CalculateArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operation: Literal["add", "subtract", "multiply", "divide"]
    left: float
    right: float


class SearchArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1)


class PlanStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    goal: str
    suggested_tool: Literal[
        "get_weather", "calculate", "local_search", "none"
    ]


class TaskPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    steps: list[PlanStep] = Field(min_length=1, max_length=6)
    done_when: str


class AgentLoopStopped(RuntimeError):
    """Agent 因失败或达到安全边界而停止。"""


@dataclass
class TaskState:
    plan: TaskPlan
    history: list[dict[str, Any]]
    tool_cache: dict[str, str] = field(default_factory=dict)


ToolHandler = Callable[[str], dict[str, Any]]


def handle_get_weather(arguments_json: str) -> dict[str, Any]:
    arguments = WeatherArguments.model_validate_json(arguments_json)
    return {"city": arguments.city, **WEATHER_DATA[arguments.city]}


def handle_calculate(arguments_json: str) -> dict[str, Any]:
    arguments = CalculateArguments.model_validate_json(arguments_json)
    left = arguments.left
    right = arguments.right

    match arguments.operation:
        case "add":
            result = left + right
        case "subtract":
            result = left - right
        case "multiply":
            result = left * right
        case "divide":
            if right == 0:
                raise AgentLoopStopped("除数不能为零。")
            result = left / right

    return {"result": result}


def handle_local_search(arguments_json: str) -> dict[str, Any]:
    arguments = SearchArguments.model_validate_json(arguments_json)
    query = arguments.query.casefold()
    matches = [
        {"title": title, "content": content}
        for title, content in LOCAL_NOTES.items()
        if query in title.casefold() or query in content.casefold()
    ]
    return {"query": arguments.query, "matches": matches}


TOOL_ROUTER: dict[str, ToolHandler] = {
    "get_weather": handle_get_weather,
    "calculate": handle_calculate,
    "local_search": handle_local_search,
}


def canonical_call_key(name: str, arguments_json: str) -> str:
    try:
        arguments = json.loads(arguments_json)
    except json.JSONDecodeError as error:
        raise AgentLoopStopped(f"工具 {name} 的参数不是合法 JSON。") from error

    normalized = json.dumps(arguments, ensure_ascii=False, sort_keys=True)
    return f"{name}:{normalized}"


def execute_tool(name: str, arguments_json: str) -> dict[str, Any]:
    handler = TOOL_ROUTER.get(name)
    if handler is None:
        raise AgentLoopStopped(f"拒绝执行未知工具：{name}")

    try:
        return handler(arguments_json)
    except ValidationError as error:
        raise AgentLoopStopped(f"工具 {name} 的参数无效。") from error


def observe_tool(state: TaskState, name: str, arguments_json: str) -> str:
    cache_key = canonical_call_key(name, arguments_json)
    cached_output = state.tool_cache.get(cache_key)
    if cached_output is not None:
        print(f"[记忆命中] {cache_key}")
        return cached_output

    observation = execute_tool(name, arguments_json)
    output = json.dumps(observation, ensure_ascii=False)
    state.tool_cache[cache_key] = output
    print(f"[动作] {name}({arguments_json})")
    print(f"[观察] {observation}")
    return output


def create_plan(client: OpenAI, user_task: str) -> TaskPlan:
    """只生成描述性计划；此函数不会执行任何工具。"""

    try:
        response = client.responses.create(
            model=MODEL,
            reasoning={"effort": "none"},
            instructions=(
                "把任务拆成简短步骤。计划只描述目标和建议工具，"
                "不得声称工具已经执行或结果已经获得。"
            ),
            input=user_task,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "task_plan",
                    "schema": PLAN_SCHEMA,
                }
            },
        )
    except OpenAIError as error:
        raise AgentLoopStopped("生成计划时模型请求失败。") from error

    try:
        return TaskPlan.model_validate_json(response.output_text)
    except ValidationError as error:
        raise AgentLoopStopped("模型返回了无效计划。") from error


def print_plan(plan: TaskPlan) -> None:
    print("[计划]")
    for index, step in enumerate(plan.steps, start=1):
        print(f"  {index}. {step.goal}（建议：{step.suggested_tool}）")
    print(f"  完成条件：{plan.done_when}")


def run_action_loop(
    client: OpenAI,
    user_task: str,
    plan: TaskPlan,
    *,
    max_rounds: int,
) -> str:
    """执行动作循环；计划不能绕过工具路由和参数校验。"""

    state = TaskState(
        plan=plan,
        history=[{"role": "user", "content": user_task}],
    )
    plan_json = plan.model_dump_json()

    for round_number in range(1, max_rounds + 1):
        print(f"\n[执行 {round_number}/{max_rounds}] 请求模型")

        try:
            response = client.responses.create(
                model=MODEL,
                reasoning={"effort": "none"},
                instructions=(
                    "你是任务执行助手。计划仅供参考，不代表任何动作已经完成。"
                    "天气、算术和本地搜索必须分别调用对应工具；"
                    "只有工具返回的观察结果可以作为执行结果。"
                    f"\n参考计划：{plan_json}"
                ),
                input=state.history,
                tools=TOOLS,
                tool_choice="auto",
            )
        except OpenAIError as error:
            raise AgentLoopStopped("执行计划时模型请求失败。") from error

        state.history.extend(
            item.model_dump(mode="json", exclude_none=True) for item in response.output
        )
        tool_calls = [item for item in response.output if item.type == "function_call"]

        if not tool_calls:
            final_answer = response.output_text.strip()
            if not final_answer:
                raise AgentLoopStopped("模型没有给出可执行动作或最终回答。")

            print(f"[成功停止] {final_answer}")
            return final_answer

        for tool_call in tool_calls:
            output = observe_tool(state, tool_call.name, tool_call.arguments)
            state.history.append(
                {
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": output,
                }
            )

    raise AgentLoopStopped(f"已达到最大轮次 {max_rounds}，任务尚未完成。")


def run_agent(client: OpenAI, user_task: str, *, max_rounds: int) -> str:
    plan = create_plan(client, user_task)
    print_plan(plan)
    return run_action_loop(client, user_task, plan, max_rounds=max_rounds)


def main() -> None:
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise SystemExit("未找到 DEEPSEEK_API_KEY，请配置环境变量或 .env。")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
        timeout=30.0,
        max_retries=1,
    )
    user_task = (
        "查询上海天气，计算 18 乘以 7，再搜索本地的出门清单，最后综合回答。"
    )

    try:
        run_agent(client, user_task, max_rounds=MAX_ROUNDS)
    except AgentLoopStopped as error:
        raise SystemExit(f"[停止] {error}") from None


if __name__ == "__main__":
    main()
