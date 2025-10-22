import json
from zai import ZhipuAiClient


def ask_llm_for_function_summary(system_prompt, user_prompt, api_key, model="glm-4.5-flash"):
    client = ZhipuAiClient(api_key=api_key)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        response_format={
            "type": "json_object"
        }
    )

    return json.loads(response.choices[0].message.content)
