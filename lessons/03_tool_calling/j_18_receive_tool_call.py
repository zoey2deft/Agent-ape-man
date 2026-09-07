"""第 18 课：从 DeepSeek Responses 输出中识别工具调用项。"""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

API_KEY_ENV = "DEEPSEEK_API_KEY"
MODEL = "deepseek-v4-flash"
WEATHER_TOOL = {
    "type": "function",
    "name": "get_weather",
    "description": "查询指定城市的天气。",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "要查询的城市名称，例如北京。",
            }
        },
        "required": ["city"],
        "additionalProperties": False,
    },
}

api_key = os.getenv(API_KEY_ENV)

if not api_key:
    raise SystemExit(f"未找到 {API_KEY_ENV}，请先配置环境变量或 .env。")

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
response = client.responses.create(
    model=MODEL,
    reasoning={"effort": "none"},
    input="北京今天天气怎么样？",
    tools=[WEATHER_TOOL],
    tool_choice="required",
)

print("响应项类型：", [item.type for item in response.output])

tool_call = next(
    (item for item in response.output if item.type == "function_call"),
    None,
)

if tool_call is None:
    raise RuntimeError("模型没有返回 function_call 项。")

print("工具调用类型：", tool_call.type)
print("工具名称：", tool_call.name)
print("原始参数：", tool_call.arguments)
print("调用 ID：", tool_call.call_id)

print(response.output[0].model_dump_json(indent=2))
