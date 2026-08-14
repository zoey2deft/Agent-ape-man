"""第 05 课：检查完整响应对象和 output_text 的来源。"""

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

response = client.responses.create(
    model="deepseek-v4-flash",
    input="用一句话解释：为什么 SDK 响应不是普通字符串？",
)

print("=== Python 对象类型 ===")
print(type(response).__name__)

print("\n=== 完整响应对象 ===")
print(response.model_dump_json(indent=2))

print("\n=== output_text 快捷属性 ===")
print(response.output_text)
