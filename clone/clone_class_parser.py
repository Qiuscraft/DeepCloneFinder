from .clone_class import CloneClass
from .clone_pair import ClonePair
import csv
import os
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from typing import Optional
from tqdm import tqdm

from clone.pair_filter_strategy import AllowAllClonePairFilter, ClonePairFilterStrategy


class CloneClassParser:
    """解析包含克隆对的CSV文件，并解析克隆类"""

    def __init__(self, filepath, encoding="utf-8"):
        self.filepath = filepath
        self.encoding = encoding
        # 用于多进程筛选的过滤器，在parse方法中设置
        self._active_filter = None

    def _read_csv(self):
        fields_list = []
        with open(self.filepath, "r", encoding=self.encoding, newline="") as f:
            for line in f:
                if line.isspace() or line.lstrip().startswith("#"):
                    continue
                fields = next(csv.reader([line]))
                fields_list.append(fields)
        return fields_list

    def _parse_clone_pair(self, fields):
        if len(fields) < 6:
            raise ValueError(
                f"Invalid clone line, expected >=6 fields, got {len(fields)}: {fields}"
            )
        f1 = fields[0].strip()
        s1 = int(fields[1].strip())
        e1 = int(fields[2].strip())
        f2 = fields[3].strip()
        s2 = int(fields[4].strip())
        e2 = int(fields[5].strip())
        f1 = os.path.normpath(f1)
        f2 = os.path.normpath(f2)
        return ClonePair(file1=f1, start1=s1, end1=e1, file2=f2, start2=s2, end2=e2)

    def _parse_clone_class(self, clone_pairs):
        # 使用并查集（DSU）将每个片段(file,start,end)作为节点，根据克隆对进行合并，
        # 最终把克隆对按照节点连通分量分组，生成 CloneClass 列表。
        if not clone_pairs:
            return []

        nodes = set()
        for p in clone_pairs:
            nodes.add((p.file1, p.start1, p.end1))
            nodes.add((p.file2, p.start2, p.end2))
        parent = {n: n for n in nodes}
        rank = {n: 0 for n in nodes}

        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]

        def union(a, b):
            ra = find(a)
            rb = find(b)
            if ra == rb:
                return
            if rank[ra] < rank[rb]:
                parent[ra] = rb
            elif rank[ra] > rank[rb]:
                parent[rb] = ra
            else:
                parent[rb] = ra
                rank[ra] += 1

        for p in clone_pairs:
            n1 = (p.file1, p.start1, p.end1)
            n2 = (p.file2, p.start2, p.end2)
            union(n1, n2)

        group_map = {}
        for p in clone_pairs:
            n1 = (p.file1, p.start1, p.end1)
            root = find(n1)
            group_map.setdefault(root, []).append(p)

        clone_classes = []
        for pairs in group_map.values():
            clone_classes.append(CloneClass(clone_pairs=pairs))
        return clone_classes

    def _filter_pair(self, pair):
        """用于多进程筛选的辅助方法"""
        return pair if self._active_filter.match(pair) else None

    def parse(
        self, filter_strategy: Optional[ClonePairFilterStrategy] = None,
        show_progress: bool = True,
        use_multiprocessing: bool = False,
        process_count: Optional[int] = None
    ):
        """解析克隆对并根据可选过滤策略汇聚成克隆类。

        Args:
            filter_strategy: 可选的过滤策略，默认为保留所有克隆对
            show_progress: 是否显示进度条，默认为True
            use_multiprocessing: 是否使用多进程筛选克隆对，默认为False
            process_count: 多进程数量，默认为CPU核心数的一半
        """
        fields_list = self._read_csv()
        clone_pairs = []
        items = tqdm(fields_list, desc="解析克隆对", unit="对") if show_progress else fields_list
        for fields in items:
            pair = self._parse_clone_pair(fields)
            clone_pairs.append(pair)
        
        active_filter = filter_strategy or AllowAllClonePairFilter()
        filtered_pairs = []
        
        # 根据是否开启多进程选择不同的筛选方式
        if use_multiprocessing:
            # 如果未指定进程数，使用CPU核心数的一半
            if process_count is None:
                process_count = max(1, multiprocessing.cpu_count() // 2)
            
            # 设置过滤器供多进程使用
            self._active_filter = active_filter
            
            # 使用多进程筛选
            with ProcessPoolExecutor(max_workers=process_count) as executor:
                if show_progress:
                    # 使用tqdm显示进度
                    filtered_results = list(
                        tqdm(
                            executor.map(self._filter_pair, clone_pairs),
                            total=len(clone_pairs),
                            desc="筛选克隆对",
                            unit="对"
                        )
                    )
                else:
                    filtered_results = list(executor.map(self._filter_pair, clone_pairs))
                
                # 过滤掉None值
                filtered_pairs = [pair for pair in filtered_results if pair is not None]
        else:
            # 保持原有逻辑
            items = tqdm(clone_pairs, desc="筛选克隆对", unit="对") if show_progress else clone_pairs
            for pair in items:
                if active_filter.match(pair):
                    filtered_pairs.append(pair)
        
        clone_classes = self._parse_clone_class(filtered_pairs)
        return clone_classes


def parse_clone_classes_from_csv(
    filepath, encoding, filter_strategy: Optional[ClonePairFilterStrategy] = None,
    show_progress: bool = True,
    use_multiprocessing: bool = False,
    process_count: Optional[int] = None
):
    parser = CloneClassParser(filepath, encoding)
    return parser.parse(
        filter_strategy=filter_strategy, 
        show_progress=show_progress,
        use_multiprocessing=use_multiprocessing,
        process_count=process_count
    )