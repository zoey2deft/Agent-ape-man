"""第 20 课：根据工具名称安全路由到本地函数。"""


WEATHER_DATA = {
    "北京": {"condition": "晴", "temperature_c": 26},
    "上海": {"condition": "多云", "temperature_c": 28},
    "深圳": {"condition": "阵雨", "temperature_c": 30},
}


def get_weather(city: str) -> dict[str, str | int]:
    """返回本地模拟天气。"""
    weather = WEATHER_DATA.get(city)

    if weather is None:
        return {"city": city, "condition": "未知", "temperature_c": "未知"}

    return {"city": city, **weather}


TOOL_HANDLERS = {
    "get_weather": get_weather,
}


def execute_tool(tool_name: str, arguments: dict[str, str]):
    """只执行白名单中存在的工具。"""
    handler = TOOL_HANDLERS.get(tool_name)

    if handler is None:
        raise ValueError(f"不允许执行工具：{tool_name}")

    return handler(**arguments)


selected_tool_name = "get_weather"
validated_arguments = {"city": "北京"}

print("模型请求的工具：", selected_tool_name)
print("本地执行结果：", execute_tool(selected_tool_name, validated_arguments))
