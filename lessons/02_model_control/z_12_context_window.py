"""第 12 课：模拟上下文截断造成的信息丢失。"""

import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-v4-flash"
KEEP_LAST_MESSAGES = 5

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise SystemExit("未找到 DEEPSEEK_API_KEY，请先配置环境变量或 .env。")

client = OpenAI(
    api_key=api_key,
    base_url=BASE_URL,
)

history = [
    {"role": "user", "content": "请记住：演示代号是 Q7-NIMBUS-482。"},
    {"role": "assistant", "content": "记住了。"},
    {"role": "user", "content": "请用一个词评价 Python。"},
    {"role": "assistant", "content": "灵活。"},
    {
        "role": "user",
        "content": "演示代号是什么？如果上下文中没有答案，只回复：不知道。",
    },
]

visible_history = history[-KEEP_LAST_MESSAGES:]

print("完整历史消息数：", len(history))
print("截断后消息数：", len(visible_history))
print("模型实际看到的历史：", visible_history)

response = client.responses.create(
    model=MODEL_NAME,
    input=visible_history,
    max_output_tokens=30,
    reasoning={"effort": "none"},
)

print("模型回答：", response.output_text)
