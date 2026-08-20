"""第 06 课：区分系统指令与用户输入。"""

import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-v4-flash"

SYSTEM_INSTRUCTION = "你是一名极简技术老师。回答必须只有一句话，不超过 30 个汉字。"
USER_INPUT = "什么是 SDK？"

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
        {"role": "system", "content": SYSTEM_INSTRUCTION},
        {"role": "user", "content": USER_INPUT},
    ],
    max_tokens=80,
)

print(response.choices[0].message.content)
