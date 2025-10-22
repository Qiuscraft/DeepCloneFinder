import json
import random

from zai import ZhipuAiClient
from utils.llm.generate_prompt import generate_prompt


def get_clone_class_functions(clone_class, function_index):
    pairs = clone_class.clone_pairs
    functions = []
    for pair in pairs:
        key1 = (pair.file1, pair.start1, pair.end1)
        key2 = (pair.file2, pair.start2, pair.end2)
        if key1 in function_index:
            functions.append(function_index[key1])
        if key2 in function_index:
            functions.append(function_index[key2])
    # 去重
    unique_functions = { (func.path, func.start_line, func.end_line): func for func in functions }
    return list(unique_functions.values())

def get_clone_class_string(clone_class, function_index):
    functions = get_clone_class_functions(clone_class, function_index)
    function_strs = []
    index = 0
    for func in functions:
        function_strs.append(f"\n// Function {index}\n")
        function_strs.append(func.code_snippet)
        function_strs.append("\n")
        index += 1
    return '\n'.join(function_strs)

def generate_jsonl(clone_class_list, function_index, model, file_path):
    jsonl = []

    index = 0
    for clone_class in clone_class_list:
        json_entry = {
            "custom_id": f"clone_class_{index}",
            "method": "POST",
            "url": "/v4/chat/completions",
            "body": {
                "model": model,
                "messages": [
                    {"role": "system","content": generate_prompt("prompts/function_summary.md", {}),},
                    {"role": "user", "content": random.choice(get_clone_class_functions(clone_class, function_index)).code_snippet}
                ],
            }
        }

        jsonl.append(json_entry)

        index += 1

    with open(file_path, 'w') as f:  # 使用上下文管理器打开文件
        for entry in jsonl:  # 遍历数据列表中的每个 JSON 对象
            json_line = json.dumps(entry)  # 将字典转换为 JSON 字符串
            f.write(json_line + '\n')  # 将 JSON 字符串写入文件并换行

def upload_batch(file_path, api_key):
    client = ZhipuAiClient(api_key=api_key)

    # 上传批处理文件
    file_object = client.files.create(
        file=open(file_path, "rb"),
        purpose="batch"
    )

    return file_object

def create_batch_task(file_object, api_key):
    client = ZhipuAiClient(api_key=api_key)
    # 创建批处理任务
    batch = client.batches.create(
        input_file_id=file_object.id,
        endpoint="/v4/chat/completions",
        auto_delete_input_file=True,
        metadata={
            "description": "DeepCloneFinder Clone Class Summarization",
            "project": "DeepCloneFinder"
        }
    )
