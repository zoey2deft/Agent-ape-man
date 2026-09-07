"""第 21 课：把工具结果关联到 call_id 并返回 DeepSeek。"""

import json
import os
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, ConfigDict


class WeatherArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    city: Literal["北京", "上海", "深圳"]


WEATHER_DATA = {
    "北京": {"condition": "晴", "temperature_c": 26},
    "上海": {"condition": "多云", "temperature_c": 28},
    "深圳": {"condition": "阵雨", "temperature_c": 30},
}
WEATHER_TOOL = {
    "type": "function",
    "name": "get_weather",
    "description": "查询指定城市的天气。",
    "parameters": {
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"],
        "additionalProperties": False,
    },
}


def get_weather(city: str) -> dict[str, str | int]:
    """返回本地模拟天气。"""
    return {"city": city, **WEATHER_DATA[city]}


load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise SystemExit("未找到 DEEPSEEK_API_KEY，请先配置环境变量或 .env。")

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
user_input = "北京今天天气怎么样？"

first_response = client.responses.create(
    model="deepseek-v4-flash",
    reasoning={"effort": "none"},
    input=user_input,
    tools=[WEATHER_TOOL],
    tool_choice="required",
)
tool_call = next(
    item for item in first_response.output if item.type == "function_call"
)

if tool_call.name != "get_weather":
    raise ValueError(f"不允许执行工具：{tool_call.name}")

arguments = WeatherArguments.model_validate_json(tool_call.arguments)
tool_result = get_weather(arguments.city)
tool_output = json.dumps(tool_result, ensure_ascii=False)

second_response = client.responses.create(
    model="deepseek-v4-flash",
    reasoning={"effort": "none"},
    instructions="根据工具结果，用一句中文回答用户。",
    input=[
        {"role": "user", "content": user_input},
        {
            "type": "function_call",
            "call_id": tool_call.call_id,
            "name": tool_call.name,
            "arguments": tool_call.arguments,
        },
        {
            "type": "function_call_output",
            "call_id": tool_call.call_id,
            "output": tool_output,
        },
    ],
    tools=[WEATHER_TOOL],
    tool_choice="none",
)

print("工具调用 ID：", tool_call.call_id)
print("本地工具结果：", tool_output)
print("模型最终回答：", second_response.output_text)
