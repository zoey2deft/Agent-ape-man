"""第 25 课：有副作用的工具执行前必须等待人工批准。"""

import json


TOOL_CALL = {
    "call_id": "call_alert_001",
    "name": "send_weather_alert",
    "arguments": {
        "recipient": "学习群",
        "message": "北京今天晴，26℃。",
    },
}
SIDE_EFFECT_TOOLS = {"send_weather_alert"}


def send_weather_alert(recipient: str, message: str) -> dict[str, object]:
    """仅模拟发送，不连接任何外部消息服务。"""
    print(f"[模拟发送] 接收方={recipient}，内容={message}")
    return {"sent": True}


TOOL_HANDLERS = {
    "send_weather_alert": send_weather_alert,
}


def execute_with_approval(tool_call: dict) -> dict[str, str]:
    """敏感工具仅在用户明确输入 y 后执行。"""
    tool_name = tool_call["name"]
    handler = TOOL_HANDLERS.get(tool_name)

    if handler is None:
        raise ValueError(f"不允许执行工具：{tool_name}")

    if tool_name in SIDE_EFFECT_TOOLS:
        print("即将执行有副作用的工具：", tool_name)
        print("参数：", tool_call["arguments"])
        choice = input("批准执行吗？输入 y 批准，其他输入拒绝：").strip().lower()

        if choice != "y":
            payload = {
                "ok": False,
                "error": {
                    "type": "approval_denied",
                    "message": "用户未批准执行",
                },
            }
            return {
                "type": "function_call_output",
                "call_id": tool_call["call_id"],
                "output": json.dumps(payload, ensure_ascii=False),
            }

    data = handler(**tool_call["arguments"])
    payload = {"ok": True, "data": data}
    return {
        "type": "function_call_output",
        "call_id": tool_call["call_id"],
        "output": json.dumps(payload, ensure_ascii=False),
    }


print(execute_with_approval(TOOL_CALL))
