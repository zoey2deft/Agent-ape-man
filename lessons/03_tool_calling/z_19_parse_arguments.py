"""第 19 课：解析并校验模型提供的工具参数。"""

import json
import os
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from z_17_tool_schema import TOOLS


class WeatherArguments(BaseModel):
    """get_weather 工具允许接收的参数。"""

    model_config = ConfigDict(extra="forbid")

    city: str = Field(min_length=1)
    unit: Literal["celsius", "fahrenheit"] = "celsius"


load_dotenv()

BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-v4-flash"

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise SystemExit("未找到 DEEPSEEK_API_KEY，请先配置环境变量或 .env。")

client = OpenAI(api_key=api_key, base_url=BASE_URL)

response = client.responses.create(
    model=MODEL_NAME,
    input="上海天气怎么样？",
    tools=TOOLS,
    tool_choice="required",
    max_output_tokens=200,
    reasoning={"effort": "none"},
)

for item in response.output:
    if item.type != "function_call":
        continue

    try:
        arguments_dict = json.loads(item.arguments)
        arguments = WeatherArguments.model_validate(arguments_dict)
    except json.JSONDecodeError as error:
        print("参数不是合法 JSON：", error)
    except ValidationError as error:
        print("参数不符合工具约定：", error)
    else:
        print("原始参数类型：", type(item.arguments).__name__)
        print("解析后类型：", type(arguments_dict).__name__)
        print("校验后的参数：", arguments.model_dump())
