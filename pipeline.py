import os
import pickle
import time

from clone.clone_class_parser import CloneClassParser
from clone.pair_filter_strategy import OnlyAllowJavaFunctionClonePairFilter
import config
from get_all_functions import extract_functions_from_directory
from utils.file.file_io import read_functions_from_disk, write_functions_to_disk
from utils.llm.clone_class_summary import create_batch_task, generate_jsonl, upload_batch

use_multiprocessing = config.use_multiprocessing
workers = config.workers


def extract_all_functions(path=None, pkl_path="functions.pkl"):
    if path is None:
        path = config.dataset_path

    if os.path.exists(pkl_path):
        functions = read_functions_from_disk(pkl_path)

    else:
        functions = extract_functions_from_directory(path, use_multiprocessing=use_multiprocessing, max_workers=workers)
        write_functions_to_disk(functions, pkl_path)
    return functions


if __name__ == "__main__":
    now = time.time()

    print('========== Extracting All Functions ==========')

    functions = extract_all_functions()

    print("Functions Extracting Time:", time.time() - now, "s")
    now = time.time()

    print('========== Indexing Functions ==========')
    
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

    print('========== Indexing Clone Pairs ==========')

    pair_index = {}
    for pair in parser.clone_pairs:
        key = (pair.file1, pair.start1, pair.end1)
        if key not in pair_index:
            pair_index[key] = []
        pair_index[key].append(pair)

        key = (pair.file2, pair.start2, pair.end2)
        if key not in pair_index:
            pair_index[key] = []
        pair_index[key].append(pair)

    print("Clone Pairs Indexing Time:", time.time() - now, "s")
    now = time.time()

    print("========== Filtering Functions ==========")

    valid_functions = []
    for func in functions:
        key = (func.path, func.start_line, func.end_line)
        if (key not in pair_index):
            valid_functions.append(func)

    print("Total Valid Functions:", len(valid_functions))
    print("Functions Filtering Time:", time.time() - now, "s")
    now = time.time()

    print('========== Testing ==========')

    with open("process/clone_classes.pkl", 'wb') as f:
        pickle.dump(clone_classes, f)

    with open("process/function_index.pkl", 'wb') as f:
        pickle.dump(function_index, f)
    '''
    generate_jsonl(clone_classes, function_index, model="glm-4-flash", file_path="process/clone_class_summaries.jsonl")

    batch_file_object = upload_batch("process/clone_class_summaries.jsonl", api_key=config.zhipuai_api_key)

    create_batch_task(batch_file_object, api_key=config.zhipuai_api_key)
    '''
    '''
    print(
        ask_llm_for_function_summary(
            system_prompt=generate_prompt("prompts/function_summary.md", {}),
            user_prompt=get_clone_class_functions(clone_classes[0], function_index)[0].code_snippet,
            api_key=config.zhipuai_api_key,
            model="glm-4.5-flash"
        )
    )
    '''
