"""第 15 课：用固定测试案例比较不同 Prompt 的行为。"""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-v4-flash"

PROMPTS = {
    "模糊 Prompt": "判断下面任务的优先级。",
    "明确 Prompt": (
        "按照以下规则判断任务优先级："
        "高＝生产故障、安全风险或数据丢失；"
        "中＝影响正常工作，但存在临时替代方法；"
        "低＝外观优化或非紧急建议。"
        "只输出一个标签：高、中或低。不要解释。"
    ),
}

TEST_CASES = [
    {"task": "线上支付重复扣款，正在影响所有用户。", "expected": "高"},
    {"task": "导出报表很慢，但可以手工复制数据完成工作。", "expected": "中"},
    {"task": "设置页面的按钮颜色和设计稿不一致。", "expected": "低"},
    {"task": "登录偶尔失败，但刷新页面后可以继续。", "expected": "中", },
]

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise SystemExit("未找到 DEEPSEEK_API_KEY，请先配置环境变量或 .env。")

client = OpenAI(api_key=api_key, base_url=BASE_URL)

for prompt_name, prompt in PROMPTS.items():
    passed_count = 0
    print(f"\n--- {prompt_name} ---")

    for case in TEST_CASES:
        response = client.responses.create(
            model=MODEL_NAME,
            instructions=prompt,
            input=case["task"],
            max_output_tokens=80,
            reasoning={"effort": "none"},
        )
        actual = response.output_text.strip()
        passed = actual == case["expected"]
        passed_count += int(passed)

        print(f"任务：{case['task']}")
        print(f"期望：{case['expected']}｜实际：{actual}")
        print(f"结果：{'通过' if passed else '失败'}")

    print(f"通过数量：{passed_count}/{len(TEST_CASES)}")
