from dataclasses import dataclass
from typing import List
from model.clone_pair import ClonePair
from model.clone_type import CloneType


@dataclass
class CloneClass:
    clone_pairs: List[ClonePair]
    clone_type: CloneType = CloneType.UNKNOWN
