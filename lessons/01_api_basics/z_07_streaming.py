"""第 07 课：逐块接收并打印 DeepSeek 的流式响应。"""

import os
import sys

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

stream = client.chat.completions.create(
    model=MODEL_NAME,
    messages=[
        {"role": "user", "content": "用五句话解释流式输出，并给出一个应用场景。"},
    ],
    max_tokens=600,
    stream=True,
)
i=0
o=0
p=0
for chunk in stream:
    # chunk.choices[0].finish_reason=None
    o=o+1
    if not chunk.choices:
        i=i+1
        continue

    content = chunk.choices[0].delta.content
    if content:
        p=p+1
        print(content, end="", flush=True)
    # if chunk.choices and chunk.choices[0].finish_reason:
    #     print("结束原因:", chunk.choices[0].finish_reason) 
print()
print("循环",o,i,p)

