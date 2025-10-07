import json
import inspect
from typing import Annotated, Any, Callable, get_origin, get_type_hints
from functools import wraps

import click

from afi.ui import Logger


class ToolParam:
    name: str
    type: Any
    description: str | None
    required: bool

    def __init__(self, name: str, param: inspect.Parameter) -> None:
        self.name = name

        if param.annotation == inspect.Parameter.empty:
            raise ValueError(
                f"parameter {name} has no type annotation",
            )
        self.type = param.annotation

        self.description = None
        if get_origin(param) is Annotated:
            self.description = param.annotation.__metadata__[1]

        self.required = param.default is param.empty

    def option(self) -> click.Option:
        return click.Option([f"--{self.name}"], type=self.type, required=self.required)


class Tool:
    name: str
    description: str | None
    command: click.Command
    params: list[ToolParam]

    def __init__(self, func: Callable) -> None:
        self.func = wrap_tool(func)
        self.name = func.__name__
        self.description = func.__doc__

        self.params = []
        sig = inspect.signature(func)
        for name, param in sig.parameters.items():
            tool_param = ToolParam(name, param)
            self.params.append(tool_param)

        self.command = click.Command(
            name=self.name,
            help=self.description,
            callback=self.call_cmd,
            params=[p.option() for p in self.params],
        )

    def call(self, **kwargs) -> str:
        result = self.func(**kwargs)
        if type(result) is dict:
            return json.dumps(result)
        else:
            return str(result)

    def call_cmd(self, **kwargs):
        log = Logger(print_tool_outputs=True)
        try:
            log.log_tool_use(self.name, kwargs)
            output = self.call(**kwargs)
            log.log_tool_output(output)
        except Exception as e:
            print(f"error: {str(e)}")


def wrap_tool(func):
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

    return wrapper
