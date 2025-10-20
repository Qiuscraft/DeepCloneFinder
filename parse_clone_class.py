import random
import time

from clone.clone_class_parser import CloneClassParser


if __name__ == "__main__":
    now = time.time()
    parser = CloneClassParser("data/msccd_default.csv")
    clone_classes = parser.parse()
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