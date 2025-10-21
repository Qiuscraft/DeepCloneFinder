from typing import List, Set, Tuple
from clone.clone_class import CloneClass
from clone.clone_pair import ClonePair


class FunctionFilter:
    """
    函数过滤器，用于筛选不在指定克隆类中的函数片段。
    """
    
    def __init__(self, clone_classes: List[CloneClass]):
        """
        初始化函数过滤器。
        
        Args:
            clone_classes: 克隆类列表，包含需要记录的函数片段信息
        """
        self._visited_snippets: Set[Tuple[str, int, int]] = set()
        
        # 将每个CloneClass的每个ClonePair的(file1, start1, end1)和(file2, start2, end2)记录在哈希容器中
        for clone_class in clone_classes:
            for clone_pair in clone_class.clone_pairs:
                # 记录第一个文件的函数片段信息
                self._visited_snippets.add((clone_pair.file1, clone_pair.start1, clone_pair.end1))
                # 记录第二个文件的函数片段信息
                self._visited_snippets.add((clone_pair.file2, clone_pair.start2, clone_pair.end2))
    
    def is_allowed(self, file: str, start: int, end: int) -> bool:
        """
        筛选函数，判断给定的函数片段是否允许通过。
        
        Args:
            file: 文件路径
            start: 起始行号
            end: 结束行号
        
        Returns:
            bool: 如果这个元组在哈希容器中已经存在，那么返回False（筛选不通过），反之返回True（通过）
        """
        return (file, start, end) not in self._visited_snippets