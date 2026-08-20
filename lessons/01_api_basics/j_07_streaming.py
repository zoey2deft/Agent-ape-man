"""第 07 课：逐事件接收并打印流式文本。"""

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

stream = client.responses.create(
    model="deepseek-v4-flash",
    instructions="使用中文回答，并写两个简短句子。",
    input="解释流式输出为什么能改善用户体验。",
    stream=True,
)

print("=== 流式文本 ===")

last_event = None
last_text_event = None
last_text_event_delta = None

for event in stream:
    last_event = event

    if event.type == "response.output_text.delta":
        print(event.delta, end="", flush=True)
        last_text_event = event
        last_text_event_delta = event.delta

print("\n=== 最后一个文本事件 ===")
print(last_text_event.model_dump_json(indent=2))

print("\n=== 最后一个文本事件delta ===")
print(last_text_event_delta)

# print("\n=== 最后一个事件 ===")
# print(last_event.model_dump_json(indent=2))