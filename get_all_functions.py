import concurrent.futures
import os

from tqdm import tqdm

from typing import List
from utils.java_code.function_info import FunctionInfo
from utils.java_code.java_parser import JavaParser


def process_file(java_file: str) -> List[FunctionInfo]:
    """
    处理单个Java文件，提取函数并返回函数信息列表。
    
    :param java_file: Java文件路径
    :return: 提取的函数信息列表
    """
    try:
        parser = JavaParser(java_file)
        return parser.extract_functions()
    except Exception as e:
        print(f"处理文件 '{java_file}' 时发生错误 {e.__class__}: {e}")
        return []


def extract_functions_from_directory(path, use_multiprocessing=False, max_workers=1):
    files = []
    for root, dirs, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith('.java'):
                files.append(os.path.join(root, filename))

    if use_multiprocessing:
        all_functions = []
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {executor.submit(process_file, file): file for file in files}
            for future in tqdm(concurrent.futures.as_completed(future_to_file), total=len(files), desc="提取进度"):
                file = future_to_file[future]
                try:
                    functions = future.result()
                    all_functions.extend(functions)
                except Exception as exc:
                    print(f"处理文件 '{file}' 时生成异常: {exc}")
        return all_functions
    else:
        all_functions = []
        for file in tqdm(files, desc="提取进度"):
            try:
                functions = process_file(file)
                all_functions.extend(functions)
            except Exception as exc:
                print(f"处理文件 '{file}' 时生成异常: {exc}")
        return all_functions
