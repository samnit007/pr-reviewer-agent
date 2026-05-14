"""LangGraph node functions. Each receives and returns PRReviewState."""

from app.schemas.state import PRReviewState, ReviewComment
from app.tools.github import parse_pr_url, fetch_pr, post_review
from app.llm.client import complete

LARGE_PR_THRESHOLD = 500  # lines


def node_fetch_pr(state: PRReviewState) -> dict:
    try:
        repo, pr_number = parse_pr_url(state.pr_url)
        data = fetch_pr(repo, pr_number)
        return {
            "repo": repo,
            "pr_number": pr_number,
            "title": data["title"],
            "description": data["description"],
            "diff": data["diff"],
            "files_changed": data["files_changed"],
            "additions": data["additions"],
            "deletions": data["deletions"],
            "current_node": "fetch_pr",
        }
    except Exception as e:
        return {"error": str(e), "current_node": "fetch_pr"}


def node_analyse_size(state: PRReviewState) -> dict:
    total = state.additions + state.deletions
    return {
        "is_large_pr": total > LARGE_PR_THRESHOLD,
        "current_node": "analyse_size",
    }


def node_summarise_only(state: PRReviewState) -> dict:
    """For large PRs: produce high-level summary instead of line-by-line review."""
    system = "You are a senior engineer. Summarise this large PR concisely."
    user = f"PR: {state.title}\n\nDescription: {state.description}\n\nDiff (truncated):\n{state.diff[:4000]}"
    text, cost = complete(system, user)
    summary = f"**Large PR Summary** ({state.additions + state.deletions} lines changed)\n\n{text}"
    return {
        "draft_review": summary,
        "token_cost_usd": state.token_cost_usd + cost,
        "current_node": "summarise_only",
    }


def node_check_style(state: PRReviewState) -> dict:
    system = """You are a code style reviewer. Identify style issues: naming conventions,
formatting, dead code, magic numbers, overly long functions.
Return a JSON array of objects: [{"path": "file.py", "line": 42, "body": "issue description", "severity": "warning"}]
Return [] if no issues. Return ONLY the JSON array."""
    user = f"PR: {state.title}\n\nDiff:\n{state.diff[:5000]}"
    text, cost = complete(system, user)
    comments = _parse_comments(text)
    return {
        "style_comments": comments,
        "token_cost_usd": state.token_cost_usd + cost,
        "current_node": "check_style",
    }


def node_check_logic(state: PRReviewState) -> dict:
    system = """You are a senior engineer reviewing for logic bugs. Look for:
off-by-one errors, unhandled edge cases, incorrect conditionals, race conditions, security issues.
Return a JSON array: [{"path": "file.py", "line": 42, "body": "issue description", "severity": "error"}]
Return [] if no issues. Return ONLY the JSON array."""
    user = f"PR: {state.title}\n\nDiff:\n{state.diff[:5000]}"
    text, cost = complete(system, user, smart=True)
    comments = _parse_comments(text)
    return {
        "logic_comments": comments,
        "token_cost_usd": state.token_cost_usd + cost,
        "current_node": "check_logic",
    }


def node_check_tests(state: PRReviewState) -> dict:
    system = """You are reviewing test coverage for a PR. Check:
Are new functions tested? Are edge cases covered? Are tests meaningful (not just happy-path)?
Return a JSON array: [{"path": "file.py", "line": null, "body": "coverage concern", "severity": "info"}]
Return [] if coverage looks adequate. Return ONLY the JSON array."""
    user = f"PR: {state.title}\nFiles changed: {', '.join(state.files_changed)}\n\nDiff:\n{state.diff[:4000]}"
    text, cost = complete(system, user)
    comments = _parse_comments(text)
    return {
        "test_comments": comments,
        "token_cost_usd": state.token_cost_usd + cost,
        "current_node": "check_tests",
    }


def node_draft_review(state: PRReviewState) -> dict:
    all_comments = state.style_comments + state.logic_comments + state.test_comments

    system = """You are a senior engineer writing a pull request review.
Be direct, constructive, and specific. Structure: brief summary paragraph, then key findings.
Reference specific files/lines where relevant."""
    findings = "\n".join(
        f"- [{c.severity.upper()}] {c.path}: {c.body}" for c in all_comments
    ) or "No specific issues found."
    user = f"""PR: {state.title}
Description: {state.description}
Files changed: {', '.join(state.files_changed)}

Findings from automated analysis:
{findings}

Write a review comment to post on the PR."""

    text, cost = complete(system, user, smart=True)
    return {
        "draft_review": text,
        "all_comments": all_comments,
        "token_cost_usd": state.token_cost_usd + cost,
        "current_node": "draft_review",
    }


def node_post_comment(state: PRReviewState) -> dict:
    try:
        url = post_review(state.repo, state.pr_number, state.draft_review)
        return {"current_node": "post_comment", "error": None}
    except Exception as e:
        return {"current_node": "post_comment", "error": f"Failed to post: {e}"}


def node_revise(state: PRReviewState) -> dict:
    system = "You are revising a PR review based on human feedback. Rewrite the review addressing the feedback."
    user = f"""Original review:
{state.draft_review}

Human feedback:
{state.human_feedback or 'Please improve the review.'}

Rewrite the review."""
    text, cost = complete(system, user, smart=True)
    return {
        "draft_review": text,
        "human_decision": None,
        "token_cost_usd": state.token_cost_usd + cost,
        "current_node": "revise",
    }


def _parse_comments(text: str) -> list[ReviewComment]:
    import json, re
    text = text.strip()
    match = re.search(r"\[[\s\S]*\]", text)
    if not match:
        return []
    try:
        items = json.loads(match.group())
        return [ReviewComment(**item) for item in items if isinstance(item, dict)]
    except Exception:
        return []
