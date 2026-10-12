"""第 25 课：在有副作用的工具执行前等待人工审批。"""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, ConfigDict, Field, ValidationError


class AlertArguments(BaseModel):
    """send_weather_alert 工具允许接收的参数。"""

    model_config = ConfigDict(extra="forbid")

    recipient: str = Field(min_length=3)
    city: str = Field(min_length=1)
    message: str = Field(min_length=1)


TOOLS = [
    {
        "type": "function",
        "name": "send_weather_alert",
        "description": "向指定收件人发送一条天气提醒；该操作会产生外部副作用。",
        "parameters": {
            "type": "object",
            "properties": {
                "recipient": {
                    "type": "string",
                    "description": "提醒的收件人，例如 learner@example.com。",
                },
                "city": {
                    "type": "string",
                    "description": "提醒对应的城市。",
                },
                "message": {
                    "type": "string",
                    "description": "准备发送的提醒正文。",
                },
            },
            "required": ["recipient", "city", "message"],
            "additionalProperties": False,
        },
        "strict": True,
    }
]

# 用内存列表模拟已经发送的提醒，不连接真实邮件或消息服务。
SENT_ALERTS: list[dict[str, str]] = []

load_dotenv()

BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-v4-flash"
USER_INPUT = (
    "请向 learner@example.com 发送一条北京天气提醒，"
    "正文是：北京今天晴，出门注意防晒。"
)


def send_weather_alert(recipient: str, city: str, message: str) -> str:
    """模拟一个会产生副作用的发送工具。"""
    SENT_ALERTS.append(
        {"recipient": recipient, "city": city, "message": message}
    )
    return "天气提醒已发送（模拟）。"


def make_tool_output(call_id: str, payload: dict) -> dict[str, str]:
    """把审批结果或执行结果编码为工具输出。"""
    return {
        "type": "function_call_output",
        "call_id": call_id,
        "output": json.dumps(payload, ensure_ascii=False),
    }


def execute_with_approval(tool_call) -> dict[str, str]:
    """展示具体操作，只在用户明确批准后执行工具。"""
    if tool_call.name != "send_weather_alert":
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
        arguments = AlertArguments.model_validate_json(tool_call.arguments)
    except ValidationError:
        return make_tool_output(
            tool_call.call_id,
            {
                "ok": False,
                "error": {
                    "type": "invalid_arguments",
                    "message": "工具参数未通过校验。",
                },
            },
        )

    print("\n待审批操作：")
    print(f"工具：{tool_call.name}")
    print(f"收件人：{arguments.recipient}")
    print(f"城市：{arguments.city}")
    print(f"正文：{arguments.message}")

    decision = input("批准执行吗？请输入 yes 批准，其余输入均拒绝：")
    approved = decision.strip().lower() == "yes"

    if not approved:
        print("用户拒绝，工具未执行。")
        return make_tool_output(
            tool_call.call_id,
            {
                "ok": False,
                "error": {
                    "type": "user_rejected",
                    "message": "用户拒绝执行此操作。",
                },
            },
        )

    result = send_weather_alert(
        recipient=arguments.recipient,
        city=arguments.city,
        message=arguments.message,
    )
    print(f"工具已执行，已发送数量：{len(SENT_ALERTS)}")
    return make_tool_output(
        tool_call.call_id,
        {"ok": True, "result": result},
    )


def main() -> None:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise SystemExit("未找到 DEEPSEEK_API_KEY，请先配置环境变量或 .env。")

    input_items = [{"role": "user", "content": USER_INPUT}]

    with OpenAI(api_key=api_key, base_url=BASE_URL) as client:
        first_response = client.responses.create(
            model=MODEL_NAME,
            input=input_items,
            tools=TOOLS,
            tool_choice="required",
            parallel_tool_calls=False,
            max_output_tokens=300,
            reasoning={"effort": "none"},
        )

        tool_calls = [
            item for item in first_response.output if item.type == "function_call"
        ]
        if not tool_calls:
            raise SystemExit("模型没有返回工具调用。")

        input_items.extend(first_response.output)
        for tool_call in tool_calls:
            input_items.append(execute_with_approval(tool_call))

        final_response = client.responses.create(
            model=MODEL_NAME,
            input=input_items,
            max_output_tokens=300,
            reasoning={"effort": "none"},
        )

    print("模型最终回答：", final_response.output_text)


if __name__ == "__main__":
    main()
