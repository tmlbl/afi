import os
import sys


class Config:
    agent_name: str
    model_name: str
    log_json: bool

    def __init__(
        self,
        model_name: str,
        agent_name: str | None = None,
    ) -> None:
        if agent_name is None:
            agent_name = os.getenv("AGENT_NAME")

        if agent_name is None:
            for arg in sys.argv:
                if not arg.startswith("python"):
                    agent_name = arg

        if agent_name is None:
            # give up
            agent_name = "no_name"

        self.agent_name = agent_name
        self.model_name = model_name

        self.log_json = not sys.stdout.isatty()

        log_json = os.getenv("AGENT_LOG_JSON")
        if log_json is not None and log_json not in ["", "0", "false"]:
            self.log_json = True

    def log_dict(self) -> dict:
        return {
            "agent": self.agent_name,
            "model": self.model_name,
        }
