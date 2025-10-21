import os
import multiprocessing
import pickle
import hashlib
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
    def __init__(self, directory_path, show_progress=True, use_multiprocessing=False, workers=1, disk_cache=True):
        self.directory_path = directory_path
        self.manager = multiprocessing.Manager()
        self.cache = self.manager.dict()
        
        if disk_cache:
            if not self._init_from_disk_cache():
                self._init_from_directory(show_progress, use_multiprocessing, workers)
                self._save_to_disk_cache()
        else:
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
    
    def _get_cache_file_path(self):
        """
        获取缓存文件的路径
        
        :return: 缓存文件的绝对路径
        """
        
        # 计算目录路径和修改时间的组合哈希值
        hash_input = str(os.path.getmtime(self.directory_path))
        directory_hash = hashlib.md5(hash_input.encode()).hexdigest()
        
        # 构建缓存目录路径 - 自动检测当前运行文件所在目录作为项目根目录
        import sys
        
        # 获取当前正在运行的主脚本路径
        # sys.argv[0] 是当前执行的Python脚本的路径
        if hasattr(sys, 'frozen'):  # 检查是否是打包后的可执行文件
            # 如果是打包后的程序，获取可执行文件所在目录
            main_script_path = os.path.dirname(os.path.abspath(sys.executable))
        else:
            # 正常Python脚本执行模式
            main_script_path = os.path.dirname(os.path.abspath(sys.argv[0]))
            
        # 将主脚本所在目录作为项目根目录
        project_root = main_script_path
        
        # 也可以选择验证是否存在关键文件来确认这是项目根目录
        # 例如检查是否存在 config.py 或者其他根目录下的标志性文件
        # if not os.path.exists(os.path.join(project_root, 'config.py')):
        #     # 如果找不到标志性文件，回退到基于当前文件位置的方法
        #     project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        
        cache_dir = os.path.join(project_root, 'cache', self.directory_path.strip('/').replace('/', '_'))
        # 确保缓存目录存在
        os.makedirs(cache_dir, exist_ok=True)
        # 返回缓存文件路径
        return os.path.join(cache_dir, f'{directory_hash}.pkl')
        
    def _init_from_disk_cache(self):
        """
        从磁盘加载缓存，确保多进程环境下的正常共享
        
        :return: 加载成功返回True，否则返回False
        """
        try:
            cache_file = self._get_cache_file_path()
            if os.path.exists(cache_file):
                with open(cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                    for key, value in cache_data.items():
                        self.cache[key] = value
                return True
        except Exception as e:
            print(f"Error loading cache from disk: {e}")
        return False
        
    def _save_to_disk_cache(self):
        """
        保存缓存到磁盘
        """
        try:
            cache_file = self._get_cache_file_path()
            cache_data = dict(self.cache)
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
        except Exception as e:
            print(f"Error saving cache to disk: {e}")