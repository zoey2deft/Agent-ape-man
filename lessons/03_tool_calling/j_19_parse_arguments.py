"""第 19 课：解析并校验模型提供的工具参数。"""

from typing import Literal

from pydantic import BaseModel, ConfigDict


class WeatherArguments(BaseModel):
    """get_weather 允许接收的参数。"""

    # 禁止额外属性
    model_config = ConfigDict(extra="forbid")

    city: Literal["北京", "上海", "深圳"]
    days: Literal["1", "2", "3"]


raw_arguments = '{"city": "北京", "days": "2"}'

print("校验前类型：", type(raw_arguments).__name__)
print("模型原始参数：", raw_arguments)

arguments = WeatherArguments.model_validate_json(raw_arguments)

print("校验后类型：", type(arguments).__name__)
print("可信城市参数：", arguments.city)
print("可信日期参数：", arguments.days)
