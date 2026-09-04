"""阶段 2 作品：多轮、结构化、有限重试的命令行任务助手。"""

import os
import time
from typing import Literal

from dotenv import load_dotenv
from openai import (
    APIConnectionError,
    APITimeoutError,
    InternalServerError,
    OpenAI,
    RateLimitError,
)
from pydantic import BaseModel


class AssistantResult(BaseModel):
    message: str
    task: str | None
    priority: Literal["低", "中", "高"] | None
    deadline: str | None


load_dotenv()

API_KEY_ENV = "DEEPSEEK_API_KEY"
MODEL = "deepseek-v4-flash"
MAX_ATTEMPTS = 3
BASE_DELAY_SECONDS = 0.5
MAX_CONTEXT_MESSAGES = 5
RETRYABLE_ERRORS = (
    APIConnectionError,
    APITimeoutError,
    RateLimitError,
    InternalServerError,
)
INSTRUCTIONS = """
你是一个任务整理助手，也可以根据当前上下文回答追问。
当用户提交新任务时，提取 task、priority 和 deadline：
- 出现“紧急”“立刻”“马上”或“今天”时，priority 为“高”；
- 出现“有空”“以后”或“不着急”时，priority 为“低”；
- 其他新任务的 priority 为“中”。
没有截止日期时 deadline 为 null。
如果用户只是在追问，不是提交新任务，task、priority、deadline 都为 null。
message 使用简短中文回答用户。
""".strip()

api_key = os.getenv(API_KEY_ENV)

if not api_key:
    raise SystemExit(f"未找到 {API_KEY_ENV}，请先配置环境变量或 .env。")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
    timeout=10.0,
    max_retries=0,
)


def request_with_retry(visible_history: list[dict[str, str]]):
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            return client.responses.parse(
                model=MODEL,
                instructions=INSTRUCTIONS,
                input=visible_history,
                text_format=AssistantResult,
            )
        except RETRYABLE_ERRORS as error:
            if attempt == MAX_ATTEMPTS:
                raise

            delay = BASE_DELAY_SECONDS * 2 ** (attempt - 1)
            print(f"暂时性错误 {type(error).__name__}，{delay} 秒后重试。")
            time.sleep(delay)

    raise RuntimeError("重试循环意外结束。")


history: list[dict[str, str]] = []

print("阶段 2 任务助手已启动；输入“退出”结束。")

while True:
    user_input = input("\n你：").strip()

    if user_input == "退出":
        print("助手：再见。")
        break

    if not user_input:
        print("请输入内容。")
        continue

    history.append({"role": "user", "content": user_input})
    visible_history = history[-MAX_CONTEXT_MESSAGES:]
    response = request_with_retry(visible_history)
    result = response.output_parsed

    if result is None:
        raise RuntimeError("模型没有返回可解析的 AssistantResult。")

    print(f"助手：{result.message}")
    print(
        "结构化结果：",
        f"task={result.task!r}, priority={result.priority!r}, deadline={result.deadline!r}",
    )
    print(
        "本轮 token：",
        f"输入={response.usage.input_tokens}, 输出={response.usage.output_tokens}",
    )
    print(f"完整历史={len(history) + 1} 条，本次发送={len(visible_history)} 条")

    history.append({"role": "assistant", "content": response.output_text})
