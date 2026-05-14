from typing import Optional, List
from pydantic import BaseModel


class ReviewComment(BaseModel):
    path: str
    line: Optional[int] = None
    body: str
    severity: str  # info | warning | error


class PRReviewState(BaseModel):
    # Input
    pr_url: str
    repo: str = ""
    pr_number: int = 0

    # Fetched PR data
    title: str = ""
    description: str = ""
    diff: str = ""
    files_changed: List[str] = []
    additions: int = 0
    deletions: int = 0

    # Analysis flags
    is_large_pr: bool = False       # > 500 lines changed

    # Review findings
    style_comments: List[ReviewComment] = []
    logic_comments: List[ReviewComment] = []
    test_comments: List[ReviewComment] = []

    # Draft
    draft_review: str = ""
    all_comments: List[ReviewComment] = []

    # Human checkpoint
    human_decision: Optional[str] = None   # approved | rejected | abandoned
    human_feedback: Optional[str] = None

    # Execution metadata
    current_node: str = ""
    token_cost_usd: float = 0.0
    error: Optional[str] = None
    run_id: str = ""
