"""第 01 课：从环境变量读取 API Key，但绝不输出 Key 本身。"""

import os
from dotenv import load_dotenv

load_dotenv()

ENV_NAME = "OPENAI_API_KEY"

api_key = os.getenv(ENV_NAME)

if api_key:
    print(f"成功：已从环境变量读取 {ENV_NAME}。")
else:
    print(f"未找到：请先设置环境变量 {ENV_NAME}。")
