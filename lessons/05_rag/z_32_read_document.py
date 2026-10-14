"""第 32 课：读取并清洗一个本地文档。"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path


DOCUMENT_PATH = Path(__file__).parent / "data" / "agent_handbook.md"


def read_and_clean(path: Path) -> str:
    """读取 UTF-8 文档，统一字符，并保留段落边界地清理空白。"""

    raw_text = path.read_text(encoding="utf-8")
    normalized = unicodedata.normalize("NFKC", raw_text)
    paragraphs = re.split(r"\n\s*\n", normalized)
    cleaned = [re.sub(r"\s+", " ", paragraph).strip() for paragraph in paragraphs]
    return "\n\n".join(paragraph for paragraph in cleaned if paragraph)


def main() -> None:
    raw_text = DOCUMENT_PATH.read_text(encoding="utf-8")
    clean_text = read_and_clean(DOCUMENT_PATH)

    print(f"文档：{DOCUMENT_PATH.name}")
    print(f"清洗前字符数：{len(raw_text)}")
    print(f"清洗后字符数：{len(clean_text)}")
    print(f"清洗后段落数：{len(clean_text.split('\n\n'))}")
    print("\n清洗后的内容：\n")
    print(clean_text)


if __name__ == "__main__":
    main()
