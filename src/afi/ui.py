import json
from typing import Any
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt

from afi.config import Config

console = Console()


class Logger:
    config: Config
    print_tool_outputs: bool

    def __init__(self, config: Config, print_tool_outputs: bool = False) -> None:
        self.config = config
        self.print_tool_outputs = print_tool_outputs
        pass

    def log_json(self, **kwargs):
        msg = self.config.log_dict()
        for k, v in kwargs.items():
            msg[k] = v
        print(json.dumps(msg))

    def log_model_response(self, content: str):
        if self.config.log_json:
            return self.log_json(
                type="model_response",
                content=content,
            )
        else:
            md = Markdown(content)
            console.print("[bold blue]AGENT[/bold blue]")
            console.print(md)

    def log_tool_use(self, name: str, input: dict):
        if self.config.log_json:
            return self.log_json(
                type="tool_use",
                tool_name=name,
                tool_input=input,
            )
        else:
            params = []
            for key, value in input.items():
                if type(value) is str:
                    value = f'"{value}"'
                params.append(f"[bold]{key}[/bold]={value}")
            params_str = " ".join(params)
            console.print(f"[bold yellow]CALL TOOL[/bold yellow] {name} {params_str}")

    def log_tool_output(self, output: Any, full: bool = False):
        if self.config.log_json:
            return self.log_json(
                type="tool_result",
                output=output[:256],
                output_size=len(output),
            )
        if full:
            console.print(f"[bold green]SUCCESS[/bold green]\n[dim]{output}[/dim]")
        else:
            truncated = output[:256]
            console.print(
                f"[bold green]SUCCESS[/bold green]\n[dim]{truncated}[/dim] ...{
                    len(output)
                } characters"
            )

    def log_error(self, message: str, err: Exception):
        if self.config.log_json:
            return self.log_json(
                type="error",
                message=message,
                error=str(err),
            )

        console.print(f"[bold red]ERROR[/bold red] {message} [red]{err}")


def prompt_user():
    return Prompt.ask("[bold green]➜[/bold green] ")
