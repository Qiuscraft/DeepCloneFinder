import os
import multiprocessing
from .detect_encoding import detect_encoding
from tqdm import tqdm


def _process_file(file_info, encoding='utf-8'):
    """
    处理单个文件的独立函数，用于多进程
    
    :param file_info: 包含root和file_name的元组
    :return: 绝对路径和文件内容的元组，如果出错则返回None
    """
    root, file_name = file_info
    file_path = os.path.join(root, file_name)
    try:
        # 使用检测到的编码打开文件
        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read()
            # 使用绝对路径作为键
            abs_path = os.path.abspath(file_path)
            return abs_path, content
    except Exception as e:
        # 处理可能的异常，例如文件权限问题、编码错误等
        print(f"Error loading file {file_path}: {e}")
        return None


class FileCache:
    def __init__(self, directory_path, show_progress=True, use_multiprocessing=False, workers=1):
        self.directory_path = directory_path
        self.manager = multiprocessing.Manager()
        self.cache = self.manager.dict()
        
        self._init_from_directory(show_progress, use_multiprocessing, workers)

    def _init_from_directory(self, show_progress: bool, use_multiprocessing: bool, workers: int):
        if not os.path.exists(self.directory_path):
            raise FileNotFoundError(f"Directory not found: {self.directory_path}")
        
        # 首先收集所有文件路径
        all_files = []
        for root, dirs, files in os.walk(self.directory_path):
            for file_name in files:
                all_files.append((root, file_name))
        
        if use_multiprocessing:
            # 创建进程池
            with multiprocessing.Pool(processes=workers) as pool:
                # 使用tqdm显示进度
                if show_progress:
                    results = list(tqdm(
                        pool.imap(_process_file, all_files),
                        total=len(all_files),
                        desc=f"Loading files with {workers} processes",
                        unit="file"
                    ))
                else:
                    results = pool.map(_process_file, all_files)
                
                # 处理结果
                for result in results:
                    if result:
                        rel_path, content = result
                        self.cache[rel_path] = content
        else:
            # 单进程处理
            for file_info in tqdm(all_files, desc="Loading files with 1 process", unit="file"):
                result = _process_file(file_info)
                if result:
                    rel_path, content = result
                    self.cache[rel_path] = content
    
    def get_file(self, file_path):
        """
        获取缓存中的文件内容
        :param file_path: 文件路径（相对于缓存目录）
        :return: 文件内容，如果文件不存在则返回None
        """
        return self.cache.get(file_path)
    
    def get_all_files(self):
        """
        获取所有缓存的文件路径
        :return: 文件路径列表
        """
        return list(self.cache.keys())
    
    def has_file(self, file_path):
        """
        检查缓存中是否存在指定文件
        :param file_path: 文件路径（相对于缓存目录）
        :return: 存在返回True，否则返回False
        """
        return file_path in self.cache
    