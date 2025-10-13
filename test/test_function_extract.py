import os
import sys

# 将项目根目录添加到Python路径中，以解决模块导入问题
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.function_extract import extract_functions_from_file

# 获取当前脚本所在的目录
# 这使得测试可以在任何工作目录下运行
current_dir = os.path.dirname(os.path.abspath(__file__))
# 构建到测试Java文件的绝对路径
TEST_JAVA_FILE = os.path.join(current_dir, "function_extract.java")

def test_extract_all_functions_and_constructors():
    """
    测试是否能从给定的Java文件中提取出所有预期的函数和构造函数。
    """
    functions = extract_functions_from_file(TEST_JAVA_FILE)

    assert len(functions) == 8

    assert functions[0].start_line == 12
    assert functions[0].end_line == 14

    assert functions[1].start_line == 18
    assert functions[1].end_line == 21

    assert functions[2].start_line == 24
    assert functions[2].end_line == 29

    assert functions[3].start_line == 33
    assert functions[3].end_line == 35

    assert functions[4].start_line == 39
    assert functions[4].end_line == 47

    assert functions[5].start_line == 42
    assert functions[5].end_line == 44

    assert functions[6].start_line == 50
    assert functions[6].end_line == 50

    assert functions[7].start_line == 53
    assert functions[7].end_line == 55
