"""
Git Operations Module for git-summarize.

Provides git command wrappers for staging, committing, and pushing changes.
"""

import subprocess
from typing import List, Optional, Tuple

from rich.console import Console

console = Console()


class GitOpsError(Exception):
    """Exception raised for Git operations errors."""

    def __init__(self, message: str, command: Optional[str] = None, stderr: Optional[str] = None):
        self.message = message
        self.command = command
        self.stderr = stderr
        super().__init__(self.message)


class GitOps:
    """Git operations helper class."""

    def __init__(self, repo_path: Optional[str] = None):
        """
        Initialize Git operations.

        Args:
            repo_path: Path to Git repository (default: current directory)
        """
        self.repo_path = repo_path

    def _run_git(
        self,
        args: List[str],
        capture_output: bool = True,
        check: bool = True,
    ) -> subprocess.CompletedProcess:
        """
        Run a Git command.

        Args:
            args: Git command arguments (without 'git')
            capture_output: Whether to capture stdout/stderr
            check: Whether to raise on non-zero exit code

        Returns:
            CompletedProcess instance

        Raises:
            GitOpsError: If command fails and check=True
        """
        cmd = ["git"] + args

        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                check=False,
                cwd=self.repo_path,
            )

            if check and result.returncode != 0:
                raise GitOpsError(
                    f"Git command failed: {' '.join(args)}",
                    command=' '.join(args),
                    stderr=result.stderr.strip(),
                )

            return result

        except subprocess.SubprocessError as e:
            raise GitOpsError(
                f"Failed to run git command: {str(e)}",
                command=' '.join(args),
            )

    def stage_all(self) -> bool:
        """
        Stage all changes (git add .).

        Returns:
            True if successful, False otherwise
        """
        try:
            self._run_git(["add", "."])
            console.print("[green]✓[/green] Staged all changes")
            return True
        except GitOpsError as e:
            console.print(f"[red]✗ Failed to stage changes:[/red] {e.stderr}")
            return False

    def stage_files(self, files: List[str]) -> bool:
        """
        Stage specific files.

        Args:
            files: List of file paths to stage

        Returns:
            True if successful, False otherwise
        """
        try:
            self._run_git(["add"] + files)
            return True
        except GitOpsError as e:
            console.print(f"[red]✗ Failed to stage files:[/red] {e.stderr}")
            return False

    def commit(self, message: str) -> Tuple[bool, str]:
        """
        Create a commit with the given message.

        Args:
            message: Commit message

        Returns:
            Tuple of (success, output/error message)
        """
        try:
            result = self._run_git(["commit", "-m", message])
            output = result.stdout.strip()
            console.print(f"[green]✓[/green] Committed: {message[:50]}...")
            return True, output
        except GitOpsError as e:
            error_msg = e.stderr or e.message
            return False, error_msg

    def get_current_branch(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Get the current branch name.

        Returns:
            Tuple of (branch_name, error_message)
        """
        try:
            result = self._run_git(["rev-parse", "--abbrev-ref", "HEAD"])
            branch = result.stdout.strip()
            return branch, None
        except GitOpsError as e:
            return None, e.stderr or e.message

    def get_remote_branches(self) -> List[str]:
        """
        Get list of remote branches.

        Returns:
            List of remote branch names
        """
        try:
            result = self._run_git(["branch", "-r"])
            branches = []
            for line in result.stdout.strip().split("\n"):
                line = line.strip()
                if line and "->" not in line:  # Skip symbolic refs
                    # Remove remote prefix (e.g., origin/)
                    if "/" in line:
                        branch = line.split("/", 1)[1]
                        branches.append(branch)
            return branches
        except GitOpsError:
            return []

    def has_remote(self) -> bool:
        """
        Check if repository has a remote configured.

        Returns:
            True if remote exists, False otherwise
        """
        try:
            result = self._run_git(["remote"], check=False)
            return bool(result.stdout.strip())
        except GitOpsError:
            return False

    def get_default_remote(self) -> Optional[str]:
        """
        Get the default remote name (origin or first remote).

        Returns:
            Remote name or None
        """
        try:
            result = self._run_git(["remote"])
            remotes = result.stdout.strip().split("\n")
            if not remotes or not remotes[0]:
                return None
            # Prefer 'origin' if it exists
            if "origin" in remotes:
                return "origin"
            return remotes[0]
        except GitOpsError:
            return None

    def push(
        self,
        branch: str,
        remote: Optional[str] = None,
        set_upstream: bool = False,
    ) -> Tuple[bool, str]:
        """
        Push changes to remote.

        Args:
            branch: Branch name to push
            remote: Remote name (default: origin)
            set_upstream: Whether to set upstream tracking

        Returns:
            Tuple of (success, output/error message)
        """
        if not remote:
            remote = self.get_default_remote()
            if not remote:
                return False, "No remote configured. Please add a remote with 'git remote add origin <url>'"

        args = ["push"]

        if set_upstream:
            args.extend(["-u", remote, branch])
        else:
            args.extend([remote, branch])

        try:
            result = self._run_git(args)
            output = result.stdout.strip()
            return True, output
        except GitOpsError as e:
            error_msg = e.stderr or e.message
            return False, error_msg

    def pull(self, rebase: bool = True) -> Tuple[bool, str]:
        """
        Pull changes from remote.

        Args:
            rebase: Whether to use rebase

        Returns:
            Tuple of (success, output/error message)
        """
        args = ["pull"]
        if rebase:
            args.append("--rebase")
        
        try:
            result = self._run_git(args)
            output = result.stdout.strip()
            return True, output
        except GitOpsError as e:
            return False, e.stderr or e.message

    def is_ahead(self, branch: str) -> bool:
        """
        Check if local branch is ahead of remote.

        Args:
            branch: Branch name

        Returns:
            True if ahead, False otherwise
        """
        try:
            remote = self.get_default_remote()
            if not remote:
                return False

            result = self._run_git(
                ["rev-list", "--count", f"{remote}/{branch}..HEAD"],
                check=False,
            )
            count = int(result.stdout.strip())
            return count > 0
        except (GitOpsError, ValueError):
            return False

    def get_status(self) -> str:
        """
        Get short Git status.

        Returns:
            Git status output
        """
        try:
            result = self._run_git(["status", "--short"])
            return result.stdout.strip()
        except GitOpsError:
            return ""


def commit_changes(message: str, repo_path: Optional[str] = None) -> bool:
    """
    Create a Git commit with the given message.

    Args:
        message: Commit message
        repo_path: Optional repository path

    Returns:
        True if successful, False otherwise
    """
    git = GitOps(repo_path)
    success, _ = git.commit(message)
    return success


def push_changes(
    branch: str,
    remote: Optional[str] = None,
    set_upstream: bool = False,
    repo_path: Optional[str] = None,
) -> bool:
    """
    Push changes to remote.

    Args:
        branch: Branch name
        remote: Remote name
        set_upstream: Whether to set upstream
        repo_path: Optional repository path

    Returns:
        True if successful, False otherwise
    """
    git = GitOps(repo_path)
    success, _ = git.push(branch, remote, set_upstream)
    return success
