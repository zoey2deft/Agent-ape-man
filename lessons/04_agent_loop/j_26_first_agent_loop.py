"""第 26 课：让模型、工具和观察结果在一个循环中交替工作。"""

import json
import os
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from pydantic import BaseModel, ConfigDict, ValidationError


MODEL = "deepseek-flash"  # DeepSeek-V4.1-Flash 的 API 模型 ID
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
        "properties": {"city": {"type": "string", "enum": ["北京", "上海"]}},
        "required": ["city"],
        "additionalProperties": False,
    },
}


class WeatherArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    city: Literal["北京", "上海"]


def main() -> None:
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise SystemExit("未找到 DEEPSEEK_API_KEY，请配置环境变量或 .env。")

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com", timeout=20, max_retries=0)
    history: list[dict[str, object]] = [
        {"role": "user", "content": "请查询本地示例数据中的北京天气，再用一句中文回答。"}
    ]

    for round_number in range(1, MAX_ROUNDS + 1):
        print(f"第 {round_number} 轮：请求 DeepSeek")
        try:
            response = client.responses.create(
                model=MODEL,
                reasoning={"effort": "none"},
                instructions="只能依据工具结果回答天气问题。取得结果后直接回答。",
                input=history,
                tools=[WEATHER_TOOL],
                tool_choice="required" if round_number == 1 else "auto",
            )
        except OpenAIError:
            raise SystemExit("DeepSeek 请求失败，循环停止。") from None

        calls = [item for item in response.output if item.type == "function_call"]
        if not calls:
            if not response.output_text:
                raise SystemExit("模型没有给出回答，循环停止。")
            print("模型回答：", response.output_text)
            return

        for call in calls:
            if call.name != "get_weather":
                raise SystemExit(f"不允许执行工具：{call.name}")
            try:
                arguments = WeatherArguments.model_validate_json(call.arguments)
            except ValidationError:
                raise SystemExit("天气工具参数无效，循环停止。") from None
            result = {"city": arguments.city, **WEATHER_DATA[arguments.city]}
            history.append({
                "type": "function_call", "call_id": call.call_id,
                "name": call.name, "arguments": call.arguments,
            })
            history.append({
                "type": "function_call_output", "call_id": call.call_id,
                "output": json.dumps(result, ensure_ascii=False),
            })
            print("工具观察：", result)

    raise SystemExit(f"达到最多 {MAX_ROUNDS} 轮，循环停止。")


if __name__ == "__main__":
    main()
