"""第 16 课：编写一个与模型无关的普通 Python 天气工具。"""


WEATHER_DATA = {
    "北京": {"condition": "晴", "temperature_c": 26},
    "上海": {"condition": "多云", "temperature_c": 28},
    "深圳": {"condition": "阵雨", "temperature_c": 30},
}


def get_weather(city: str) -> dict[str, str | int]:
    """根据城市名返回本地模拟天气。"""
    weather = WEATHER_DATA.get(city)

    if weather is None:
        return {"city": city, "condition": "未知", "temperature_c": "未知"}

    return {"city": city, **weather}


if __name__ == "__main__":
    result = get_weather("北京")
    print("工具输入：北京")
    print(f"工具输出：{result}")
