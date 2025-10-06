import inspect
import typing
from typing import get_origin, get_args, Annotated

type_map: list[tuple[type, str]] = [
    (str, "string"),
    (int, "integer"),
    (float, "number"),
    (bool, "boolean"),
]


def unwrap_optional(py_type: type) -> type:
    if get_origin(py_type) is typing.types.UnionType:
        args = get_args(py_type)

        non_none_types = [t for t in args if t is not type(None)]

        if len(non_none_types) != 1:
            raise ValueError(
                f"Union must have exactly one non-None type, got {non_none_types}"
            )

        if len(args) != 2:
            raise ValueError(f"Union must be Optional (T | None), got {args}")

        return non_none_types[0]
    else:
        return py_type


def py_type_to_json(py_type):
    py_type = unwrap_optional(py_type)

    for t, j in type_map:
        if py_type is t:
            return j
        if get_origin(py_type) is Annotated:
            if get_args(py_type)[0] == t:
                return j

    raise ValueError(
        f"Cannot use {py_type.__name__} in tool definition, "
        "must be one of: " + ", ".join(t.__name__ for t, _ in type_map),
    )


def make_tool_def(func):
    """
    Convert a function signature to a Claude/MCP-style JSON schema definition
    """

    sig = inspect.signature(func)

    tool = {
        "name": func.__name__,
    }

    if func.__doc__:
        tool["description"] = func.__doc__

    input_schema = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    for name, param in sig.parameters.items():
        if param.annotation == inspect.Parameter.empty:
            raise ValueError(f"Parameter {name} must have a type annotation")

        prop = {
            "type": py_type_to_json(param.annotation),
        }

        if get_origin(param.annotation) is Annotated:
            # TODO: validate the shape of Annotated is what we expect
            prop["description"] = param.annotation.__metadata__[0]

        if param.default is param.empty:
            input_schema["required"].append(name)

        input_schema["properties"][name] = prop

    if len(input_schema["required"]) == 0:
        del input_schema["required"]

    tool["input_schema"] = input_schema

    return tool
