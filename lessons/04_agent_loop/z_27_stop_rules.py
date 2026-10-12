"""第 27 课：让 Agent Loop 无论成功或失败都能明确停止。"""

from __future__ import annotations

import json
import os
from typing import Any, Literal

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from pydantic import BaseModel, ConfigDict, ValidationError


MODEL = "deepseek-flash"
MAX_ROUNDS = 3

WEATHER_DATA = {
    "北京": {"condition": "晴", "temperature_c": 26},
    "上海": {"condition": "多云", "temperature_c": 28},
}

WEATHER_TOOL = {
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
}


class WeatherArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    city: Literal["北京", "上海"]


class AgentLoopStopped(RuntimeError):
    """Agent 因失败或达到安全边界而停止。"""


def get_weather(arguments: WeatherArguments) -> dict[str, str | int]:
    return {"city": arguments.city, **WEATHER_DATA[arguments.city]}


def run_agent(client: OpenAI, user_task: str, *, max_rounds: int) -> str:
    """执行有界 Agent Loop，并在每一种终止路径上给出明确结果。"""

    if max_rounds < 1:
        raise ValueError("max_rounds 必须大于或等于 1。")

    history: list[dict[str, Any]] = [{"role": "user", "content": user_task}]

    for round_number in range(1, max_rounds + 1):
        print(f"\n[第 {round_number}/{max_rounds} 轮] 请求模型")

        try:
            response = client.responses.create(
                model=MODEL,
                reasoning={"effort": "none"},
                instructions=(
                    "你是天气助手。回答天气问题前必须调用 get_weather；"
                    "获得工具结果后，用一句中文回答，不要编造工具未提供的信息。"
                ),
                input=history,
                tools=[WEATHER_TOOL],
                tool_choice="auto",
            )
        except OpenAIError as error:
            raise AgentLoopStopped("模型请求失败。") from error

        history.extend(
            item.model_dump(mode="json", exclude_none=True) for item in response.output
        )
        tool_calls = [item for item in response.output if item.type == "function_call"]

        # 成功停止：模型不再请求工具，并给出了非空最终回答。
        if not tool_calls:
            final_answer = response.output_text.strip()
            if not final_answer:
                raise AgentLoopStopped("模型既没有调用工具，也没有给出最终回答。")

            print(f"[成功停止] {final_answer}")
            return final_answer

        for tool_call in tool_calls:
            if tool_call.name != "get_weather":
                raise AgentLoopStopped(f"拒绝执行未知工具：{tool_call.name}")

            try:
                arguments = WeatherArguments.model_validate_json(tool_call.arguments)
            except ValidationError as error:
                raise AgentLoopStopped("天气工具参数无效。") from error

            observation = get_weather(arguments)
            print(f"[动作] get_weather(city={arguments.city!r})")
            print(f"[观察] {observation}")

            history.append(
                {
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": json.dumps(observation, ensure_ascii=False),
                }
            )

    # 上限停止：模型仍想继续，但应用拒绝进入下一轮。
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
            "请查询本地示例数据中的上海天气，再给我一句出门建议。",
            max_rounds=MAX_ROUNDS,
        )
    except AgentLoopStopped as error:
        raise SystemExit(f"[停止] {error}") from None


if __name__ == "__main__":
    main()
