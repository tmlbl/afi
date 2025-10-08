from typing import Callable

from anthropic import Anthropic
from anthropic.types import MessageParam, ToolResultBlockParam


from afi.json_schema import make_tool_def
from afi.tool import Tool
from afi.config import Config
from afi.ui import Logger, prompt_user


class Agent:
    prompt: str
    system_prompt: str
    config: Config
    tools: dict[str, Tool]

    def __init__(
        self,
        prompt: str = "",
        system_prompt: str = "",
        tools: list[Callable] = [],
    ) -> None:
        self.prompt = prompt
        self.system_prompt = system_prompt
        self.tools = {}

        self.config = Config(
            model_name="claude-sonnet-4-5",
        )

        for tool in tools:
            if tool.__name__ in self.tools:
                raise ValueError(
                    f"duplicate entries for tool name: {tool.__name__}",
                )

            self.tools[tool.__name__] = Tool(tool)

        self.log = Logger(self.config)

    def get_tools_json_schema(self):
        schema = []
        for tool in self.tools.values():
            schema.append(make_tool_def(tool))
        return schema

    def call_tool(self, name: str, input: dict):
        if name not in self.tools:
            raise ValueError(f"No tool registered with name: {name}")
        output = self.tools[name].func(**input)
        return str(output)

    def run(self, prompt: str | None = None, interactive: bool = False) -> None:
        if prompt is not None:
            self.prompt = prompt
        self.run_agent_claude(interactive=interactive)

    def run_agent_claude(
        self, interactive: bool = False, messages: list[MessageParam] = []
    ):
        client = Anthropic()

        if not interactive:
            messages.append(MessageParam(role="user", content=self.prompt))
        else:
            content = prompt_user()
            messages.append(MessageParam(role="user", content=content))

        while True:
            response = client.messages.create(
                model=self.config.model_name,
                max_tokens=1024,
                tools=self.get_tools_json_schema(),
                messages=messages,
                system=self.system_prompt,
            )
            # TODO: handle errors like anthropic._exceptions.OverloadedError: Error code: 529

            # add assistant response to conversation
            messages.append(
                MessageParam(
                    role="assistant",
                    content=response.content,
                )
            )

            tool_results = []

            for block in response.content:
                if block.type == "text":
                    self.log.log_model_response(block.text)
                elif block.type == "tool_use":
                    input = (
                        block.input
                        if type(block.input) is dict
                        else block.input.__dict__
                    )
                    self.log.log_tool_use(block.name, input)
                    try:
                        tool_output = self.call_tool(block.name, input)
                        tool_results.append(
                            ToolResultBlockParam(
                                type="tool_result",
                                tool_use_id=block.id,
                                content=tool_output,
                            )
                        )
                        self.log.log_tool_output(tool_output)
                    except Exception as e:
                        tool_results.append(
                            ToolResultBlockParam(
                                type="tool_result",
                                tool_use_id=block.id,
                                content=str(e),
                                is_error=True,
                            )
                        )
                        self.log.log_error(f"invoking {block.name}", e)

            # check if done for prompt
            if response.stop_reason == "end_turn":
                break

            # add tool results to conversation
            if len(tool_results) > 0:
                messages.append(
                    MessageParam(
                        role="user",
                        content=tool_results,
                    )
                )

        if interactive:
            self.run_agent_claude(interactive=True, messages=messages)
