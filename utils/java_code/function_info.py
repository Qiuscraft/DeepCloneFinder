import os
from dataclasses import dataclass


@dataclass
class FunctionInfo:
    """Simple container for Java function metadata."""

    start_line: int
    end_line: int
    code_snippet: str
    subdirectory: str
    filename: str
    path: str  # 绝对路径
    embedding: str | None = None  # 用于存储函数的嵌入表示
