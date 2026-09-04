"""第 16 课：编写一个与模型无关的普通 Python 工具。"""


def get_weather(city: str) -> str:
    """从本地模拟数据中查询城市天气。"""
    weather_data = {
        "北京": "晴，25°C",
        "上海": "多云，28°C",
        "深圳": "雷阵雨，30°C",
        "广州": "小雨，27°C"
    }
    return weather_data.get(city, f"暂无 {city} 的天气数据")


if __name__ == "__main__":
    print(get_weather("北京"))
    print(get_weather("成都"))
    print(get_weather("广州"))
