from typing import get_origin, get_args
from types import UnionType


def unwrap_optional(py_type: type) -> type:
    if get_origin(py_type) is UnionType:
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
