"""GitHub API tool — fetch PR data and post review comments."""

import re
from github import Github
from app.config import settings

_gh = Github(settings.github_token)


def parse_pr_url(url: str) -> tuple[str, int]:
    """Extract 'owner/repo' and PR number from a GitHub PR URL."""
    match = re.search(r"github\.com/([^/]+/[^/]+)/pull/(\d+)", url)
    if not match:
        raise ValueError(f"Invalid GitHub PR URL: {url}")
    return match.group(1), int(match.group(2))


def fetch_pr(repo_name: str, pr_number: int) -> dict:
    """Return PR metadata + unified diff."""
    repo = _gh.get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    files = list(pr.get_files())
    diff_parts = []
    for f in files:
        diff_parts.append(f"### {f.filename} (+{f.additions} -{f.deletions})")
        if f.patch:
            diff_parts.append(f.patch)

    return {
        "title": pr.title,
        "description": pr.body or "",
        "diff": "\n".join(diff_parts),
        "files_changed": [f.filename for f in files],
        "additions": pr.additions,
        "deletions": pr.deletions,
    }


def post_review(repo_name: str, pr_number: int, body: str) -> str:
    """Post a review comment on the PR. Returns the review URL."""
    repo = _gh.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    review = pr.create_review(body=body, event="COMMENT")
    return review.html_url
