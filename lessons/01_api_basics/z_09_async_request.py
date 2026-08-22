"""第 09 课：使用异步客户端发送一次 DeepSeek 请求。"""

import asyncio
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI


load_dotenv()

BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-v4-flash"


async def main() -> None:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise SystemExit("未找到 DEEPSEEK_API_KEY，请先配置环境变量或 .env。")

    async with AsyncOpenAI(
        api_key=api_key,
        base_url=BASE_URL,
    ) as client:
        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": "用一句话解释 Python 中的 await。"},
            ],
            max_tokens=50,
        )

    print(response.choices[0].message.content)


if __name__ == "__main__":
    asyncio.run(main())
