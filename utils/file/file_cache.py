import os
import multiprocessing
from .detect_encoding import detect_encoding
from tqdm import tqdm


class FileCache:
    def __init__(self, directory_path, show_progress=True, use_multiprocess=True, max_workers=None):
        """
        初始化FileCache对象，读取指定目录下的所有文件到内存
        
        :param directory_path: 要缓存的目录路径
        :param show_progress: 是否显示加载进度条
        :param use_multiprocess: 是否使用多进程加速
        :param max_workers: 最大进程数，默认为CPU核心数的一半
        """
        self.directory_path = directory_path
        self.cache = {}  # 使用字典存储文件路径和内容的映射
        self._load_files(show_progress, use_multiprocess, max_workers)
    
    def _process_file(self, file_info):
        """
        处理单个文件的函数，用于多进程
        
        :param file_info: 包含root和file_name的元组
        :return: 相对路径和文件内容的元组，如果出错则返回None
        """
        root, file_name = file_info
        file_path = os.path.join(root, file_name)
        try:
            # 检测文件编码
            encoding = detect_encoding(file_path)
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

    def _load_files(self, show_progress=True, use_multiprocess=True, max_workers=None):
        """
        加载目录下的所有文件到内存
        
        :param show_progress: 是否显示加载进度条
        :param use_multiprocess: 是否使用多进程加速
        :param max_workers: 最大进程数，默认为CPU核心数的一半
        """
        if not os.path.exists(self.directory_path):
            raise FileNotFoundError(f"Directory not found: {self.directory_path}")
        
        # 首先收集所有文件路径
        all_files = []
        for root, dirs, files in os.walk(self.directory_path):
            for file_name in files:
                all_files.append((root, file_name))
        
        # 使用单进程加载
        if not use_multiprocess or len(all_files) <= 1:
            # 使用tqdm创建进度条
            file_iterator = all_files
            if show_progress:
                file_iterator = tqdm(all_files, desc="Loading files", unit="file")
            
            for root, file_name in file_iterator:
                result = self._process_file((root, file_name))
                if result:
                    rel_path, content = result
                    self.cache[rel_path] = content
        else:
            # 使用多进程加载
            # 确定进程数
            if max_workers is None:
                # 默认使用CPU核心数的一半
                max_workers = max(1, multiprocessing.cpu_count() // 2)
            
            # 调整进程数，避免进程数超过文件数
            max_workers = min(max_workers, len(all_files))
            
            # 创建进程池
            with multiprocessing.Pool(processes=max_workers) as pool:
                # 使用tqdm显示进度
                if show_progress:
                    results = list(tqdm(
                        pool.imap(self._process_file, all_files),
                        total=len(all_files),
                        desc=f"Loading files with {max_workers} processes",
                        unit="file"
                    ))
                else:
                    results = pool.map(self._process_file, all_files)
                
                # 处理结果
                for result in results:
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
    
    def clear_cache(self):
        """
        清空缓存
        """
        self.cache.clear()
    
    def reload_cache(self, show_progress=False, use_multiprocess=False, max_workers=None):
        """
        重新加载缓存
        
        :param show_progress: 是否显示加载进度条
        :param use_multiprocess: 是否使用多进程加速
        :param max_workers: 最大进程数，默认为CPU核心数的一半
        """
        self.cache.clear()
        self._load_files(show_progress, use_multiprocess, max_workers)