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

    print('========== Reading Clone Pairs ==========')

    parser = CloneClassParser("data/msccd_default.csv")

    print("Total Clone Pairs:", len(parser.clone_pairs))

    print("Clone Pairs Reading Time:", time.time() - now, "s")
    now = time.time()

    print('========== Filtering Clone Pairs ==========')

    filter_strategy = OnlyAllowJavaFunctionClonePairFilter()

    parser.apply_filter_strategy(filter_strategy, show_progress=True)

    print("Total Clone Pairs After Filtering:", len(parser.clone_pairs))

    print("Clone Pairs Filtering Time:", time.time() - now, "s")
    now = time.time()

    '''
    print('========== Filtering Clone Pairs ==========')

    filter_strategy = OnlyAllowJavaFunctionClonePairFilter(file_cache)

    print("Clone Pairs Filtering Time:", time.time() - now, "s")
    now = time.time()
    '''
    
    '''
    print('==========Extracting Functions from File Cache==========')
    
    # 从FileCache中提取所有函数
    all_functions = extract_functions_from_file_cache(file_cache, use_multiprocessing=mp, max_workers=max_workers)
    print(f"Extracted {len(all_functions)} functions from FileCache")
    
    print("Function Extraction Time:", time.time() - now, "s")
    now = time.time()
    
    print('==========Filtering Functions==========')
    
    # 创建函数过滤器
    function_filter = FunctionFilter(clone_classes)
    
    # 过滤不在克隆类中的函数
    filtered_functions = []
    for func in all_functions:
        if function_filter.is_allowed(func.path, func.start_line, func.end_line):
            filtered_functions.append(func)
    
    print(f"Filtered down to {len(filtered_functions)} functions")
    print("Function Filtering Time:", time.time() - now, "s")
    '''
    