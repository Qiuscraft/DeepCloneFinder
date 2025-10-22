import difflib
from dataclasses import dataclass
from .clone_type import CloneType
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
            FileNotFoundError: 如果文件不存在或在缓存中找不到
        """
        # 使用辅助方法获取两个文件的代码片段
        snippet1 = self._get_file_snippet(self.file1, self.start1, self.end1, file_cache)
        snippet2 = self._get_file_snippet(self.file2, self.start2, self.end2, file_cache)
        
        return snippet1, snippet2
        
    def _get_file_snippet(self, file_path: str, start_line: int, end_line: int, file_cache: FileCache = None) -> str:
        """
        辅助方法：获取单个文件的代码片段。
        
        Args:
            file_path: 文件路径
            start_line: 起始行号
            end_line: 结束行号
            file_cache: 可选的FileCache对象
        
        Returns:
            str: 代码片段
        
        Raises:
            FileNotFoundError: 如果文件不存在或在缓存中找不到
        """
        if file_cache:
            # 尝试从缓存中获取文件内容
            content = file_cache.get_file(file_path)
            
            if content:
                lines = content.splitlines(keepends=True)
            else:
                # 查找缓存中最相似的文件路径
                similar_paths = self._find_similar_paths(file_path, file_cache)
                if similar_paths:
                    error_msg = f"File not found in cache: {file_path}\nMost similar paths in cache: {', '.join(similar_paths)}"
                else:
                    error_msg = f"File not found in cache: {file_path}\nNo similar paths found in cache"
                raise FileNotFoundError(error_msg)
        else:
            # 原有的文件读取逻辑
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        
        # 确保行号在有效范围内
        start_idx = max(0, start_line - 1)  # 转换为0索引
        end_idx = min(len(lines), end_line)
        return ''.join(lines[start_idx:end_idx])
        
    def _find_similar_paths(self, target_path: str, file_cache: FileCache, max_results: int = 3) -> list[str]:
        """
        查找缓存中与目标路径最相似的文件路径。
        
        Args:
            target_path: 目标文件路径
            file_cache: FileCache对象
            max_results: 返回的最大结果数量
        
        Returns:
            list[str]: 最相似的文件路径列表
        """
        # 获取缓存中所有的文件路径 - 使用正确的属性名'cache'
        cache_paths = list(file_cache.cache.keys())
        
        # 计算相似度并排序
        similarities = [(path, difflib.SequenceMatcher(None, target_path, path).ratio()) for path in cache_paths]
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # 返回前max_results个最相似的路径
        return [path for path, _ in similarities[:max_results]]