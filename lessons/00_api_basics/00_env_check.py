"""第 00 课：确认 uv 为项目选择的 Python 运行环境。"""

import sys
from pathlib import Path


print("=== Python 运行环境 ===")
print(f"Python 版本：{sys.version.split()[0]}")
print(f"解释器位置：{sys.executable}")
print(f"环境目录：{sys.prefix}")
print(f"是否为项目 .venv：{'是' if Path(sys.prefix).name == '.venv' else '否'}")
print(f"运行目录：{Path.cwd()}")
