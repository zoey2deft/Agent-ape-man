"""第 17 课：使用 JSON Schema 描述天气工具。"""

import json


WEATHER_TOOL = {
    "type": "function",
    "name": "get_weather",
    "description": "查询指定城市的天气。",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "要查询的城市名称，例如北京。",
            }
        },
        "required": ["city"],
        "additionalProperties": False,
    },
}

# print(WEATHER_TOOL)
# print(type(WEATHER_TOOL))

print(json.dumps(WEATHER_TOOL, ensure_ascii=True, indent=2))

