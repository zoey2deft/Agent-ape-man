"""第 10 课：使用 Responses API 显式维护多轮消息历史。"""

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

history = [
    {
        "role": "user",
        "content": "请记住：我的项目代号是银杏。只回复：记住了。",
    },
]

first_response = client.responses.create(
    model=MODEL_NAME,
    input=history,
    max_output_tokens=50,
    reasoning={"effort": "none"},
)
first_answer = first_response.output_text
print("第一轮助手：", first_answer)

history.append({"role": "assistant", "content": first_answer})
history.append({"role": "user", "content": "我的项目代号是什么？"})

second_response = client.responses.create(
    model=MODEL_NAME,
    input=history,
    max_output_tokens=50,
    reasoning={"effort": "none"},
)
second_answer = second_response.output_text
print("第二轮助手：", second_answer)
