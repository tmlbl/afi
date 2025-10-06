from typing import Callable

from anthropic import Anthropic
from anthropic.types import MessageParam, ToolResultBlockParam


from afi.json_schema import make_tool_def
from afi.tool import wrap_tool
from afi.ui import log_model_response, log_tool_use


class Agent:
    def __init__(
        self,
        default_prompt: str,
        default_system_prompt: str = "",
        tools: list[Callable] = [],
    ) -> None:
        self.prompt = default_prompt
        self.system_prompt = default_system_prompt
        self.tools = {}
        self.model_name = "claude-sonnet-4-5-20250929"

        for tool in tools:
            if tool.__name__ in self.tools:
                raise ValueError(
                    f"duplicate entries for tool name: {tool.__name__}",
                )

            self.tools[tool.__name__] = wrap_tool(tool)

        print(self.get_tools_json_schema())

    def get_tools_json_schema(self):
        schema = []
        for func in self.tools.values():
            schema.append(make_tool_def(func))
        return schema

    def call_tool(self, name: str, input: dict):
        if name not in self.tools:
            raise ValueError(f"No tool registered with name: {name}")
        output = self.tools[name](**input)
        return str(output)

    def run(self) -> None:
        self.run_agent_claude()

    def run_agent_claude(self):
        client = Anthropic()

        messages = [MessageParam(role="user", content=self.prompt)]

        while True:
            response = client.messages.create(
                model=self.model_name,
                max_tokens=1024,
                tools=self.get_tools_json_schema(),
                messages=messages,
            )

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
                    log_model_response(block.text)
                elif block.type == "tool_use":
                    input = (
                        block.input
                        if type(block.input) is dict
                        else block.input.__dict__
                    )
                    log_tool_use(block.name, input)
                    try:
                        tool_output = self.call_tool(block.name, input)
                        tool_results.append(
                            ToolResultBlockParam(
                                type="tool_result",
                                tool_use_id=block.id,
                                content=tool_output,
                            )
                        )
                        print("tool result:", tool_output)
                    except Exception as e:
                        tool_results.append(
                            ToolResultBlockParam(
                                type="tool_result",
                                tool_use_id=block.id,
                                content=str(e),
                                is_error=True,
                            )
                        )
                        print("tool invoke error:", e)

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
