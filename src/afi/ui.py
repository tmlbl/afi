from typing import Any
from rich.console import Console

console = Console()


class Logger:
    print_tool_outputs: bool

    def __init__(self, print_tool_outputs: bool = False) -> None:
        self.print_tool_outputs = print_tool_outputs
        pass

    def log_model_response(self, content: str):
        console.print(f"[bold blue]AGENT[/bold blue] {content}")

    def log_tool_use(self, name: str, input: dict):
        params = []
        for key, value in input.items():
            if type(value) is str:
                value = f'"{value}"'
            params.append(f"[bold]{key}[/bold]={value}")
        params_str = " ".join(params)
        console.print(f"[bold red]TOOL[/bold red] {name} {params_str}")

    def log_tool_output(self, output: Any):
        if self.print_tool_outputs:
            console.print(f"[bold red]OUTPUT[/bold red] [dim]{output}[/dim]")
        else:
            truncated = output[:256]
            console.print(
                f"[bold red]OUTPUT[/bold red] [dim]{truncated}[/dim] ...{len(output)} characters"
            )

    def log_error(self, message: str, err: Exception):
        console.print(f"[bold red]ERROR[/bold red] {message} [red]{err}")
