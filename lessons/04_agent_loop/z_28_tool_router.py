"""第 28 课：使用显式路由把模型请求分发给多个本地工具。"""

from __future__ import annotations

import json
import os
from collections.abc import Callable
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
                "city": {
                    "type": "string",
                    "enum": ["北京", "上海"],
                    "description": "要查询的城市。",
                }
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

    return {
        "operation": arguments.operation,
        "left": left,
        "right": right,
        "result": result,
    }


# 只有这里登记过的名字才能映射到 Python 函数。
TOOL_ROUTER: dict[str, ToolHandler] = {
    "get_weather": handle_get_weather,
    "calculate": handle_calculate,
}


def execute_tool(name: str, arguments_json: str) -> dict[str, Any]:
    """通过显式白名单路由工具，绝不根据名称执行任意代码。"""

    handler = TOOL_ROUTER.get(name)
    if handler is None:
        raise AgentLoopStopped(f"拒绝执行未知工具：{name}")

    try:
        return handler(arguments_json)
    except ValidationError as error:
        raise AgentLoopStopped(f"工具 {name} 的参数无效。") from error


def run_agent(client: OpenAI, user_task: str, *, max_rounds: int) -> str:
    history: list[dict[str, Any]] = [{"role": "user", "content": user_task}]

    for round_number in range(1, max_rounds + 1):
        print(f"\n[第 {round_number}/{max_rounds} 轮] 请求模型")

        try:
            response = client.responses.create(
                model=MODEL,
                reasoning={"effort": "none"},
                instructions=(
                    "你是任务助手。天气必须查询 get_weather，算术必须调用 calculate；"
                    "拿到全部工具结果后再给出简洁中文回答。"
                ),
                input=history,
                tools=TOOLS,
                tool_choice="auto",
            )
        except OpenAIError as error:
            raise AgentLoopStopped("模型请求失败。") from error

        history.extend(
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
            observation = execute_tool(tool_call.name, tool_call.arguments)
            print(f"[路由] {tool_call.name} -> {TOOL_ROUTER[tool_call.name].__name__}")
            print(f"[观察] {observation}")
            history.append(
                {
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": json.dumps(observation, ensure_ascii=False),
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
            "查询上海天气，再计算 18 乘以 7，最后一起告诉我。",
            max_rounds=MAX_ROUNDS,
        )
    except AgentLoopStopped as error:
        raise SystemExit(f"[停止] {error}") from None


if __name__ == "__main__":
    main()
