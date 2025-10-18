from model.clone_class import CloneClass
from model.clone_pair import ClonePair
import csv
import os


class CloneClassParser:
    """解析包含克隆对的CSV文件，并解析克隆类"""

    def __init__(self, filepath, encoding="utf-8"):
        self.filepath = filepath
        self.encoding = encoding

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

    def parse(self):
        fields_list = self._read_csv()
        clone_pairs = []
        for fields in fields_list:
            pair = self._parse_clone_pair(fields)
            clone_pairs.append(pair)
        clone_classes = self._parse_clone_class(clone_pairs)
        return clone_classes


def parse_clone_classes_from_csv(filepath, encoding):
    parser = CloneClassParser(filepath, encoding)
    return parser.parse()


if __name__ == "__main__":
    parser = CloneClassParser("test/test.csv")
    clone_classes = parser.parse()
    for idx, clone_class in enumerate(clone_classes):
        print(f"Clone Class {idx + 1}:")
        for pair in clone_class.clone_pairs:
            print(f"{pair}")
        print(f"{clone_class.clone_type}")
