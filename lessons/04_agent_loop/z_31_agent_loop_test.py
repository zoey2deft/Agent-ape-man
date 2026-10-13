"""第 31 课：用确定性的假模型测试 Agent Loop 的关键路径。"""

from __future__ import annotations

import copy
import unittest
from collections import deque
from dataclasses import dataclass, field
from typing import Any

from z_30_plan_and_act import (
    AgentLoopStopped,
    PlanStep,
    TaskPlan,
    run_action_loop,
)


@dataclass(frozen=True)
class FakeOutputItem:
    """测试所需的最小 Responses API 输出项。"""

    type: str
    name: str = ""
    arguments: str = ""
    call_id: str = ""

    def model_dump(self, **_: Any) -> dict[str, Any]:
        if self.type == "function_call":
            return {
                "type": self.type,
                "name": self.name,
                "arguments": self.arguments,
                "call_id": self.call_id,
            }
        return {"type": self.type}


@dataclass(frozen=True)
class FakeResponse:
    output: list[FakeOutputItem] = field(default_factory=list)
    output_text: str = ""


class FakeResponsesEndpoint:
    """按预设顺序返回响应，并记录每次请求。"""

    def __init__(self, responses: list[FakeResponse]) -> None:
        self._responses = deque(responses)
        self.requests: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> FakeResponse:
        self.requests.append(copy.deepcopy(kwargs))
        if not self._responses:
            raise AssertionError("假模型没有剩余响应，Agent 却仍在请求。")
        return self._responses.popleft()


class FakeClient:
    def __init__(self, responses: list[FakeResponse]) -> None:
        self.responses = FakeResponsesEndpoint(responses)


def function_call(
    name: str,
    arguments: str,
    call_id: str,
) -> FakeOutputItem:
    return FakeOutputItem(
        type="function_call",
        name=name,
        arguments=arguments,
        call_id=call_id,
    )


class AgentLoopTests(unittest.TestCase):
    def setUp(self) -> None:
        self.plan = TaskPlan(
            steps=[PlanStep(goal="完成用户任务", suggested_tool="none")],
            done_when="已经给出最终回答",
        )

    def run_with(
        self,
        responses: list[FakeResponse],
        *,
        max_rounds: int = 3,
    ) -> tuple[str, FakeClient]:
        client = FakeClient(responses)
        answer = run_action_loop(
            client,  # type: ignore[arg-type]
            "测试任务",
            self.plan,
            max_rounds=max_rounds,
        )
        return answer, client

    def test_direct_answer(self) -> None:
        answer, client = self.run_with([FakeResponse(output_text="直接回答")])

        self.assertEqual(answer, "直接回答")
        self.assertEqual(len(client.responses.requests), 1)

    def test_one_tool_call(self) -> None:
        answer, client = self.run_with(
            [
                FakeResponse(
                    output=[
                        function_call(
                            "get_weather",
                            '{"city":"北京"}',
                            "call-weather",
                        )
                    ]
                ),
                FakeResponse(output_text="北京天气已查询。"),
            ]
        )

        self.assertEqual(answer, "北京天气已查询。")
        second_input = client.responses.requests[1]["input"]
        outputs = [
            item
            for item in second_input
            if item.get("type") == "function_call_output"
        ]
        self.assertEqual(len(outputs), 1)
        self.assertEqual(outputs[0]["call_id"], "call-weather")

    def test_multiple_tool_calls(self) -> None:
        answer, client = self.run_with(
            [
                FakeResponse(
                    output=[
                        function_call(
                            "get_weather",
                            '{"city":"上海"}',
                            "call-weather",
                        ),
                        function_call(
                            "calculate",
                            '{"operation":"multiply","left":18,"right":7}',
                            "call-calculate",
                        ),
                    ]
                ),
                FakeResponse(output_text="两个工具都已完成。"),
            ]
        )

        self.assertEqual(answer, "两个工具都已完成。")
        second_input = client.responses.requests[1]["input"]
        output_ids = {
            item["call_id"]
            for item in second_input
            if item.get("type") == "function_call_output"
        }
        self.assertEqual(output_ids, {"call-weather", "call-calculate"})

    def test_round_limit(self) -> None:
        client = FakeClient(
            [                FakeResponse(
                    output=[
                        function_call(
                            "get_weather",
                            '{"city":"北京"}',
                            "call-1",
                        )
                    ]
                ),
                FakeResponse(
                    output=[
                        function_call(
                            "get_weather",
                            '{"city":"北京"}',
                            "call-2",
                        )
                    ]
                ),
            ]
        )

        with self.assertRaisesRegex(AgentLoopStopped, "最大轮次 2"):
            run_action_loop(
                client,  # type: ignore[arg-type]
                "测试任务",
                self.plan,
                max_rounds=2,
            )

        self.assertEqual(len(client.responses.requests), 2)

    def test_unknown_tool_fails_closed(self) -> None:
        client = FakeClient(
            [
                FakeResponse(
                    output=[function_call("delete_files", "{}", "call-unsafe")]
                )
            ]
        )

        with self.assertRaisesRegex(AgentLoopStopped, "未知工具"):
            run_action_loop(
                client,  # type: ignore[arg-type]
                "测试任务",
                self.plan,
                max_rounds=2,
            )
    def test_divide_by_zero_fails(self) -> None:
        client = FakeClient(
            [
                FakeResponse(
                    output=[
                        function_call(
                            "calculate",
                            '{"operation":"divide","left":10,"right":0}',
                            "call-zero",
                        )
                    ]
                )
            ]
        )

        with self.assertRaisesRegex(AgentLoopStopped, "除数不能为零"):
            run_action_loop(
                client,  # type: ignore[arg-type]
                "测试任务",
                self.plan,
                max_rounds=2,
            )

if __name__ == "__main__":
    unittest.main(verbosity=2)
