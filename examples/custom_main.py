import afi


def run(agent: afi.Agent):
    for lang in ["python", "golang", "zig", "c"]:
        agent.run(prompt=f"Write 'hello world' in {lang}")


afi.main(afi.Agent(), run=run)
