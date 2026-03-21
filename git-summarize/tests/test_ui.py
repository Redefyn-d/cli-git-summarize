"""
Tests for the UI module.
"""

from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console

from git_summarize.parser import CommitSuggestion
from git_summarize.ui import UI, UserAction


class TestUserAction:
    """Tests for UserAction enum."""

    def test_user_action_values(self):
        """Test UserAction enum values."""
        assert UserAction.SELECT.value == "select"
        assert UserAction.EDIT.value == "edit"
        assert UserAction.REJECT.value == "reject"
        assert UserAction.REGENERATE.value == "regenerate"
        assert UserAction.QUIT.value == "quit"


class TestUI:
    """Tests for UI class."""

    @pytest.fixture
    def console(self):
        """Create a test console."""
        return Console(file=StringIO(), width=100)

    @pytest.fixture
    def ui(self, console):
        """Create a UI instance."""
        return UI(console=console)

    def test_init_default_console(self):
        """Test UI with default console."""
        ui = UI()
        assert ui.console is not None

    def test_init_custom_console(self, console):
        """Test UI with custom console."""
        ui = UI(console=console)
        assert ui.console is console

    def test_show_error(self, ui, console):
        """Test showing error message."""
        ui.show_error("Test error", "Test Error")

        output = console.file.getvalue()
        assert "Test error" in output

    def test_show_warning(self, ui, console):
        """Test showing warning message."""
        ui.show_warning("Test warning", "Test Warning")

        output = console.file.getvalue()
        assert "Test warning" in output

    def test_show_success(self, ui, console):
        """Test showing success message."""
        ui.show_success("Test success", "Test Success")

        output = console.file.getvalue()
        assert "Test success" in output

    def test_show_info(self, ui, console):
        """Test showing info message."""
        ui.show_info("Test info", "Test Info")

        output = console.file.getvalue()
        assert "Test info" in output

    def test_show_context(self, ui, console):
        """Test showing Git context."""
        ui.show_context(
            branch="feature/test",
            files_changed=3,
            insertions=15,
            deletions=5,
        )

        output = console.file.getvalue()
        assert "feature/test" in output
        assert "3 file(s)" in output

    def test_show_suggestions(self, ui, console):
        """Test showing commit suggestions."""
        suggestions = [
            CommitSuggestion(
                subject="feat(auth): add login",
                commit_type="feat",
                scope="auth",
            ),
            CommitSuggestion(
                subject="fix(auth): fix logout bug",
                commit_type="fix",
                scope="auth",
            ),
        ]

        ui.show_suggestions(
            suggestions=suggestions,
            provider="claude",
            model="claude-3-sonnet-20240229",
        )

        output = console.file.getvalue()
        assert "feat(auth)" in output
        assert "fix(auth)" in output
        assert "claude" in output

    def test_show_suggestion_with_body(self, ui, console):
        """Test showing suggestion with body."""
        suggestion = CommitSuggestion(
            subject="feat: add feature",
            body="This is the body of the commit message.",
            commit_type="feat",
        )

        ui._display_suggestion(suggestion, 1)

        output = console.file.getvalue()
        assert "add feature" in output
        assert "body of the commit" in output

    def test_show_invalid_suggestion(self, ui, console):
        """Test showing invalid suggestion."""
        suggestion = CommitSuggestion(
            subject="Invalid message",
            is_valid=False,
            validation_errors=["Does not follow format"],
        )

        ui._display_suggestion(suggestion, 1)

        output = console.file.getvalue()
        assert "Invalid message" in output
        assert "Does not follow format" in output

    def test_show_no_changes(self, ui, console):
        """Test showing no changes message."""
        ui.show_no_changes()

        output = console.file.getvalue()
        assert "No staged changes" in output or "git add" in output

    def test_show_provider_error(self, ui, console):
        """Test showing provider error."""
        ui.show_provider_error("claude", "API key invalid")

        output = console.file.getvalue()
        assert "claude" in output
        assert "API key" in output

    def test_show_commit_success(self, ui, console):
        """Test showing commit success."""
        ui.show_commit_success("feat: add new feature with long description")

        output = console.file.getvalue()
        assert "Committed" in output

    def test_show_preview(self, ui, console):
        """Test showing commit preview."""
        ui.prompt_preview("feat: test commit")

        output = console.file.getvalue()
        assert "Preview" in output
        assert "test commit" in output


class TestUIPromptSelection:
    """Tests for UI prompt selection methods."""

    @pytest.fixture
    def console(self):
        """Create a test console."""
        return Console(file=StringIO(), width=100)

    @pytest.fixture
    def ui(self, console):
        """Create a UI instance."""
        return UI(console=console)

    def test_prompt_selection_select(self, ui):
        """Test selecting a suggestion."""
        with patch("git_summarize.ui.Prompt.ask", return_value="1"):
            action, index = ui.prompt_selection(num_suggestions=3)

            assert action == UserAction.SELECT
            assert index == 0

    def test_prompt_selection_second_option(self, ui):
        """Test selecting second suggestion."""
        with patch("git_summarize.ui.Prompt.ask", return_value="2"):
            action, index = ui.prompt_selection(num_suggestions=3)

            assert action == UserAction.SELECT
            assert index == 1

    def test_prompt_selection_edit(self, ui):
        """Test choosing edit action."""
        with patch("git_summarize.ui.Prompt.ask", return_value="e"):
            action, index = ui.prompt_selection(num_suggestions=3)

            assert action == UserAction.EDIT
            assert index == 0

    def test_prompt_selection_quit(self, ui):
        """Test choosing quit action."""
        with patch("git_summarize.ui.Prompt.ask", return_value="q"):
            action, index = ui.prompt_selection(num_suggestions=3)

            assert action == UserAction.QUIT
            assert index == 0

    def test_prompt_selection_regenerate(self, ui):
        """Test choosing regenerate action."""
        with patch("git_summarize.ui.Prompt.ask", return_value="r"):
            action, index = ui.prompt_selection(
                num_suggestions=3,
                allow_regenerate=True,
            )

            assert action == UserAction.REGENERATE
            assert index == 0

    def test_prompt_selection_default(self, ui):
        """Test default selection (first option)."""
        with patch("git_summarize.ui.Prompt.ask", return_value=""):
            action, index = ui.prompt_selection(num_suggestions=3)

            assert action == UserAction.SELECT
            assert index == 0


class TestUIPromptEdit:
    """Tests for UI prompt edit methods."""

    @pytest.fixture
    def console(self):
        """Create a test console."""
        return Console(file=StringIO(), width=100)

    @pytest.fixture
    def ui(self, console):
        """Create a UI instance."""
        return UI(console=console)

    def test_prompt_edit_single_line(self, ui):
        """Test editing with single line."""
        with patch("git_summarize.ui.Prompt.ask", side_effect=["feat: edited", ""]):
            result = ui.prompt_edit("feat: original")

            assert result == "feat: edited"

    def test_prompt_edit_multiple_lines(self, ui):
        """Test editing with multiple lines."""
        with patch(
            "git_summarize.ui.Prompt.ask",
            side_effect=["feat: edited", "Body line", ""],
        ):
            result = ui.prompt_edit("feat: original")

            assert "feat: edited" in result
            assert "Body line" in result

    def test_prompt_edit_cancel_empty(self, ui):
        """Test cancelling edit with empty input."""
        with patch("git_summarize.ui.Prompt.ask", return_value=""):
            result = ui.prompt_edit("feat: original")

            assert result is None

    def test_prompt_edit_keyboard_interrupt(self, ui):
        """Test cancelling edit with keyboard interrupt."""
        with patch(
            "git_summarize.ui.Prompt.ask",
            side_effect=KeyboardInterrupt(),
        ):
            result = ui.prompt_edit("feat: original")

            assert result is None


class TestUIPromptConfirm:
    """Tests for UI prompt confirm methods."""

    @pytest.fixture
    def console(self):
        """Create a test console."""
        return Console(file=StringIO(), width=100)

    @pytest.fixture
    def ui(self, console):
        """Create a UI instance."""
        return UI(console=console)

    def test_prompt_confirm_yes(self, ui):
        """Test confirming with yes."""
        with patch("git_summarize.ui.Confirm.ask", return_value=True):
            result = ui.prompt_confirm_commit("feat: test")

            assert result is True

    def test_prompt_confirm_no(self, ui):
        """Test confirming with no."""
        with patch("git_summarize.ui.Confirm.ask", return_value=False):
            result = ui.prompt_confirm_commit("feat: test")

            assert result is False
