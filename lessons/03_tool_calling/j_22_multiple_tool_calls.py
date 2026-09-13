"""第 22 课：处理一次响应中的多个工具调用。"""

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
    "description": "查询一个指定城市的天气；多个城市必须分别调用。",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "enum": ["北京", "上海", "深圳"],
            }
        },
        "required": ["city"],
        "additionalProperties": False,
    },
}


def get_weather(city: str) -> dict[str, str | int]:
    return {"city": city, **WEATHER_DATA[city]}


load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise SystemExit("未找到 DEEPSEEK_API_KEY，请先配置环境变量或 .env。")

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
user_input = "请分别查询北京和上海今天的天气。"

first_response = client.responses.create(
    model="deepseek-v4.1-flash-expires-on-0910",
    reasoning={"effort": "none"},
    instructions="每个城市分别调用一次 get_weather，不要合并城市参数。",
    input=user_input,
    tools=[WEATHER_TOOL],
    tool_choice="required",
)
tool_calls = [
    item for item in first_response.output if item.type == "function_call"
]

if not tool_calls:
    raise RuntimeError("模型没有返回任何 function_call。")

input_items = [{"role": "user", "content": user_input}]

for tool_call in tool_calls:
    input_items.append(
        {
            "type": "function_call",
            "call_id": tool_call.call_id,
            "name": tool_call.name,
            "arguments": tool_call.arguments,
        }
    )

for tool_call in tool_calls:
    if tool_call.name != "get_weather":
        raise ValueError(f"不允许执行工具：{tool_call.name}")

    arguments = WeatherArguments.model_validate_json(tool_call.arguments)
    tool_result = get_weather(arguments.city)
    input_items.append(
        {
            "type": "function_call_output",
            "call_id": tool_call.call_id,
            "output": json.dumps(tool_result, ensure_ascii=False),
        }
    )
    print(f"已处理 {arguments.city}：{tool_call.call_id}")

second_response = client.responses.create(
    model="deepseek-v4.1-flash-expires-on-0910",
    reasoning={"effort": "none"},
    instructions="根据所有工具结果，用一句中文回答用户。",
    input=input_items,
    tools=[WEATHER_TOOL],
    tool_choice="none",
)

print("工具调用数量：", len(tool_calls))
print("模型最终回答：", second_response.output_text)
