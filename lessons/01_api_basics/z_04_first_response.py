"""第 04 课：使用 OpenAI Python SDK 调用 DeepSeek 兼容接口。"""

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
        {"role": "user", "content": "用一句话说明 SDK 相比手写 HTTP 的作用。"},
    ],
    max_tokens=90,
)
print(response.choices[0].message.content)
