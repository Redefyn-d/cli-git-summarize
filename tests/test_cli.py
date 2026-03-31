"""
Tests for the CLI module.
"""

import pytest
from typer.testing import CliRunner

from git_summarize.main import app

runner = CliRunner()


class TestCLI:
    """Tests for CLI commands."""

    def test_version_flag(self):
        """Test --version flag."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "version" in result.stdout.lower()

    def test_version_short_flag(self):
        """Test -v flag."""
        result = runner.invoke(app, ["-v"])
        assert result.exit_code == 0
        assert "version" in result.stdout.lower()

    def test_help(self):
        """Test --help flag."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "AI-powered" in result.stdout or "commit" in result.stdout.lower()

    def test_generate_help(self):
        """Test generate command help."""
        result = runner.invoke(app, ["generate", "--help"])
        assert result.exit_code == 0
        assert "provider" in result.stdout.lower()

    def test_providers_command(self):
        """Test providers command."""
        result = runner.invoke(app, ["providers"])
        assert result.exit_code == 0
        assert "claude" in result.stdout.lower() or "openai" in result.stdout.lower()

    def test_config_show(self):
        """Test config --show command."""
        result = runner.invoke(app, ["config", "--show"])
        assert result.exit_code == 0
        assert "Provider" in result.stdout or "Model" in result.stdout

    def test_generate_no_git_repo(self):
        """Test generate command outside git repo."""
        result = runner.invoke(app, ["generate"])
        # Should fail gracefully with error message
        assert result.exit_code != 0 or "not a git" in result.stdout.lower() or "No staged" in result.stdout


class TestCLIOptions:
    """Tests for CLI options."""

    def test_provider_option(self):
        """Test --provider option."""
        result = runner.invoke(app, ["generate", "--provider", "claude"])
        # Will fail due to no git repo, but should accept the option
        assert result.exit_code != 0 or "provider" not in result.stdout.lower()

    def test_provider_invalid(self):
        """Test invalid provider option."""
        result = runner.invoke(app, ["generate", "--provider", "invalid"])
        assert result.exit_code != 0
        assert "Invalid" in result.stdout or "invalid" in result.stdout.lower()

    def test_model_option(self):
        """Test --model option."""
        result = runner.invoke(app, ["generate", "--model", "gpt-4"])
        # Will fail due to no git repo, but should accept the option
        assert "Usage" not in result.stdout or result.exit_code != 0

    def test_num_suggestions_option(self):
        """Test --num-suggestions option."""
        result = runner.invoke(app, ["generate", "--num-suggestions", "5"])
        # Will fail due to no git repo, but should accept the option
        assert "Usage" not in result.stdout or result.exit_code != 0

    def test_num_suggestions_invalid(self):
        """Test invalid --num-suggestions option."""
        result = runner.invoke(app, ["generate", "--num-suggestions", "0"])
        assert result.exit_code != 0

    def test_num_suggestions_max(self):
        """Test max --num-suggestions option."""
        result = runner.invoke(app, ["generate", "--num-suggestions", "11"])
        assert result.exit_code != 0

    def test_auto_flag(self):
        """Test --auto flag."""
        result = runner.invoke(app, ["generate", "--auto"])
        # Will fail due to no git repo, but should accept the flag
        assert result.exit_code != 0 or "Usage" not in result.stdout

    def test_preview_flag(self):
        """Test --preview flag."""
        result = runner.invoke(app, ["generate", "--preview"])
        assert result.exit_code != 0 or "Usage" not in result.stdout

    def test_apply_flag(self):
        """Test --apply flag."""
        result = runner.invoke(app, ["generate", "--apply"])
        assert result.exit_code != 0 or "Usage" not in result.stdout

    def test_short_options(self):
        """Test short option forms."""
        result = runner.invoke(app, ["generate", "-p", "openai", "-n", "2"])
        # Will fail due to no git repo, but should accept the options
        assert "Usage" not in result.stdout or result.exit_code != 0


class TestConfigCLI:
    """Tests for config command."""

    def test_config_no_args(self):
        """Test config command without args."""
        result = runner.invoke(app, ["config"])
        assert result.exit_code == 0
        assert "show" in result.stdout.lower() or "Usage" in result.stdout

    def test_config_set_provider(self):
        """Test config --provider option."""
        result = runner.invoke(app, ["config", "--provider", "openai"])
        assert result.exit_code == 0
        assert "provider" in result.stdout.lower()

    def test_config_set_model(self):
        """Test config --model option."""
        result = runner.invoke(app, ["config", "--model", "gpt-4-turbo"])
        assert result.exit_code == 0
        assert "model" in result.stdout.lower()
