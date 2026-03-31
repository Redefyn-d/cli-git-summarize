"""
Response Parser Module for git-summarize.

Extracts and validates commit message suggestions from AI responses.
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class CommitSuggestion:
    """A single commit message suggestion."""

    subject: str
    body: Optional[str] = None
    footer: Optional[str] = None
    full_message: str = ""
    commit_type: Optional[str] = None
    scope: Optional[str] = None
    is_valid: bool = True
    validation_errors: list[str] = None

    def __post_init__(self):
        if self.validation_errors is None:
            self.validation_errors = []

        # Build full message if not provided
        if not self.full_message:
            self.full_message = self.subject
            if self.body:
                self.full_message += f"\n\n{self.body}"
            if self.footer:
                self.full_message += f"\n\n{self.footer}"

    def __str__(self) -> str:
        return self.full_message


@dataclass
class ParseResult:
    """Result of parsing an AI response."""

    suggestions: list[CommitSuggestion]
    raw_response: str
    parse_errors: list[str] = None

    def __post_init__(self):
        if self.parse_errors is None:
            self.parse_errors = []

    @property
    def has_suggestions(self) -> bool:
        """Check if any suggestions were parsed."""
        return len(self.suggestions) > 0

    @property
    def valid_suggestions(self) -> list[CommitSuggestion]:
        """Get only valid suggestions."""
        return [s for s in self.suggestions if s.is_valid]


class ResponseParser:
    """
    Parses AI responses to extract commit message suggestions.

    Handles various response formats and validates against
    Conventional Commits specification.
    """

    # Separator patterns for multiple suggestions
    SEPARATORS = [
        r"\n---+\n",  # --- on its own line
        r"\n===+\n",  # === on its own line
        r"\n\*\*\*+\n",  # *** on its own line
        r"\n\d+\.\s+",  # Numbered list (1., 2., etc.)
        r"\nOption\s*\d+",  # Option 1, Option 2, etc.
        r"\nSuggestion\s*\d+",  # Suggestion 1, Suggestion 2, etc.
    ]

    # Conventional commits regex
    CONVENTIONAL_COMMIT_PATTERN = re.compile(
        r"^(?P<type>[a-z]+)"  # Type (required)
        r"(?:\((?P<scope>[^)]+)\))?"  # Scope (optional)
        r":\s+"  # Colon separator
        r"(?P<description>.+)$",  # Description (required)
        re.MULTILINE,
    )

    # Valid commit types per Conventional Commits
    VALID_TYPES = {
        "feat",
        "fix",
        "docs",
        "style",
        "refactor",
        "perf",
        "test",
        "chore",
        "ci",
        "build",
        "revert",
    }

    def parse(self, response_text: str) -> ParseResult:
        """
        Parse AI response and extract commit suggestions.

        Args:
            response_text: Raw response text from AI

        Returns:
            ParseResult with extracted suggestions
        """
        errors = []
        suggestions = []

        # Clean up the response
        cleaned = self._clean_response(response_text)

        # Try to split into multiple suggestions
        raw_suggestions = self._split_suggestions(cleaned)

        for raw in raw_suggestions:
            suggestion = self._parse_single_suggestion(raw.strip())
            if suggestion:
                suggestions.append(suggestion)

        # If no suggestions found, try treating entire response as one
        if not suggestions and cleaned.strip():
            suggestion = self._parse_single_suggestion(cleaned.strip())
            if suggestion:
                suggestions.append(suggestion)
            else:
                errors.append("Could not parse any commit messages from response")
        elif not suggestions and not cleaned.strip():
            errors.append("Empty response received")

        return ParseResult(
            suggestions=suggestions,
            raw_response=response_text,
            parse_errors=errors,
        )

    def _clean_response(self, text: str) -> str:
        """Clean up AI response text."""
        # Remove markdown code blocks
        text = re.sub(r"```(?:commit)?\s*\n?", "", text)
        text = re.sub(r"```\s*\n?", "", text)

        # Remove common prefixes
        text = re.sub(r"^(Here are|Here's|I've generated|Generated)\s*(some\s*)?commit messages?\s*[:\.]?\s*\n?", "", text, flags=re.IGNORECASE)

        # Remove "Suggestion:" prefixes
        text = re.sub(r"^\s*Suggestion\s*\d*\s*:\s*", "", text, flags=re.MULTILINE)

        # Normalize line endings
        text = text.replace("\r\n", "\n")

        return text.strip()

    def _split_suggestions(self, text: str) -> list[str]:
        """Split text into individual suggestions."""
        # Try each separator pattern
        for pattern in self.SEPARATORS:
            parts = re.split(pattern, text, flags=re.IGNORECASE)
            if len(parts) > 1:
                # Filter empty parts
                return [p.strip() for p in parts if p.strip()]

        # No separator found, return as single suggestion
        return [text]

    def _parse_single_suggestion(self, text: str) -> Optional[CommitSuggestion]:
        """Parse a single commit message from text."""
        if not text.strip():
            return None

        lines = text.strip().split("\n")
        subject = lines[0].strip()

        # Parse subject line
        match = self.CONVENTIONAL_COMMIT_PATTERN.match(subject)
        if not match:
            # Try to extract what we can
            return self._create_fallback_suggestion(text)

        commit_type = match.group("type")
        scope = match.group("scope")
        description = match.group("description")

        # Validate type
        errors = []
        if commit_type not in self.VALID_TYPES:
            errors.append(f"Invalid commit type: {commit_type}")

        # Validate subject length
        if len(subject) > 72:
            errors.append(f"Subject line exceeds 72 characters ({len(subject)} chars)")

        # Check for period at end
        if description.rstrip().endswith("."):
            errors.append("Subject line should not end with a period")

        # Extract body and footer
        body = None
        footer = None

        if len(lines) > 1:
            # Find blank line separating body from footer
            body_lines = []
            footer_lines = []
            in_footer = False

            for line in lines[1:]:
                stripped = line.strip()
                if not stripped:
                    if body_lines and not in_footer:
                        in_footer = True
                    continue

                if in_footer:
                    footer_lines.append(stripped)
                else:
                    body_lines.append(stripped)

            if body_lines:
                body = "\n".join(body_lines)
            if footer_lines:
                footer = "\n".join(footer_lines)

        return CommitSuggestion(
            subject=subject,
            body=body,
            footer=footer,
            commit_type=commit_type,
            scope=scope,
            is_valid=len(errors) == 0,
            validation_errors=errors,
        )

    def _create_fallback_suggestion(self, text: str) -> CommitSuggestion:
        """Create a suggestion when parsing fails."""
        lines = text.strip().split("\n")
        subject = lines[0].strip()

        body = None
        if len(lines) > 1:
            body_lines = [l.strip() for l in lines[1:] if l.strip()]
            if body_lines:
                body = "\n".join(body_lines)

        return CommitSuggestion(
            subject=subject,
            body=body,
            is_valid=False,
            validation_errors=["Does not follow Conventional Commits format"],
        )

    def validate_commit_message(self, message: str) -> tuple[bool, list[str]]:
        """
        Validate a commit message against Conventional Commits.

        Args:
            message: Commit message to validate

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        lines = message.strip().split("\n")

        if not lines:
            return False, ["Empty commit message"]

        subject = lines[0]

        # Check format
        match = self.CONVENTIONAL_COMMIT_PATTERN.match(subject)
        if not match:
            errors.append("Subject does not follow Conventional Commits format")
            return False, errors

        commit_type = match.group("type")

        # Validate type
        if commit_type not in self.VALID_TYPES:
            errors.append(f"Invalid commit type: {commit_type}")

        # Check subject length
        if len(subject) > 72:
            errors.append(f"Subject line too long ({len(subject)} > 72 chars)")

        # Check for period
        if subject.rstrip().endswith("."):
            errors.append("Subject should not end with a period")

        # Check for lowercase type
        if commit_type != commit_type.lower():
            errors.append("Commit type should be lowercase")

        return len(errors) == 0, errors

    def format_for_display(self, suggestion: CommitSuggestion, index: int = 0) -> str:
        """
        Format a suggestion for display in the UI.

        Args:
            suggestion: Commit suggestion to format
            index: Optional index number for display

        Returns:
            Formatted string for display
        """
        prefix = f"[{index + 1}] " if index > 0 else ""

        # Highlight the subject
        result = f"{prefix}{suggestion.subject}"

        if suggestion.body:
            result += f"\n\n{suggestion.body}"

        if suggestion.footer:
            result += f"\n\n{suggestion.footer}"

        if not suggestion.is_valid and suggestion.validation_errors:
            errors = ", ".join(suggestion.validation_errors)
            result += f"\n⚠️  {errors}"

        return result
