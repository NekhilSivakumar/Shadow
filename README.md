# Digital Twin — Hackathon Scaffold

Two-person build: Person B (brain/agent) + Person A (body/control layer),
merging over a shared, frozen contract in `shared/contracts.py`.

## Structure

```
digital-twin/
├── shared/            # Owned jointly — treat contracts.py as frozen
│   ├── contracts.py   # AgentAction / ActionResult / TwinStatus
│   └── config.py
├── brain/             # Person B's folder only
│   ├── agent_loop.py
│   ├── memory/
│   ├── connectors/
│   ├── onboarding/
│   └── api/
├── body/              # Person A's folder only
│   └── control_layer.py   # stub — Person A replaces with real implementation
├── .env.example
└── requirements.txt
```

## Setup

```bash
python -m venv venv
source venv/bin/activate      # venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env          # fill in real keys
```

## Running (two separate processes)

Brain (Person B):
```bash
uvicorn brain.api.main:app --reload --port 8000
```

Body (Person A — stub included, swap in the real control layer):
```bash
uvicorn body.control_layer:app --reload --port 8001
```

## Testing the seam without waiting on the other person

Brain side, with a fake ActionResult:
```bash
curl -X POST http://localhost:8000/start-task \
  -H "Content-Type: application/json" \
  -d '"open notion and check my tasks"'
```

Body side, with a fake AgentAction:
```bash
curl -X POST http://localhost:8001/execute \
  -H "Content-Type: application/json" \
  -d '{"action_id":"test-1","type":"screenshot"}'
```

## Git workflow

- Branch: `person-a-body` / `person-b-brain`, off `main`.
- Only edit your own top-level folder. Only touch `shared/contracts.py`
  together, on a call.
- Rebase onto `main` before opening a PR so contract drift shows up as a
  merge conflict immediately, not a runtime bug later.
