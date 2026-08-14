"""第 05 课：检查 DeepSeek Chat Completions 的响应对象结构。"""

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

response = client.chat.completions.create(
    model=MODEL_NAME,
    messages=[
        {"role": "user", "content": "只回复：正在检查响应对象。"},
    ],
    max_tokens=50,
)

print("=== 响应对象类型 ===")
print(type(response).__name__)

print("\n=== 完整响应对象 ===")
print(response.model_dump_json(indent=2))

print("\n=== 最终文本 ===")
print(response.choices[0].message.content)
