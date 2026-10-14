"""第 35 课：调用阿里云百炼的 Embeddings API 生成真实向量。

使用 Qwen3-Embedding 系列的 text-embedding-v4 和 OpenAI SDK 兼容接口。
密钥来自 DASHSCOPE_API_KEY，接口地址使用本工作空间的北京地域地址。
后续生成仍沿用 DeepSeek Responses；两种客户端的密钥不能混用。
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from openai import OpenAI


EMBEDDING_MODEL = "text-embedding-v4"
EMBEDDING_BASE_URL = "https://ws-rnhut51sb00stnnl.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"


def create_embedding(client: OpenAI, text: str) -> list[float]:
    if not text.strip():
        raise ValueError("Embedding 文本不能为空。")
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
        encoding_format="float",
    )
    return response.data[0].embedding


def create_embedding_client() -> OpenAI:
    load_dotenv()
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise SystemExit("未找到 DASHSCOPE_API_KEY，请配置环境变量或 .env。")
    return OpenAI(
        api_key=api_key,
        base_url=EMBEDDING_BASE_URL,
        timeout=30.0,
        max_retries=1,
    )


def main() -> None:
    text = "RAG 先检索证据，再生成回答。"
    embedding = create_embedding(create_embedding_client(), text)

    print(f"文本：{text}")
    print(f"模型：{EMBEDDING_MODEL}")
    print(f"向量维度：{len(embedding)}")
    print(f"前 8 个数值：{embedding[:8]}")


if __name__ == "__main__":
    main()
