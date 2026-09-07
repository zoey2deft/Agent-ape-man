"""第 21 课：将本地工具结果关联到 call_id 并返回模型。"""

import json
import os
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, ConfigDict, Field

from z_16_local_function import get_weather
from z_17_tool_schema import TOOLS


class WeatherArguments(BaseModel):
    """get_weather 工具允许接收的参数。"""

    model_config = ConfigDict(extra="forbid")

    city: str = Field(min_length=1)
    unit: Literal["celsius", "fahrenheit"] = "celsius"


TOOL_FUNCTIONS = {
    "get_weather": get_weather,
}

load_dotenv()

BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-v4-flash"
USER_INPUT = "深圳天气怎么样？请使用摄氏度。"

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise SystemExit("未找到 DEEPSEEK_API_KEY，请先配置环境变量或 .env。")

client = OpenAI(api_key=api_key, base_url=BASE_URL)

input_items = [{"role": "user", "content": USER_INPUT}]

first_response = client.responses.create(
    model=MODEL_NAME,
    input=input_items,
    tools=TOOLS,
    tool_choice="required",
    max_output_tokens=200,
    reasoning={"effort": "none"},
)

tool_call = next(
    (item for item in first_response.output if item.type == "function_call"),
    None,
)
if tool_call is None:
    raise SystemExit("模型没有返回工具调用。")

arguments_dict = json.loads(tool_call.arguments)
arguments = WeatherArguments.model_validate(arguments_dict)

tool_function = TOOL_FUNCTIONS.get(tool_call.name)
if tool_function is None:
    raise SystemExit(f"拒绝执行未知工具：{tool_call.name}")
print("请求 call_id：", tool_call.call_id)
tool_result = tool_function(city=arguments.city)
print("本地工具结果：", tool_result)

input_items.extend(first_response.output)
input_items.append(
    {
        "type": "function_call_output",
        "call_id": tool_call.call_id,
        "output": tool_result,
    }
)
print("回传 call_id：", input_items[-1]["call_id"])

final_response = client.responses.create(
    model=MODEL_NAME,
    input=input_items,
    max_output_tokens=200,
    reasoning={"effort": "none"},
)

print("模型最终回答：", final_response.output_text)
