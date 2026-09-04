"""第 11 课：用 Responses API 和 Pydantic 获得结构化结果。"""

import os
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel


class TaskInfo(BaseModel):
    task: str
    priority: Literal["低", "中", "高"]
    deadline: str | None


load_dotenv()

API_KEY_ENV = "DEEPSEEK_API_KEY"
MODEL = "deepseek-v4-flash"
INSTRUCTIONS = """
把用户的任务描述提取为结构化数据。
priority 只能是“低”“中”“高”；没有截止日期时，deadline 必须是 null。
""".strip()

api_key = os.getenv(API_KEY_ENV)

if not api_key:
    raise SystemExit(f"未找到 {API_KEY_ENV}，请先配置环境变量或 .env。")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
)

user_input = input("请输入一条任务描述：").strip()

if not user_input:
    raise SystemExit("任务描述不能为空。")

response = client.responses.parse(
    model=MODEL,
    instructions=INSTRUCTIONS,
    input=user_input,
    text_format=TaskInfo,
)

task_info = response.output_parsed

if task_info is None:
    raise SystemExit("模型没有返回可解析的 TaskInfo。")

print("模型原始 JSON：", response.output_text)
print("Pydantic 对象：", task_info)
print("字段读取：", task_info.task, task_info.priority, task_info.deadline)
print("\n=== 完整响应对象 ===")
print(response.model_dump_json(indent=2))