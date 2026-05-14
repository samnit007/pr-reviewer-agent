# PR Reviewer Agent

> A LangGraph agent that reviews GitHub pull requests — fetches the diff, analyses style, logic, and test coverage through specialised nodes, drafts a review, then pauses for human approval before posting.

**Status:** Week 4 — backend state machine complete, frontend in progress.

## State machine

```
START → fetch_pr → analyse_diff_size
                        ↓               ↓
                  (large PR)      (normal PR)
                  summarise_only  check_style → check_logic → check_tests
                        ↓               ↓
                    draft_review ←──────┘
                        ↓
              ⏸ HUMAN APPROVAL CHECKPOINT
               ↙          ↓          ↘
          approved      rejected    abandoned
             ↓             ↓            ↓
       post_comment      revise        END
             ↓             ↓
            END       draft_review (loop)
```

## Stack

| Layer | Choice |
|---|---|
| Agent orchestration | LangGraph (StateGraph + MemorySaver checkpointing) |
| LLM | Claude Haiku (style/tests) + Sonnet (logic/draft — higher stakes) |
| GitHub integration | PyGithub — fetch diff, post review comments |
| Backend | FastAPI |
| Frontend | Vue 3 + TypeScript + Tailwind |

## Run locally

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in ANTHROPIC_API_KEY and GITHUB_TOKEN
uvicorn app.main:app --reload --port 8000
```
