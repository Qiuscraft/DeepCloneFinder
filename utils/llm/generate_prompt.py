def generate_prompt(filepath, replacement_dict):
    with open(filepath, 'r', encoding='utf-8') as f:
        prompt = f.read()
    for key, value in replacement_dict.items():
        prompt = prompt.replace(f'{{{{{key}}}}}', value)
    return prompt