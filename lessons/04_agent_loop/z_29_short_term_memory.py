"""第 29 课：用任务级短期记忆避免重复执行相同工具调用。"""

from __future__ import annotations

import json
import os
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Literal

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from pydantic import BaseModel, ConfigDict, ValidationError


MODEL = "deepseek-flash"
MAX_ROUNDS = 4

WEATHER_DATA = {
    "北京": {"condition": "晴", "temperature_c": 26},
    "上海": {"condition": "多云", "temperature_c": 28},
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
]


class WeatherArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    city: Literal["北京", "上海"]


class CalculateArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operation: Literal["add", "subtract", "multiply", "divide"]
    left: float
    right: float


class AgentLoopStopped(RuntimeError):
    """Agent 因失败或达到安全边界而停止。"""


@dataclass
class TaskState:
    """只保存完成当前任务所需的状态。"""

    history: list[dict[str, Any]]
    tool_cache: dict[str, str] = field(default_factory=dict)
    rounds_used: int = 0


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


TOOL_ROUTER: dict[str, ToolHandler] = {
    "get_weather": handle_get_weather,
    "calculate": handle_calculate,
}


def canonical_call_key(name: str, arguments_json: str) -> str:
    """把语义相同的 JSON 参数转换成稳定的缓存键。"""

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
    """优先复用当前任务的观察结果，否则执行工具并写入短期记忆。"""

    cache_key = canonical_call_key(name, arguments_json)
    cached_output = state.tool_cache.get(cache_key)
    if cached_output is not None:
        print(f"[记忆命中] {cache_key}")
        return cached_output

    observation = execute_tool(name, arguments_json)
    output = json.dumps(observation, ensure_ascii=False)
    state.tool_cache[cache_key] = output
    print(f"[记忆写入] {cache_key} -> {observation}")
    return output


def run_agent(client: OpenAI, user_task: str, *, max_rounds: int) -> str:
    state = TaskState(history=[{"role": "user", "content": user_task}])

    for round_number in range(1, max_rounds + 1):
        state.rounds_used = round_number
        print(f"\n[第 {round_number}/{max_rounds} 轮] 请求模型")

        try:
            response = client.responses.create(
                model=MODEL,
                reasoning={"effort": "none"},
                instructions=(
                    "你是任务助手。每次用户要求的天气查询都要调用 get_weather；"
                    "需要算术时调用 calculate。获得全部结果后再回答。"
                ),
                input=state.history,
                tools=TOOLS,
                tool_choice="auto",
            )
        except OpenAIError as error:
            raise AgentLoopStopped("模型请求失败。") from error

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

    try:
        run_agent(
            client,
            "请分别查询两次上海天气，确认两次结果是否一致。",
            max_rounds=MAX_ROUNDS,
        )
    except AgentLoopStopped as error:
        raise SystemExit(f"[停止] {error}") from None


if __name__ == "__main__":
    main()
