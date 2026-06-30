"""GitHub client: create issues and code-generation pull requests."""
from __future__ import annotations

from dataclasses import dataclass

from pipeline.config import Config
from pipeline.retry import with_backoff


@dataclass
class CreatedIssue:
    number: int
    url: str
    title: str


@dataclass
class CreatedPullRequest:
    number: int
    url: str
    branch: str


class GitHubClient:
    def __init__(self, config: Config):
        config.require("github_token", "github_repo_owner", "github_repo_name")
        self._config = config
        self._repo = None

    def _get_repo(self):
        if self._repo is not None:
            return self._repo
        from github import Github

        gh = Github(self._config.github_token)
        self._repo = gh.get_repo(f"{self._config.github_repo_owner}/{self._config.github_repo_name}")
        return self._repo

    @with_backoff(attempts=4)
    def create_issue(
        self, *, title: str, body: str, labels: list[str] | None = None
    ) -> CreatedIssue:
        repo = self._get_repo()
        issue = repo.create_issue(title=title, body=body, labels=labels or [])
        return CreatedIssue(number=issue.number, url=issue.html_url, title=issue.title)

    @with_backoff(attempts=4)
    def create_branch(self, branch_name: str, base_branch: str = "main") -> None:
        repo = self._get_repo()
        base = repo.get_branch(base_branch)
        repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base.commit.sha)

    @with_backoff(attempts=4)
    def write_file(self, *, branch: str, path: str, content: str, message: str) -> None:
        repo = self._get_repo()
        try:
            existing = repo.get_contents(path, ref=branch)
            repo.update_file(path, message, content, existing.sha, branch=branch)
        except Exception:  # noqa: BLE001 - file genuinely doesn't exist on this branch yet
            repo.create_file(path, message, content, branch=branch)

    @with_backoff(attempts=4)
    def create_pull_request(
        self, *, branch: str, title: str, body: str, base_branch: str = "main"
    ) -> CreatedPullRequest:
        repo = self._get_repo()
        pr = repo.create_pull(title=title, body=body, head=branch, base=base_branch, draft=False)
        return CreatedPullRequest(number=pr.number, url=pr.html_url, branch=branch)
