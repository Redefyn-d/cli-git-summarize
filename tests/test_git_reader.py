"""
Tests for the Git Reader module.
"""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from git_summarize.git_reader import GitContext, GitDiff, GitReader, GitReaderError


class TestGitDiff:
    """Tests for GitDiff dataclass."""

    def test_create_git_diff(self):
        """Test creating a GitDiff."""
        diff = GitDiff(
            file_path="src/test.py",
            old_file=None,
            new_file="src/test.py",
            diff_text="+print('hello')",
            is_new_file=True,
        )

        assert diff.file_path == "src/test.py"
        assert diff.is_new_file is True
        assert diff.is_deleted is False

    def test_git_diff_renamed(self):
        """Test GitDiff for renamed file."""
        diff = GitDiff(
            file_path="new_name.py",
            old_file="old_name.py",
            new_file="new_name.py",
            diff_text="",
            is_renamed=True,
        )

        assert diff.is_renamed is True
        assert diff.old_file == "old_name.py"


class TestGitContext:
    """Tests for GitContext dataclass."""

    def test_create_context(self):
        """Test creating a GitContext."""
        context = GitContext(
            repo_root="/test/repo",
            branch_name="main",
            is_dirty=False,
            staged_files=["file1.py"],
            diffs=[],
            files_changed=1,
            insertions=10,
            deletions=5,
        )

        assert context.repo_root == "/test/repo"
        assert context.branch_name == "main"
        assert context.has_changes is True

    def test_context_no_changes(self):
        """Test context with no staged changes."""
        context = GitContext(
            repo_root="/test/repo",
            branch_name="main",
            is_dirty=False,
            staged_files=[],
            diffs=[],
        )

        assert context.has_changes is False

    def test_context_diff_text(self):
        """Test combined diff text property."""
        diffs = [
            GitDiff(
                file_path="file1.py",
                old_file=None,
                new_file="file1.py",
                diff_text="+line1",
            ),
            GitDiff(
                file_path="file2.py",
                old_file=None,
                new_file="file2.py",
                diff_text="+line2",
            ),
        ]

        context = GitContext(
            repo_root="/test",
            branch_name="main",
            is_dirty=False,
            diffs=diffs,
        )

        assert "+line1" in context.diff_text
        assert "+line2" in context.diff_text


class TestGitReader:
    """Tests for GitReader class."""

    @pytest.fixture
    def mock_git_reader(self):
        """Create a GitReader with mocked subprocess."""
        with patch.object(GitReader, "_validate_repo"):
            reader = GitReader.__new__(GitReader)
            reader.repo_path = Path("/test/repo")
            reader._run_git = MagicMock(return_value="")
            return reader

    def test_init_validates_repo(self):
        """Test that __init__ validates repository."""
        with patch.object(GitReader, "_validate_repo") as mock_validate:
            GitReader("/test/repo")
            mock_validate.assert_called_once()

    def test_init_defaults_to_current_dir(self):
        """Test that repo_path defaults to current directory."""
        with patch.object(GitReader, "_validate_repo"):
            reader = GitReader()
            assert reader.repo_path == Path.cwd()

    def test_validate_repo_success(self, mock_git_reader):
        """Test repo validation success."""
        mock_git_reader._run_git = MagicMock(return_value=".git")

        # Should not raise
        mock_git_reader._validate_repo()

    def test_validate_repo_failure(self, mock_git_reader):
        """Test repo validation failure."""
        mock_git_reader._run_git = MagicMock(side_effect=GitReaderError("Not a repo"))

        with pytest.raises(GitReaderError):
            mock_git_reader._validate_repo()

    def test_run_git_success(self, mock_git_reader):
        """Test running git command successfully."""
        mock_git_reader._run_git = MagicMock(return_value="main")

        result = mock_git_reader._run_git("rev-parse", "--abbrev-ref", "HEAD")
        assert result == "main"

    def test_run_git_failure(self, mock_git_reader):
        """Test running git command with failure."""
        mock_git_reader._run_git = MagicMock(
            side_effect=GitReaderError("Command failed")
        )

        with pytest.raises(GitReaderError):
            mock_git_reader._run_git("invalid-command")

    def test_get_repo_root(self, mock_git_reader):
        """Test getting repository root."""
        mock_git_reader._run_git = MagicMock(return_value="/absolute/path/to/repo")

        result = mock_git_reader.get_repo_root()
        assert result == "/absolute/path/to/repo"

    def test_get_branch_name(self, mock_git_reader):
        """Test getting branch name."""
        mock_git_reader._run_git = MagicMock(return_value="feature/test")

        result = mock_git_reader.get_branch_name()
        assert result == "feature/test"

    def test_get_branch_name_detached_head(self, mock_git_reader):
        """Test getting branch name when detached."""
        mock_git_reader._run_git = MagicMock(side_effect=GitReaderError("detached"))

        result = mock_git_reader.get_branch_name()
        assert result == "HEAD (detached)"

    def test_get_staged_files_empty(self, mock_git_reader):
        """Test getting staged files when none exist."""
        mock_git_reader._run_git = MagicMock(return_value="")

        result = mock_git_reader.get_staged_files()
        assert result == []

    def test_get_staged_files_multiple(self, mock_git_reader):
        """Test getting multiple staged files."""
        mock_git_reader._run_git = MagicMock(return_value="file1.py\nfile2.py\nfile3.py")

        result = mock_git_reader.get_staged_files()
        assert len(result) == 3
        assert "file1.py" in result

    def test_get_diff_stats(self, mock_git_reader):
        """Test getting diff statistics."""
        mock_git_reader._run_git = MagicMock(
            return_value=" 3 files changed, 15 insertions(+), 5 deletions(-)"
        )

        files, insertions, deletions = mock_git_reader.get_diff_stats()
        assert files == 3
        assert insertions == 15
        assert deletions == 5

    def test_get_diff_stats_empty(self, mock_git_reader):
        """Test getting diff stats with no changes."""
        mock_git_reader._run_git = MagicMock(return_value="")

        files, insertions, deletions = mock_git_reader.get_diff_stats()
        assert files == 0
        assert insertions == 0
        assert deletions == 0

    def test_get_recent_commits(self, mock_git_reader):
        """Test getting recent commits."""
        mock_git_reader._run_git = MagicMock(
            return_value="feat: add feature\nfix: fix bug\nchore: update deps"
        )

        result = mock_git_reader.get_recent_commits(limit=3)
        assert len(result) == 3
        assert "feat: add feature" in result

    def test_get_recent_commits_empty(self, mock_git_reader):
        """Test getting recent commits when none exist."""
        mock_git_reader._run_git = MagicMock(return_value="")

        result = mock_git_reader.get_recent_commits()
        assert result == []

    def test_is_repo_dirty_true(self, mock_git_reader):
        """Test detecting dirty repository."""
        mock_git_reader._run_git = MagicMock(return_value=" M file.py")

        result = mock_git_reader.is_repo_dirty()
        assert result is True

    def test_is_repo_dirty_false(self, mock_git_reader):
        """Test detecting clean repository."""
        mock_git_reader._run_git = MagicMock(return_value="")

        result = mock_git_reader.is_repo_dirty()
        assert result is False

    def test_parse_diffs_empty(self, mock_git_reader):
        """Test parsing diffs when none exist."""
        mock_git_reader._run_git = MagicMock(return_value="")
        mock_git_reader.get_file_diff = MagicMock(return_value="")

        result = mock_git_reader.parse_diffs()
        assert result == []

    def test_parse_diffs_new_file(self, mock_git_reader):
        """Test parsing diff for new file."""
        mock_git_reader._run_git = MagicMock(return_value="A\tnew_file.py")
        mock_git_reader.get_file_diff = MagicMock(return_value="+content")

        result = mock_git_reader.parse_diffs()
        assert len(result) == 1
        assert result[0].file_path == "new_file.py"
        assert result[0].is_new_file is True

    def test_parse_diffs_modified_file(self, mock_git_reader):
        """Test parsing diff for modified file."""
        mock_git_reader._run_git = MagicMock(return_value="M\tmodified.py")
        mock_git_reader.get_file_diff = MagicMock(return_value="-old\n+new")

        result = mock_git_reader.parse_diffs()
        assert len(result) == 1
        assert result[0].is_new_file is False
        assert result[0].is_deleted is False

    def test_parse_diffs_deleted_file(self, mock_git_reader):
        """Test parsing diff for deleted file."""
        mock_git_reader._run_git = MagicMock(return_value="D\tdeleted.py")
        mock_git_reader.get_file_diff = MagicMock(return_value="-content")

        result = mock_git_reader.parse_diffs()
        assert len(result) == 1
        assert result[0].is_deleted is True

    def test_get_context(self, mock_git_reader):
        """Test getting complete Git context."""
        mock_git_reader._run_git = MagicMock(side_effect=[
            "/test/repo",  # get_repo_root
            "feature/test",  # get_branch_name
            "",  # is_repo_dirty
            "file1.py\nfile2.py",  # get_staged_files
            "A\tfile1.py\nM\tfile2.py",  # parse_diffs (name-status)
            " 2 files changed, 10 insertions(+), 2 deletions(-)",  # get_diff_stats
            "feat: previous commit",  # get_recent_commits
        ])
        mock_git_reader.get_file_diff = MagicMock(return_value="+content")

        context = mock_git_reader.get_context()

        assert isinstance(context, GitContext)
        assert context.branch_name == "feature/test"
        assert context.files_changed == 2


class TestGitReaderError:
    """Tests for GitReaderError exception."""

    def test_error_message(self):
        """Test error message."""
        error = GitReaderError("Something went wrong")
        assert str(error) == "Something went wrong"

    def test_error_with_path(self):
        """Test error with repository path."""
        error = GitReaderError("Not a repository: /invalid/path")
        assert "/invalid/path" in str(error)
