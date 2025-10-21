from dataclasses import dataclass
import os
from .clone_type import CloneType
from utils.file.detect_encoding import detect_encoding
from utils.file.file_cache import FileCache


@dataclass
class ClonePair:
    file1: str
    start1: int
    end1: int
    file2: str
    start2: int
    end2: int
    clone_type: CloneType = CloneType.UNKNOWN
    
    def get_code_snippets(self, file_cache: FileCache = None) -> tuple[str, str]:
        """
        获取两个克隆对的代码片段。
        
        Args:
            file_cache: 可选的FileCache对象，如果提供，则从缓存中获取文件内容
        
        Returns:
            tuple[str, str]: 包含两个文件中对应代码片段的元组
        
        Raises:
            FileNotFoundError: 如果文件不存在
        """
        # 读取第一个文件的代码片段
        if file_cache:
            # 尝试多种方式从缓存中获取文件内容
            # 1. 直接使用文件路径查询
            content = file_cache.get_file(self.file1)
            
            # 2. 如果直接查询失败，尝试通过比较文件名或绝对路径查找
            if not content:
                for cached_path, cached_content in file_cache.cache.items():
                    if os.path.basename(cached_path) == os.path.basename(self.file1) or \
                       os.path.abspath(cached_path) == os.path.abspath(self.file1):
                        content = cached_content
                        break
            
            if content:
                lines1 = content.splitlines(keepends=True)
            else:
                # 如果缓存中找不到，使用原有的文件读取逻辑
                encoding1 = detect_encoding(self.file1)
                with open(self.file1, 'r', encoding=encoding1) as f:
                    lines1 = f.readlines()
        else:
            # 原有的文件读取逻辑
            encoding1 = detect_encoding(self.file1)
            with open(self.file1, 'r', encoding=encoding1) as f:
                lines1 = f.readlines()
        
        # 确保行号在有效范围内
        start_idx1 = max(0, self.start1 - 1)  # 转换为0索引
        end_idx1 = min(len(lines1), self.end1)
        snippet1 = ''.join(lines1[start_idx1:end_idx1])
        
        # 读取第二个文件的代码片段
        if file_cache:
            # 尝试多种方式从缓存中获取文件内容
            # 1. 直接使用文件路径查询
            content = file_cache.get_file(self.file2)
            
            # 2. 如果直接查询失败，尝试通过比较文件名或绝对路径查找
            if not content:
                for cached_path, cached_content in file_cache.cache.items():
                    if os.path.basename(cached_path) == os.path.basename(self.file2) or \
                       os.path.abspath(cached_path) == os.path.abspath(self.file2):
                        content = cached_content
                        break
            
            if content:
                lines2 = content.splitlines(keepends=True)
            else:
                # 如果缓存中找不到，使用原有的文件读取逻辑
                encoding2 = detect_encoding(self.file2)
                with open(self.file2, 'r', encoding=encoding2) as f:
                    lines2 = f.readlines()
        else:
            # 原有的文件读取逻辑
            encoding2 = detect_encoding(self.file2)
            with open(self.file2, 'r', encoding=encoding2) as f:
                lines2 = f.readlines()
        
        # 确保行号在有效范围内
        start_idx2 = max(0, self.start2 - 1)  # 转换为0索引
        end_idx2 = min(len(lines2), self.end2)
        snippet2 = ''.join(lines2[start_idx2:end_idx2])
        
        return snippet1, snippet2