from dataclasses import dataclass
import javalang
import os


@dataclass
class FunctionInfo:
    """
    数据结构，用于存储函数的起始行数、终止行数和代码片段。
    """
    start_line: int
    end_line: int
    code_snippet: str


class JavaParser:
    """
    一个用于解析Java文件的类，可以从中提取函数信息。
    """

    def __init__(self, file_path: str):
        """
        初始化JavaParser。

        :param file_path: Java文件的路径。
        """
        self.file_path = file_path
        self.source_code = self._read_source_code()
        self.lines = self.source_code.splitlines(True)
        self.tokens = list(javalang.tokenizer.tokenize(self.source_code))
        self.tree = self._parse_source_code()

    def _read_source_code(self) -> str:
        """
        读取源文件内容。
        """
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _parse_source_code(self):
        """
        使用javalang解析源代码。
        """
        try:
            return javalang.parse.parse(self.source_code)
        except javalang.tokenizer.LexerError as e:
            print(f"Error lexing file {self.file_path}: {e}")
            return None
        except javalang.parser.JavaSyntaxError as e:
            print(f"Error parsing file {self.file_path}: {e}")
            return None

    def _get_node_end_line(self, node) -> int:
        """
        获取一个AST节点的结束行号。
        这个实现通过从节点的起始位置开始，在令牌流中查找匹配的右花括号'}'来确定结束行。
        它会忽略注释和字符串中的括号。
        """
        start_pos = node.position
        if not start_pos:
            return 0

        # 找到方法体开始的 '{'
        body_start_token_index = -1
        for i, token in enumerate(self.tokens):
            if token.position >= start_pos:
                if isinstance(token, javalang.tokenizer.Separator) and token.value == '{':
                    body_start_token_index = i
                    break

        if body_start_token_index == -1:
            # 没有方法体 (例如抽象方法)
            # 查找分号
            for i, token in enumerate(self.tokens):
                 if token.position >= start_pos:
                    if isinstance(token, javalang.tokenizer.Separator) and token.value == ';':
                        return token.position.line
            return start_pos.line

        open_braces = 0
        for i in range(body_start_token_index, len(self.tokens)):
            token = self.tokens[i]
            if isinstance(token, javalang.tokenizer.Separator):
                if token.value == '{':
                    open_braces += 1
                elif token.value == '}':
                    open_braces -= 1
                    if open_braces == 0:
                        return token.position.line

        return start_pos.line # 如果代码不完整，返回起始行


    def extract_functions(self) -> list[FunctionInfo]:
        """
        从解析树中提取所有函数，并将其转换为FunctionInfo对象列表。
        """
        if not self.tree:
            return []

        functions = []
        # 定义要查找的节点类型：方法和构造函数
        node_types = (javalang.tree.MethodDeclaration, javalang.tree.ConstructorDeclaration)

        # 遍历AST中的所有节点
        for path, node in self.tree:
            # 检查节点是否是我们感兴趣的类型
            if isinstance(node, node_types):
                start_line = node.position.line
                end_line = self._get_node_end_line(node)

                # javalang的行号是1-based的
                snippet_lines = self.lines[start_line - 1:end_line]
                code_snippet = "".join(snippet_lines).strip()

                functions.append(FunctionInfo(
                    start_line=start_line,
                    end_line=end_line,
                    code_snippet=code_snippet
                ))
        return functions


def extract_functions_from_file(file_path: str) -> list[FunctionInfo]:
    """
    读取一个.java文件，提取其中所有的函数，并返回一个FunctionInfo列表。

    :param file_path: .java文件的路径。
    :return: 一个包含所有函数信息的FunctionInfo对象列表。
    """
    parser = JavaParser(file_path)
    return parser.extract_functions()

