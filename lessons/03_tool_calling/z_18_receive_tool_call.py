"""第 18 课：从 Responses API 响应中识别工具调用项。"""

import os

from dotenv import load_dotenv
from openai import OpenAI

from z_17_tool_schema import TOOLS


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

found_tool_call = False

for item in response.output:
    print("响应项类型：", item.type)

    if item.type == "function_call":
        found_tool_call = True
        print("识别到工具调用")
        print("工具名：", item.name)
        print("原始参数：", item.arguments)

if not found_tool_call:
    print("本次响应中没有工具调用。")
