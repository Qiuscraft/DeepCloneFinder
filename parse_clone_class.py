import time
import time
import random

from clone.clone_class_parser import CloneClassParser
from clone.pair_filter_strategy import OnlyAllowJavaFunctionClonePairFilter
import config
from utils.file.file_cache import FileCache


if __name__ == "__main__":
    now = time.time()
    parser = CloneClassParser("data/msccd_default.csv")
    
    file_cache = FileCache(config.dataset_path, show_progress=True)
    
    # 创建过滤策略时传入FileCache
    filter_strategy = OnlyAllowJavaFunctionClonePairFilter(file_cache=file_cache)
    
    # 解析克隆类
    clone_classes = parser.parse(filter_strategy=filter_strategy)
    print("Total Clone Classes:", len(clone_classes))
    print("Total Clone Pairs:", sum(len(cc.clone_pairs) for cc in clone_classes))
    print("Parsing Time:", time.time() - now)
    print("Random Sample Clone Class:")
    if not clone_classes:
        print("No clone classes found.")
    else:
        sample = random.choice(clone_classes)
        print(f"Total Pairs: {len(sample.clone_pairs)}")
        for idx, pair in enumerate(sample.clone_pairs, start=1):
            print(
                f"Pair {idx}: {pair.file1}:{pair.start1}-{pair.end1} <-> "
                f"{pair.file2}:{pair.start2}-{pair.end2}"
            )