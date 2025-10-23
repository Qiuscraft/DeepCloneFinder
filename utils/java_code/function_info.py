from dataclasses import dataclass
from typing import List
import json


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

    def to_dict(self) -> dict:
        return {
            'start_line': self.start_line,
            'end_line': self.end_line,
            'code_snippet': self.code_snippet,
            'subdirectory': self.subdirectory,
            'filename': self.filename,
            'path': self.path,
            'embedding': self.embedding,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'FunctionInfo':
        return cls(
            start_line=data['start_line'],
            end_line=data['end_line'],
            code_snippet=data['code_snippet'],
            subdirectory=data['subdirectory'],
            filename=data['filename'],
            path=data['path'],
            embedding=data.get('embedding'),
        )


def save_to_json(functions: List[FunctionInfo], filepath: str):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump([func.to_dict() for func in functions], f, ensure_ascii=False, indent=4)


def load_from_json(filepath: str) -> List[FunctionInfo]:
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return [FunctionInfo.from_dict(item) for item in data]
