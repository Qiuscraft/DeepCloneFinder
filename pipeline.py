import time

from clone.clone_class_parser import CloneClassParser
from clone.pair_filter_strategy import OnlyAllowJavaFunctionClonePairFilter
import config
from get_all_functions import extract_functions_from_directory

use_multiprocessing = config.use_multiprocessing
workers = config.workers



if __name__ == "__main__":
    now = time.time()

    print('========== Extracting All Functions ==========')
    functions = extract_functions_from_directory(config.dataset_path, use_multiprocessing=use_multiprocessing, max_workers=workers)

    print("Functions Extracting Time:", time.time() - now, "s")
    now = time.time()

    print('========== Indexing Functions ==========')
    # 创建函数索引，便于后续查找
    function_index = {}
    for func in functions:
        key = (func.path, func.start_line, func.end_line)
        function_index[key] = func

    print("Functions Indexing Time:", time.time() - now, "s")
    now = time.time()

    print('========== Reading Clone Pairs ==========')

    parser = CloneClassParser("data/msccd_default.csv")

    print("Total Clone Pairs:", len(parser.clone_pairs))

    print("Clone Pairs Reading Time:", time.time() - now, "s")
    now = time.time()

    print('========== Filtering Clone Pairs ==========')

    filter_strategy = OnlyAllowJavaFunctionClonePairFilter(function_index)

    parser.apply_filter_strategy(filter_strategy, show_progress=True)

    print("Total Clone Pairs After Filtering:", len(parser.clone_pairs))

    print("Clone Pairs Filtering Time:", time.time() - now, "s")
    now = time.time()

    print('========== Parsing Clone Classes ==========')
    clone_classes = parser.parse()
    
    print("Total Clone Classes:", len(clone_classes))

    print("Clone Classes Parsing Time:", time.time() - now, "s")
    now = time.time()
