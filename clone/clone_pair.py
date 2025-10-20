from dataclasses import dataclass
from .clone_type import CloneType


@dataclass
class ClonePair:
    file1: str
    start1: int
    end1: int
    file2: str
    start2: int
    end2: int
    clone_type: CloneType = CloneType.UNKNOWN
