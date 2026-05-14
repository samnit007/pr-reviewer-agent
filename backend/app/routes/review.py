import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.graph.graph import graph
from app.schemas.state import PRReviewState

router = APIRouter()


class StartRequest(BaseModel):
    pr_url: str


class DecisionRequest(BaseModel):
    run_id: str
    decision: str        # approved | rejected | abandoned
    feedback: Optional[str] = None


def _config(run_id: str) -> dict:
    return {"configurable": {"thread_id": run_id}}


@router.post("/review/start")
def start_review(req: StartRequest):
    run_id = str(uuid.uuid4())
    initial = PRReviewState(pr_url=req.pr_url, run_id=run_id)

    result = graph.invoke(initial.model_dump(), config=_config(run_id))

    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])

    return {
        "run_id": run_id,
        "status": "awaiting_approval",
        "title": result.get("title"),
        "files_changed": result.get("files_changed", []),
        "additions": result.get("additions", 0),
        "deletions": result.get("deletions", 0),
        "is_large_pr": result.get("is_large_pr", False),
        "draft_review": result.get("draft_review"),
        "comment_count": len(result.get("all_comments", [])),
        "token_cost_usd": result.get("token_cost_usd", 0),
        "nodes_visited": _visited_nodes(result),
    }


@router.post("/review/decide")
def decide(req: DecisionRequest):
    if req.decision not in ("approved", "rejected", "abandoned"):
        raise HTTPException(status_code=400, detail="decision must be approved | rejected | abandoned")

    state_update = {
        "human_decision": req.decision,
        "human_feedback": req.feedback,
    }
    graph.update_state(_config(req.run_id), state_update, as_node="human_router")
    result = graph.invoke(None, config=_config(req.run_id))

    return {
        "run_id": req.run_id,
        "decision": req.decision,
        "status": "posted" if req.decision == "approved" else "revised" if req.decision == "rejected" else "abandoned",
        "draft_review": result.get("draft_review"),
        "token_cost_usd": result.get("token_cost_usd", 0),
        "error": result.get("error"),
    }


@router.get("/review/{run_id}")
def get_state(run_id: str):
    state = graph.get_state(_config(run_id))
    if not state or not state.values:
        raise HTTPException(status_code=404, detail="Run not found")
    return state.values


def _visited_nodes(state: dict) -> list[str]:
    nodes = ["fetch_pr", "analyse_size"]
    if state.get("is_large_pr"):
        nodes.append("summarise_only")
    else:
        nodes += ["check_style", "check_logic", "check_tests"]
    nodes.append("draft_review")
    return nodes
