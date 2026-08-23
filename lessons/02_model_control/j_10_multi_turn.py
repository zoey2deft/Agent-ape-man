"""第 10 课：由应用程序保存并重发显式历史，实现多轮对话。"""

import os
import json

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

API_KEY_ENV = "DEEPSEEK_API_KEY"
MODEL = "deepseek-v4-flash"
INSTRUCTIONS = "始终使用中文回答。"

api_key = os.getenv(API_KEY_ENV)

if not api_key:
    raise SystemExit(f"未找到 {API_KEY_ENV}，请先配置环境变量或 .env。")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
)

project_code = input("请输入一个要让模型记住的项目代号：").strip()

if not project_code:
    raise SystemExit("项目代号不能为空。")

history = [
    {
        "role": "user",
        "content": f"请记住：我的项目代号是 {project_code}。只回答‘已记住’。",
    }
]

first_response = client.responses.create(
    model=MODEL,
    instructions=INSTRUCTIONS,
    input=history,
)
print(f"第一轮模型：{first_response.output_text}")

history.append(
    {
        "role": "assistant",
        "content": first_response.output_text,
    }
)
history.append(
    {
        "role": "user",
        "content": "我刚才让你记住的项目代号是什么？只回答项目代号。",
    }
)

second_response = client.responses.create(
    model=MODEL,
    instructions=INSTRUCTIONS,
    input=history,
)
print(f"第二轮模型：{second_response.output_text}")

print(history)

print("\n=== 完整历史记录 ===")
print(json.dumps(history, ensure_ascii=False, indent=2))