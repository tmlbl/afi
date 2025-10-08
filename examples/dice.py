import random

import afi


def roll():
    """Roll the dice! If you dare..."""

    a = random.randrange(1, 6)
    b = random.randrange(1, 6)
    return f"{a}, {b}"


agent = afi.Agent(
    prompt="Roll until you get doubles",
    tools=[roll],
)

afi.main(agent)
