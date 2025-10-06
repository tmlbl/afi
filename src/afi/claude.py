from anthropic import Anthropic
from anthropic.types import MessageParam, ToolResultBlockParam

from afi.ui import log_model_response, log_tool_use
from afi.tool import get_claude_tool_defs, call_tool

MODEL_NAME = "claude-sonnet-4-5-20250929"


def run_agent_claude(
    prompt: str,
):
    client = Anthropic()

    messages = [MessageParam(role="user", content=prompt)]

    while True:
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=1024,
            tools=get_claude_tool_defs(),
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
                    block.input if type(block.input) is dict else block.input.__dict__
                )
                log_tool_use(block.name, input)
                try:
                    tool_output = call_tool(block.name, input)
                    tool_results.append(
                        ToolResultBlockParam(
                            type="tool_result",
                            tool_use_id=block.id,
                            content=tool_output,
                        )
                    )
                except Exception as e:
                    tool_results.append(
                        ToolResultBlockParam(
                            type="tool_result",
                            tool_use_id=block.id,
                            content=str(e),
                            is_error=True,
                        )
                    )

        # check if done for prompt
        if response.stop_reason == "end_turn":
            break

        # add tool results to conversation
        messages.append(
            MessageParam(
                role="user",
                content=tool_results,
            )
        )
