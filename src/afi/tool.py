import inspect
from typing import get_type_hints
from functools import wraps
from afi.json_schema import make_tool_def

tool_funcs = {}


def call_tool(name: str, input: dict):
    output = tool_funcs[name](**input)
    return str(output)


def get_claude_tool_defs():
    tool_defs = []
    for func in tool_funcs.values():
        tool_def = make_tool_def(func)
        tool_defs.append(tool_def)
    return tool_defs


def tool(func):
    """
    Wraps a regular Python function and adds it to the tool registry,
    allowing an agent started from this process to call it.

    Function parameters must have type annotations, and only consist
    of simple scalar types like str, int, float or bool.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # validate argument types at call time and give
        # the agent a helpful error if they're wrong
        sig = inspect.signature(func)

        hints = get_type_hints(func)
        bound = sig.bind(*args, **kwargs)

        for param_name, value in bound.arguments.items():
            expected_type = hints[param_name]
            if not isinstance(value, expected_type):
                raise ValueError(
                    f"{param_name} must be {expected_type.__name__}, "
                    f"got {type(value).__name__}"
                )

        return func(*args, **kwargs)

    tool_funcs[func.__name__] = wrapper
    return wrapper
