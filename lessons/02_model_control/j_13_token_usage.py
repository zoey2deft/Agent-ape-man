"""第 13 课：读取 token 用量，并观察上下文增长。"""

import os

from dotenv import load_dotenv
from openai import OpenAI


def print_usage(label: str, response: object) -> None:
    usage = response.usage

    if usage is None:
        raise SystemExit(f"{label}响应没有返回 token 用量。")

    print(f"\n=== {label} ===")
    print(f"模型回答：{response.output_text}")
    print(f"输入 token：{usage.input_tokens}")
    print(f"输出 token：{usage.output_tokens}")
    print(f"总 token：{usage.total_tokens}")


load_dotenv()

API_KEY_ENV = "DEEPSEEK_API_KEY"
MODEL = "deepseek-v4-flash"
INSTRUCTIONS = "只回答‘已收到’，不要补充解释。"
BACKGROUND_SENTENCE = "这是用于观察上下文增长的项目背景信息。"

api_key = os.getenv(API_KEY_ENV)

if not api_key:
    raise SystemExit(f"未找到 {API_KEY_ENV}，请先配置环境变量或 .env。")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
)

short_input = "请确认收到这条短消息。"
long_input = BACKGROUND_SENTENCE * 20 + "\n请确认收到以上背景。"

short_response = client.responses.create(
    model=MODEL,
    instructions=INSTRUCTIONS,
    input=short_input,
)

long_response = client.responses.create(
    model=MODEL,
    instructions=INSTRUCTIONS,
    input=long_input,
)

print_usage("短上下文", short_response)
print_usage("长上下文", long_response)

if short_response.usage is None or long_response.usage is None:
    raise SystemExit("无法比较输入 token。")

input_growth = long_response.usage.input_tokens - short_response.usage.input_tokens
print(f"\n上下文增长带来的输入 token 增量：{input_growth}")
