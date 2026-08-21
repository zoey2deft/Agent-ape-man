"""第 08 课：识别并友好报告常见 API 错误。"""

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
USE_FAKE_KEY = True 
USE_FAKE_URL = "https://127.0.0.1:1"

api_key = os.getenv(API_KEY_ENV)

if not api_key:
    raise SystemExit(f"未找到 {API_KEY_ENV}，请先配置环境变量或 .env。")

client = OpenAI(
    api_key="lesson-invalid-key" if USE_FAKE_KEY else api_key,
    base_url="https://api.deepseek.com",
    # base_url=USE_FAKE_URL,
    timeout=3.0,
    max_retries=0,
)

try:
    response = client.responses.create(
        model="deepseek-v4-flash",
        input="只回复：请求成功。",
    )
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
else:
    print(response.output_text)
