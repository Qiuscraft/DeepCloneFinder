import pickle
from typing import List
from utils.java_code.function_extract import FunctionInfo

def write_functions_to_disk(functions: List[FunctionInfo], file_path: str):
    """
    将FunctionInfo列表写入磁盘。

    :param functions: 要写入的FunctionInfo对象列表。
    :param file_path: 目标文件路径。
    """
    with open(file_path, 'wb') as f:
        pickle.dump(functions, f)

def read_functions_from_disk(file_path: str) -> List[FunctionInfo]:
    """
    从磁盘读取FunctionInfo列表。

    :param file_path: 源文件路径。
    :return: 从文件中读取的FunctionInfo对象列表。
    """
    with open(file_path, 'rb') as f:
        functions = pickle.load(f)
    return functions

