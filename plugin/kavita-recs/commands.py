"""Slash command registration for kavita-recs."""


def register_commands(ctx):
    """Register placeholder slash commands."""

    def todayread_command(args):
        return "kavita-recs scaffold is installed. `/todayread` is not implemented yet."

    ctx.register_command(
        "todayread",
        todayread_command,
        "Generate today's reading recommendation from Kavita.",
    )
