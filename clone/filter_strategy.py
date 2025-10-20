from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Callable, Iterable, List

from .clone_pair import ClonePair


class CombinationOperator(Enum):
    """组合多个过滤策略时使用的逻辑算子。"""

    ALL = auto()
    ANY = auto()


class ClonePairFilterStrategy(ABC):
    """用于判断克隆对是否保留的策略抽象。"""

    def __call__(self, pair: ClonePair) -> bool:
        return self.match(pair)

    def __and__(self, other: "ClonePairFilterStrategy") -> "ClonePairFilterStrategy":
        return CompositeClonePairFilterStrategy([self, other], CombinationOperator.ALL)

    def __or__(self, other: "ClonePairFilterStrategy") -> "ClonePairFilterStrategy":
        return CompositeClonePairFilterStrategy([self, other], CombinationOperator.ANY)

    def __invert__(self) -> "ClonePairFilterStrategy":
        return NegatedClonePairFilterStrategy(self)

    @abstractmethod
    def match(self, pair: ClonePair) -> bool:
        """当克隆对满足策略时返回 True。"""


class CompositeClonePairFilterStrategy(ClonePairFilterStrategy):
    def __init__(
        self,
        strategies: Iterable[ClonePairFilterStrategy],
        operator: CombinationOperator = CombinationOperator.ALL,
    ) -> None:
        self._operator = operator
        self._strategies: List[ClonePairFilterStrategy] = list(strategies)
        if not self._strategies:
            raise ValueError("At least one strategy must be supplied.")

    def match(self, pair: ClonePair) -> bool:
        if self._operator is CombinationOperator.ALL:
            return all(strategy.match(pair) for strategy in self._strategies)
        return any(strategy.match(pair) for strategy in self._strategies)


class NegatedClonePairFilterStrategy(ClonePairFilterStrategy):
    def __init__(self, strategy: ClonePairFilterStrategy) -> None:
        self._delegate = strategy

    def match(self, pair: ClonePair) -> bool:
        return not self._delegate.match(pair)


class AllowAllClonePairFilter(ClonePairFilterStrategy):
    """保留所有克隆对的兜底策略。"""

    def match(self, pair: ClonePair) -> bool:
        return True


class CallableClonePairFilterStrategy(ClonePairFilterStrategy):
    """让简单可调用对象充当过滤策略的适配器。"""

    def __init__(self, predicate: Callable[[ClonePair], bool]) -> None:
        if not callable(predicate):
            raise TypeError("predicate must be callable")
        self._predicate = predicate

    def match(self, pair: ClonePair) -> bool:
        return bool(self._predicate(pair))
