"""第 13 课：读取 Responses API 返回的 token 用量。"""

import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-v4-flash"

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise SystemExit("未找到 DEEPSEEK_API_KEY，请先配置环境变量或 .env。")

client = OpenAI(
    api_key=api_key,
    base_url=BASE_URL,
)

short_input = "请确认你已经读完这句话。"
long_input = (
    "Agent 会接收目标、读取上下文、选择下一步，并根据结果继续处理。" * 40
    + "\n请确认你已经读完这些内容。"
)

for label, input_text in [("短输入", short_input), ("长输入", long_input)]:
    response = client.responses.create(
        model=MODEL_NAME,
        instructions="无论输入多长，都只回复：收到。",
        input=input_text,
        max_output_tokens=20,
        reasoning={"effort": "none"},
    )

    usage = response.usage
    if usage is None:
        raise SystemExit("响应中没有 token 用量信息。")

    print(f"{label}回答：{response.output_text}")
    print(f"{label} input_tokens：{usage.input_tokens}")
    print(f"{label} output_tokens：{usage.output_tokens}")
    print(f"{label} total_tokens：{usage.total_tokens}")
    print()
