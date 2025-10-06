from afi.claude import run_agent_claude
from afi.tool import tool


def main(prompt: str):
    run_agent_claude(prompt=prompt)


__all__ = ["tool", "main"]
