"""第 24 课：把工具错误转换为模型可以处理的结果。"""

import asyncio
import json
import os
from typing import Any, Literal

from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from z_16_local_function import get_weather
from z_17_tool_schema import TOOLS


class WeatherArguments(BaseModel):
    """get_weather 工具允许接收的参数。"""

    model_config = ConfigDict(extra="forbid")

    city: str = Field(min_length=1)
    unit: Literal["celsius", "fahrenheit"] = "celsius"


def get_weather_with_failure(city: str) -> str:
    """用一个特殊城市模拟工具内部故障。"""
    if city == "故障城":
        raise RuntimeError("模拟上游天气服务故障")
    return get_weather(city)


TOOL_FUNCTIONS = {
    "get_weather": get_weather_with_failure,
}

# 练习时改成 True，可在不依赖模型随机输出的情况下测试参数错误分支。
SIMULATE_INVALID_ARGUMENTS = False

load_dotenv()

BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-v4-flash"
USER_INPUT = (
    "分别查询北京和故障城的天气，使用摄氏度。"
    "必须为每个城市单独调用一次 get_weather。"
    "如果工具返回错误，请明确说明查询失败，不要编造天气。"
)


def make_tool_output(call_id: str, payload: dict[str, Any]) -> dict[str, str]:
    """把应用层结果编码为 Responses API 接收的工具输出项。"""
    return {
        "type": "function_call_output",
        "call_id": call_id,
        "output": json.dumps(payload, ensure_ascii=False),
    }


async def execute_tool_call(tool_call) -> dict[str, str]:
    """执行一次工具调用；失败也返回结果，不让异常中断整个闭环。"""
    try:
        arguments_dict = json.loads(tool_call.arguments)
        if (
            SIMULATE_INVALID_ARGUMENTS
            and isinstance(arguments_dict, dict)
            and arguments_dict.get("city") == "北京"
        ):
            arguments_dict["unit"] = "kelvin"
        arguments = WeatherArguments.model_validate(arguments_dict)
    except json.JSONDecodeError:
        print("参数错误：工具参数不是合法 JSON")
        return make_tool_output(
            tool_call.call_id,
            {
                "ok": False,
                "error": {
                    "type": "invalid_json",
                    "message": "工具参数不是合法 JSON。",
                },
            },
        )
    except ValidationError:
        print("参数错误：工具参数未通过字段校验")
        return make_tool_output(
            tool_call.call_id,
            {
                "ok": False,
                "error": {
                    "type": "invalid_arguments",
                    "message": (
                        "city 必须是非空字符串，unit 必须是 celsius 或 fahrenheit。"
                    ),
                },
            },
        )

    tool_function = TOOL_FUNCTIONS.get(tool_call.name)
    if tool_function is None:
        print(f"路由错误：拒绝执行未知工具 {tool_call.name}")
        return make_tool_output(
            tool_call.call_id,
            {
                "ok": False,
                "error": {
                    "type": "unknown_tool",
                    "message": "应用不支持这个工具。",
                },
            },
        )

    try:
        tool_result = await asyncio.to_thread(tool_function, city=arguments.city)
    except Exception as error:
        print(f"执行错误：{arguments.city}（{type(error).__name__}）")
        return make_tool_output(
            tool_call.call_id,
            {
                "ok": False,
                "error": {
                    "type": "tool_execution_error",
                    "message": "天气服务暂时不可用。",
                },
            },
        )

    print(f"执行成功：{arguments.city}")
    return make_tool_output(
        tool_call.call_id,
        {"ok": True, "result": tool_result},
    )


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
        tool_outputs = await asyncio.gather(
            *(execute_tool_call(tool_call) for tool_call in tool_calls)
        )

        for tool_output in tool_outputs:
            print("回传结果：", tool_output["output"])
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
