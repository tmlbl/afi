def log_model_response(content: str):
    print("model response:", content)


def log_tool_use(name: str, input: dict):
    print(f"invoking tool {name} with input {input}")
