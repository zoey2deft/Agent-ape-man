"""第 09 课：在等待模型响应时继续执行其他任务。"""

import asyncio
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI


load_dotenv()

API_KEY_ENV = "DEEPSEEK_API_KEY"
api_key = os.getenv(API_KEY_ENV)

if not api_key:
    raise SystemExit(f"未找到 {API_KEY_ENV}，请先配置环境变量或 .env。")


async def main() -> None:
    client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
    )

    print("把模型请求交给事件循环")
    request_task = asyncio.create_task(
        client.responses.create(
            model="deepseek-v4-flash",
            input="用一句话解释 Python 中 await 的作用。",
        )
    )

    for second in range(1, 6):
        if request_task.done():
            break

        await asyncio.sleep(1)
        print(f"等待模型时，完成了第 {second} 秒的其他工作")

    response = await request_task
    print("模型请求完成")
    print(response.output_text)


if __name__ == "__main__":
    asyncio.run(main())
