from typing import Callable
import click

from afi.agent import Agent


def main(agent: Agent, run: Callable[[Agent], None] | None = None):
    tool_group = click.Group(name="tool")

    for tool in agent.tools.values():
        tool_group.add_command(tool.command)

    def root_callback(ctx: click.Context, interactive: bool, system: str):
        agent.system_prompt = system
        if ctx.invoked_subcommand is None:
            if run is not None and not interactive:
                run(agent)
            else:
                agent.run(interactive=interactive)

    root = click.Group(
        callback=click.pass_context(root_callback),
        invoke_without_command=True,
        no_args_is_help=False,
        params=[
            click.Option(
                ["--interactive", "-i"],
                is_flag=True,
                default=False,
                help="Chat with your agent",
            ),
            click.Option(
                ["--system", "-s"],
                default=agent.system_prompt,
                help="Override the system prompt",
            ),
        ],
    )
    root.add_command(tool_group)

    root()
