"""
Tests for the Prompt Builder module.
"""

import pytest

from git_summarize.git_reader import GitContext, GitDiff
from git_summarize.prompt_builder import PromptBuilder, PromptComponents


class TestPromptBuilder:
    """Tests for PromptBuilder class."""

    @pytest.fixture
    def sample_context(self):
        """Create a sample GitContext for testing."""
        return GitContext(
            repo_root="/test/repo",
            branch_name="feature/test-branch",
            is_dirty=False,
            staged_files=["src/main.py", "tests/test_main.py"],
            diffs=[
                GitDiff(
                    file_path="src/main.py",
                    old_file=None,
                    new_file="src/main.py",
                    diff_text="""diff --git a/src/main.py b/src/main.py
index abc123..def456 100644
--- a/src/main.py
+++ b/src/main.py
@@ -1,5 +1,8 @@
 def main():
-    print("Hello")
+    print("Hello, World!")
+    return 0
+
+
+if __name__ == "__main__":
+    exit(main())""",
                    is_new_file=False,
                    is_deleted=False,
                    is_renamed=False,
                )
            ],
            diff_summary="1 modified file(s)",
            recent_commits=[
                "feat: add initial project structure",
                "chore: set up CI/CD",
            ],
            files_changed=1,
            insertions=5,
            deletions=1,
        )

    @pytest.fixture
    def builder(self):
        """Create a PromptBuilder instance."""
        return PromptBuilder(num_suggestions=3)

    def test_build_returns_prompt_components(self, builder, sample_context):
        """Test that build returns PromptComponents."""
        result = builder.build(sample_context)

        assert isinstance(result, PromptComponents)
        assert result.system_prompt is not None
        assert result.user_prompt is not None

    def test_system_prompt_contains_conventional_commits(self, builder, sample_context):
        """Test that system prompt mentions Conventional Commits."""
        result = builder.build(sample_context)

        assert "Conventional Commits" in result.system_prompt
        assert "feat" in result.system_prompt
        assert "fix" in result.system_prompt

    def test_system_prompt_includes_num_suggestions(self, builder, sample_context):
        """Test that system prompt includes the number of suggestions."""
        builder = PromptBuilder(num_suggestions=5)
        result = builder.build(sample_context)

        assert "5" in result.system_prompt

    def test_user_prompt_contains_branch_info(self, builder, sample_context):
        """Test that user prompt includes branch name."""
        result = builder.build(sample_context)

        assert "feature/test-branch" in result.user_prompt

    def test_user_prompt_contains_diff_stats(self, builder, sample_context):
        """Test that user prompt includes diff statistics."""
        result = builder.build(sample_context)

        assert "Files changed: 1" in result.user_prompt
        assert "Insertions: 5" in result.user_prompt
        assert "Deletions: 1" in result.user_prompt

    def test_user_prompt_contains_diff_text(self, builder, sample_context):
        """Test that user prompt includes diff content."""
        result = builder.build(sample_context)

        assert "def main():" in result.user_prompt
        assert "Hello, World!" in result.user_prompt

    def test_user_prompt_contains_recent_commits(self, builder, sample_context):
        """Test that user prompt includes recent commits."""
        result = builder.build(sample_context)

        assert "add initial project structure" in result.user_prompt
        assert "set up CI/CD" in result.user_prompt

    def test_truncate_diff_when_too_long(self, builder, sample_context):
        """Test that diff is truncated when exceeding max length."""
        builder = PromptBuilder(max_diff_length=100)

        # Create context with large diff
        large_context = GitContext(
            repo_root="/test/repo",
            branch_name="main",
            is_dirty=False,
            staged_files=["large.py"],
            diffs=[
                GitDiff(
                    file_path="large.py",
                    old_file=None,
                    new_file="large.py",
                    diff_text="\n".join([f"+line {i}" for i in range(1000)]),
                    is_new_file=True,
                    is_deleted=False,
                    is_renamed=False,
                )
            ],
            diff_summary="1 new file",
            recent_commits=[],
            files_changed=1,
            insertions=1000,
            deletions=0,
        )

        result = builder.build(large_context)

        assert "truncated" in result.user_prompt.lower()

    def test_build_minimal_prompt(self, builder, sample_context):
        """Test building a minimal prompt."""
        result = builder.build_minimal_prompt(sample_context)

        assert isinstance(result, PromptComponents)
        assert len(result.user_prompt) < len(builder.build(sample_context).user_prompt)

    def test_format_recent_commits_empty(self, builder):
        """Test formatting empty recent commits."""
        result = builder._format_recent_commits([])
        assert "none" in result.lower()

    def test_format_recent_commits_limits_to_five(self, builder):
        """Test that recent commits are limited to 5."""
        commits = [f"commit {i}" for i in range(10)]
        result = builder._format_recent_commits(commits)

        assert "commit 1" in result
        assert "commit 5" in result
        assert "commit 6" not in result

    def test_builder_with_single_suggestion(self, sample_context):
        """Test builder configured for single suggestion."""
        builder = PromptBuilder(num_suggestions=1)
        result = builder.build(sample_context)

        assert "1 commit message" in result.system_prompt or "1 suggestion" in result.system_prompt.lower()

    def test_builder_includes_recent_commits_flag(self, sample_context):
        """Test disabling recent commits."""
        builder = PromptBuilder(include_recent_commits=False)
        result = builder.build(sample_context)

        # Should not include detailed commit history
        assert "add initial project structure" not in result.user_prompt


class TestPromptComponents:
    """Tests for PromptComponents dataclass."""

    def test_create_components(self):
        """Test creating PromptComponents."""
        components = PromptComponents(
            system_prompt="You are a helpful assistant.",
            user_prompt="Generate a commit message.",
        )

        assert components.system_prompt == "You are a helpful assistant."
        assert components.user_prompt == "Generate a commit message."
