import os
from typing import List, Optional

import javalang

from utils.file.detect_encoding import detect_encoding
from utils.file.file_cache import FileCache
from utils.java_code.function_info import FunctionInfo


class JavaParser:
    """Parse a Java source file and extract method information."""

    def __init__(self, file_path: str, file_cache: Optional[FileCache] = None, file_content: Optional[str] = None):
        self.file_path = file_path
        self.filename = os.path.basename(file_path)
        self.subdirectory = os.path.basename(os.path.dirname(file_path))
        self.source_code = self._read_source_code(file_cache, file_content)
        self.lines = self.source_code.splitlines(True)
        self.tokens = list(javalang.tokenizer.tokenize(self.source_code))
        self.tree = self._parse_source_code()

    def _read_source_code(self, file_cache: Optional[FileCache], file_content: Optional[str]) -> str:
        # 优先使用直接提供的文件内容
        if file_content is not None:
            return file_content
        
        # 如果提供了文件缓存，尝试从缓存中获取文件内容
        if file_cache and file_cache.has_file(self.file_path):
            return file_cache.get_file(self.file_path)
        
        # 否则，从文件系统读取文件内容（原有逻辑）
        with open(self.file_path, "r", encoding=detect_encoding(self.file_path)) as f:
            return f.read()

    def _parse_source_code(self):
        return javalang.parse.parse(self.source_code)

    def _get_node_end_line(self, node) -> int:
        start_pos = node.position
        if not start_pos:
            return 0

        body_start_token_index = -1
        for i, token in enumerate(self.tokens):
            if token.position >= start_pos:
                if isinstance(token, javalang.tokenizer.Separator) and token.value == "{":
                    body_start_token_index = i
                    break

        if body_start_token_index == -1:
            for token in self.tokens:
                if token.position >= start_pos:
                    if isinstance(token, javalang.tokenizer.Separator) and token.value == ";":
                        return token.position.line
            return start_pos.line

        open_braces = 0
        for token in self.tokens[body_start_token_index:]:
            if isinstance(token, javalang.tokenizer.Separator):
                if token.value == "{":
                    open_braces += 1
                elif token.value == "}":
                    open_braces -= 1
                    if open_braces == 0:
                        return token.position.line

        return start_pos.line

    def extract_functions(self) -> List[FunctionInfo]:
        if not self.tree:
            return []

        functions: List[FunctionInfo] = []
        node_types = (javalang.tree.MethodDeclaration, javalang.tree.ConstructorDeclaration)

        for _, node in self.tree:
            if isinstance(node, node_types):
                start_line = node.position.line
                end_line = self._get_node_end_line(node)
                snippet_lines = self.lines[start_line - 1 : end_line]
                code_snippet = "".join(snippet_lines).strip()
                functions.append(
                    FunctionInfo(
                        start_line=start_line,
                        end_line=end_line,
                        code_snippet=code_snippet,
                        subdirectory=self.subdirectory,
                        filename=self.filename,
                        path=self.file_path,
                    )
                )
        return functions