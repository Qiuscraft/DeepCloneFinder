import time

from clone.clone_class_parser import CloneClassParser
from clone.pair_filter_strategy import OnlyAllowJavaFunctionClonePairFilter
import config
from utils.file.file_cache import FileCache
from get_all_functions import extract_functions_from_file_cache
from function.function_filter import FunctionFilter

mp = config.use_multiprocessing
workers = config.workers



if __name__ == "__main__":
    now = time.time()
    
    print('========== Loading File Cache ==========')
    file_cache = FileCache(config.dataset_path, show_progress=True, use_multiprocessing=mp, workers=workers, disk_cache=True)
    
    print("File Cache Creation Time:", time.time() - now, "s")
    now = time.time()
    
    print('========== Parsing Clone Classes ==========')

    filter_strategy = OnlyAllowJavaFunctionClonePairFilter(file_cache)
    
    parser = CloneClassParser("data/msccd_default.csv")
    clone_classes = parser.parse()

    print("Total Clone Classes:", len(clone_classes))
    print("Total Clone Pairs:", sum(len(cc.clone_pairs) for cc in clone_classes))

    print("Clone Class Parsing Time:", time.time() - now, "s")
    now = time.time()
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
    