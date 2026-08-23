"""第 11 课：使用 Pydantic 定义并接收结构化输出。"""

import os
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel


load_dotenv()

BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-v4-flash"


class StudyTask(BaseModel):
    title: str
    priority: Literal["low", "medium", "high"]
    tags: list[str]
    estimated_hours: int


api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise SystemExit("未找到 DEEPSEEK_API_KEY，请先配置环境变量或 .env。")

client = OpenAI(
    api_key=api_key,
    base_url=BASE_URL,
)

response = client.responses.parse(
    model=MODEL_NAME,
    instructions="从用户的话中提取一项学习任务。",
    input="周五之前完成 Responses API 课程笔记，优先级很高，标签是 Python 和 Agent，预计需要 2 小时。",
    text_format=StudyTask,
    max_output_tokens=120,
    reasoning={"effort": "none"},
)

task = response.output_parsed
if task is None:
    raise SystemExit("模型没有返回可解析的结构化结果。")

print("对象类型：", type(task).__name__)
print("标题：", task.title)
print("优先级：", task.priority)
print("预计小时：", task.estimated_hours)
print("标签：", task.tags)
