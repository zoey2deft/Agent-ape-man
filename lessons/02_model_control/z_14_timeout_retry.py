"""第 14 课：为临时错误实现有上限的指数退避重试。"""

import os
import time

from dotenv import load_dotenv
from openai import APIConnectionError, APIStatusError, OpenAI


load_dotenv()

BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-v4-flash"

MAX_ATTEMPTS = 5
BASE_DELAY_SECONDS = 1.0
MAX_DELAY_SECONDS = 4.0
RETRYABLE_STATUS_CODES = {408, 409, 429}

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise SystemExit("未找到 DEEPSEEK_API_KEY，请先配置环境变量或 .env。")

client = OpenAI(
    api_key=api_key,
    base_url=BASE_URL,
    timeout=30.0,
    # 本课手写重试，所以关闭 SDK 默认重试，避免两层重试叠加。
    max_retries=0,
)


def is_retryable(error: Exception) -> bool:
    """网络错误、超时、限流和服务端错误通常适合重试。"""
    if isinstance(error, APIConnectionError):
        return True

    if isinstance(error, APIStatusError):
        return (
            error.status_code in RETRYABLE_STATUS_CODES
            or error.status_code >= 500
        )

    return False


def retry_delay(failed_attempt: int) -> float:
    """第 1、2、3……次失败后等待 1、2、4……秒，并限制最大值。"""
    exponential_delay = BASE_DELAY_SECONDS * 2 ** (failed_attempt - 1)
    return min(exponential_delay, MAX_DELAY_SECONDS)


delay_plan = [retry_delay(attempt) for attempt in range(1, MAX_ATTEMPTS)]
print(f"如果连续失败，重试前的等待计划：{delay_plan}")

for attempt in range(1, MAX_ATTEMPTS + 1):
    try:
        print(f"正在进行第 {attempt}/{MAX_ATTEMPTS} 次请求……")
        response = client.responses.create(
            model=MODEL_NAME,
            instructions="只用一句简短中文回答。",
            input="为什么重试次数必须有上限？",
            max_output_tokens=80,
            reasoning={"effort": "none"},
        )
        print(f"模型回答：{response.output_text}")
        break
    except (APIConnectionError, APIStatusError) as error:
        if not is_retryable(error):
            raise

        if attempt == MAX_ATTEMPTS:
            print("已达到最大尝试次数，停止重试。")
            raise

        delay = retry_delay(attempt)
        print(f"遇到临时错误 {type(error).__name__}，等待 {delay} 秒后重试。")
        time.sleep(delay)
