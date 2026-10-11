"""第 23 课：并行执行互不依赖的工具调用。"""

import asyncio
import json
import os
import time
from typing import Literal

from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel, ConfigDict, Field

from z_16_local_function import get_weather
from z_17_tool_schema import TOOLS


class WeatherArguments(BaseModel):
    """get_weather 工具允许接收的参数。"""

    model_config = ConfigDict(extra="forbid")

    city: str = Field(min_length=1)
    unit: Literal["celsius", "fahrenheit"] = "celsius"


def get_weather_with_delay(city: str) -> str:
    """用一秒阻塞等待模拟真实天气服务的网络耗时。"""
    time.sleep(1)
    return get_weather(city)


TOOL_FUNCTIONS = {
    "get_weather": get_weather_with_delay,
}

load_dotenv()

BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-v4-flash"
USER_INPUT = (
    "分别查询上海和广州的天气，使用摄氏度。"
    "必须为每个城市单独调用一次 get_weather。"
)


async def execute_tool_call(tool_call) -> dict[str, str]:
    """在线程中执行一个同步工具，并保留它自己的 call_id。"""
    arguments_dict = json.loads(tool_call.arguments)
    arguments = WeatherArguments.model_validate(arguments_dict)

    tool_function = TOOL_FUNCTIONS.get(tool_call.name)
    if tool_function is None:
        raise ValueError(f"拒绝执行未知工具：{tool_call.name}")

    started_at = time.perf_counter()
    tool_result = await asyncio.to_thread(tool_function, city=arguments.city)
    elapsed = time.perf_counter() - started_at

    print(f"{arguments.city} 完成，用时 {elapsed:.2f} 秒")
    return {
        "type": "function_call_output",
        "call_id": tool_call.call_id,
        "output": tool_result,
    }


async def main() -> None:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise SystemExit("未找到 DEEPSEEK_API_KEY，请先配置环境变量或 .env。")

    input_items = [{"role": "user", "content": USER_INPUT}]

    async with AsyncOpenAI(api_key=api_key, base_url=BASE_URL) as client:
        first_response = await client.responses.create(
            model=MODEL_NAME,
            input=input_items,
            tools=TOOLS,
            tool_choice="required",
            parallel_tool_calls=True,
            max_output_tokens=300,
            reasoning={"effort": "none"},
        )

        tool_calls = [
            item for item in first_response.output if item.type == "function_call"
        ]
        if not tool_calls:
            raise SystemExit("模型没有返回工具调用。")

        input_items.extend(first_response.output)

        started_at = time.perf_counter()
        tool_outputs = await asyncio.gather(
            *(execute_tool_call(tool_call) for tool_call in tool_calls)
        )
        total_elapsed = time.perf_counter() - started_at

        print(f"全部工具用时：{total_elapsed:.2f} 秒")
        input_items.extend(tool_outputs)

        final_response = await client.responses.create(
            model=MODEL_NAME,
            input=input_items,
            max_output_tokens=300,
            reasoning={"effort": "none"},
        )

    print("模型最终回答：", final_response.output_text)


if __name__ == "__main__":
    asyncio.run(main())
