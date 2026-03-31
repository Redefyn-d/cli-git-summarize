"""
git-summarize: AI-powered Git commit message generator.

Generates clean, conventional commit messages from staged Git diffs
using AI language models (Claude, OpenAI, Ollama, Gemini).
"""

__version__ = "1.1.0"
__author__ = "Git Summarize Contributors"

from git_summarize.config import Config, get_config

__all__ = ["__version__", "Config", "get_config"]
