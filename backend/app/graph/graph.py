"""LangGraph state machine definition."""

from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.schemas.state import PRReviewState
from app.graph.nodes import (
    node_fetch_pr,
    node_analyse_size,
    node_summarise_only,
    node_check_style,
    node_check_logic,
    node_check_tests,
    node_draft_review,
    node_post_comment,
    node_revise,
)


def route_after_size(state: PRReviewState) -> Literal["summarise_only", "check_style"]:
    if state.error:
        return END
    return "summarise_only" if state.is_large_pr else "check_style"


def route_after_checkpoint(state: PRReviewState) -> Literal["post_comment", "revise", "__end__"]:
    decision = state.human_decision
    if decision == "approved":
        return "post_comment"
    if decision == "rejected":
        return "revise"
    return "__end__"  # abandoned


def build_graph():
    builder = StateGraph(PRReviewState)

    builder.add_node("fetch_pr", node_fetch_pr)
    builder.add_node("analyse_size", node_analyse_size)
    builder.add_node("summarise_only", node_summarise_only)
    builder.add_node("check_style", node_check_style)
    builder.add_node("check_logic", node_check_logic)
    builder.add_node("check_tests", node_check_tests)
    builder.add_node("draft_review", node_draft_review)
    builder.add_node("post_comment", node_post_comment)
    builder.add_node("revise", node_revise)

    builder.set_entry_point("fetch_pr")
    builder.add_edge("fetch_pr", "analyse_size")
    builder.add_conditional_edges("analyse_size", route_after_size)

    # Large PR path
    builder.add_edge("summarise_only", "draft_review")

    # Full review path
    builder.add_edge("check_style", "check_logic")
    builder.add_edge("check_logic", "check_tests")
    builder.add_edge("check_tests", "draft_review")

    # Human-in-the-loop interrupt before posting
    builder.add_edge("draft_review", END)

    # After human decision
    builder.add_node("human_router", lambda s: s)  # pass-through
    builder.add_conditional_edges("human_router", route_after_checkpoint)
    builder.add_edge("post_comment", END)
    builder.add_edge("revise", "draft_review")

    checkpointer = MemorySaver()
    return builder.compile(
        checkpointer=checkpointer,
        interrupt_after=["draft_review"],
    )


graph = build_graph()
