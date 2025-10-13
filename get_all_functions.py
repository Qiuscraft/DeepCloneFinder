import concurrent.futures
import os
import random

from tqdm import tqdm

from config import dataset_path
from utils.function_extract import extract_functions_from_file, FunctionInfo
from utils.file_io import write_functions_to_disk
from typing import List
from utils.logger import logger


def get_all_java_files(directory: str) -> list[str]:
    """
    遍历指定目录及其所有子目录，返回所有.java文件的绝对路径列表。

    :param directory: 要遍历的目录路径。
    :return: 一个包含所有.java文件绝对路径的列表。
    """
    java_files = []
    logger.info(f"正在从 '{directory}' 目录中搜寻.java文件...")
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".java"):
                java_files.append(os.path.join(root, file))
    logger.info(f"搜寻完成，共找到 {len(java_files)} 个.java文件。")
    return java_files


def process_file(java_file: str) -> List[FunctionInfo]:
    """
    处理单个Java文件，提取函数并返回函数信息列表。
    这是一个用于多进程的工作函数。
    """
    try:
        return extract_functions_from_file(java_file)
    except Exception as e:
        # 在多线程中打印需要小心，但对于错误报告是可接受的。
        # 加一个换行符以避免与tqdm进度条混淆。
        logger.error(f"处理文件 '{java_file}' 时发生错误 {e.__class__}: {e}")
        return []  # 返回空列表表示此文件没有成功提取函数


def main():
    """
    主函数，执行遍历、提取和计数操作。
    """
    if not os.path.isdir(dataset_path):
        logger.error(f"Error: 在 'config.py' 中配置的数据集路径 '{dataset_path}' 不是一个有效的目录。")
        return

    java_files = get_all_java_files(dataset_path)
    if not java_files:
        return

    logger.info("开始从所有.java文件中多进程提取函数...")
    all_functions: List[FunctionInfo] = []
    # 使用ProcessPoolExecutor进行多进程处理
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # 提交所有任务
        future_to_file = {executor.submit(process_file, java_file): java_file for java_file in java_files}
        # 使用tqdm显示进度
        for future in tqdm(concurrent.futures.as_completed(future_to_file), total=len(java_files), desc="提取进度"):
            try:
                functions_list = future.result()
                if functions_list:
                    all_functions.extend(functions_list)
            except Exception as exc:
                java_file = future_to_file[future]
                logger.error(f"处理文件 '{java_file}' 时生成异常: {exc}")

    output_file = "functions.pkl"
    logger.info(f"开始将提取的函数写入到 '{output_file}'...")
    write_functions_to_disk(all_functions, output_file)
    logger.info("写入完成！")

    if all_functions:
        logger.info("随机挑选3个函数进行展示:")
        num_to_display = min(3, len(all_functions))
        selected_functions = random.sample(all_functions, num_to_display)
        for i, func in enumerate(selected_functions):
            logger.info(f"--- 函数 {i + 1}/{num_to_display} ---")
            logger.info(f"  父文件夹: {func.subdirectory}")
            logger.info(f"  文件名: {func.filename}")
            logger.info(f"  行数: {func.start_line}-{func.end_line}")
            logger.info(f"  代码:\n{func.code_snippet}")
            logger.info("-" * (len(f"--- 函数 {i + 1}/{num_to_display} ---")))

    total_functions_count = len(all_functions)

    logger.info("提取完成！")
    logger.info(f"在 {len(java_files)} 个.java文件中，总共提取了 {total_functions_count} 个函数。")


if __name__ == "__main__":
    main()
