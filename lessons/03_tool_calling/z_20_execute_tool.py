"""第 20 课：根据工具名安全路由到本地函数。"""

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

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise SystemExit("未找到 DEEPSEEK_API_KEY，请先配置环境变量或 .env。")

client = OpenAI(api_key=api_key, base_url=BASE_URL)

response = client.responses.create(
    model=MODEL_NAME,
    input="上海天气怎么样？请使用摄氏度。",
    tools=TOOLS,
    tool_choice="required",
    max_output_tokens=200,
    reasoning={"effort": "none"},
)

for item in response.output:
    if item.type != "function_call":
        continue

    arguments_dict = json.loads(item.arguments)
    arguments = WeatherArguments.model_validate(arguments_dict)

    tool_function = TOOL_FUNCTIONS.get(item.name)
    if tool_function is None:
        print("拒绝执行未知工具：", item.name)
        continue

    tool_result = tool_function(city=arguments.city)
    print("允许执行工具：", item.name)
    print("本地工具结果：", tool_result)
