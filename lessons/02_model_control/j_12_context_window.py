"""第 12 课：观察上下文截断如何造成早期信息丢失。"""

import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

API_KEY_ENV = "DEEPSEEK_API_KEY"
MODEL = "deepseek-v4-flash"
CONTEXT_MESSAGE_LIMIT = 3
INSTRUCTIONS = "仅依据本次收到的上下文回答；找不到项目代号时只回答‘无法确定’。"

api_key = os.getenv(API_KEY_ENV)

if not api_key:
    raise SystemExit(f"未找到 {API_KEY_ENV}，请先配置环境变量或 .env。")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
)

project_code = input("请输入要让模型记住的项目代号：").strip()

if not project_code:
    raise SystemExit("项目代号不能为空。")

full_history = [
    {
        "role": "user",
        "content": f"请记住：项目代号是 {project_code}。只回答‘已记住’。",
    }
]

first_response = client.responses.create(
    model=MODEL,
    instructions=INSTRUCTIONS,
    input=full_history,
)
print(f"第一轮模型：{first_response.output_text}")

full_history.append(
    {
        "role": "assistant",
        "content": first_response.output_text,
    }
)

# 用两组示例消息快速构造一段较长历史，避免为了演示而多次调用 API。
full_history.extend(
    [
        {"role": "user", "content": "补充：界面背景使用蓝色。"},
        {"role": "assistant", "content": "已记录界面背景使用蓝色。"},
        {"role": "user", "content": "补充：项目语言使用 Python。"},
        {"role": "assistant", "content": "已记录项目语言使用 Python。"},
        {"role": "user", "content": "最开始的项目代号是什么？"},
    ]
)

# 真实上下文窗口按 token 计算；这里用消息条数模拟“从开头丢弃旧内容”。
visible_context = full_history[-CONTEXT_MESSAGE_LIMIT:]
dropped_count = len(full_history) - len(visible_context)

print(f"完整历史消息数：{len(full_history)}")
print(f"本次发送消息数：{len(visible_context)}")
print(f"从开头丢弃消息数：{dropped_count}")
print("\n=== 模型实际收到的上下文 ===")

for message in visible_context:
    print(f"{message['role']}: {message['content']}")

second_response = client.responses.create(
    model=MODEL,
    instructions=INSTRUCTIONS,
    input=visible_context,
)

print(f"\n截断后模型：{second_response.output_text}")
