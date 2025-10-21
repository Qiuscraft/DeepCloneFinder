import concurrent.futures
import os
import random

from tqdm import tqdm

from utils.file.file_cache import FileCache
from utils.file.file_io import write_functions_to_disk
from utils.file.line_counter import count_lines_in_file
from typing import List, Dict, Tuple
from utils.java_code.function_info import FunctionInfo
from utils.java_code.java_parser import JavaParser
from utils.logger.logger import logger


def process_file_content(java_file: str, file_content: str) -> List[FunctionInfo]:
    """
    处理单个Java文件内容，提取函数并返回函数信息列表。
    
    :param java_file: Java文件路径
    :param file_content: Java文件的内容
    :return: 提取的函数信息列表
    """
    try:
        # 使用直接传递的文件内容创建JavaParser
        parser = JavaParser(java_file, file_content=file_content)
        return parser.extract_functions()
    except Exception as e:
        logger.error(f"处理文件 '{java_file}' 时发生错误 {e.__class__}: {e}")
        return []


def extract_functions_from_file_cache(
    file_cache: FileCache, 
    use_multiprocessing: bool = True, 
    max_workers: int = 18
) -> List[FunctionInfo]:
    """
    从FileCache对象中提取所有Java文件中的函数信息。

    :param file_cache: 包含Java文件的FileCache对象
    :param use_multiprocessing: 是否使用多进程处理，默认为True
    :param max_workers: 多进程处理时的最大进程数，默认为18
    :return: 提取的所有函数信息列表
    """
    # 过滤出.java文件
    java_files = [file_path for file_path in file_cache.get_all_files() if file_path.endswith('.java')]
    
    if not java_files:
        return []
    
    all_functions: List[FunctionInfo] = []
    
    if use_multiprocessing:
        # 使用ProcessPoolExecutor进行多进程处理
        # 获取FileCache内部的共享字典对象
        file_cache_dict = file_cache.cache
        
        # 直接遍历共享字典的键值对，只处理.java文件
        java_file_contents = [(java_file, content) for java_file, content in file_cache_dict.items() if java_file.endswith('.java')]
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务 - 直接传递文件路径和内容
            # 这样避免了在子进程中再次查找共享字典
            future_to_file = {executor.submit(process_file_content, java_file, content): java_file for java_file, content in java_file_contents}
            # 使用tqdm显示进度
            for future in tqdm(concurrent.futures.as_completed(future_to_file), total=len(java_file_contents), desc="提取进度"):
                try:
                    functions_list = future.result()
                    if functions_list:
                        all_functions.extend(functions_list)
                except Exception as exc:
                    java_file = future_to_file[future]
                    logger.error(f"处理文件 '{java_file}' 时生成异常: {exc}")
    else:
        # 使用单线程处理
        for java_file in tqdm(java_files, desc="提取进度"):
            try:
                # 对于单线程模式，我们可以继续使用file_cache以提高性能
                parser = JavaParser(java_file, file_cache)
                functions_list = parser.extract_functions()
                if functions_list:
                    all_functions.extend(functions_list)
            except Exception as exc:
                logger.error(f"处理文件 '{java_file}' 时生成异常: {exc}")
    
    return all_functions