from zai import ZhipuAiClient
import json

from utils.prompt import generate_prompt

# 初始化客户端
client = ZhipuAiClient(api_key="your-api-key")

prompt = generate_prompt("prompts/clone_class_summary.md", {})

# 基础 JSON 模式
response = client.chat.completions.create(
    model="glm-4.5-flash",
    messages=[
        {
            "role": "system",
            "content": prompt
        },
        {
            "role": "user",
            "content": clone_class
        }
    ],
    response_format={
        "type": "json_object"
    }
)

# 解析结果
result = json.loads(response.choices[0].message.content)
print(result)