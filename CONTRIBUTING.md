# Contributing

## Setup

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Running tests

```bash
pytest tests/
```

## Adding a new review node

1. Add node function to `app/graph/nodes.py`
2. Register node in `app/graph/graph.py` via `builder.add_node()`
3. Wire edges in `build_graph()`
4. Add tests in `backend/tests/`

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Claude API key |
| `GITHUB_TOKEN` | Yes | PAT with `repo` scope |
| `FAST_MODEL` | No | Defaults to Claude Haiku |
| `SMART_MODEL` | No | Defaults to Claude Sonnet |
