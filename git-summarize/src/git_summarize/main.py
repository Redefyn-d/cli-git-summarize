"""
git-summarize: AI-powered Git commit message generator.

Main entry point for the gcm command.
"""

from git_summarize.cli import app, cli

# Export app for Typer entry point
__all__ = ["app", "cli"]

# Main entry point
if __name__ == "__main__":
    cli()
