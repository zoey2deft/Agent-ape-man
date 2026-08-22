"""第 08 课：识别 DeepSeek 兼容请求中的常见 SDK 异常。"""

import os

from dotenv import load_dotenv
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)


load_dotenv()

BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-v4-flash"
SIMULATE_AUTH_ERROR = False

real_api_key = os.getenv("DEEPSEEK_API_KEY")
api_key = "fake-key-for-practice" if SIMULATE_AUTH_ERROR else real_api_key
if not api_key:
    raise SystemExit("未找到 DEEPSEEK_API_KEY，请先配置环境变量或 .env。")

client = OpenAI(
    api_key=api_key,
    base_url=BASE_URL,
    timeout=15.0,
    max_retries=0,
)

try:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": "只回复：错误处理测试成功。"},
        ],
        max_tokens=50,
    )
except AuthenticationError:
    print("认证失败：请检查 API Key。")
except RateLimitError:
    print("请求过多：请稍后重试。")
except APITimeoutError:
    print("请求超时：服务未在规定时间内响应。")
except APIConnectionError:
    print("连接失败：请检查网络或 API 地址。")
except APIStatusError as error:
    print(f"API 返回 HTTP 错误：{error.status_code}")
else:
    print(response.choices[0].message.content)
