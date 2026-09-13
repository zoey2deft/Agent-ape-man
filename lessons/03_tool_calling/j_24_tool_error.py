"""第 24 课：把工具错误转换成模型可处理的结果。"""

import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, ValidationError


class WeatherArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    city: Literal["北京", "上海", "故障城市"]


WEATHER_DATA = {
    "北京": {"condition": "晴", "temperature_c": 26},
    "上海": {"condition": "多云", "temperature_c": 28},
}
TOOL_CALLS = [
    {"call_id": "call_ok", "arguments": '{"city": "北京"}'},
    {"call_id": "call_bad_args", "arguments": '{"city": "广州"}'},
    {"call_id": "call_failed", "arguments": '{"city": "故障城市"}'},
]


def get_weather(city: str) -> dict[str, str | int]:
    """返回天气，或模拟外部天气服务故障。"""
    if city == "故障城市":
        raise RuntimeError("天气服务暂时不可用")

    return {"city": city, **WEATHER_DATA[city]}


def execute_tool_safely(tool_call: dict[str, str]) -> dict[str, str]:
    """无论成功或失败，都返回可关联的工具结果。"""
    try:
        arguments = WeatherArguments.model_validate_json(tool_call["arguments"])
        data = get_weather(arguments.city)
        payload = {"ok": True, "data": data}
    except ValidationError:
        payload = {
            "ok": False,
            "error": {
                "type": "invalid_arguments",
                "message": "城市参数不符合要求",
            },
        }
    except RuntimeError:
        payload = {
            "ok": False,
            "error": {
                "type": "execution_error",
                "message": "天气服务暂时不可用",
            },
        }

    return {
        "type": "function_call_output",
        "call_id": tool_call["call_id"],
        "output": json.dumps(payload, ensure_ascii=False),
    }


for call in TOOL_CALLS:
    print(execute_tool_safely(call))
