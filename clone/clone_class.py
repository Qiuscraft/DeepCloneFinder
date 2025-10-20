from dataclasses import dataclass
from typing import List
from .clone_pair import ClonePair
from .clone_type import CloneType


@dataclass
class CloneClass:
    clone_pairs: List[ClonePair]
    clone_type: CloneType = CloneType.UNKNOWN
