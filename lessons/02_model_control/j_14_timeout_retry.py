"""第 14 课：为暂时性错误实现有上限的指数退避重试。"""

import os
import time

from dotenv import load_dotenv
from openai import (
    APIConnectionError,
    APITimeoutError,
    InternalServerError,
    OpenAI,
    RateLimitError,
)


class SimulatedTransientError(Exception):
    """用于稳定演示暂时性失败，不代表真实 SDK 异常。"""


load_dotenv()

API_KEY_ENV = "DEEPSEEK_API_KEY"
MODEL = "deepseek-v4-flash"
MAX_ATTEMPTS = 4
SIMULATED_FAILURES = 2
BASE_DELAY_SECONDS = 0.5
MAX_DELAY_SECONDS = 2.0
RETRYABLE_ERRORS = (
    SimulatedTransientError,
    APIConnectionError,
    APITimeoutError,
    RateLimitError,
    InternalServerError,
)

api_key = os.getenv(API_KEY_ENV)

if not api_key:
    raise SystemExit(f"未找到 {API_KEY_ENV}，请先配置环境变量或 .env。")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
    timeout=10.0,
    max_retries=0,
)


def create_response_with_retry():
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            print(f"第 {attempt}/{MAX_ATTEMPTS} 次尝试")

            if attempt <= SIMULATED_FAILURES:
                raise SimulatedTransientError("模拟暂时性服务故障")

            return client.responses.create(
                model=MODEL,
                input="只回答：重试成功。",
            )
        except RETRYABLE_ERRORS as error:
            if attempt == MAX_ATTEMPTS:
                print("已达到最大尝试次数，停止重试。")
                raise

            delay = min(
                BASE_DELAY_SECONDS * 2 ** (attempt - 1),
                MAX_DELAY_SECONDS,
            )
            print(f"捕获 {type(error).__name__}，等待 {delay} 秒后重试。")
            time.sleep(delay)

    raise RuntimeError("重试循环意外结束。")


response = create_response_with_retry()
print(f"模型回答：{response.output_text}")
