import click

from afi.agent import Agent


def main(agent: Agent):
    tool_group = click.Group(name="tool")

    for tool in agent.tools.values():
        tool_group.add_command(tool.command)

    def root_callback(ctx: click.Context):
        if ctx.invoked_subcommand is None:
            agent.run()

    root = click.Group(
        callback=click.pass_context(root_callback),
        invoke_without_command=True,
        no_args_is_help=False,
    )
    root.add_command(tool_group)

    root()
