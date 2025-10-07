import inspect
import typing
from typing import get_origin, get_args, Annotated

from afi.tool import Tool

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


def make_tool_def(tool: Tool) -> dict:
    tool_def: dict = {
        "name": tool.name,
    }

    if tool.description:
        tool_def["description"] = tool.description

    input_schema = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    for param in tool.params:
        prop = {
            "type": py_type_to_json(param.type),
        }

        if param.description:
            prop["description"] = param.description

        if param.required:
            input_schema["required"].append(param.name)

        input_schema["properties"][param.name] = prop

    if len(input_schema["required"]) == 0:
        del input_schema["required"]

    tool_def["input_schema"] = input_schema

    return tool_def
