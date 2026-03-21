"""
Tests for the Response Parser module.
"""

import pytest

from git_summarize.parser import CommitSuggestion, ParseResult, ResponseParser


class TestCommitSuggestion:
    """Tests for CommitSuggestion dataclass."""

    def test_create_simple_suggestion(self):
        """Test creating a basic commit suggestion."""
        suggestion = CommitSuggestion(
            subject="feat(auth): add login functionality",
            commit_type="feat",
            scope="auth",
        )

        assert suggestion.subject == "feat(auth): add login functionality"
        assert suggestion.commit_type == "feat"
        assert suggestion.scope == "auth"
        assert suggestion.is_valid is True
        assert suggestion.full_message == "feat(auth): add login functionality"

    def test_create_suggestion_with_body(self):
        """Test creating a suggestion with body."""
        suggestion = CommitSuggestion(
            subject="fix(api): resolve null pointer exception",
            body="Fixed NPE in UserService when user email is null.",
            commit_type="fix",
            scope="api",
        )

        assert "Fixed NPE" in suggestion.full_message
        assert suggestion.body is not None

    def test_create_suggestion_with_footer(self):
        """Test creating a suggestion with footer."""
        suggestion = CommitSuggestion(
            subject="docs: update README",
            footer="Closes #123",
            commit_type="docs",
        )

        assert "Closes #123" in suggestion.full_message

    def test_invalid_suggestion(self):
        """Test creating an invalid suggestion."""
        suggestion = CommitSuggestion(
            subject="Fixed some stuff",
            is_valid=False,
            validation_errors=["Does not follow Conventional Commits format"],
        )

        assert suggestion.is_valid is False
        assert len(suggestion.validation_errors) == 1

    def test_str_representation(self):
        """Test string representation."""
        suggestion = CommitSuggestion(
            subject="chore: update dependencies",
        )

        assert str(suggestion) == "chore: update dependencies"


class TestResponseParser:
    """Tests for ResponseParser class."""

    @pytest.fixture
    def parser(self):
        """Create a parser instance."""
        return ResponseParser()

    def test_parse_single_suggestion(self, parser):
        """Test parsing a single commit message."""
        response = "feat(parser): add support for nested expressions"

        result = parser.parse(response)

        assert result.has_suggestions is True
        assert len(result.suggestions) == 1
        assert result.suggestions[0].commit_type == "feat"
        assert result.suggestions[0].scope == "parser"

    def test_parse_multiple_suggestions_with_separator(self, parser):
        """Test parsing multiple suggestions separated by ---."""
        response = """feat(core): add new feature

Description of the feature.
---
fix(core): fix existing bug

Description of the fix.
---
refactor(core): improve code structure

Description of refactor."""

        result = parser.parse(response)

        assert result.has_suggestions is True
        assert len(result.suggestions) == 3
        assert result.suggestions[0].commit_type == "feat"
        assert result.suggestions[1].commit_type == "fix"
        assert result.suggestions[2].commit_type == "refactor"

    def test_parse_with_markdown_code_blocks(self, parser):
        """Test parsing response with markdown code blocks."""
        response = """```
feat(ui): add dark mode support

Implemented dark mode with CSS variables.
```"""

        result = parser.parse(response)

        assert result.has_suggestions is True
        assert "feat(ui)" in result.suggestions[0].subject

    def test_parse_invalid_format(self, parser):
        """Test parsing invalid commit message format."""
        response = "I fixed some bugs and added features"

        result = parser.parse(response)

        assert result.has_suggestions is True
        assert result.suggestions[0].is_valid is False

    def test_parse_empty_response(self, parser):
        """Test parsing empty response."""
        result = parser.parse("")

        assert result.has_suggestions is False
        # Empty response returns no suggestions (may or may not have errors)
        assert len(result.suggestions) == 0

    def test_parse_with_numbered_list(self, parser):
        """Test parsing suggestions in numbered list format."""
        response = """1. feat(api): add endpoint

2. fix(api): fix validation

3. docs(api): update docs"""

        result = parser.parse(response)

        assert len(result.suggestions) == 3

    def test_validate_valid_commit_message(self, parser):
        """Test validating a valid commit message."""
        message = "feat(auth): add OAuth2 support"

        is_valid, errors = parser.validate_commit_message(message)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_invalid_type(self, parser):
        """Test validating commit with invalid type."""
        message = "feature(auth): add OAuth2 support"

        is_valid, errors = parser.validate_commit_message(message)

        assert is_valid is False
        assert any("Invalid commit type" in e for e in errors)

    def test_validate_subject_too_long(self, parser):
        """Test validating commit with long subject."""
        message = "feat(auth): " + "a" * 100

        is_valid, errors = parser.validate_commit_message(message)

        assert is_valid is False
        assert any("too long" in e for e in errors)

    def test_validate_subject_with_period(self, parser):
        """Test validating commit with period at end."""
        message = "feat(auth): add OAuth2 support."

        is_valid, errors = parser.validate_commit_message(message)

        assert is_valid is False
        assert any("period" in e for e in errors)

    def test_all_valid_commit_types(self, parser):
        """Test all valid conventional commit types."""
        types = ["feat", "fix", "docs", "style", "refactor", "perf", "test", "chore", "ci", "build", "revert"]

        for commit_type in types:
            message = f"{commit_type}: test message"
            is_valid, errors = parser.validate_commit_message(message)
            assert is_valid is True, f"Type {commit_type} should be valid"

    def test_parse_suggestion_with_body_and_footer(self, parser):
        """Test parsing suggestion with body and footer."""
        response = """feat(core): add caching layer

Implemented Redis-based caching for improved performance.
Added cache invalidation on data updates.

Closes #456
Fixes #123"""

        result = parser.parse(response)

        assert result.has_suggestions is True
        suggestion = result.suggestions[0]
        assert suggestion.body is not None
        assert "Redis" in suggestion.body
        assert suggestion.footer is not None
        assert "Closes #456" in suggestion.footer


class TestParseResult:
    """Tests for ParseResult dataclass."""

    def test_has_suggestions_true(self):
        """Test has_suggestions property when suggestions exist."""
        result = ParseResult(
            suggestions=[CommitSuggestion(subject="feat: test")],
            raw_response="feat: test",
        )

        assert result.has_suggestions is True

    def test_has_suggestions_false(self):
        """Test has_suggestions property when no suggestions."""
        result = ParseResult(
            suggestions=[],
            raw_response="",
        )

        assert result.has_suggestions is False

    def test_valid_suggestions_filter(self):
        """Test that valid_suggestions filters invalid ones."""
        result = ParseResult(
            suggestions=[
                CommitSuggestion(subject="feat: valid", is_valid=True),
                CommitSuggestion(subject="invalid", is_valid=False),
                CommitSuggestion(subject="fix: also valid", is_valid=True),
            ],
            raw_response="test",
        )

        valid = result.valid_suggestions
        assert len(valid) == 2
        assert all(s.is_valid for s in valid)
