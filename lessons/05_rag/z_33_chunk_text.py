"""第 33 课：将长文本切成可检索的块。"""

from __future__ import annotations

import re

from z_32_read_document import DOCUMENT_PATH, read_and_clean


def chunk_text(text: str, max_chars: int = 70) -> list[str]:
    """优先按段落切分，再把过长段落按句子切分。"""

    if max_chars <= 0:
        raise ValueError("max_chars 必须大于 0。")

    paragraphs = [item.strip() for item in text.split("\n\n") if item.strip()]
    units: list[str] = []
    pending_headings: list[str] = []
    for paragraph in paragraphs:
        if paragraph.startswith("#"):
            pending_headings.append(paragraph)
            continue
        units.append("\n".join([*pending_headings, paragraph]))
        pending_headings.clear()
    if pending_headings:
        units.append("\n".join(pending_headings))

    chunks: list[str] = []

    for paragraph in units:
        if len(paragraph) <= max_chars:
            chunks.append(paragraph)
            continue

        sentences = [
            sentence.strip()
            for sentence in re.split(r"(?<=[。！？!?])", paragraph)
            if sentence.strip()
        ]
        current = ""
        for sentence in sentences:
            if len(sentence) > max_chars:
                if current:
                    chunks.append(current)
                    current = ""
                chunks.extend(
                    sentence[start : start + max_chars]
                    for start in range(0, len(sentence), max_chars)
                )
                continue
            candidate = current + sentence
            if current and len(candidate) > max_chars:
                chunks.append(current)
                current = sentence
            else:
                current = candidate
        if current:
            chunks.append(current)

    return chunks


def main() -> None:
    chunks = chunk_text(read_and_clean(DOCUMENT_PATH))
    for index, chunk in enumerate(chunks, start=1):
        print(f"[块 {index} | {len(chunk)} 字符]")
        print(chunk, end="\n\n")


if __name__ == "__main__":
    main()
