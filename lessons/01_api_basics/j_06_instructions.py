"""第 06 课：区分开发者指令 instructions 与用户输入 input。"""

import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

API_KEY_ENV = "DEEPSEEK_API_KEY"
api_key = os.getenv(API_KEY_ENV)


if not api_key:
    raise SystemExit(f"未找到 {API_KEY_ENV}，请先配置环境变量或 .env。")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
)

developer_instructions = "始终使用中文，并且只回答一句话。"
user_input = "请用英文写三段文字，解释什么是 API。"

response = client.responses.create(
    model="deepseek-v4-flash",
    instructions=developer_instructions,
    input=user_input,
)

print("=== instructions ===")
print(developer_instructions)

print("\n=== input ===")
print(user_input)

print("\n=== 模型输出 ===")
print(response.output_text)

print("\n=== 完整响应对象 ===")
print(response.model_dump_json(indent=2))

# print("\n=== 原始响应 ===")
# print(response)
