"""阶段 1 作品：支持普通或流式输出的单轮命令行模型客户端。"""

import os

from dotenv import load_dotenv
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    InternalServerError,
    OpenAI,
    RateLimitError,
)


load_dotenv()

API_KEY_ENV = "DEEPSEEK_API_KEY"
MODEL = "deepseek-v4-flash"
INSTRUCTIONS = "始终使用中文回答。"

api_key = os.getenv(API_KEY_ENV)

if not api_key:
    raise SystemExit(f"未找到 {API_KEY_ENV}，请先配置环境变量或 .env。")

mode = input("请选择输出模式（1=普通，2=流式）：").strip()

if mode not in {"1", "2"}:
    raise SystemExit("模式无效，请输入 1 或 2。")

user_input = input("请输入你的问题：").strip()

if not user_input:
    raise SystemExit("问题不能为空。")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
    timeout=30.0,
)

try:
    if mode == "1":
        response = client.responses.create(
            model=MODEL,
            instructions=INSTRUCTIONS,
            input=user_input,
        )
        print("\n=== 模型回答 ===")
        print(response.output_text)
    else:
        stream = client.responses.create(
            model=MODEL,
            instructions=INSTRUCTIONS,
            input=user_input,
            stream=True,
        )
        print("\n=== 模型回答 ===")

        for event in stream:
            if event.type == "response.output_text.delta":
                print(event.delta, end="", flush=True)

        print()
except AuthenticationError:
    print("认证失败：请检查 DEEPSEEK_API_KEY。")
except RateLimitError:
    print("请求过快：请稍后重试。")
except APITimeoutError:
    print("请求超时：服务端没有在限定时间内响应。")
except APIConnectionError:
    print("连接失败：请检查网络和 API 地址。")
except InternalServerError:
    print("服务端错误：请稍后重试。")
except APIStatusError as error:
    print(f"API 返回错误状态：HTTP {error.status_code}。")
