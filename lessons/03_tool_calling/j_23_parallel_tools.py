"""第 23 课：并行执行互不依赖的工具调用。"""

import time
from concurrent.futures import ThreadPoolExecutor


WEATHER_DATA = {
    "北京": {"condition": "晴", "temperature_c": 26},
    "上海": {"condition": "多云", "temperature_c": 28},
    "深圳": {"condition": "阵雨", "temperature_c": 30},
}
TOOL_CALLS = [
    {
        "call_id": "call_beijing",
        "name": "get_weather",
        "arguments": {"city": "北京"},
    },
    {
        "call_id": "call_shanghai",
        "name": "get_weather",
        "arguments": {"city": "上海"},
    },
    {
        "call_id": "call_shenzhen",
        "name": "get_weather",
        "arguments": {"city": "深圳"},
    },
]


def get_weather(city: str) -> dict[str, str | int]:
    """用一秒等待模拟网络工具。"""
    time.sleep(1)
    return {"city": city, **WEATHER_DATA[city]}


def execute_tool_call(tool_call: dict) -> dict:
    """执行一个已校验的工具调用，并保留原 call_id。"""
    if tool_call["name"] != "get_weather":
        raise ValueError(f"不允许执行工具：{tool_call['name']}")

    return {
        "call_id": tool_call["call_id"],
        "output": get_weather(**tool_call["arguments"]),
    }


start = time.perf_counter()

with ThreadPoolExecutor(max_workers=len(TOOL_CALLS)) as executor:
    results = list(executor.map(execute_tool_call, TOOL_CALLS))

elapsed = time.perf_counter() - start

for result in results:
    print(result)

print(f"并行执行耗时：{elapsed:.2f} 秒")
print(type(TOOL_CALLS))