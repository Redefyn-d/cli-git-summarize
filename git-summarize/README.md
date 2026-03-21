# git-summarize (gcm)

AI-powered Git commit message generator that suggests clean, conventional commit messages based on your staged changes.

## Features

- 🤖 **Multiple AI Backends**: Support for Claude, OpenAI, and Ollama (local)
- 📝 **Conventional Commits**: Generates messages following the [Conventional Commits](https://www.conventionalcommits.org/) specification
- 🎨 **Rich UI**: Beautiful terminal interface with spinners, colors, and interactive selection
- ⚡ **Fast & Modular**: Clean architecture with swappable components
- 🔧 **Configurable**: Environment variables or config file for API keys and preferences

## Installation

```bash
pip install git-summarize
```

Or install from source:

```bash
git clone https://github.com/git-summarize/git-summarize.git
cd git-summarize
pip install -e .
```

## Quick Start

1. **Set up your AI provider** (choose one):

```bash
# For Claude
export ANTHROPIC_API_KEY="your-key-here"

# For OpenAI
export OPENAI_API_KEY="your-key-here"

# For Ollama (local, no key needed)
ollama pull llama2  # or any other model
```

2. **Stage your changes**:

```bash
git add .
```

3. **Generate commit message**:

```bash
gcm
```

## Usage

```bash
# Basic usage (interactive selection)
gcm

# Specify AI provider
gcm --provider claude
gcm --provider openai
gcm --provider ollama

# Specify model
gcm --model claude-3-sonnet-20240229
gcm --model gpt-4-turbo-preview
gcm --model llama2

# Non-interactive (auto-select first suggestion)
gcm --auto

# Show more suggestions
gcm --num-suggestions 5

# Preview without committing
gcm --preview

# Apply commit directly with first suggestion
gcm --apply

# Show version
gcm --version

# Show help
gcm --help
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude | - |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `OLLAMA_HOST` | Ollama server host | `http://localhost:11434` |
| `GCM_PROVIDER` | Default AI provider | `claude` |
| `GCM_MODEL` | Default model name | Provider-specific |
| `GCM_NUM_SUGGESTIONS` | Number of suggestions | `3` |

### Config File

Create `~/.git-summarize/config.toml`:

```toml
[default]
provider = "claude"
model = "claude-3-sonnet-20240229"
num_suggestions = 3

[providers.ollama]
host = "http://localhost:11434"
```

## Conventional Commits Format

Generated messages follow the format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types include: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `ci`, `build`, `revert`

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CLI Layer (Typer)                       │
│                    Entry point, flags                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Git Reader Module                         │
│              Reads staged diffs, branch info                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Prompt Builder Module                      │
│           Formats diff + metadata into LLM prompt            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    AI Provider Layer                         │
│         Swappable: Claude │ OpenAI │ Ollama                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┘
│                   Response Parser Module                     │
│           Extracts 1-3 commit suggestions                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Interactive UI (Rich)                      │
│          Numbered picker, spinner, edit/reject flow          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      git commit                              │
└─────────────────────────────────────────────────────────────┘
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check src/git_summarize

# Run type checker
mypy src/git_summarize
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit a PR.
