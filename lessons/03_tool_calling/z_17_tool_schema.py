"""第 17 课：使用 JSON Schema 描述工具能力和参数。"""

import json

TOOLS = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "查询指定城市的当前天气，仅在用户询问天气时使用。",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "要查询的城市名称，例如北京、上海。",
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "温度单位。",
                },
            },
            "required": ["city"],
            "additionalProperties": False,
        },
        "strict": True,
    }
]


if __name__ == "__main__":
    print(json.dumps(TOOLS, ensure_ascii=False, indent=2))
