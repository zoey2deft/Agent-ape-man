"""第 26 课：用循环连接模型、工具调用和观察结果。"""

from __future__ import annotations

import json
import os
from typing import Any, Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, ConfigDict


MODEL = "deepseek-flash"

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
    """应用层允许传给天气工具的参数。"""

    model_config = ConfigDict(extra="forbid")

    city: Literal["北京", "上海"]


def get_weather(arguments: WeatherArguments) -> dict[str, str | int]:
    """执行本地工具；模型只负责提出调用请求。"""

    return {"city": arguments.city, **WEATHER_DATA[arguments.city]}


def run_agent(client: OpenAI, user_task: str) -> str:
    """重复“决策、行动、观察”，直到模型给出最终回答。"""

    history: list[dict[str, Any]] = [{"role": "user", "content": user_task}]
    round_number = 0

    while True:
        round_number += 1
        print(f"\n[第 {round_number} 轮] 请求模型")

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

        # DeepSeek Responses API 是无状态的，下一轮需要完整的历史。
        history.extend(
            item.model_dump(mode="json", exclude_none=True) for item in response.output
        )

        tool_calls = [item for item in response.output if item.type == "function_call"]
        if not tool_calls:
            final_answer = response.output_text.strip()
            if not final_answer:
                raise RuntimeError("模型既没有调用工具，也没有给出最终回答。")

            print(f"[完成] {final_answer}")
            return final_answer

        for tool_call in tool_calls:
            if tool_call.name != "get_weather":
                raise RuntimeError(f"拒绝执行未知工具：{tool_call.name}")

            arguments = WeatherArguments.model_validate_json(tool_call.arguments)
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
    run_agent(client, "请查询本地示例数据中的上海天气，再给我一句出门建议。")


if __name__ == "__main__":
    main()
