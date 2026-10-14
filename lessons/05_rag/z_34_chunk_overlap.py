"""第 34 课：观察重叠切块对跨边界信息的影响。"""

from __future__ import annotations


TEXT = "检索系统先定位相关证据，再把证据交给模型。没有证据时必须承认资料不足。"


def sliding_chunks(text: str, size: int, overlap: int) -> list[str]:
    """按固定窗口切块，并让相邻窗口保留 overlap 个字符。"""

    if size <= 0:
        raise ValueError("size 必须大于 0。")
    if not 0 <= overlap < size:
        raise ValueError("overlap 必须满足 0 <= overlap < size。")

    step = size - overlap
    chunks = []
    for start in range(0, len(text), step):
        chunks.append(text[start : start + size])
        if start + size >= len(text):
            break
    return chunks


def show(label: str, chunks: list[str]) -> None:
    print(label)
    for index, chunk in enumerate(chunks, start=1):
        print(f"  {index}: {chunk!r}")


def main() -> None:
    show("无重叠：", sliding_chunks(TEXT, size=18, overlap=0))
    print()
    show("有重叠：", sliding_chunks(TEXT, size=18, overlap=12))


if __name__ == "__main__":
    main()
