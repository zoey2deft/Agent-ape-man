"""第 03 课：观察一次 DeepSeek Responses API 的原始 HTTP 请求与响应。"""

import json
import os
from urllib.request import Request, urlopen

from dotenv import load_dotenv


load_dotenv()

URL = "https://api.deepseek.com/responses"
MODEL = "deepseek-v4-flash"
API_KEY_ENV = "DEEPSEEK_API_KEY"
SEND_REQUEST = True

api_key = os.getenv(API_KEY_ENV)
body = {
    "model": MODEL,
    "input": "只回复：HTTP 请求成功。",
    "max_output_tokens": 50,
}
body_bytes = json.dumps(body, ensure_ascii=False).encode("utf-8")

print("=== 请求 ===")
print("Method: POST")
print(f"URL: {URL}")
print("Headers:")
print("  Content-Type: application/json")
print("  Authorization: Bearer <已隐藏>")
print("Body:")
print(json.dumps(body, ensure_ascii=False, indent=2))

if not SEND_REQUEST:
    print("\n演示模式：请求尚未发送。确认请求内容后，将 SEND_REQUEST 改为 True。")
elif not api_key:
    raise SystemExit(f"未找到 {API_KEY_ENV}，请先配置环境变量或 .env。")
else:
    request = Request(
        URL,
        data=body_bytes,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )

    with urlopen(request, timeout=30) as response:
        response_body = json.loads(response.read().decode("utf-8"))
        print("\n=== 响应 ===")
        print(f"Status: {response.status} {response.reason}")
        print("Body:")
        print(json.dumps(response_body, ensure_ascii=False, indent=2))
