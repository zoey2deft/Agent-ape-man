"""第 15 课：用同一组固定案例比较两个 Prompt 的行为。"""

import os
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel


class PriorityDecision(BaseModel):
    priority: Literal["低", "中", "高"]


load_dotenv()

API_KEY_ENV = "DEEPSEEK_API_KEY"
MODEL = "deepseek-v4-flash"

PROMPTS = {
    "Prompt A（模糊）": "判断任务优先级：低、中、高。",
    "Prompt B（明确规则）": """
判断任务优先级：
- 出现“紧急”“立刻”“马上”或“今天”时为高；
- 出现“有空”“以后”或“不着急”时为低；
- 其他情况为中。
""".strip(),
}

TEST_CASES = [
    ("服务器正在报错，请马上处理。", "高"),
    ("请在本周五前整理会议记录。比较需要", "中"),
    ("以后有空时研究一下新的配色方案。", "低"),
]

api_key = os.getenv(API_KEY_ENV)

if not api_key:
    raise SystemExit(f"未找到 {API_KEY_ENV}，请先配置环境变量或 .env。")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
)

for prompt_name, instructions in PROMPTS.items():
    passed = 0
    print(f"\n=== {prompt_name} ===")

    for task, expected in TEST_CASES:
        response = client.responses.parse(
            model=MODEL,
            instructions=instructions,
            input=task,
            text_format=PriorityDecision,
        )
        decision = response.output_parsed

        if decision is None:
            raise RuntimeError("模型没有返回可解析的优先级。")

        actual = decision.priority
        is_passed = actual == expected
        passed += int(is_passed)

        print(f"任务：{task}")
        print(f"预期：{expected}，实际：{actual}，结果：{'通过' if is_passed else '失败'}")

    print(f"得分：{passed}/{len(TEST_CASES)}")
