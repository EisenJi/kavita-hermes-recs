"""Hermes plugin entrypoint for kavita-recs."""


def register(ctx):
    """Register tools and commands with Hermes.

    The implementation is intentionally minimal during scaffold stage.
    """
    from .commands import register_commands
    from .tools import register_tools

    register_tools(ctx)
    register_commands(ctx)
